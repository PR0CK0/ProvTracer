import re

from recorder.userEventStringers.contextStringer import ContextStringer

class MouseEventsStringer(ContextStringer):  
  def __init__(self, mouseEventsFile):
    super().__init__(mouseEventsFile)
    
  def getMouseEventsString(self):
    resultString = ''
    
    with open(self._eventsFile, 'r', encoding = 'utf-8', errors = 'replace') as file:
      for line in file:
        match = re.match(r'(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - )?(Mouse clicked at|Mouse scrolled at) (.+)', line)
        if match:
          event = match.group(1) + ' ' + match.group(2)
          event = re.sub(r'[()]', '', event)
          resultString += event.strip() + '\n'
    
    return resultString