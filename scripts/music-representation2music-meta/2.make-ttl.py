import html
import json
from pprint import pprint
from rdflib import DCTERMS, Graph, Namespace, OWL, RDF, RDFS
import re
import requests
from contextlib import suppress
import yaml

# CONSTANTS & CONFIG

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
mei_files_url = sorted(f.readlines())
f.close()


# HELPERS


def clean(s):
    s = html.unescape(s)
    s = s.strip()
    s = s.replace('  ', ' ')
    return s


def normalise(s):
    s = re.sub('[^a-zA-Z]+', '', s)
    s = s.lower()
    return s


def extractComposers(file, data):
    composers = []

    # fileDesc > titleStmt > respStmt > persName{@role=composer}
    with suppress(KeyError):
        if type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']) is list:
            for persName in data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']:
                if persName['role'] == 'composer':
                    composers.append(persName['value'])
        else:
            print("Ce n'est une liste !")
            if data['meiHead']['fileDesc']['titleStmt']['respStmt']['persName']['role'] == 'composer':
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
            if metaFrame['frameInfo']['referenceKey'] in ['COM', 'COM2']:
                composers.append(metaFrame['frameInfo']['referenceValue'])

    # fileDesc > sourceDesc > source > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if type(data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']) is list:
            for name in data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name'][
                'role'] == 'composer':
                composers.append(
                    data['meiHead']['fileDesc']['sourceDesc']['source']['titleStmt']['respStmt']['name']['value'])

    # fileDesc > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if type(data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']) is list:
            for name in data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']['role'] == 'composer':
                composers.append(data['meiHead']['fileDesc']['titleStmt']['respStmt']['name']['value'])

    # workDesc > work > titleStmt > respStmt > name{@role=composer}
    with suppress(KeyError):
        if type(data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']) is list:
            for name in data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']:
                if name['role'] == 'composer':
                    composers.append(name['value'])
        else:
            if data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']['role'] == 'composer':
                composers.append(data['meiHead']['workDesc']['work']['titleStmt']['respStmt']['name']['value'])

    if len(composers) == 0:
        print(file)

    return list(set([clean(c) for c in composers]))


# CALL SHERLOCK API

# mei_files_url = ['https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/scores/De_Rore/De_Rore_Di_tempo_in_tempo_mi_si_fa_men_dura.mei']

for x in mei_files_url:
    x = x.replace('\n', '')
    r = requests.post(
        conf['sherlock']['service']['mei']['head'],
        data=json.dumps({'file_url': x}),
        headers={'Content-Type': 'application/json'}
    )
    try:
        r.raise_for_status()
        data = r.json()
        print(x)
        # pprint(data)
        composers = extractComposers(x, data)
        print(composers)
    except requests.exceptions.HTTPError as err:
        pass
        # pprint(x)
        # pprint('ERROR')
        # pprint(r)
        # pprint(err)
