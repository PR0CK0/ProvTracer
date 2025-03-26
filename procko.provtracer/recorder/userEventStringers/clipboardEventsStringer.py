import sys, os

from recorder.userEventStringers.contextStringer import ContextStringer
from helperz import fileUtils

class ClipboardEventsStringer(ContextStringer):
  def __init__(self, clipboardEventsFile):
    super().__init__(clipboardEventsFile)
  
  def getClipboardEventsString(self):
    resultString = ''
    
    with open(self._eventsFile, 'r', encoding = 'utf-8', errors = 'replace') as file:
      for line in file:
        resultString += fileUtils.cleanText(line, 'filecontent')
        
    return resultString