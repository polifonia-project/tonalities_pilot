# grep -rh "2<" . | grep referenceKey | awk '{$1=$1};1' | sort | uniq
# g cert

import html
import json
import os
import pandas
from pathlib import Path
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

# COLLECT SCORES URL

f = open('scores-url-list.txt', 'r')
mei_files_url = [x.replace('\n', '').strip() for x in f.readlines()]
mei_files_url = sorted(filter(lambda x: x != '', mei_files_url))
f.close()

########################################################################################################################
# METADATA EXTRACTION HELPERS
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


def _extract_role(data, role):
    x = []

    # fileDesc > titleStmt > respStmt > persName{@role=?}
    with suppress(KeyError):
        for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
            if persName['role'] == role:
                x.append(persName['value'])

    # fileDesc > sourceDesc > source > titleStmt > respStmt > name{@role=?}
    with suppress(KeyError):
        for name in data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']:
            if name['role'] == role:
                x.append(name['value'])

    # fileDesc > titleStmt > respStmt > name{@role=?}
    with suppress(KeyError):
        for name in data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']:
            if name['role'] == role:
                x.append(name['value'])

    # workDesc > work > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        for name in data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']:
            if name['role'] == role:
                x.append(name['value'])

    return list(set(x))


def _extract_composers(data):
    composers = []
    attributed_composers = []

    composers += _extract_role(data, 'composer')

    # fileDesc > titleStmt > composer
    with suppress(KeyError):
        composers.append(data['meiHead']['fileDesc']['titleStmt']['composer'])

    # workList* > work > composer
    with suppress(KeyError):
        for work in data['meiHead']['workList']:
            for composer in work['composer']:
                if composer['analog'] == 'humdrum:COA':
                    attributed_composers.append(composer['value'])
                else:
                    composers.append(composer['value'])

    # extMeta > frames > metaFrame > frameInfo > referenceValue when referenceKey=COM
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if metaFrame['frameInfo']['referenceKey'] in ['COM', 'COM1', 'COM2']:
                composers.append(metaFrame['frameInfo']['referenceValue'])

    composers += read_humdrum_frame(data, 'COM')

    # Détection du compositeur attribué

    # extMeta > frames > metaFrame > frameInfo > referenceValue when referenceKey=COA
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if metaFrame['frameInfo']['referenceKey'] in ['COA', 'COA1', 'COA2', 'COA3', 'COA4']:
                if metaFrame['frameInfo']['referenceValue'] in composers:
                    composers.remove(metaFrame['frameInfo']['referenceValue'])
                attributed_composers.append(metaFrame['frameInfo']['referenceValue'])

    return {
        'composers': list(set([clean(c) for c in composers])),
        'attributed_composers': list(set([clean(c) for c in attributed_composers]))
    }


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
        if title:
            if 'type' in title and title['type'] == 'subordinate':
                subordinate_titles.append(title['value'])
            else:
                titles.append(' '.join(title['value'].split()))

    titles += read_humdrum_frame(data, 'OTL')
    titles += read_humdrum_frame(data, 'OTL2')

    return [list(set(titles)), list(set(subordinate_titles))]


def extract_titles(data):
    return _extract_all_kind_of_titles(data)[0]


def extract_subordinate_titles(data):
    return _extract_all_kind_of_titles(data)[1]


def extract_encoding_dates(data):
    # fileDesc > pubStmt > date
    with suppress(KeyError):
        if data['meiHead']['fileDesc']['pubStmt']['date']['type'] == 'encoding-date':
            return pandas.to_datetime(data['meiHead']['fileDesc']['pubStmt']['date']['value'])

    return None


def extract_distributors(data):
    # fileDesc > titleStmt > pubStmt > availability > distributor
    with suppress(KeyError):
        return [data['meiHead']['fileDesc']['pubStmt']['availability']['distributor']]

    return []


def extract_editors(data):
    x = []

    # fileDesc > titleStmt > respStmt > persName{@role="editor"}
    with suppress(KeyError):
        for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
            if persName['role'] == 'editor':
                x.append(persName['value'])

    # fileDesc > pubStmt > respStmt > persName{@role="editor"}
    with suppress(KeyError):
        for persName in data['meiHead']['fileDesc']['pubStmt']['respStmt']['persName']:
            if persName['role'] == 'editor' and persName['analog'] != 'humdrum:EED':
                x.append(persName['value'])

    x += _extract_role(data, 'arranger')

    return x


def extract_digital_editors(data):
    x = []

    # fileDesc > pubStmt > respStmt > persName{@role="digital editor"}
    with suppress(KeyError):
        for persName in data['meiHead']['fileDesc']['pubStmt']['respStmt']['persName']:
            if persName['role'] == 'digital editor':
                x.append(' '.join(persName['value'].replace('\n', '').split()))

    x += read_humdrum_frame(data, 'EED')

    # fileDesc > pubStmt > respStmt > persName{@role="editor" @analog="humdrum:EED"}
    with suppress(KeyError):
        for persName in data['meiHead']['fileDesc']['pubStmt']['respStmt']['persName']:
            if persName['role'] == 'editor' and persName['analog'] == 'humdrum:EED':
                x.append(persName['value'])

    return list(set(x))


def extract_lyricists(data):
    return _extract_role(data, 'lyricist')


def extract_encoding_applications(data):
    x = []

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
                x.append(a)

    return x


def extract_scholarly_catalogues_abbreviation_and_number(data):
    x = []

    # workList* > work > identifier
    with suppress(KeyError):
        for work in data['meiHead']['workList']:
            if work['identifier']['analog'] == 'humdrum:SCT':
                x.append(work['identifier']['value'])

    x += read_humdrum_frame(data, 'SCT')

    return list(set(x))


def read_humdrum_frame(data, key):
    x = []

    # extMeta > frames* > metaFrame > frameInfo
    with suppress(KeyError):
        for metaFrame in data['meiHead']['extMeta']['frames']:
            if (metaFrame['frameInfo']['referenceKey']) == key:
                x.append(metaFrame['frameInfo']['referenceValue'])

    return [clean(x) for x in x]


def extract_composer_s_dates(data):
    return read_humdrum_frame(data, 'CDT') + read_humdrum_frame(data, 'CDT2')


def extract_genres(data):
    genres = []

    for genre in read_humdrum_frame(data, 'AGN'):
        _genres = genre.split(';')
        _genres = [g.strip() for g in _genres]
        genres += _genres

    return genres


def extract_scholarly_catalogues(data):
    return read_humdrum_frame(data, 'SCA')


def extract_voices(data):
    return read_humdrum_frame(data, 'voices')


def extract_encoders(data):
    return read_humdrum_frame(data, 'ENC')


def extract_encoding_dates_of_the_electronic_document(data):
    return read_humdrum_frame(data, 'END')


def extract_electronic_edition_versions(data):
    return read_humdrum_frame(data, 'EEV')


def extract_nota_bene(data):
    return read_humdrum_frame(data, 'ONB')


def extract_number(data):
    return read_humdrum_frame(data, 'ONM')


def extract_movement_designation(data):
    return read_humdrum_frame(data, 'OMD')


def extract_title_of_larger_work(data):
    return list(set(read_humdrum_frame(data, 'OPR')))


def extract_rdfkern(data):
    return read_humdrum_frame(data, 'RDF**kern')


def extract_manuscript_sources_names(data):
    return read_humdrum_frame(data, 'SMS')


def extract_system_decoration(data):
    return read_humdrum_frame(data, 'system-decoration')


def extract_voices_opr(data):
    return read_humdrum_frame(data, 'voices-OPR')


def extract_voices(data):
    return read_humdrum_frame(data, 'voices')


def extract_project_description(data):
    with suppress(KeyError):
        # encodingDesc > projectDesc > p*
        return [x['value'] for x in (data['meiHead']['encodingDesc']['projectDesc']['p'])]
    return []


def pick_names(x):
    if list != type(x):
        x = [x]

    names = []

    for s in x:
        parts = s.split(";")
        parts = [_.strip() for _ in parts]
        names += parts

    return names


# python3 2.extract-data.py | grep • | grep -v "\[\]" | sort | uniq
def cleanup_metadata(d):
    for k, v in d.items():
        if k == "attributed_composers":
            pass
        if k == "composer_s_dates":
            pass
        if k == "composers":
            pass
        if k == "digital_editors":
            pass
        if k == "distributors":
            pass
        if k == "editors":
            d[k] = pick_names(v)
        if k == "electronic_edition_versions":
            if v:
                d[k] = [(lambda x: x[:-1] if x[-1] == '/' else x)(x) for x in v]
        if k == "encoders":
            d[k] = pick_names(v)
        if k == "encoding_applications":
            pass
        if k == "encoding_dates":
            d[k] = [str(v)]
        if k == "encoding_dates_of_the_electronic_document":
            if v:
                d[k] = [(lambda x: x[:-1] if x[-1] == '/' else x)(x) for x in v]
        if k == "genres":
            # Il y a des dates dans le champ genre
            pass
        if k == "lyricists":
            pass
        if k == "manuscript_sources_names":
            pass
        if k == "movement_designation":
            pass
        if k == "nota_bene":
            pass
        if k == "number":
            pass
        if k == "project_description":
            pass
        if k == "rdfkern":
            pass
        if k == "scholarly_catalogues":
            pass
        if k == "scholarly_catalogues_abbreviation_and_number":
            pass
        if k == "subordinate_titles":
            pass
        if k == "system_decoration":
            pass
        if k == "title_of_larger_work":
            pass
        if k == "titles":
            pass
        if k == "voices":
            pass
        if k == "voices_opr":
            pass

    for k, v in d.items():
        if k not in ['score_uri', 'encoding_applications']:
            d[k] = sorted(v)

    return d

########################################################################################################################
# CALL SHERLOCK API
########################################################################################################################


os.makedirs('cache', exist_ok=True)
os.makedirs('metadata-json', exist_ok=True)

extract_functions = [v for k, v in globals().items() if k.startswith('extract_') and callable(v)]
extract_functions = sorted(extract_functions, key=lambda x: x.__name__)

for i, file in enumerate(mei_files_url):
    print(f"🌲  {i  +1}/{len(mei_files_url)} — {file.replace('https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/scores', '')}")

    file_name = file.replace(conf['polifonia']['tonalities']['scores']['base_url'], '')
    cache_file = Path('cache/' + file_name + '.json')
    cache_file.parent.mkdir(exist_ok=True, parents=True)
    data = None

    if Path(cache_file).is_file():
        f = open(cache_file)
        data = json.load(f)
        f.close()
    else:
        r = requests.post(
            conf['sherlock']['service']['mei']['head'],
            data=json.dumps({'file_url': file}),
            headers={'Content-Type': 'application/json'},
        )
        try:
            r.raise_for_status()
            data = r.json()
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except requests.exceptions.HTTPError as err:
            print(f"   {file}")
            print(f"   ERROR — {err}")

    if data:
        d = {
            "score_uri": file
        }
        for func in extract_functions:
            func_name = func.__name__.replace('extract_', '')
            x = func(data)
            d[func_name] = x
        d = cleanup_metadata(d)

        json_file = Path('metadata-json/' + file_name + '.json')
        json_file.parent.mkdir(exist_ok=True, parents=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=4)
