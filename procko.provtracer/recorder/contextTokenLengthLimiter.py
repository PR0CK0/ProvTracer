from recorder.contextFileEnum import ContextFileEnum

class ContextTokenLengthLimiter(ContextFileEnum):  
  def __init_(self):
    pass
  
  def limitLength(self, contextText, contextType):    
    limit = self.__determineCharacterLimit(contextType)
            
    if contextText == '':
      emptyString = self.__checkEmpty(contextText, contextType)
      return emptyString
    
    if len(contextText) > limit:
      return contextText[:limit]
    
    return contextText
    
  def __determineCharacterLimit(self, contextType):
    if contextType == super().MOUSE_EVENTS:
      return super().MOUSE_EVENTS_CHAR_LIMIT
    if contextType == super().KEYBOARD_EVENTS:
      return super().KEYBOARD_EVENTS_CHAR_LIMIT
    if contextType == super().WINDOW_EVENTS:
      return super().WINDOW_EVENTS_CHAR_LIMIT
    if contextType == super().CLIPBOARD_EVENTS:
      return super().CLIPBOARD_EVENTS_CHAR_LIMIT
    
  def __checkEmpty(self, contextText, contextType):
    isEmpty = not bool(contextText.strip())
    
    if isEmpty:
      if contextType == super().MOUSE_EVENTS:
        return super().MOUSE_EVENTS_EMPTY
      if contextType == super().KEYBOARD_EVENTS:
        return super().KEYBOARD_EVENTS_EMPTY
      if contextType == super().WINDOW_EVENTS:
        return super().WINDOW_EVENTS_EMPTY
      if contextType == super().CLIPBOARD_EVENTS:
        return super().CLIPBOARD_EVENTS_EMPTY