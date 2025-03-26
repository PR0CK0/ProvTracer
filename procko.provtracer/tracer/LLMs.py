from enum import Enum

class LLMs(Enum):
  GPT_4O = 'gpt-4o'
  GPT_4O_MINI = 'gpt-4o-mini'
  GPT_4_TURBO = 'gpt-4-turbo'

class LLMConfig:
  LLMS_AVAILABLE = tuple(model.value for model in LLMs)
  _LLM_CHOSEN = LLMs.GPT_4O_MINI.value

  @classmethod
  def getDefaultLLM(cls):
    return LLMs.GPT_4O_MINI.value

  @classmethod
  def getLLMChosen(cls):
    return cls._LLM_CHOSEN

  @classmethod
  def setLLMChosen(cls, value):
    if value in cls.LLMS_AVAILABLE:
      cls._LLM_CHOSEN = value
    else:
      raise ValueError(f'Invalid LLM value: {value}')