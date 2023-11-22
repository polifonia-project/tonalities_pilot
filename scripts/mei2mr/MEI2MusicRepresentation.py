'''
Created on Nov 10, 2023

@author: christophe
This takes mei files and converts analytical annotations (currently stored in text representations) to polifonia music-representations
'''
from rdflib.namespace import DC




if __name__ == '__main__':
    pass
class annotationGroup(object):
    def __init__(self, annotation):
        durationFrame = 4
        
        highLowOffsets = getHighLowFragmentOffsets(annotation)
        
        self.offsetHigh=highLowOffsets[0] + durationFrame
        self.offsetLow = highLowOffsets[1] - durationFrame
        self.elements = [annotation]
        
    def getHighLowFragmentOffsets(self, annotation):
        offsetList = []
        for element in annotation.describesFragment:
            for offset in element.offset:
                if offset not in offsetList: offsetList.append(offset)
                
        offsetList.sort()
        return [offset[0], offset[-1]]

def createLabel2ClassDic (th):
    label2ClassDic = {}
    for thClass in th.classes():
        for label in thClass.label:
            label2ClassDic[label] = thClass
    return label2ClassDic

def getAnnotatorByID(individualID):
    ''' TODO: use a dictionary...'''

    
    for individual in sherlock.individuals():
        if individual.name == individualID:
            return individual
            
    return mr.Annotator(individualID)     

def normalizeAnnotationString(annotationString):
    ''' this is just a workaround to normalize Josquin annotations'''
    if len (annotationString)==2:
        annotationString = annotationString[0] + "_" + annotationString[1]
    
    return annotationString
        


def getObservationSubjectFromAnnotation(annotationString):
    
    annotationString = normalizeAnnotationString(annotationString)
    observationSubjectList = []
    
    ''' get individual class labels : by convention they are separated by '_' '''
     
    
    classLabels = annotationString.split("_")
    for classLabel in classLabels :
        if classLabel in label2ClassDic:
            observationSubjectList.append(label2ClassDic[classLabel])
        else:
            print ("Cannot identify the following label : " + classLabel)
    
    return observationSubjectList
            
def getHighLowFragmentOffsets(annotation):
    offsetList = []
    for element in annotation.describesFragment:
        for offset in element.offsets:
            if offset not in offsetList: offsetList.append(offset)
            
    offsetList.sort()
    if len(offsetList) == 0:
        return None
    return [offsetList[0], offsetList[-1]]
        

def createAnnotation(creationDate, annotatorID, noteList, observationSubjectList):
    with sherlock:
        annotationInstance = mr.Annotation(uuid.uuid4 ()) 
        annotationInstance.created = str(creationDate)
        annotationInstance.hasAnnotator.append(getAnnotatorByID(annotatorID))
        observationInstance = mr.Observation(uuid.uuid4 ())
        observationInstance.created = str(creationDate)
        observationInstance.hasSubject = observationSubjectList
        annotationInstance.hasObservation = observationInstance
        analysisInstance.hasAnnotation.append(annotationInstance)
        scoreInstance.hasAnnotation.append(annotationInstance)
    
        
        for note in noteList: 
            fragmentInstance = mr.Fragment(str(uuid.uuid4 ()) + "_" + note.id)
            if hasattr(fragmentInstance, "offsets"): # this won't be kept in the graph - only used for internal grouping purposes
                fragmentInstance.offsets.append(note.offset)
            else: 
                fragmentInstance.offsets = [note.offset] 
            annotationInstance.describesFragment.append(fragmentInstance )  
            
    
    return annotationInstance


def addAnnotationToGroup(annotation, annotationGroupList):
    higlLowOffset = getHighLowFragmentOffsets(annotation)
    if higlLowOffset == None:
        print ("Cannot group this annotation: " + str(annotation))
        return None
    for group in annotationGroupList:
        if group.offsetHigh >= higlLowOffset[0] and group.offsetLow <= higlLowOffset[1]:
            group.elements.append(annotation)
            return group
        
   
    group = annotationGroup(annotation) 
    annotationGroupList.append(group)
    return group

def groupAnnotations (annotationList, topObservationSubject, bottomObservationSubjectList):  
    annotationGroupList = []
    topAnnotationList = []
    for annotation in annotationList:
        for bottomObservationSubject in bottomObservationSubjectList:
            for subject in annotation.hasObservation.hasSubject:
                if bottomObservationSubject.iri in subject.iri:  
                    addAnnotationToGroup(annotation, annotationGroupList)
        
    
    for annotationGroup in annotationGroupList:
       
         
        
        with sherlock:
            topAnnotationInstance = createAnnotation(creationDate, annotatorID, [], [topObservationSubject])
            topAnnotationList.append(topAnnotationInstance)
            for annotationInstance in annotationGroup.elements:
                annotationInstance.isDerivedFrom.append(topAnnotationInstance)
                for fragment in annotationInstance.describesFragment:
                    topAnnotationInstance.describesFragment.append(fragment)
            
    
    return topAnnotationList

def getOntoClasses(th, classNameList):
    classList = []
    for element in th.classes():
        if element.name in classNameList:
            classList.append(element)
    return classList
    
       
import os, uuid
from datetime import datetime as DT
from music21 import converter, environment
from music21.note import Note, Rest
from owlready2 import *        


dt_string = DT.now().strftime("%d%m%Y_%H%M")
us = environment.UserSettings()
us['musicxmlPath'] = '/Applications/MuseScore 3.app'

''' urls and iris '''
meiURL = 'https://raw.githubusercontent.com/polifonia-project/tonalities_pilot/main/scores/Josquin/Josquin_Chansons/Jos2826_test.mei'
MROutput = '/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/music-representation/' + dt_string + '.owl'
mrPath = "https://raw.githubusercontent.com/polifonia-project/music-representation-ontology/main/ontology/music-representation.owl" 
mmPath = "https://raw.githubusercontent.com/polifonia-project/music-meta-ontology/main/ontology/musicmeta.owl"  
corePath = "https://raw.githubusercontent.com/polifonia-project/core-ontology/main/ontology/core.owl"
theoreticalModelPath = "/Users/christophe/Documents/GitHub/modal-tonal-ontology_Polifonia/annotationModels/Cadences_FilaberGuillotelGurrieri_2023.owl"
fileName = meiURL.split("/")[-1]

''' annotator, title '''
annotatorID = "bf2213e9-c8db-4c96-97b8-8eaa4b70c9b3"
title = "Cadence analysis with Cadences_FilaberGuillotelGurrieri_2023"


''' load music representation ontology '''
sherlock = get_ontology("https://data-iremus.huma-num.fr/sherlock/id/representation/") # import from Tonalities 
mr = get_ontology(mrPath).load()
mm = get_ontology(mmPath).load()
core = get_ontology(corePath).load()
dc = get_ontology("http://purl.org/dc/terms/").load()
th = get_ontology(theoreticalModelPath).load()
sc = get_ontology(meiURL.replace(fileName, ""))

sherlock.imported_ontologies.append(mr)
sherlock.imported_ontologies.append(dc)

core.title.python_name = "coreTitle"

label2ClassDic= createLabel2ClassDic(th)

''' read the MEI ''' 

''' read files and store cadence analyses in list '''
 
    
    
''' get file update date '''
creationDate = DT.now().strftime("%Y-%m-%d %H:%M:%S.%f") ### TODO

''' create score,  analysis and analyst '''
with sc:
    scoreInstance = owl.Thing(fileName)    

with sherlock: 
    scoreInstance.is_a.append(mm.Score)
     
    analysisInstance = mr.Analysis(uuid.uuid4 ())
    analystInstance = getAnnotatorByID(annotatorID)

    analysisInstance.involvesAnalyst.append(analystInstance)
    analysisInstance.coreTitle.append(title)

print (fileName)
work = converter.parseURL(meiURL)



annotationList = [] # list of all annotated elements 


''' loop over annotations and convert them in polifonia MR'''
for part in work.parts: 
    flatPart = part.flat
    for annotation in part.flat.getElementsByClass('TextExpression'):   
        noteList = []
        for note in flatPart.getElementsByOffset(annotation.offset, classList=[Note, Rest]):
            noteList.append(note)  
        annotationList.append (createAnnotation(creationDate, annotatorID, noteList, getObservationSubjectFromAnnotation(annotation.content)))
            

classList = getOntoClasses(th, ["Altizans_a", "Altizans_A", "Bassizans_B", "Bassizans_b", "Bassizans_P", "Cantizans_C", "Cantizans_c", "Cantizans_ç", "Tenorizans_T", "Tenorizans_t", "Contratenorizans"])

''' apply rules to deduce derived relations ? '''
for topAnnotation in groupAnnotations (annotationList, th.Cadence, classList):
    annotationList.append(topAnnotation)

   
    
''' write onto file '''
sherlock.save(file = MROutput) 



        
        
        