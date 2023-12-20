import glob
import json
import os
from rdflib import DCTERMS, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
import sys

################################################################################
# SETUP
################################################################################

g = Graph()

S = Namespace('http://data-iremus.huma-num.fr/id/')
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

    score_uri = URIRef(data['score_uri'])

    # https://github.com/polifonia-project/tonalities_pilot/blob/main/scores/scoresMeta_.owl
    g.add((score_uri, RDF.type, MM['DigitalScore']))
    edtionSituation = URIRef(cache.get_uuid([data['score_uri'], 'editionSituation', 'uuid'], True))
    g.add((edtionSituation, RDF.type, MM['EditionSituation']))

    for k, v in data.items():
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
            pass
        if k == "electronic_edition_versions":
            pass
        if k == "encoders":
            pass
        if k == "encoding_applications":
            pass
        if k == "encoding_dates":
            pass
        if k == "encoding_dates_of_the_electronic_document":
            pass
        if k == "genres":
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
            for i in range(0, len(v)):
                title_uri = URIRef(cache.get_uuid([data['score_uri'], 'titles', i], True))
                g.add((score_uri, PC['hasTitle'], S[title_uri]))
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

# Christophe ne fait rien de : PDT,

# Deal with a date :
# for dateElement in datesElectronicEdition:
#     with targetOnto:
#         timeIntervalInstance = coreOnto.TimeInterval(getUUID())
#         timeIntervalInstance.time.append(dateElement)
#         editionSituationInstance.hasTimeInterval.append (timeIntervalInstance)

# def getElectronicEditorInstance (editorName):
#     for element in targetOnto.search(type = coreOnto.Agent):
#         if editorName in element.coreName  :
#             if metaOnto.Editor not in element.is_a :
#                 element.is_a.append(metaOnto.Editor)
#             return element
#     else:
#         with targetOnto:
#             editor = metaOnto.Editor(getUUID())
#             editor.coreName.append(editorName)
#         return editor

# def getElectronicPublishers (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "YEP"))

# def getElectronicPublisherInstance (electronicPublisher):
#     for element in targetOnto.search(type = coreOnto.Agent):
#         if electronicPublisher in element.coreName  :
#             if targetOnto.publisher not in element.is_a :
#                 element.is_a.append(targetOnto.Publisher)
#             return element
#     else:
#         publisher = metaOnto.Publisher(getUUID())
#         publisher.coreName.append(electronicPublisher)
#         return publisher


# def getElectronicVersions (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "EEV"))

# def getEncoders (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "ENC"))

# def getEncoderInstance (encoderName):
#     for element in targetOnto.search(type = coreOnto.Agent):
#         if encoderName in element.coreName  :
#             if metaOnto.Encoder not in element.is_a :
#                 element.is_a.append(metaOnto.Encoder)
#             return element
#     else:
#         encoderI = metaOnto.Encoder(getUUID())
#         encoderI.coreName.append(encoderName)
#         return encoderI

# def getEncodingDates (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "END"))

# def getLicenses (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "YEM"))

# def getLicenseInstance (licenseName):
#     for element in targetOnto.search(type = targetOnto.License):
#         if licenseName in element.coreName  :
#             return element
#     else:
#         licence = targetOnto.MusicArtist(getUUID())
#         licence.coreName.append(licence)
#         return licence

# def getMusicArtists(rootElement):
#     meiComposers = getTextNodesFromXpath(rootElement, "//mei:work/mei:composer")
#     humDrumComposers = getMetaDataFromHumdrumCodes(rootElement, "COM")
#     return concatenateLists([meiComposers, humDrumComposers])

# def getMusicArtistInstance (musicArtistName):
#     #name
#     for element in targetOnto.search(type = metaOnto.MusicArtist):
#         if musicArtistName in element.coreName  :
#             return element
#     else:
#         musicArtistInstance = metaOnto.MusicArtist(getUUID())
#         musicArtistInstance.coreName.append(musicArtistName)
#         return musicArtistInstance


# def getMetaDataFromHumdrumCodes (rootElement, humdrumCode):
#     metadataList = []
#     nodeList= getNodesFromXpath(rootElement, "//frames:metaFrame[child::frames:frameInfo/frames:referenceKey[text()='" + humdrumCode + "']]")
#     for node in nodeList :
#         metadataList = metadataList +(getTextNodesFromXpath(node, "frames:frameInfo/frames:referenceValue"))
#     return metadataList

# def getMusicGenres (rootElement):
#     return cleanList (getMetaDataFromHumdrumCodes(rootElement, "AGN"))

# def getMusicGenreInstance (musicGenreName):
#     for element in targetOnto.search(type = metaOnto.MusicGenre):
#         if musicGenreName in element.coreName  :
#             return element
#     else:
#         with targetOnto:
#             musicGenreInstance = metaOnto.MusicGenre(getUUID())
#             musicGenreInstance.coreName.append(musicGenreName)
#         return musicGenreInstance


# def getNodesFromXpath(element, xpath):
#     elementList = []
#     for element in rootElement.xpath(xpath, namespaces=ns):
#         elementList.append(element)
#     return elementList

# def getOpusStatements(rootElement):
#     opusList = getMetaDataFromHumdrumCodes(rootElement, "OPS")

#     if len (opusList) > 0 : return opusList

#     SCTList = cleanList(getMetaDataFromHumdrumCodes(rootElement, "SCT"))
#     SCAList = cleanList(getMetaDataFromHumdrumCodes(rootElement, "SCT"))

#     if len (SCAList) >0:
#         return SCAList
#     else:
#         return SCTList
#     return

# def getOpusStatementInstance(opusStatementName):
#     for element in targetOnto.search(type = metaOnto.OpusStatement):
#         if opusStatementName in [element.opusNumber]:
#             return element
#     else:
#         with targetOnto:
#             opusStatement = metaOnto.OpusStatement(getUUID())
#             opusStatement.opusNumber =opusStatementName
#     return opusStatement

# def getOriginalEditors (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "YOE"))

# def getOriginalPublishers (rootElement):
#     return cleanList(getMetaDataFromHumdrumCodes(rootElement, "PPR"))

# def getPlacesFirstPublished (rootElement):
#     return getMetaDataFromHumdrumCodes(rootElement, "PPP")


# def getPlacesElectronicEdition (root):
#     return [] # TODO

# def getPlaceInstance (placeName):
#     for element in targetOnto.search(type = metaOnto.Place):
#         if placeName in element.title:
#             return element
#     else:
#         opusStatement = metaOnto.OpusStatement(getUUID())
#         opusStatement.title.append(opusStatement)
#     return opusStatement

# def getRoot(meiURI):
#     res =  rq.get(meiURI)
#     parser = ET.XMLParser()
#     for element in res:
#         parser.feed(element)
#     root = parser.close()

#     return root

# def getTextNodesFromXpath (element, xpath):
#     elementList = []
#     for element in element.xpath(xpath, namespaces=ns):
#         if ";" in element.text:
#             for item in element.text.split(";"):
#                 elementList.append(item.strip())
#         else:
#             elementList.append(element.text.strip())
#     return elementList

# def getTitles (rootElement):
#     meiTitles = cleanList(getTextNodesFromXpath(rootElement, "//mei:work/mei:title[not(@analog='humdrum:Xfi')]"))
#     humDrumTitles = cleanList(getMetaDataFromHumdrumCodes(rootElement, "OTL"))


#     return concatenateLists([meiTitles, humDrumTitles])

# def getTitleInstance (titleName):
#     for element in targetOnto.search(type = coreOnto.Title):
#         if titleName in element.coreName:
#             return element
#     else:
#         title = coreOnto.Title(getUUID())
#         title.coreName.append(titleName)
#     return title

# def setPythonNamesForProperties():
#     for prop in coreOnto.data_properties():
#         if prop._name == "name":
#             prop.python_name = "coreName"

#         if prop._name == "title":
#             prop.python_name = "coreTitle"

#     for prop in metaOnto.object_properties():
#         if prop._name == "creates":
#             prop.python_name = "metaCreates"


# if __name__ == '__main__':
#     pass

# ''' paths '''
# targetFilePath = "/Users/christophe/Documents/GitHub/tonalities-pilot/scores/scoresMeta.owl" # the target file
# musicMetaOntologyFilePath = "/Users/christophe/Documents/GitHub/tonalities-pilot/scores/musicmeta.owl" ## once music-meta will be updated, this sould be a Github URL
# scorePaths = "/Users/christophe/Documents/GitHub/tonalities-pilot/scores/Josquin/" # the score folder on github

# ''' namespaces '''
# ns = {'mei': 'http://www.music-encoding.org/ns/mei',
#           'frames': 'http://www.humdrum.org/ns/humxml'
#           }

# ''' ontos '''
# sourceOnto = get_ontology(musicMetaOntologyFilePath).load() ### this is the actuel polifonia-meta ontology
# targetOnto = get_ontology(targetFilePath).load()
# targetOnto.imported_ontologies.append(sourceOnto)

# ''' shorthand for cascading imports '''
# metaOnto = targetOnto.imported_ontologies[0]
# coreOnto = targetOnto.imported_ontologies[0].imported_ontologies[0]

# ''' shorthands for properties '''
# setPythonNamesForProperties() # shorthands for some properties

# ''' get what's needed on github'''
# rawFilePath = "https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/"
# page = requests.get("https://github.com/polifonia-project/tonalities_pilot/tree/main/scores/Josquin")


# gitHubDic = json.loads(page.text)
# filePathList = []

# for item in gitHubDic["payload"]["tree"]["items"]:
#     if item["contentType"] != "file": continue
#     ''' any filters ? '''
#     if ".mei" not in item["path"]: continue
#     if "CGN" in item["name"]:continue
#     if "MG" in item["name"]:continue
#     if "AF" in item["name"]:continue
#     if "2914" in item["name"]:continue

#     filePathList.append([rawFilePath + item["path"], item["name"]])


# ''' process the file list '''
# for filePathItem in  filePathList:
#     meiURI =  filePathItem[0]
#     print (meiURI)

#     ''' read the mei file and get metadata'''
#     rootElement = getRoot(meiURI)

#     ''' composer, title '''
#     musicArtists = getMusicArtists(rootElement)
#     titles = getTitles (rootElement)


#     ''' genres, opus, licence'''
#     musicGenres = getMusicGenres(rootElement)
#     opusStatements = getOpusStatements(rootElement)
#     licenses = getLicenses(rootElement)

#     ''' electronic editors, encoders, publishers, versions'''
#     placesElectronicEdition = getPlacesElectronicEdition (rootElement)
#     electronicVersions = getElectronicVersions (rootElement)

#     encoders = getEncoders(rootElement)
#     encodingDates = getEncodingDates (rootElement)

#     electronicPublishers = getElectronicPublishers (rootElement)

#     ''' original editors, publishers, dates, places '''
#     originalEditors = getOriginalEditors (rootElement)
#     originalPublishers = getOriginalPublishers(rootElement)
#     #placesFirstPublished = getPlacesFirstPublished(rootElement)

#     ''' create individuals '''
#     with targetOnto:
#         compositionPartInstance = metaOnto.CompositionPart(getUUID())
#         instrumentationInstance = metaOnto.Instrumentation(getUUID())
#         digitalScoreInstance = metaOnto.DigitalScore(meiURI)
#         publicationSituationInstance = metaOnto.PublicationSituation(getUUID())

#         creativeProcessInstance = metaOnto.CreativeProcess(getUUID())
#         creativeActionInstance = metaOnto.CreativeAction(getUUID())
#         musicEntityInstance = metaOnto.MusicEntity(getUUID())

#         creativeProcessInstance.involvesCreativeAction.append(creativeActionInstance)
#         creativeActionInstance.executesTask.append(metaOnto.MusicWriting)
#         musicEntityInstance.metaCreates.append(creativeProcessInstance)
#         musicEntityInstance.hasPart.append(compositionPartInstance)
#         compositionPartInstance.hasInstrumentation.append(instrumentationInstance)
#         instrumentationInstance.hasScore.append(digitalScoreInstance)
#         digitalScoreInstance.hasPublicationSituation.append (publicationSituationInstance)

#         ''' does a composer exist ? '''
#         for element in musicArtists:
#             musicArtistInstance = getMusicArtistInstance(element)
#             creativeActionInstance.involvesAgent.append(musicArtistInstance)

#         ''' does an opus statement exist '''
#         for element in opusStatements:
#             opusStatementInstance = getOpusStatementInstance(element)
#             musicEntityInstance.hasOpusStatement.append(opusStatementInstance)

#         ''' does a licence exist ? '''
#         for element in licenses:
#             licenceInstance = getLicenseInstance (element)
#             digitalScoreInstance.hasLicense.append(licenceInstance)

#         ''' does a title exist ? '''
#         for element in titles:
#             titleInstance = getTitleInstance (element)
#             digitalScoreInstance.hasTitle.append(titleInstance)

#         ''' does a place exist ? '''
#         for element in placesElectronicEdition:
#             placeInstance = getPlaceInstance(element)
#             publicationSituationInstance.hasPlace (placeInstance)

#         ''' does an electronic publisher exist ?'''
#         for element in electronicPublishers:
#             electronicPublisherInstance = getElectronicPublisherInstance(element)
#             publicationSituationInstance.hasPublisher.append(electronicPublisherInstance)

#         ''' does an editor exist ? '''
#         editors = False


#         EED
#         editionSituationInstance = metaOnto.EditionSituation(getUUID())
#         for element in electronicEditors:
#             editors = True
#             editionSituationInstance.hasEditor.append (getElectronicEditorInstance (element))
#             for place in placesElectronicEdition:
#                 with targetOnto:
#                     placeInstance = getPlaceInstance (place)
#                     editionSituationInstance.hasPlace.append(placeInstance)

#             for element in electronicVersions:
#                 editionSituationInstance.versionInfo.append(element)


#         if editors == True:
#             digitalScoreInstance.hasEditionSituation.append(editionSituationInstance)

#         ''' does an encoder exist ? '''
#         encodersB = False
#         encodingSituationInstance = metaOnto.EncodingSituation(getUUID())
#         for element in encoders:
#             encodersB = True
#             encodingSituationInstance.hasEncoder.append (getEncoderInstance (element))
#             for place in placesElectronicEdition:
#                 with targetOnto:
#                     placeInstance = getPlaceInstance (place)
#                     encodingSituationInstance.hasPlace.append(placeInstance)

#             for dateElement in encodingDates:
#                 with targetOnto:
#                     timeIntervalInstance = coreOnto.TimeInterval(getUUID())
#                     timeIntervalInstance.time.append(dateElement)
#                     encodingSituationInstance.hasTimeInterval.append (timeIntervalInstance)


#         if encodersB == True:
#             digitalScoreInstance.hasEncodingSituation.append(encodingSituationInstance)


#         for musicGenreName in musicGenres:
#             musicGenreInstance = getMusicGenreInstance (musicGenreName)
#             musicEntityInstance.hasGenre.append(musicGenreInstance)

# ''' save the whole thing '''
# targetOnto.save(file = targetFilePath+ "_")
