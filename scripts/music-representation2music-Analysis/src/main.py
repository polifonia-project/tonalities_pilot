'''
Created on Sep 26, 2023

@author: CGN
used to convert Polifonia annotation/observation individuals in individuals of the theoretical models (Polifonia analysis ontology)    


1. read the polifonia meta export 
2. rebuild the dependencies and put the instances into the ontology
3. feed the stuff in a file 

'''

from owlready2 import * 
from builtins import isinstance 
from rdflib import OWL, RDF, RDFS, Graph, URIRef, Literal, Namespace


def changeScoreURI(g):
    for s, p, o in g:
        if "https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/scores/" in str(o): # the score path
            gitHubFileName = str(o).split("/")[-1]
            githubFilePath = str(o).replace(gitHubFileName, "")
            g.remove((s, p, o))
            g.add ((s, p, URIRef(githubFilePath+gitHubFileName+"_")))    
    return g 

def completeGraph(g):
    # add namespaces
    rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    dcterms = Namespace('http://purl.org/dc/terms/')
    owl = Namespace ('http://www.w3.org/2002/07/owl#')
    core = Namespace ('https://w3id.org/polifonia/ontology/core/')
    mr = Namespace ('https://w3id.org/polifonia/ontology/music-representation/')
    mm = Namespace ('https://w3id.org/polifonia/ontology/music-meta/') 
    
    g.bind('dcterms', dcterms)
    g.bind('owl', owl)
    g.bind('rdf', rdf)
    g.bind('core', core)
    g.bind('mr', mr)
    g.bind('mm', mm) 

    # add IRI 
    ontology_iri = URIRef("https://w3id.org/polifonia/ontology/music-representation")
    g.add((ontology_iri, RDF.type, OWL.Ontology))
    g.add((ontology_iri, RDFS.label, Literal("Ontology exported from Tonalities / Polifonia"))) 
    
    # add annotation properties
    g.add((dcterms.created, rdf.type, owl.AnnotationProperty))
    g.add((core.isDerivedFrom, rdf.type, owl.AnnotationProperty))
    g.add((core.title, rdf.type, owl.AnnotationProperty))
    g.add((mr.describesFragment, rdf.type, owl.AnnotationProperty))
    g.add((mr.hasAnnotation, rdf.type, owl.AnnotationProperty))
    g.add((mr.hasAnnotator, rdf.type, owl.AnnotationProperty))
    g.add((mr.hasFragment, rdf.type, owl.AnnotationProperty))
    g.add((mr.hasObservation, rdf.type, owl.AnnotationProperty))
    g.add((mr.hasSubject, rdf.type, owl.AnnotationProperty))
    g.add((mr.involvesAnalyst, rdf.type, owl.AnnotationProperty))
    return g
 

def createAnalyticalInstances(annotationIndividual):
    analyticalInstanceList = []
    ''' check if the corresponding class is in the target ontology, if not, import'''
    for observation in annotationIndividual.hasObservation:
        observationSubjectList = observation.hasSubject
        for observationSubject in observationSubjectList:
            manageImportsForThisObservation(observationSubject)
            
        
            with targetOnto:
                if not hasattr(observationSubject, "is_a"):
                    if "#" in observationSubject:
                        className = observationSubject.split("#")[-1]
                    else:
                        className =  observationSubject.split("/")[-1] 
                else:
                    className = observationSubject.name
                
                ''' get the right import '''
                for importedOnto in targetOnto.imported_ontologies:
                    if importedOnto.name == getOntoName(observationSubject): 
                    
                        createdInstance = getattr(importedOnto, className)()
                        createdInstance.name = observation.name 
                        createdInstance.created = annotationIndividual.created 
                        createdInstance.creator = annotationIndividual.hasAnnotator 
                        for element in annotationIndividual.describesFragment:
                            createdInstance.P140_assigned_attribute_to.append(element)
                                    
                        analyticalInstanceList.append(createdInstance)  
    return analyticalInstanceList

def createClassesFromAnnotations(analysisIndividual, derivedFromAnnotation):
    ''' this takes as an entry point a top level annotation (analysisIndividual)
    lists the bottom level annotations (derivedFromTopAnnotations)
    
    and reconnects both levels with the correct property '''
    
    derivedFromTopAnnotations = getAnnotations(analysisIndividual, derivedFromAnnotation)# gets the derived annotations

    for derivedAnnotation in derivedFromTopAnnotations:
        bottomAnalyticalInstances = createAnalyticalInstances (derivedAnnotation)
        
        ''' connect top to bottom '''
        topAnalyticalInstances = getAnalyticalInstancesFromAnnotation(derivedFromAnnotation)
        
        
        for bottomAnalyticalInstance in bottomAnalyticalInstances:
            for topAnalyticalInstance in topAnalyticalInstances:
                reconnectTopBottom(topAnalyticalInstance, bottomAnalyticalInstance)
            
        createClassesFromAnnotations(derivedFromAnnotation, derivedAnnotation)
        
def getAnalysis():
    ''' returns the Analysis instance (there is only one) of the export '''
    for classInstanceAnalysis in onto.search (is_a = onto.Analysis):
        if onto.Analysis in classInstanceAnalysis.is_a :
            return classInstanceAnalysis

def getAnalyticalInstancesFromAnnotation(annotation):
    ''' this takes an annotation and returns the corresponding observation instances in the target ontology '''
    analyticalInstanceList = []
    
    if hasattr(annotation, "hasObservation"):
        for observation in annotation.hasObservation:
            analyticalInstance = getIndividualByName(observation.name)
            if analyticalInstance != None:
                analyticalInstanceList.append(analyticalInstance)
    
    return analyticalInstanceList

def getAnnotations(analysisIndividual, derivedFrom = None):
    annotationList = []
    
    if derivedFrom == None: # top level
        if hasattr(analysisIndividual, "hasAnnotation" ):
            for annotation in analysisIndividual.hasAnnotation:
                if len (annotation.isDerivedFrom) == 0:
                    annotationList.append(annotation)
    
    else:
        for annotationInstance in onto.search (is_a = onto.Annotation):  
            if hasattr(annotationInstance, "isDerivedFrom" ):
                if derivedFrom in annotationInstance.isDerivedFrom:
                    annotationList.append(annotationInstance)                    
    return annotationList

def getIndividualByName (indName):     
    for individual in targetOnto.individuals():
        if individual.name == indName:
            return individual
            
    return None

def getOntoName(ontoIRI):
    ''' used to get the onto iri either from a string or from an individual '''
    ontoName = None
    if hasattr(ontoIRI, "iri"): ontoIRI = ontoIRI.iri
    ''' IRI with # '''
    if "#" in ontoIRI:
        ontoIri = ontoIRI.split("#")[0]
        ontoName = ontoIri.split("/")[-1]
        
    else: 
        ''' IRI with / '''
        className =  ontoIRI.split("/")[-1]
        ontoIri = ontoIRI.split ("/" + className)[0]
        ontoName = ontoIri.split("/")[-1]
    return ontoName

def getPropertiesOfTopClass (topInstance):
    value2PropertyDict = {}
    ancestorList = []
    
    for topClass in topInstance.is_a:
        for topClassAncestor in topClass.ancestors() :
            ancestorList.append(topClassAncestor)
        
    for ancestor in ancestorList:
        for element in ancestor.is_a:
            if isinstance(element, owlready2.Restriction):
                value2PropertyDict[element.value] = element.property
    return value2PropertyDict

def manageImportsForThisObservation (observationSubject):
    ''' import the corresponding ontology if necessary '''
    if not hasattr(observationSubject, "is_a"): # this is a recognized class 
        ontologyExists = False 
        ontoName = getOntoName (observationSubject) 
        for importedOnto in targetOnto.imported_ontologies:
            if importedOnto.name == ontoName: 
                ontologyExists = True
            
        if ontologyExists == False:
            ontologyToBeImported = get_ontology(ontoDic[ontoName]).load()
            targetOnto.imported_ontologies.append(ontologyToBeImported)

def reconnectTopBottom (topInstance, bottomInstance):
    possibleConnectionList = []
    
    bottomAncestorList = []
    ''' get properties of top class '''
    value2PropertyDict=getPropertiesOfTopClass(topInstance)
    
    ''' get ancestors of bottom instance '''
    for bottomClass in bottomInstance.is_a:
        for bottomClassAncestor in bottomClass.ancestors() :
            bottomAncestorList.append(bottomClassAncestor)
            
    ''' check if one of the bottom ancestors is a key in the dictionary '''
    for bottomAncestor in bottomAncestorList:
        if bottomAncestor in value2PropertyDict:
            possibleConnectionList.append(bottomAncestor)
            
    if len (possibleConnectionList)>=1:
        
        if len (possibleConnectionList)>1: 
            print ("Several association possibilities for " + str (bottomInstance))
        
        with targetOnto: 
            
            prop = value2PropertyDict[possibleConnectionList[0]]._name
            getattr(topInstance, prop).append(bottomInstance)
            
    else: 
        print ("Cannot associate bottom instance " + str (bottomInstance) + "to top instance " + str(topInstance))


def setDigitalScore():
    MM = onto.get_namespace("https://w3id.org/polifonia/ontology/music-meta/")
    OWL = onto.get_namespace("http://www.w3.org/2002/07/owl#")
  
    for classInstanceAnalysis in onto.search (is_a = MM.DigitalScore):
        with targetOnto:
            createdInstance = MM.DigitalScore()
            createdInstance.name = classInstanceAnalysis.name
            for sameAs in classInstanceAnalysis.INDIRECT_equivalent_to:
                FileName = sameAs.split("/")[-1]
                GHString = sameAs.replace(FileName, "")
                GH = onto.get_namespace(GHString)
                
            
                
                with GH:
                    score = Thing() 
                    score.name = FileName[0:-1] 
                
                createdInstance.equivalent_to = [score]                
                #createdInstance.equivalent_to.append(score)       
            
    

if __name__ == '__main__':
    pass
''' ontology dictionaries '''


''' TODO: the dic should be created dynamically based on the ontologies available in the interface... '''

ontoDic = {
    "Cadences_FilaberGuillotelGurrieri_2023": "https://raw.githubusercontent.com/polifonia-project/music-analysis-ontology/main/annotationModels/Cadences_FilaberGuillotelGurrieri_2023.owl",
    "zarlino": "https://raw.githubusercontent.com/polifonia-project/music-analysis-ontology/main/annotationModels/zarlino.owl",
    "Fugues": "https://github.com/polifonia-project/music-analysis-ontology/blob/main/annotationModels/Fugue.owl"
    }

''' pathes to import and export '''

importFilePath = "/Users/christophe/Downloads/Bologna_modalInference_1.ttl" 
targetFilePath = "/Users/christophe/Documents/New York 2023/analysisOntology.owl"


''' convert the turtle input into RDF; change and add what's needed; and load everything into a graph'''
g = Graph()
g.parse(importFilePath, format="turtle") 
g = changeScoreURI(g) # this is a workaround to change temporally the score IRI // otherwise owlReady crashes unexpectedly 
g= completeGraph(g) # add namespaces. etc. 
g.serialize("temp.rdf", format="xml")
onto = get_ontology("temp.rdf").load() # import from Tonalities 

''' this is the target graph, i.e. where the data will be fed in '''
targetOnto = get_ontology("analysisOntology.rdf").load()

''' take the analysis individual as an entry point (there is only one) ''' 
analysisIndividual = getAnalysis()

''' create digital score '''
setDigitalScore()

''' create recursively ontology classes and properties starting from top annotation (i.e. analysis) '''
topLevelAnnotations = getAnnotations(analysisIndividual)

for topLevelAnnotation in topLevelAnnotations:
    topAnalyticalInstances = createAnalyticalInstances (topLevelAnnotation)
    
    ''' get derived level annotations and create corresponding classes '''
    createClassesFromAnnotations(analysisIndividual, topLevelAnnotation)

    
''' write onto file '''
targetOnto.save(file = targetFilePath) 




