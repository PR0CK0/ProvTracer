from tracer.gptCall.gptPrompter import GPTPrompter

class LLMPrompter:
	def __init__(self, contexts, apiKey):
		self.__contexts = contexts
		self.__apiKey = apiKey

	def promptLLM(self, screenshotImageFilePath):
		gptPrompter = GPTPrompter(screenshotImageFilePath, self.__contexts, self.__apiKey)
