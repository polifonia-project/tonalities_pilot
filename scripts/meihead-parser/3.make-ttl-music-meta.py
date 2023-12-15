import glob
import json
import os
from rdflib import DCTERMS, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
import sys

################################################################################
# SETUP
################################################################################

g = Graph()

PC = Namespace('https://w3id.org/polifonia/ontology/core/')
MR = Namespace('https://w3id.org/polifonia/ontology/music-representation/')
MM = Namespace('https://w3id.org/polifonia/ontology/music-meta/')

g.bind('dcterms', DCTERMS)
g.bind('owl', OWL)
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('core', PC)
g.bind('mr', MR)
g.bind('mm', MM)

metadata_json_files = glob.glob('./metadata-json/**/*.json', recursive=True)

sys.path.append(os.path.abspath(os.path.join('./sherlockcachemanagement', '')))
from sherlockcachemanagement import Cache  # nopep8
cache = Cache('cache.yaml')

################################################################################
# PROCESS DATA…
################################################################################

for f in metadata_json_files:
    f = open(f)
    data = json.load(f)
    f.close()

    g.add((URIRef(data['score_uri']), RDF.type, MM['DigitalScore']))

################################################################################
# THAT'S ALL FOLKS!
################################################################################

g.serialize(destination="tonalities-mei-corpus-musicmeta.ttl")
cache.bye()
