import os
from openai import OpenAI

from recorder.userEventStringers.mouseEventsStringer      import MouseEventsStringer
from recorder.userEventStringers.keyboardEventsStringer   import KeyboardEventsStringer
from recorder.userEventStringers.windowEventsStringer     import WindowEventsStringer
from recorder.userEventStringers.clipboardEventsStringer  import ClipboardEventsStringer
from recorder.contextTokenLengthLimiter                   import ContextTokenLengthLimiter
from tracer.LLMs                                          import LLMConfig
from tracer.gptCall.gpt                                   import GPT
from tracer.gptCall.gptPromptMessageTemplate              import GPTPromptMessageTemplate
from tracer.promptLoader                                  import PromptLoader
from helperz.imageUtils                                   import ImageUtils
from helperz.fileUtils                                    import ContextFileUtils

class GPTPrompter(GPT):    
  def __init__(self, screenshotImageFilePath, contexts, apiKey): 
    self.__client = OpenAI(api_key = apiKey)
    
    self.__promptLoader = PromptLoader()
    self.__imageUtils = ImageUtils()
    
    self.__screenshotImageFilePath = screenshotImageFilePath
    self.__screenshotImageBase64 = self.__imageUtils.getBase64Image(screenshotImageFilePath)
    self.__contexts = contexts
    
    if not self.__contexts.recordOnly:
      self.getPlaintextResponse()
  
  def getPlaintextResponse(self):    
    gptPromptTemplate = GPTPromptMessageTemplate(self.buildPromptString(super().PROMPT_TYPE_PLAINTEXT), self.__screenshotImageBase64)
    gptMessage = gptPromptTemplate.getMessage()
    
    response = None
    try:
      response = self.__client.chat.completions.create(
        model = LLMConfig.getLLMChosen(),
        messages = gptMessage,
        max_tokens = super().GPT_MAX_TOKENS,
        temperature = super().GPT_TEMPERATURE,
        presence_penalty = super().GPT_PRESENCE_PENALTY
      )
    except Exception as e:
      print(e)
      print('Bad file for %s' %self.__screenshotImageFilePath)
      
    # TODO maybe remove image here if bad? save from 400 exception?
    if response is not None:
      responseContent = response.choices[0].message.content
      self.saveResponseToFile(responseContent)
      
  def saveResponseToFile(self, response):
    outputFolder = os.path.dirname(os.path.dirname(self.__screenshotImageFilePath))
    fileTimestamp = os.path.splitext(os.path.basename(self.__screenshotImageFilePath))[0].replace('screenshot_', '')

    responsesFolder = os.path.join(outputFolder, 'responses')
    os.makedirs(responsesFolder, exist_ok = True)

    responseFilePath = os.path.join(responsesFolder, f'response_{fileTimestamp}.txt')
    with open(responseFilePath, 'w', encoding = 'utf-8') as file:
      file.write(response)

    print(f'response_{fileTimestamp}')
    
  def buildPromptString(self, promptType):
    contextFileUtils = ContextFileUtils()
    contextTokenLengthLimiter = ContextTokenLengthLimiter()
    
    promptString = ''

    if promptType == self.PROMPT_TYPE_PLAINTEXT:
      promptString = self.__promptLoader.getPrompt('promptBodies', 'plaintextPrompt')
    else:
      promptString = self.__promptLoader.getPrompt('promptBodies', 'turtlePrompt')

    promptString += '\n'
    if self.__contexts.isOpenEnded:
      promptString += self.__promptLoader.getPrompt('transitions', 'openEndedTransition') + '\n'
    elif self.__contexts.isSideBySide:
      promptString += self.__promptLoader.getPrompt('transitions', 'sideBySideTransition') + '\n'

    if self.__contexts.isPrimerContextEnabled or self.__contexts.areMouseEventsEnabled or self.__contexts.areKeyboardEventsEnabled or self.__contexts.areWindowEventsEnabled  or self.__contexts.areClipboardEventsEnabled or self.__contexts.isNarratorAudioEnabled or self.__contexts.isSourceArtifactEnabled:
      promptString += '\n'
      promptString += self.__promptLoader.getPrompt('transitions', 'contextTransition') + '\n'
    else:
      self.savePromptToFile(promptString)
      return promptString
  
    if self.__contexts.isPrimerContextEnabled:
      promptString += self.__promptLoader.getPrompt('modifiers', 'primerContextModifier') + '\n'
      promptString += self.__contexts.primerContext + '\n'
      
    if self.__contexts.areWindowEventsEnabled:
      filePath = contextFileUtils.getContextFile(self.__screenshotImageFilePath, 'window_events')
      
      if os.path.exists(filePath):
        windowEventsStringer = WindowEventsStringer(filePath)
        compressedWindowEventsString = contextTokenLengthLimiter.limitLength(windowEventsStringer.getWindowEventsString(), 'window_events')
        if promptString.strip():
          promptString += self.__promptLoader.getPrompt('modifiers', 'windowEventsModifier') + '\n'
          promptString += compressedWindowEventsString + '\n'
      
    if self.__contexts.areMouseEventsEnabled:
      filePath = contextFileUtils.getContextFile(self.__screenshotImageFilePath, 'mouse_events')
      
      if os.path.exists(filePath):
        mouseEventsStringer = MouseEventsStringer(filePath)
        compressedMouseEventsString = contextTokenLengthLimiter.limitLength(mouseEventsStringer.getMouseEventsString(), 'mouse_events')
        if promptString.strip():
          promptString += self.__promptLoader.getPrompt('modifiers', 'mouseEventsModifier') + '\n'
          promptString += compressedMouseEventsString + '\n'
      
    if self.__contexts.areKeyboardEventsEnabled:
      filePath = contextFileUtils.getContextFile(self.__screenshotImageFilePath, 'keyboard_events')
            
      if os.path.exists(filePath):
        keyboardEventsStringer = KeyboardEventsStringer(filePath)
        compressedKeyboardEventsString = contextTokenLengthLimiter.limitLength(keyboardEventsStringer.getKeyboardEventsString(), 'keyboard_events')
        if promptString.strip():
          promptString += self.__promptLoader.getPrompt('modifiers', 'keyboardEventsModifier') + '\n'
          promptString += compressedKeyboardEventsString + '\n'
        
    if self.__contexts.areClipboardEventsEnabled:
      filePath = contextFileUtils.getContextFile(self.__screenshotImageFilePath, 'clipboard_events')
            
      if os.path.exists(filePath):
        clipboardEventsStringer = ClipboardEventsStringer(filePath)
        compressedClipboardEventsString = contextTokenLengthLimiter.limitLength(clipboardEventsStringer.getClipboardEventsString(), 'clipboard_events')
        if promptString.strip():
          promptString += self.__promptLoader.getPrompt('modifiers', 'clipboardEventsModifier') + '\n'  
          promptString += compressedClipboardEventsString + '\n'

    self.savePromptToFile(promptString)
    return promptString
  
  def savePromptToFile(self, promptString):
    outputFolder = os.path.dirname(os.path.dirname(self.__screenshotImageFilePath))
    fileTimestamp = os.path.splitext(os.path.basename(self.__screenshotImageFilePath))[0].replace('screenshot_', '')

    promptsFolder = os.path.join(outputFolder, 'prompts')
    os.makedirs(promptsFolder, exist_ok = True)

    promptsFilePath = os.path.join(promptsFolder, f'prompt_{fileTimestamp}.txt')
    with open(promptsFilePath, 'w', encoding = 'utf-8') as file:
      file.write(promptString)