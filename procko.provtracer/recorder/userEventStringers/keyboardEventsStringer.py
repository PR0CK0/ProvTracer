import re

from recorder.userEventStringers.contextStringer import ContextStringer

class KeyboardEventsStringer(ContextStringer):
  __IS_OUTPUT_LITERAL = True

  __specialKeys = {
      'Key.enter': '\n',
      'Key.space': ' ',
      'Key.backspace': '\b'
  }
  
  __ignoredKeys = {
      'Key.up',
      'Key.down',
      'Key.left',
      'Key.right'
  }
  
  def __init__(self, keyboardEventsFile):
    super().__init__(keyboardEventsFile)

  def getKeyboardEventsString(self):
    with open(self._eventsFile, 'r') as file:
      resultString = []
      
      for line in file:
        match = re.match(r'(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - )?Key pressed: (.+)', line)
        if match:
          key = match.group(1)
          
          if key in self.__specialKeys:
            keyOutput = self.__specialKeys[key]
          elif key in self.__ignoredKeys:
            continue
          else:
            keyOutput = key.strip("'")

          if self.__IS_OUTPUT_LITERAL:
            resultString.append(keyOutput)
          else:
            resultString.append(f'Key pressed: {key}')

    return ''.join(resultString) if self.__IS_OUTPUT_LITERAL else '\n'.join(resultString)