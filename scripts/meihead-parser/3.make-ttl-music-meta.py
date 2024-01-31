import glob
import json
import os
from rdflib import DCTERMS, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, XSD
import sys

################################################################################
# SETUP
################################################################################


S = Namespace('http://data-iremus.huma-num.fr/id/')
PC = Namespace('https://w3id.org/polifonia/ontology/core/')
MR = Namespace('https://w3id.org/polifonia/ontology/music-representation/')
MM = Namespace('https://w3id.org/polifonia/ontology/music-meta/')

g = Graph(base=S)

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

    score = URIRef(data['score_uri'])

    # https://github.com/polifonia-project/tonalities_pilot/blob/main/scores/scoresMeta_.owl

    g.add((score, RDF.type, MM['DigitalScore']))
    music_entity = URIRef(cache.get_uuid([data['score_uri'], 'MusicEntity', 'uuid'], True))
    g.add((music_entity, RDF.type, MM['MusicEntity']))
    instrumentation = URIRef(cache.get_uuid([data['score_uri'], 'Instrumentation', 'uuid'], True))
    g.add((music_entity, PC['hasPart'], instrumentation))
    g.add((instrumentation, MM['hasScore'], score))
    creative_process = URIRef(cache.get_uuid([data['score_uri'], 'CreativeProcess', 'uuid'], True))
    g.add((creative_process, RDF.type, MM['CreativeProcess']))
    g.add((creative_process, MM['creates'], music_entity))
    creative_action = URIRef(cache.get_uuid([data['score_uri'], 'CreativeAction', 'uuid'], True))
    g.add((creative_action, RDF.type, MM['CreativeAction']))
    g.add((creative_process, MM['involvesCreativeAction'], creative_action))
    creative_task = URIRef(cache.get_uuid([data['score_uri'], 'CreativeTask', 'uuid'], True))
    g.add((creative_task, RDF.type, PC['CreativeTask']))
    g.add((creative_task, RDF.type, MM['MusicWriting']))
    g.add((creative_action, PC['executesTask'], creative_task))
    publication_situation = URIRef(cache.get_uuid([data['score_uri'], 'PublicationSituation', 'uuid'], True))
    original_edition_situation = URIRef(cache.get_uuid([data['score_uri'], 'OriginalEditionSituation', 'uuid'], True))
    digital_edition_situation = URIRef(cache.get_uuid([data['score_uri'], 'DigitalEditionSituation', 'uuid'], True))
    encoding_situation = URIRef(cache.get_uuid([data['score_uri'], 'EncodingSituation', 'uuid'], True))
    g.add((publication_situation, RDF.type, MM['PublicationSituation']))
    g.add((original_edition_situation, RDF.type, MM['OriginalEditionSituation']))
    g.add((digital_edition_situation, RDF.type, MM['DigitalEditionSituation']))
    g.add((encoding_situation, RDF.type, MM['EncodingSituation']))
    g.add((score, MM['hasPublicationSituation'], publication_situation))
    g.add((score, MM['hasOriginalEditionSituation'], original_edition_situation))
    g.add((score, MM['hasDigitalEditionSituation'], digital_edition_situation))
    g.add((score, MM['hasEncodingSituation'], encoding_situation))
    g.add((digital_edition_situation, PC['isDerivedFrom'], original_edition_situation))

    for k, v in data.items():
        if k == "attributed_composers":
            for x in v:
                composer = URIRef(cache.get_uuid(['composers', x, 'uuid'], True))
                g.add((composer, RDF.type, MM['MusicArtist']))
                g.add((creative_action, PC['involvesAgent'], composer))
                g.add((composer, PC['isInvolvedIn'], creative_process))
                g.add((composer, PC['name'], Literal(x)))
        if k == "composer_s_dates":
            # C'est vraiment n'importe quoi, cf. Jos2710_CGN.mei
            pass
        if k == "composers":
            for x in v:
                composer = URIRef(cache.get_uuid(['composers', x, 'uuid'], True))
                g.add((composer, RDF.type, MM['MusicArtist']))
                g.add((creative_action, PC['involvesAgent'], composer))
                g.add((composer, PC['isInvolvedIn'], creative_process))
                g.add((composer, PC['name'], Literal(x)))
        if k == "digital_editors":
            for x in v:
                editor = URIRef(cache.get_uuid(['persons', x, 'uuid'], True))
                g.add((digital_edition_situation, MM['hasEditor'], editor))
        if k == "distributors":
            pass
        if k == "editors":
            for x in v:
                editor = URIRef(cache.get_uuid(['persons', x, 'uuid'], True))
                g.add((original_edition_situation, MM['hasEditor'], editor))
        if k == "electronic_edition_versions":
            pass
        if k == "encoders":
            for x in v:
                encoder = URIRef(cache.get_uuid(['persons', x, 'uuid'], True))
                g.add((encoding_situation, MM['hasEncoder'], encoder))
        if k == "encoding_applications":
            pass
        if k == "encoding_dates":
            for x in v:
                x = x[:10]
                time_interval = URIRef(cache.get_uuid([score, 'EncodingSituation', 'TimeInterval', x, 'uuid'], True))
                g.add((encoding_situation, PC['hasTimeInterval'], time_interval))
                g.add((time_interval, RDF.type, PC['TimeInterval']))
                g.add((time_interval, PC['startTime'], Literal(x, datatype=XSD.date)))
                g.add((time_interval, PC['endTime'], Literal(x, datatype=XSD.date)))
            pass
        if k == "encoding_dates_of_the_electronic_document":
            pass
        if k == "genres":
            for x in v:
                genre = URIRef(cache.get_uuid(['genres', x, 'uuid'], True))
                g.add((music_entity, MM['hasGenre'], genre))
                g.add((genre, RDF.type, MM['MusicGenre']))
                g.add((genre, RDFS.label, Literal(x, datatype=XSD.string)))
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
            for i in range(0, len(v)):
                title_uri = URIRef(cache.get_uuid([data['score_uri'], 'titles', i], True))
                g.add((score, PC['hasTitle'], S[title_uri]))
                g.add((S[title_uri], RDF.type, PC['Title']))
                g.add((S[title_uri], PC['name'], Literal(v[i])))
            pass
        if k == "voices":
            pass
        if k == "voices_opr":
            pass

################################################################################
# THAT'S ALL FOLKS!
################################################################################

g.serialize(destination="tonalities-mei-corpus-musicmeta.ttl")
cache.bye()
