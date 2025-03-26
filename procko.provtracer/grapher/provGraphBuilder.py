import os, sys, re, getpass, platform
from datetime import datetime
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from rdflib.namespace import RDFS, PROV, XSD, FOAF

from recorder.contextTokenLengthLimiter import ContextTokenLengthLimiter

BASE_IRI = 'http://example.org/terms#'
BFO_IRI = 'http://purl.obolibrary.org/obo/bfo#'

class ProvGraphBuilder:
  def __init__(self, outputPath):
    self.graph = Graph()

    self.EX = Namespace(BASE_IRI)
    self.BFO = Namespace(BFO_IRI)
    self.graph.bind('prov', PROV)
    self.graph.bind('xsd', XSD)
    self.graph.bind('ex', self.EX)
    self.graph.bind('foaf', FOAF)
    self.graph.bind('bfo', self.BFO)

    self.graph.add((PROV.Activity, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((PROV.Activity, URIRef('http://www.w3.org/2002/07/owl#equivalentClass'), self.BFO['0000015']))
    self.graph.add((PROV.Agent, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((PROV.Agent, URIRef('http://www.w3.org/2002/07/owl#subClassOf'), self.BFO['0000023']))
    self.graph.add((PROV.Entity, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((PROV.Entity, URIRef('http://www.w3.org/2002/07/owl#equivalentClass'), self.BFO['0000002']))

    self.graph.add((self.BFO['0000015'], RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.BFO['0000015'], RDFS.label, Literal('Process')))
    self.graph.add((self.BFO['0000015'], RDFS.isDefinedBy, URIRef(self.BFO)))
    self.graph.add((self.BFO['0000023'], RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.BFO['0000023'], RDFS.label, Literal('Role')))
    self.graph.add((self.BFO['0000023'], RDFS.isDefinedBy, URIRef(self.BFO)))
    self.graph.add((self.BFO['0000002'], RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.BFO['0000002'], RDFS.label, Literal('Continuant')))
    self.graph.add((self.BFO['0000002'], RDFS.isDefinedBy, URIRef(self.BFO)))

    self.graph.add((self.EX.WorkSession, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.EX.WorkSession, RDF.type, PROV.Activity))
    self.graph.add((self.EX.WorkTimeslice, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.EX.WorkTimeslice, RDF.type, PROV.Activity))
    self.graph.add((self.EX.TimeslicePacket, RDF.type, URIRef('http://www.w3.org/2002/07/owl#Class')))
    self.graph.add((self.EX.TimeslicePacket, RDF.type, PROV.Entity))

    self.knowledgeWorker = self.EX.KnowledgeWorker
    self.graph.add((self.knowledgeWorker, RDF.type, PROV.Agent))
    systemUsername = self.getSystemUsername()
    self.graph.add((self.knowledgeWorker, FOAF.accountName, Literal(systemUsername)))

    self.contextTokenLengthLimiter = ContextTokenLengthLimiter()
    self.workTimeslices = {}
    self.initializeSession(outputPath)

  def getSystemUsername(self):
    try:
      username = os.getenv('USERNAME') or os.getenv('USER')
      if username:
        return username
      return getpass.getuser()
    except Exception as e:
      print(f'Warning: Failed to get system username: {e}')
      if platform.system() == 'Windows':
        return 'Unknown Windows User'
      elif platform.system() == 'Linux':
        return 'Unknown Linux User'
      else:
        return 'Unknown User'

  def sanitizeText(self, text):
    sanitizedText = text.replace('\n', ' ').replace('\r', ' ')
    sanitizedText = re.sub(r'[^\x20-\x7E]+', '', sanitizedText)
    return sanitizedText.strip()

  def initializeSession(self, outputPath):
    self.sessionFolder = outputPath
    self.sessionTimestamp, self.sessionName = self.extractSessionTimestamp(outputPath)
    self.sessionTimestamp = self.formatToISO8601(self.sessionTimestamp)
    self.workSession = URIRef(f'{self.EX}WorkSession_{self.sessionTimestamp}')

    self.graph.add((self.workSession, RDF.type, self.EX.WorkSession))
    self.graph.add((self.workSession, self.EX.sessionName, Literal(self.sessionName)))
    self.graph.add((self.workSession, PROV.wasAssociatedWith, self.knowledgeWorker))
    self.graph.add((self.knowledgeWorker, PROV.influenced, self.workSession))

  def formatToISO8601(self, timestamp):
    try:
      dt_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H-%M-%S')
      return dt_obj.isoformat()
    except ValueError as e:
      print(f'Error formatting timestamp: {e}')
      return timestamp

  def extractSessionTimestamp(self, folderPath):
    folderName = os.path.basename(folderPath)
    match = re.match(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_?(.*)', folderName)
    if match:
      timestamp, sessionName = match.groups()
      return timestamp.replace('_', 'T', 1), sessionName or 'unnamed'
    raise ValueError(f'Invalid session folder name: {folderName}')

  def createWorkTimeslice(self, timestamp):
    if timestamp not in self.workTimeslices:
      workTimeslice = self.EX[f'WorkTimeslice_{timestamp}']
      self.graph.add((workTimeslice, RDF.type, self.EX.WorkTimeslice))
      self.graph.add((workTimeslice, PROV.startedAtTime, Literal(timestamp, datatype=XSD.dateTime)))
      self.graph.add((workTimeslice, PROV.wasAssociatedWith, self.knowledgeWorker))
      self.graph.add((workTimeslice, PROV.wasInformedBy, self.workSession))
      self.workTimeslices[timestamp] = workTimeslice

    return self.workTimeslices[timestamp]

  def chainWorkTimeslices(self):
    sorted_timestamps = sorted(self.workTimeslices.keys())
    for i in range(1, len(sorted_timestamps)):
      earlier_timeslice = self.workTimeslices[sorted_timestamps[i - 1]]
      later_timeslice = self.workTimeslices[sorted_timestamps[i]]
      self.graph.add((earlier_timeslice, PROV.influenced, later_timeslice))
      self.graph.add((later_timeslice, PROV.wasInfluencedBy, earlier_timeslice))

  def parseContexts(self):
    contextsPath = os.path.join(self.sessionFolder, 'contexts')
    primerPath = os.path.join(contextsPath, 'primer_context.txt')

    if os.path.exists(primerPath):
      with open(primerPath, 'r', encoding = 'utf-8', errors = 'replace') as file:
        primerContent = self.sanitizeText(file.read())
        self.graph.add((self.workSession, self.EX.primerContext, Literal(primerContent)))

    eventFolders = ['window_events', 'keyboard_events', 'mouse_events', 'clipboard_events']
    for eventType in eventFolders:
      eventPath = os.path.join(contextsPath, eventType)
      if os.path.isdir(eventPath):
        for eventFile in os.listdir(eventPath):
          if eventFile.endswith('.txt'):
            with open(os.path.join(eventPath, eventFile), 'r', encoding = 'utf-8', errors = 'replace') as file:
              eventContent = self.contextTokenLengthLimiter.limitLength(self.sanitizeText(file.read()), eventType)
              timestamp = self.extractAndValidateTimestamp(eventFile)
              if timestamp:
                workTimeslice = self.createWorkTimeslice(timestamp)
                packet = self.createTimeslicePacket(workTimeslice, timestamp)
                self.addAttributeToTimeslicePacket(packet, eventType, eventContent)

  def parsePromptsAndResponses(self):
    promptsPath = os.path.join(self.sessionFolder, 'prompts')
    responsesPath = os.path.join(self.sessionFolder, 'responses')

    try:
      for promptFile in os.listdir(promptsPath):
        if promptFile.endswith('.txt'):
          with open(os.path.join(promptsPath, promptFile), 'r', encoding = 'utf-8', errors = 'replace') as file:
            promptContent = self.sanitizeText(file.read())
            timestamp = self.extractAndValidateTimestamp(promptFile)
            if timestamp:
              workTimeslice = self.createWorkTimeslice(timestamp)
              packet = self.createTimeslicePacket(workTimeslice, timestamp)
              self.addAttributeToTimeslicePacket(packet, 'prompt', promptContent)
    except FileNotFoundError:
        print(f"Warning: Prompts folder '{promptsPath}' not found. Skipping prompts parsing.")
    
    try:
      for responseFile in os.listdir(responsesPath):
        if responseFile.endswith('.txt'):
          with open(os.path.join(responsesPath, responseFile), 'r', encoding = 'utf-8', errors = 'replace') as file:
            responseContent = self.sanitizeText(file.read())
            timestamp = self.extractAndValidateTimestamp(responseFile)
            if timestamp:
              workTimeslice = self.createWorkTimeslice(timestamp)
              packet = self.createTimeslicePacket(workTimeslice, timestamp)
              self.addAttributeToTimeslicePacket(packet, 'response', responseContent)
    except FileNotFoundError:
        print(f"Warning: Responses folder '{responsesPath}' not found. Skipping responses parsing.")

  def parseScreenshots(self):
    screenshotsPath = os.path.join(self.sessionFolder, 'screenshots')

    for screenshotFile in os.listdir(screenshotsPath):
      if screenshotFile.endswith('.png'):
        timestamp = self.extractAndValidateTimestamp(screenshotFile)
        if timestamp:
          workTimeslice = self.createWorkTimeslice(timestamp)
          packet = self.createTimeslicePacket(workTimeslice, timestamp)
          self.addAttributeToTimeslicePacket(packet, 'screenshot', screenshotFile)

  def createTimeslicePacket(self, workTimeslice, timestamp):
    packet = self.EX[f'TimeslicePacket_{timestamp}']
    self.graph.add((packet, RDF.type, self.EX.TimeslicePacket))
    self.graph.add((packet, PROV.wasGeneratedBy, workTimeslice))
    self.graph.add((workTimeslice, PROV.generated, packet))
    self.graph.add((packet, PROV.generatedAtTime, Literal(timestamp, datatype=XSD.dateTime)))
    return packet

  def addAttributeToTimeslicePacket(self, packet, attribute, value):
    self.graph.add((packet, self.EX[attribute], Literal(value)))

  def extractAndValidateTimestamp(self, fileName):
    match = re.search(r'(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', fileName)
    if match:
      timestamp_str = match.group(1)
      try:
        dt_obj = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
        return dt_obj.isoformat()
      except ValueError:
        pass
    return None

  def buildGraph(self):
    self.parseContexts()
    self.parsePromptsAndResponses()
    self.parseScreenshots()
    self.chainWorkTimeslices()

    sanitizedTimestamp = self.sessionTimestamp.replace(':', '-')
    sessionInfo = sanitizedTimestamp
    if self.sessionName:
      sessionInfo += f'_{self.sessionName}'
    rdfOutputFilename = f'{sessionInfo}_provenance_traces.ttl'
    rdfOutputPath = os.path.join(self.sessionFolder, rdfOutputFilename)
    self.graph.serialize(destination = rdfOutputPath, format = 'turtle')
    print(f'RDF graph saved to {rdfOutputPath}')