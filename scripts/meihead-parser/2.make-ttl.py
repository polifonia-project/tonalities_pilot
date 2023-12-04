# grep -rh "2<" . | grep referenceKey | awk '{$1=$1};1' | sort | uniq
# TODO <referenceKey language="LAT" primary="true">OTL2</referenceKey>
# TODO <referenceKey>CDT2</referenceKey>
# TODO <referenceKey>COA2</referenceKey>
# TODO <referenceKey>COM2</referenceKey>
# TODO <referenceKey>OTL2</referenceKey>

import html
import json
import pandas
from pprint import pprint
from rdflib import DCTERMS, Graph, Namespace, OWL, RDF, RDFS
import re
import requests
from contextlib import suppress
import yaml

########################################################################################################################
# CONSTANTS & CONFIG
########################################################################################################################

with open('conf.yaml') as f:
    conf = yaml.load(f, Loader=yaml.loader.SafeLoader)

# INIT GRAPH

g = Graph()

NS_CORE = Namespace('https://w3id.org/polifonia/ontology/core/')
NS_MR = Namespace('https://w3id.org/polifonia/ontology/music-representation/')
NS_MM = Namespace('https://w3id.org/polifonia/ontology/music-meta/')

g.bind('dcterms', DCTERMS)
g.bind('owl', OWL)
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('core', NS_CORE)
g.bind('mr', NS_MR)
g.bind('mm', NS_MM)

# COLLECT SCORES URL

f = open('scores-url-list.txt', 'r')
mei_files_url = [x.replace('\n', '').strip() for x in f.readlines()]
mei_files_url = sorted(filter(lambda x: x != '', mei_files_url))
f.close()

########################################################################################################################
# HELPERS
########################################################################################################################


def clean(s):
    s = html.unescape(s)
    s = s.replace('\n', ' ')
    s = ' '.join(s.split())
    s = s.strip()
    return s


def normalise(s):
    s = re.sub('[^a-zA-Z]+', '', s)
    s = s.lower()
    return s


def _extract_composers(data):
    composers = []
    attributed_composers = []

    # fileDesc > titleStmt > respStmt > persName{@role=composer}
    with suppress(KeyError):
        if (type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']) is list):
            for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
                if persName['role'] == 'composer':
                    composers.append(persName['value'])
        else:
            print("Ce n'est une liste !")
            if (data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']['role'] == 'composer'):
                composers.append(data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']['value'])

    # fileDesc > titleStmt > composer
    with suppress(KeyError):
        composers.append(data['meiHead']['fileDesc']['titleStmt']['composer'])

    # workList* > work > composer
    with suppress(KeyError):
        for work in data['meiHead']['workList']:
            composers.append(work['composer'])

    # extMeta > frames > metaFrame > frameInfo > referenceValue when referenceKey=COM
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if metaFrame['frameInfo']['referenceKey'] in ['COM', 'COM1', 'COM2']:
                composers.append(metaFrame['frameInfo']['referenceValue'])

    # fileDesc > sourceDesc > source > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if (type(data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']) is list):
            for name in data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if (data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']['role'] == 'composer'):
                composers.append(data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']['value'])

    # fileDesc > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']) is list:
            for name in data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if (data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']['role'] == 'composer'):
                composers.append(data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']['value'])

    # workDesc > work > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if (type(data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']) is list):
            for name in data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if (data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']['role'] == 'composer'):
                composers.append(data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']['value'])

    composers += extract_humdrum_frame(data, 'COM')

    # Détection du compositeur attribué

    # extMeta > frames > metaFrame > frameInfo > referenceValue when referenceKey=COA
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if metaFrame['frameInfo']['referenceKey'] in ['COA', 'COA1', 'COA2']:
                if metaFrame['frameInfo']['referenceValue'] in composers:
                    composers.remove(metaFrame['frameInfo']['referenceValue'])
                attributed_composers.append(metaFrame['frameInfo']['referenceValue'])

    composers = list(set([clean(c) for c in composers]))
    attributed_composers = list(set([clean(c) for c in attributed_composers]))

    return {'composers': composers, 'attributed_composers': attributed_composers}


def extract_composers(data):
    return _extract_composers(data)['composers']


def extract_attributed_composers(data):
    return _extract_composers(data)['attributed_composers']


def _extract_all_kind_of_titles(data):
    titles = []
    subordinate_titles = []

    titles_data = []

    # fileDesc > titleStmt > title
    with suppress(KeyError):
        title = data['meiHead']['fileDesc']['titleStmt']['title']
        if isinstance(title, list):
            titles_data += title
        else:
            titles_data.append(title)

    # workList > work > title
    with suppress(KeyError):
        for work in data['meiHead']['workList']:
            title = work['title']
            title = list(filter(lambda t: t['analog'] != 'humdrum:Xfi', title))
            if isinstance(title, list):
                titles_data += title
            else:
                titles_data.append(title)

    # compute data
    for title in titles_data:
        if 'type' in title and title['type'] == 'subordinate':
            subordinate_titles.append(title['value'])
        else:
            titles.append(' '.join(title['value'].split()))

    titles += extract_humdrum_frame(data, 'OTL')

    return [list(set(titles)), list(set(subordinate_titles))]


def extract_titles(data):
    return _extract_all_kind_of_titles(data)[0]


def extract_subordinate_titles(data):
    return _extract_all_kind_of_titles(data)[1]


def extract_encoding_date(data):
    # fileDesc > pubStmt > date
    with suppress(KeyError):
        if data['meiHead']['fileDesc']['pubStmt']['date']['type'] == 'encoding-date':
            return pandas.to_datetime(data['meiHead']['fileDesc']['pubStmt']['date']['value'])

    return None


def extract_distributor(data):
    # fileDesc > titleStmt > pubStmt > availability > distributor
    with suppress(KeyError):
        return data['meiHead']['fileDesc']['pubStmt']['availability']['distributor']

    return None


def extract_editors(data):
    editors = []

    # fileDesc > titleStmt > respStmt > persName{@role=editor}
    with suppress(KeyError):
        if (type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']) is list):
            for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
                if persName['role'] == 'editor':
                    editors.append(persName['value'])

    return editors


def extract_digital_editors(data):
    editors = []

    # fileDesc > pubStmt > respStmt > persName{@role=editor}
    with suppress(KeyError):
        if (type(data['meiHead']['fileDesc']['pubStmt']['respStmt']['persName']) is list):
            for persName in data['meiHead']['fileDesc']['pubStmt']['respStmt']['persName']:
                if persName['role'] == 'digital editor':
                    editors.append(' '.join(persName['value'].replace('\n', '').split()))

    return editors


def extract_lyricists(data):
    lyricists = []

    # fileDesc > titleStmt > respStmt > persName{@role=lyricist}
    with suppress(KeyError):
        if (type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']) is list):
            for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
                if persName['role'] == 'lyricist':
                    lyricists.append(persName['value'])

    return lyricists


def extract_encoding_applications(data):
    res = []

    # encodingDesc > appInfo > application
    with suppress(KeyError):
        for application in data['meiHead']['encodingDesc']['appInfo']['application']:
            a = {}
            with suppress(KeyError):
                a['date'] = application['isodate']
            with suppress(KeyError):
                a['applicationVersion'] = application['version']
            with suppress(KeyError):
                a['applicationName'] = application['name']
            with suppress(KeyError):
                a['note'] = application['p']
            if len(a) != 0:
                res.append(a)

    return res


def extract_scholarly_catalogue_abbreviation_and_number(data):
    catalogue_numbers = []

    # workList* > work > identifier
    with suppress(KeyError):
        for work in data['meiHead']['workList']:
            if work['identifier']['analog'] == 'humdrum:SCT':
                catalogue_numbers.append(work['identifier']['value'])

    catalogue_numbers += extract_humdrum_frame(data, 'SCT')

    return list(set(catalogue_numbers))


def extract_humdrum_frame(data, key):
    values = []

    # extMeta > frames* > metaFrame > frameInfo
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if (metaFrame['frameInfo']['referenceKey']) == key:
                values.append(metaFrame['frameInfo']['referenceValue'])

    return values


def extract_composer_s_dates(data):
    return extract_humdrum_frame(data, 'CDT')


def extract_genres(data):
    genres = []

    for genre in extract_humdrum_frame(data, 'AGN'):
        _genres = genre.split(';')
        _genres = [g.strip() for g in _genres]
        genres += _genres

    return genres


def extract_scholarly_catalogue(data):
    return extract_humdrum_frame(data, 'SCA')


def extract_voices(data):
    return extract_humdrum_frame(data, 'voices')


def extract_encoders(data):
    return extract_humdrum_frame(data, 'ENC')


def extract_encoding_dates_of_the_electronic_document(data):
    return extract_humdrum_frame(data, 'END')


def extract_electronic_editors(data):
    return extract_humdrum_frame(data, 'EED')


def extract_electronic_edition_versions(data):
    return extract_humdrum_frame(data, 'EEV')


def extract_nota_bene(data):
    return [clean(x) for x in extract_humdrum_frame(data, 'ONB')]

########################################################################################################################
# CALL SHERLOCK API
########################################################################################################################


for i, file in enumerate(mei_files_url):
    r = requests.post(
        conf['sherlock']['service']['mei']['head'],
        data=json.dumps({'file_url': file}),
        headers={'Content-Type': 'application/json'},
    )
    try:
        r.raise_for_status()
        data = r.json()

        print(f"    🌲 {i}/{len(mei_files_url)} 🌲 {file.replace('https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/scores', '')} 🌲")

        for _ in ['composers', 'titles', 'subordinate_titles', 'composers', 'attributed_composers', 'editors', 'digital_editors', 'encoding_date', 'encoding_applications', 'distributor', 'lyricists', 'composer_s_dates', 'genres', 'scholarly_catalogue', 'scholarly_catalogue_abbreviation_and_number', 'voices', 'encoders', 'encoding_dates_of_the_electronic_document', 'electronic_edition_versions', 'nota_bene']:
            func = globals()['extract_' + _]
            print(f"    {_.ljust(50)} : {func(data)}")

    except requests.exceptions.HTTPError as err:
        pprint(file)
        pprint('ERROR')
        pprint(r)
        pprint(err)
