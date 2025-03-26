import os
import json

class PromptLoader():
  __PROMPTS_FILENAME = 'prompts.json'
  __PROMPTS_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), __PROMPTS_FILENAME)
  
  def __init__(self):
    self.__prompts = self.loadPrompts()

  def loadPrompts(self):
    if not os.path.exists(self.__PROMPTS_FILEPATH):
      raise FileNotFoundError(f'Prompt file {self.__PROMPTS_FILEPATH} not found.')
    
    with open(self.__PROMPTS_FILEPATH, 'r', encoding = 'utf-8') as file:
      return json.load(file)
  
  def getPrompt(self, category, promptKey):
    categoryPrompts = self.__prompts.get(category)
    if categoryPrompts:
      return categoryPrompts.get(promptKey, 'Prompt not found')
    return 'Category not found'