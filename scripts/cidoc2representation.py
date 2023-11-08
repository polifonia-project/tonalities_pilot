'''
Created on Nov 3, 2023

This takes Tonalities's cidoc export and converts it to Polifonia's music-representation

@author: christophe
'''

from owlready2 import * 
from builtins import isinstance , getattr
from rdflib import OWL, RDF, RDFS, Graph, URIRef, Literal, Namespace



def completeGraph(g):
    # add namespaces
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    dcterms = Namespace('http://purl.org/dc/terms/')
    owl = Namespace ('http://www.w3.org/2002/07/owl#')
    core = Namespace ('https://w3id.org/polifonia/ontology/core/')
    mr = Namespace ('https://w3id.org/polifonia/ontology/music-representation/')
    mm = Namespace ('https://w3id.org/polifonia/ontology/music-meta/')  
    crm = Namespace ('http://www.cidoc-crm.org/cidoc-crm/')  
    sherlock = Namespace ('http://data-iremus.huma-num.fr/ns/sherlock#') 
    iremus = Namespace ('http://data-iremus.huma-num.fr/id/') 
     
    
    g.bind('dcterms', dcterms)
    g.bind('owl', owl)
    g.bind('rdf', rdf)
    g.bind('core', core)
    g.bind('mr', mr)
    g.bind('mm', mm)  
    g.bind('crm', crm)
    g.bind('sherlock', sherlock)
    g.bind('iremus', iremus)
    

    # add IRI 
    ontology_iri = URIRef("http://www.cidoc-crm.org/cidoc-crm/")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, RDFS.label, Literal("CIDOC conversion 2 PON"))) 
    
    g.add((crm.P140_assigned_attribute_to, rdf.type, owl.ObjectProperty))
    g.add((crm.P141_assigned, rdf.type, owl.ObjectProperty))
    g.add((crm.P14_carried_out_by, rdf.type, owl.ObjectProperty))
    g.add((crm.P177_assigned_property_of_type, rdf.type, owl.ObjectProperty))
    g.add((crm.P1_is_identified_by, rdf.type, owl.AnnotationProperty))
    g.add((crm.P2_has_type, rdf.type, owl.ObjectProperty))
    #g.add((crm.P4_has_time-span, rdf.type, owl.ObjectProperty)) # hyphen problem here
    g.add((crm.P82a_begin_of_the_begin, rdf.type, owl.ObjectProperty))
    g.add((crm.P9_consists_of, rdf.type, owl.ObjectProperty))
    g.add((dcterms.created, rdf.type, owl.AnnotationProperty))
    g.add((dcterms.creator, rdf.type, owl.AnnotationProperty))
    g.add((sherlock.has_document_context, rdf.type, owl.AnnotationProperty))
    
    
    return g


def getE28List():
    'E28 are the intersection of P141 and P140 objectds '
    ' they correspond to one annotation'
    E28IRIList = []
    
    
    for E13_1 in onto.search (is_a = onto.E13_Attribute_Assignment):
        if "P106" in E13_1.P177_assigned_property_of_type: continue
        for E13_2 in onto.search (is_a = onto.E13_Attribute_Assignment): 
            if E13_1.iri == E13_2.iri: continue
            if "P106" in E13_2.P177_assigned_property_of_type: continue
            
            for element in E13_1.P177_assigned_property_of_type:
                if isinstance(element, str) == False: continue 
                if "P67" in element:
                    if onto.P2_has_type in E13_2.P177_assigned_property_of_type:
                        if E13_1.P141_assigned == E13_2.P140_assigned_attribute_to:
                            if E13_1.P141_assigned[0] in E28IRIList: continue
                            E28IRIList.append(E13_1.P141_assigned[0])
                
            for element in E13_2.P177_assigned_property_of_type: 
                if isinstance(element, str) == False: continue 
                if "P67" in element:
                    if onto.P2_has_type in E13_1.P177_assigned_property_of_type:
                        if E13_2.P141_assigned == E13_1.P140_assigned_attribute_to:
                            if E13_2.P141_assigned[0] in E28IRIList: continue
                            E28IRIList.append(E13_2.P141_assigned[0])
    return E28IRIList       
        

def getE13_P140_IRI (iri):
    E13List = []
    for E13 in onto.search (is_a = onto.E13_Attribute_Assignment):
        for element in E13.P140_assigned_attribute_to:
            if iri == element:
                E13List.append(E13)
    return E13List
            
def getE13_P141_IRI (iri):
    E13List = []
    for E13 in onto.search (is_a = onto.E13_Attribute_Assignment):
        for element in E13.P141_assigned:
            if iri == element:
                E13List.append(E13)
    return E13List

def filterE13_with_P177_P106 (E13List):
    FilteredE13List=[]
    for E13 in E13List:
        for element in E13.P177_assigned_property_of_type:
            if not isinstance(element, str): continue
            if "P106" in element:
                FilteredE13List.append(E13)
    return FilteredE13List

def filterE13_with_P177_P67 (E13List):
    FilteredE13List=[]
    for E13 in E13List:
        for element in E13.P177_assigned_property_of_type:
            if "P67" in element:
                FilteredE13List.append(E13)
    return FilteredE13List

def filterE13_with_P177_P2 (E13List):
    FilteredE13List=[]
    for E13 in E13List:
        for element in E13.P177_assigned_property_of_type:
            if onto.P2_has_type == element:
                FilteredE13List.append(E13)
    return FilteredE13List

def createFragmentFromIRI(scoreElementIRI):
    scoreElementName = scoreElementIRI.split("/")[-1]
    with targetOnto:
        fragmentInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Fragment(scoreElementName)

    ''' TODO : based on the IRI, build the correct music projection element'''
    
    return fragmentInstance

def createObservationFromIRI (E13Name):
    with targetOnto:
        with targetOnto:
            observationInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Observation(E13Name)
        return observationInstance
    
    
def createMusicProjectionFromIRI (musicProjectionIRI, E13Name):
    if "#" in musicProjectionIRI:
        className = musicProjectionIRI.split("#")[-1]
        
    else:
    
        className = musicProjectionIRI.split("/")[-1]
    theoreticalModel = getTheoreticalOntologyForIRI (musicProjectionIRI)
    
    with targetOnto:
        projectionInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").MusicProjection(E13Name + "_" + className)
        projectionInstance.is_a.append(getattr(theoreticalModel, className))
        
    return projectionInstance


def createAnnotatorFromIRI (annotatorIRI):    
    with targetOnto:
            annotatorInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Annotator(annotatorIRI.split("/")[-1])
             
            ''' TODO: complete information here ''' 
    return annotatorInstance
             

def getAnnotatorFromIRI (annotatorIRI): 
    for annotator in targetOnto.search(is_a = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Annotator):
        if annotator.name == annotatorIRI.split("/")[-1]:
            return annotator 
    return createAnnotatorFromIRI (annotatorIRI)
        
    
        

def getTheoreticalOntologyForIRI (observationIRI):
    ''' import the corresponding ontology if necessary ''' 
    if "#" in observationIRI:
        className = observationIRI.split("#")[-1]
        modelBaseIri = observationIRI.replace("#" + className, "#")
        ontoName = modelBaseIri.split("/")[-1].replace("#", "")
        
    else:
    
        className = observationIRI.split("/")[-1]
        modelBaseIri = observationIRI.replace(className, "")
        ontoName = modelBaseIri.split("/")[-2]
    
    
     
    ontologyExists = False
    for importedOnto in targetOnto.imported_ontologies:
        if importedOnto.name == ontoName: 
            ontologyExists = True
        
    if ontologyExists == False:
        ontologyToBeImported = get_ontology(ontoDic[ontoName]).load()
        targetOnto.imported_ontologies.append(ontologyToBeImported)
        
        
    return get_ontology(modelBaseIri)



def createAnnotationFromE28IRI(E28IRI): 
    E13_P141List = getE13_P141_IRI(E28IRI)
    E13_P141List_filterdE13_with_P177_P67 = filterE13_with_P177_P67(E13_P141List) # fragment(s)
    
    E13_140List = getE13_P140_IRI(E28IRI)
    E13_140List_filterdE13_with_P177_P2 = filterE13_with_P177_P2(E13_140List)
 
    with targetOnto:
        annotationInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Annotation(E13_P141List_filterdE13_with_P177_P67[0].name)
        
        for analysis in analysisList:
            analysis.hasAnnotation.append(annotationInstance)
        
        for fragment in  E13_P141List_filterdE13_with_P177_P67[0].P140_assigned_attribute_to:
            annotationInstance.hasFragment.append(createFragmentFromIRI(fragment))
        
        E13Name = E13_140List_filterdE13_with_P177_P2[0].name
        print (len (E13_140List_filterdE13_with_P177_P2))
        annotationInstance.hasObservation = createObservationFromIRI(E13Name)
        
        for E13_140List_filterdE13_with_P177_P2_E in E13_140List_filterdE13_with_P177_P2:
            if len (E13_140List_filterdE13_with_P177_P2) == 2:
                    print ()
            for musicProjection in E13_140List_filterdE13_with_P177_P2_E.P141_assigned:
                annotationInstance.hasObservation.hasSubject.append(createMusicProjectionFromIRI(musicProjection, E13Name))
             
            
        for annotator in E13_P141List_filterdE13_with_P177_P67[0].P14_carried_out_by:
            annotationInstance.hasAnnotator.append(getAnnotatorFromIRI(annotator)) 
            
        for dctermsCreated in E13_P141List_filterdE13_with_P177_P67[0].created:
            annotationInstance.created.append(dctermsCreated)  
            
    ''' process the bottom levels (if any) recursively '''
    E13_140List_filteredE13_with_P177_P106 = filterE13_with_P177_P106(E13_140List)
    
    for E13_140_filteredE13_with_P177_P106 in E13_140List_filteredE13_with_P177_P106:
        for bottomE28IRI in E13_140_filteredE13_with_P177_P106.P141_assigned:
            bottomAnnotation = createAnnotationFromE28IRI(bottomE28IRI)
            bottomAnnotation.isDerivedFrom.append(annotationInstance)
            
    return annotationInstance
        

def getTopAnnotationIRIs(E28IRIList):
    'top annotations are E28s witch are not the objects of P141<=E13=>P_177=>P106 but only P141<=E13=>P_177=>P67 ''' 
    topAnnotationIRIList = []
    
    for E28IRI in E28IRIList:
        E13_P141_IRI = getE13_P141_IRI (E28IRI)
        
        E13_with_P177_P106 = filterE13_with_P177_P106(E13_P141_IRI)
        if len(E13_with_P177_P106) == 0: 
            topAnnotationIRIList.append(E28IRI)  
    return topAnnotationIRIList

def createAnalystFromIRI (E21IRI):   
    with targetOnto:
        analystInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Analyst(E21IRI.split("/")[-1])
        
        '''TODO: specify names etc. '''
        
        return analystInstance
        
    


def createAnalysis():
    analysisList = []
    ''' process E7s '''
    for E7 in  onto.search (is_a = onto.E7_Activity): 
        with targetOnto:
            analysisInstance = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Analysis(E7.name)
            for identifiedBy in E7.P1_is_identified_by:
                analysisInstance.title.append(identifiedBy) 
                analysisList.append(analysisInstance)
                
            for analyst in E7.P14_carried_out_by:
                analysisInstance.involvesAnalyst.append(createAnalystFromIRI(analyst))
                
    return analysisList
            
def bindAnnotationsToScore (score):
    for annotation in targetOnto.search(is_a = get_ontology("https://w3id.org/polifonia/ontology/music-representation/").Annotation):
        score.hasAnnotation.append(annotation)

def setScore():
    ''' get the score iri '''
    has_document_contextBool = False
    scoreIRI = None
    for E13 in onto.search (is_a = onto.E13_Attribute_Assignment):
        if has_document_contextBool == True: break
        if hasattr(E13, "has_document_context"):
            for element in E13.has_document_context:
                scoreIRI = element
                has_document_contextBool = True
                break
    
    if "_" in scoreIRI:
        scoreIRI = scoreIRI.split("_")[0]
    scoreName = scoreIRI.split("/")[-1]
    
    with targetOnto:
        scoreInstance = get_ontology("https://w3id.org/polifonia/ontology/music-meta/").Score(scoreName)
        
    return scoreInstance 
    

if __name__ == '__main__':
    pass

''' paths to import and export '''

importFilePath = "/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/cidoc/Bologna_modalInference_1.ttl" 
targetFilePath = "/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/music-representation/Bologna_modalInference_1.owl"

ontoDic = {
    "Cadences_FilaberGuillotelGurrieri_2023": "https://raw.githubusercontent.com/polifonia-project/music-analysis-ontology/main/annotationModels/Cadences_FilaberGuillotelGurrieri_2023.owl",
    "zarlino": "https://raw.githubusercontent.com/polifonia-project/music-analysis-ontology/main/annotationModels/zarlino.owl",
    "Fugues": "https://github.com/polifonia-project/music-analysis-ontology/blob/main/annotationModels/Fugue.owl"
    }

''' convert the turtle input into RDF; change and add what's needed; and load everything into a graph'''
g = Graph()
g.parse(importFilePath, format="turtle") 
#g = changeIRI(g) # this is a workaround to change temporally the score and iremus IRIs // otherwise owlReady crashes unexpectedly 
g= completeGraph(g) # add namespaces. etc. 
g.serialize("temp.rdf", format="xml")
onto = get_ontology("temp.rdf").load() # import from Tonalities 

''' this is the target graph, i.e. where the data will be fed in ''' 
targetOnto = get_ontology("analysisOntology.rdf").load()
targetOnto.base_iri = "http://modality-tonality.huma-num.fr/analysis/"

''' import music representation ''' 
targetOnto.imported_ontologies.append(get_ontology("https://raw.githubusercontent.com/polifonia-project/music-representation-ontology/main/ontology/music-representation.owl").load())

''' create analyses =>E7'''
analysisList = createAnalysis () 
 

''' get all E28 iris (they correspond to annotations) ''' 
E28IRIList = getE28List()

''' get top annotation iris '''
topE28List = getTopAnnotationIRIs (E28IRIList)

''' create top annotations and bottom annotations recursively'''
for topE28IRI in topE28List:
    createAnnotationFromE28IRI(topE28IRI)

''' set score and connect annotationns '''

bindAnnotationsToScore(setScore())

''' write onto file '''
targetOnto.save(file = targetFilePath)