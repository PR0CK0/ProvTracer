import re

from recorder.userEventStringers.contextStringer import ContextStringer
from helperz import fileUtils

class WindowEventsStringer(ContextStringer):
  __NO_ACTIVE_WINDOW = 'No Active Window'
  
  def __init__(self, windowEventsFile):
    super().__init__(windowEventsFile)

  def getWindowEventsString(self):
    resultString = ''
    
    with open(self._eventsFile, 'r', encoding = 'utf-8', errors = 'replace') as file:
      for line in file:
        if self.__NO_ACTIVE_WINDOW not in line:
          cleanedLine = fileUtils.cleanText(line, 'filecontent')
          resultString += cleanedLine.strip() + '\n'
    
    return resultString