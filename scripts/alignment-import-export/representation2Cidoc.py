'''
Created on Nov 5, 2023

@author: christophe

This takes Polifonia's music representation ontology and converts it to SHERLOCK/CIDOC 
'''
from owlready2 import *   
import os, uuid, time  
from datetime import datetime as DT


if __name__ == '__main__':
    pass


def scoreToE1(score):
    
    E1Instance = crm.E1_CRM_Entity(uuid.uuid4 ())
    E42Instance = crm.E42_Identifier(uuid.uuid4 ())
    
    
    E1Instance.P1_is_identified_by.append(E42Instance)
    E42Instance.P190_has_symbolic_content.append(score.iri)
    
    return E1Instance

def analysisToE7(analysis):
    with sherlock:
        E7Instance = crm.E7_Activity(analysis.name)
        
        E41Instance = crm.E41_Appellation(uuid.uuid4 ())
        E41Instance.P190_has_symbolic_content =  analysis.coreTitle
        E7Instance.P1_is_identified_by.append(E41Instance)
        E52Instance = crm["E52_Time-Span"](uuid.uuid4 ())
        E52Instance.P82a_begin_of_the_begin.append(getEarliestTimeStampFromAnnotations())
        
        for analyst in analysis.involvesAnalyst:
            E21Instance = getE21FromUUID (analyst.name)
            E7Instance.creator.append(E21Instance)
            E7Instance.P14_carried_out_by.append(E21Instance)
        
        E7Instance.has_privacy_type= privacyType
        E7Instance.P2_has_type.append(activityType) 
         
        for E13 in getE13():
            E7Instance.P9_consists_of.append(E13)
    return E7Instance
    
    
def setCreatorAndDateToE13(E13, creator, date):
    E13.P14_carried_out_by.append(creator)
    E13.creator.append(creator)
    E13.created.append(date)
    
    
    

def annotationToE13Pattern(annotation):
    E13_P_177_P67Instance = crm.E13_Attribute_Assignment(annotation.name)
    E13_P_177_P67Instance.P177_assigned_property_of_type.append(crm.P67_refers_to)
   
    E28Instance = crm.E28_Conceptual_Object(uuid.uuid4 ())
    E13_P_177_P67Instance.P141_assigned.append(E28Instance)
    
    E13_P_177_P2Instance = crm.E13_Attribute_Assignment(annotation.hasObservation.name)
    E13_P_177_P2Instance.P140_assigned_attribute_to.append(E28Instance)
    E13_P_177_P2Instance.P177_assigned_property_of_type.append(crm.P2_has_type)
    
    for fragment in annotation.describesFragment:
        E1Instance = crm.E1_CRM_Entity(fragment.name)
        E13_P_177_P67Instance.P140_assigned_attribute_to.append(E1Instance)    
        
    for observationSubject in annotation.hasObservation.hasSubject:
        E1Instance = crm.E1_CRM_Entity(observationSubject)
        E13_P_177_P2Instance.P141_assigned.append(E1Instance)
        
    bottomAnnotationList = getBottomAnnotations(annotation)
    
    ''' if the annotation has child annotation, extend annotation pattern '''
    if len (bottomAnnotationList) != 0:
        E13_P177_P106Instance = crm.E13_Attribute_Assignment(uuid.uuid4 ())
        E13_P177_P106Instance.P140_assigned_attribute_to.append(E28Instance)
        E13_P177_P106Instance.P177_assigned_property_of_type.append(crm.P106_is_composed_of)
    
    
        for bottomAnnotation in bottomAnnotationList:
            E13_P_177_P67InstanceBottom = annotationToE13Pattern(bottomAnnotation)
            connectTopBottom(E13_P_177_P67Instance, E13_P_177_P67InstanceBottom)
        
    return E13_P_177_P67Instance


def connectTopBottom (E13_P_177_P67InstanceTop, E13_P_177_P67InstanceBottom): 
    for P141_elementTop in E13_P_177_P67InstanceTop.P141_assigned: 
        if crm.E28_Conceptual_Object in P141_elementTop.is_a: 
        
            for E13_P177 in getE13_P177_ConnectedToE28 (P141_elementTop):
            
                for P141_elementBottom in E13_P_177_P67InstanceBottom.P141_assigned: 
                    if crm.E28_Conceptual_Object in P141_elementBottom.is_a: 
                        E13_P177.P141_assigned.append(P141_elementBottom)
    

def getE13_P177_ConnectedToE28(E28):
    E13List = []
    for E13 in sherlock.search (is_a = crm.E13_Attribute_Assignment):
        if E28 in E13.P140_assigned_attribute_to:
            E13List.append(E13)
    
    return E13List

 
           

def getBottomAnnotations (topAnnotation):
    childAnnotationList = []
    ''' given a top annotation, return the annotations witch are derived for the top annotation'''  
    for annotation in inputOnto.search (type = mr.Annotation):    
        if hasattr(annotation, "isDerivedFrom"):
            if topAnnotation in annotation.isDerivedFrom: 
                childAnnotationList.append (annotation)
    
    return childAnnotationList

def getEarliestTimeStampFromAnnotations():
    creationDateList = []
    for annotation in inputOnto.search (type = mr.Annotation): 
        try: 
            timeR = time.mktime(DT.strptime(annotation.created[0],"%Y-%m-%d %H:%M:%S.%f").timetuple()) 
            creationDateList.append([timeR, annotation])
        except: 
            print ("Cannot read annotation creation date: " + str (annotation))
    
    
    if len (creationDateList) == 0: return DT.now().strftime("%Y-%m-%d %H:%M:%S.%f") 
    creationDateList.sort(key=lambda x: x[0], reverse=True)
    
    return creationDateList[0][1].created[0]
    
        

def getAnalysis ():
    analysisList = []
    for analysis in inputOnto.search (type = mr.Analysis):
        analysisList.append(analysis)
    
    return analysisList

def getScore():
    scoreList = []
    for score in inputOnto.search (type = mm.Score):
        scoreList.append(score)
    
    return scoreList

def getTopAnnotations():
    annotationList = []
    for annotation in inputOnto.search (type = mr.Annotation):
        if len (annotation.isDerivedFrom) != 0: continue
        annotationList.append(annotation)
    
    return annotationList

def getE13 ():
    E13List = []
    for E13 in sherlock.search (type = crm.E13_Attribute_Assignment):
        E13List.append(E13)
    return E13List
         

def getE21FromUUID(E21UUID):
    for E21 in sherlock.search (type = crm.E21_Person): 
        if E21.name == E21UUID:
            return E21
    with sherlock:
        E21Instance = crm.E21_Person(E21UUID)
       
    return E21Instance 
   
dt_string = DT.now().strftime("%d%m%Y_%H%M")

''' paths '''
crmPath = "/Users/christophe/Documents/CIDOC/CIDOC_CRM_v7.1.2.rdf"
inputPath = "/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/music-representation/21112023_2107.owl"
cidocOutputPath = "/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/cidoc/" + dt_string + '.owl'
mmPath = "https://raw.githubusercontent.com/polifonia-project/music-meta-ontology/main/ontology/musicmeta.owl"  
mrPath = "https://raw.githubusercontent.com/polifonia-project/music-representation-ontology/main/ontology/music-representation.owl"
corePath = "https://raw.githubusercontent.com/polifonia-project/core-ontology/main/ontology/core.owl"

''' ontologies '''
sherlock = get_ontology("https://data-iremus.huma-num.fr/sherlock/id/") 
sherlock_ns = get_ontology("http://data-iremus.huma-num.fr/ns/sherlock#")
crm = get_ontology(crmPath).load()
inputOnto = get_ontology(inputPath).load()
mm = get_ontology(mmPath).load()
mr = get_ontology(mrPath).load()
core = get_ontology(corePath).load()

''' imports '''
sherlock.imported_ontologies.append(crm) 

''' python names '''
core.title.python_name = "coreTitle"

''' add sherlock elements'''

with sherlock:
    class has_privacy_type(ObjectProperty, FunctionalProperty):
        namespace = sherlock_ns 

with sherlock:
    namespace = sherlock 
    privacyType = owl.Thing("cabe46bf-23d4-4392-aa20-b3eb21ad7dfd")
    activityType = owl.Thing("21816195-6708-4bbd-a758-ee354bb84900")
    

with sherlock : 
    for score in getScore():
        E1Instance = scoreToE1(score)
          
    for annotation in getTopAnnotations():
        E13Pattern = annotationToE13Pattern(annotation)
          
    for analysis in getAnalysis():
        E7Instance = analysisToE7(analysis)
     
    

''' write onto file '''
sherlock.save(file = cidocOutputPath)

