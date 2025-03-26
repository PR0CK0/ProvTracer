class Contexts():
  sessionName = ''
  primerContext = ''
  
  isPrimerContextEnabled = False
  areMouseEventsEnabled = False
  areKeyboardEventsEnabled = False
  areWindowEventsEnabled = False
  areClipboardEventsEnabled = False
  isNarratorAudioEnabled = False
  isSourceArtifactEnabled = False
  sourceArtifactFilePath = ''
  
  isOpenEnded = True
  isSideBySide = False

  recordOnly = False
    
  def __init__(self, isPrimerContextEnabled = False, areMouseEventsEnabled = False, areKeyboardEventsEnabled = False, areWindowEventsEnabled = False,  areClipboardEventsEnabled = False, isNarratorAudioEnabled = False, isSourceArtifactEnabled = False):
    self.isPrimerContextEnabled = isPrimerContextEnabled
    self.areMouseEventsEnabled = areMouseEventsEnabled
    self.areKeyboardEventsEnabled = areKeyboardEventsEnabled
    self.areWindowEventsEnabled = areWindowEventsEnabled
    self.areClipboardEventsEnabled = areClipboardEventsEnabled
    self.isNarratorAudioEnabled = isNarratorAudioEnabled
    self.isSourceArtifactEnabled = isSourceArtifactEnabled
    
  def setRecordOnly(self, recordOnly):
    self.recordOnly = recordOnly

  def setOpenEnded(self, isOpenEnded):
    self.isOpenEnded = isOpenEnded

  def setSideBySide(self, isSideBySide):
    self.isSideBySide = isSideBySide
    
  def setSessionName(self, text):
    self.sessionName = text  
  
  def setPrimerContext(self, text):
    self.primerContext = text
    
  def setSourceArtifactFilePath(self, filePath):
    self.sourceArtifactFilePath = filePath
    
  def __str__(self):
    return (f'isPrimerContextEnabled: {self.isPrimerContextEnabled}\n'
            f'areWindowEventsEnabled: {self.areWindowEventsEnabled}\n'
            f'areMouseEventsEnabled: {self.areMouseEventsEnabled}\n'
            f'areKeyboardEventsEnabled: {self.areKeyboardEventsEnabled}\n'
            f'areClipboardEventsEnabled: {self.areClipboardEventsEnabled}\n'
            f'isNarratorAudioEnabled: {self.isNarratorAudioEnabled}\n'
            f'isSourceArtifactEnabled: {self.isSourceArtifactEnabled}\n'
            f'isOpenEnded: {self.isOpenEnded}\n'
            f'isSideBySide: {self.isSideBySide}')