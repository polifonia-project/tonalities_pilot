import json
import os
from pprint import pprint
from pathlib import Path
from pprint import pprint
from rdflib import DCTERMS, Graph, Namespace, OWL, RDF, RDFS
import yaml

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
