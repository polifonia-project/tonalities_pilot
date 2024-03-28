import glob
import json
import os
from rdflib import DCTERMS, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD
import sys

################################################################################
# SETUP
################################################################################

S = Namespace('http://data-iremus.huma-num.fr/id/')
SNS = Namespace('http://data-iremus.huma-num.fr/ns/sherlock#')
CRM = Namespace('http://www.cidoc-crm.org/cidoc-crm/')
LRMOO = Namespace('https://www.iflastandards.info/lrm/lrmoo')

g = Graph(base=S)

g.bind('crm', CRM)
g.bind('dcterms', DCTERMS)
g.bind('lrmoo', LRMOO)
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('sherlock', SNS)

json_files = glob.glob('metadata-json/**/*.json', recursive=True)

sys.path.append(os.path.abspath(os.path.join('./sherlockcachemanagement', '')))
from sherlockcachemanagement import Cache  # nopep8
cache = Cache('cache-sherlock-projects.yaml')

################################################################################
# PROCESS
################################################################################

for f in json_files:
    with open(f, 'r', encoding='utf-8') as f:
        d = json.load(f)
        u = d['score_uri']
        u = u.split('/scores/')
        corpus_name = '/'.join(u[1].split('/')[:-1]).replace('%20', ' ')

        # CORPUS
        corpus_uri = URIRef(cache.get_uuid(['corpuses', corpus_name, 'uuid'], True))
        g.add((corpus_uri, RDF.type, SNS['Corpus']))

        # CORPUS E41
        corpus_e41_uri = URIRef(cache.get_uuid(['corpuses', corpus_name, 'e41', 'uuid'], True))
        g.add((corpus_uri, CRM['P1_is_identified_by'], corpus_e41_uri))
        g.add((corpus_e41_uri, RDF.type, CRM['E41_Identifier']))
        g.add((corpus_e41_uri, CRM['P190_has_symbolic_content'], Literal(corpus_name)))

        # CORPUS E65
        corpus_e65_uri = URIRef(cache.get_uuid(['corpuses', corpus_name, 'e65', 'uuid'], True))
        g.add((corpus_e65_uri, RDF.type, CRM['E65_Creation']))
        g.add((corpus_e65_uri, CRM['P2_has_type'], URIRef('21816195-6708-4bbd-a758-ee354bb84900')))
        g.add((URIRef('d9dafa60-75d1-4c34-8d1d-5ec12ffa0ea8'), CRM['P9_consists_of'], corpus_e65_uri))
        g.add((corpus_e65_uri, CRM['P94_has_created'], corpus_uri))
        g.add((corpus_e65_uri, CRM['P14_carried_out_by'], URIRef('56ed1334-b47a-440a-b78d-04c8d3cfc311')))  # Tonaliteam

        # F3
        f3_uri = URIRef(cache.get_uuid(['scores', d['score_uri'], 'uuid'], True))
        g.add((f3_uri, RDF.type, LRMOO['F3_Manifestation']))
        g.add((f3_uri, CRM['P2_has_type'], S['792f6ea9-3d3d-4504-9042-4a3f8e23f542']))  # Partition
        g.add((f3_uri, CRM['P2_has_type'], S['bf9dce29-8123-4e8e-b24d-0c7f134bbc8e']))  # Fichier MEI
        g.add((corpus_uri, SNS['has_member'], f3_uri))

        # F3 E42
        f3_e42_uri = URIRef(cache.get_uuid(['scores', d['score_uri'], 'e42', 'uuid'], True))
        g.add((f3_e42_uri, RDF.type, CRM['E42_Identifier']))
        g.add((f3_e42_uri, CRM['P2_has_type'], S['bf9dce29-8123-4e8e-b24d-0c7f134bbc8e']))  # Fichier MEI
        g.add((f3_e42_uri, CRM['P190_has_symbolic_content'], URIRef(d['score_uri'])))
        g.add((f3_uri, CRM['P1_is_identified_by'], f3_e42_uri))

################################################################################
# THAT'S ALL FOLKS!
################################################################################

g.serialize(destination="tonalities-sherlock-projects.ttl")
cache.bye()
