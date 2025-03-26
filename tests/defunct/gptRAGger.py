import os, sys, threading
from datetime import datetime
from openai import OpenAI

base = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base, 'helperz\\'))

from tracer.gptCall.gptCaller import GPTCaller
from helperz.imageUtils import ImageUtils

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
sessionStartTimestamp = datetime.now().strftime(DATETIME_FORMAT)

# TODO sanity if checks may be unnecessary

# TODO may have to go with different logic... upload screenshot as RAG input every time, because message content image base64 not seeming to work... can possibly overwrite with same ID to save ops... reference this ID as the working image in each prompt
  # image_file -> file_id, purpose = 'vision'
  
# TODO we can possibly look at SEVERAL images at once, not just one, because of RAG
# either
  # upload one image at a time, deleting the previous
  # pick a number of them to look at, possibly ALL, and batch RAG across them

# TODO...
# 1. upload as base64 NOT possible with assistant
# 2. upload to vector store (done) and reference it with assistant (not possible, unsupported file type)
# 3. upload screenshot as URL and reference it directly?
# https://platform.openai.com/docs/api-reference/messages/createMessage

class GPTRAGger(GPTCaller):
  def __init__(self, contexts, deleteExtant = True):
    self.__contexts = contexts
    self.deleteExtant = deleteExtant
    
    self.__imageUtils = ImageUtils()
    
    self.client = OpenAI(api_key = super().API_KEY)
    self.vectorStore = None
    self.uploadedSourceArtifactFile = None
    self.assistant = None
    self.thread = None
    
    if self.deleteExtant:
      self.__startDeleteThreads()
      
    # TODO
    # i make thread and join because assistant creation and file upload takes an indeterminate amount of time
    assistantCreationThread = threading.Thread(target = self.createRAGAssistant)
    assistantCreationThread.start()
    assistantCreationThread.join()
    
    # TODO RAG prompt input...
    # The issue is that chat completions are atomic, while assistant calls are "live", meaning you repeatedly message an assistant within a thread, or "session". Each action is a "run".
    # So... when starting GPTCaller, need to branch: 1. like normal, atomic prompts and 2. spawn a thread and allow "atomic prompts", i.e., runs within that thread. 

    # definitively... need an answer... but i don't think RAG image inputs are possible. we could use a completions vision to get a textual description of the image and use alongside a normal assistant call for RAG.

  def createRAGAssistant(self):
    print('--Creating RAG assistant...')
    
    self.__createVectorStore()
    self.__createAssistant()

    # TODO ONLY IF NOT EXTANT... because there is one per session!
    self.__uploadSourceArtifactFileToVectorStore(self.__contexts.sourceArtifactFilePath)
  
  # TODO TODO TODO
  # TODO upload screenshot image every single time
  def promptRAGAssistant(self, screenshotImageFilePath):
    # TODO TODO TODO
    self.__uploadScreenshot(screenshotImageFilePath)
    self.__createAssistantThread(screenshotImageFilePath)
    self.__createRun()
    


  # TODO not even used...
  # TODO issue is it's not in any specific vector store... have to specify
  def __uploadScreenshot(self, screenshotImageFilePath):
    print('testing screenshot upload...')
    self.uploadedScreenshotFile = self.client.files.create(file = open(screenshotImageFilePath, 'rb'), purpose = 'vision')
    
    if self.vectorStore and self.uploadedSourceArtifactFile:
      self.client.beta.vector_stores.files.create(vector_store_id = self.vectorStore.id, file_id = self.uploadedScreenshotFile.id)
      print(f"Uploaded: '{self.uploadedSourceArtifactFile.filename}' to vector store {self.vectorStore.id}")
    else:
      print('Vector store or uploaded file not found.')


  def __startDeleteThreads(self):
    fileThread = threading.Thread(target = self.__deleteFiles)
    vectorStoreThread = threading.Thread(target = self.__deleteVectorStores)

    fileThread.start()
    vectorStoreThread.start()
    
    fileThread.join()
    vectorStoreThread.join()
    
  def __deleteFiles(self):
    files = self.client.files.list()
    if files.data:
      for file in files.data:
        try:
          self.client.files.delete(file.id)
          print(f"---Deleted: '{file.filename}' -- {file.id}")
        except Exception as e:
          print(f'---Problem RAG file - skipping! Error: {e}')
    else:
      print('---No RAG files to delete.')

  def __deleteVectorStores(self):
    vectorStores = self.client.beta.vector_stores.list()
    if vectorStores.data:
      for vs in vectorStores.data:
        try:
          self.client.beta.vector_stores.delete(vs.id)
          name = getattr(vs, 'name', 'Unknown Name')
          id = getattr(vs, 'id', 'Unknown ID')
          print(f"---Deleted: '{name}' -- {id}")
        except Exception as e:
          print(f'---Problem RAG vector store - skipping! Error: {e}')
    else:
      print('---No RAG vector stores to delete.')

  # TODO rename vs
  def __createVectorStore(self):
    name = 'test_vector_store_' + sessionStartTimestamp
    self.vectorStore = self.client.beta.vector_stores.create(name = name)
    print(f"--Created: '{self.vectorStore.name}' -- {self.vectorStore.id}")
    
  def __uploadSourceArtifactFileToVectorStore(self, sourceArtifactFilePath):
    self.uploadedSourceArtifactFile = self.client.files.create(file = open(sourceArtifactFilePath, 'rb'), purpose = 'assistants')
    
    if self.vectorStore and self.uploadedSourceArtifactFile:
      self.client.beta.vector_stores.files.create(vector_store_id = self.vectorStore.id, file_id = self.uploadedSourceArtifactFile.id)
      print(f"Uploaded: '{self.uploadedSourceArtifactFile.filename}' to vector store {self.vectorStore.id}")
    else:
      print('Vector store or uploaded file not found.')

  def __createAssistant(self):
    if self.vectorStore:
      name = 'test_' + sessionStartTimestamp
      self.assistant = self.client.beta.assistants.create(
        name = name,
        instructions = 'This is a test. Let me know you work!',
        model = 'gpt-4o',
        tools = [{'type': 'file_search'}],
        tool_resources = {
          'file_search': {
            'vector_store_ids': [self.vectorStore.id]
          }
        }
      )
      print(f'--Created assistant with vector store id: {self.vectorStore.id}')
    else:
      print('--Vector store not found.')

  def __createAssistantThread(self, screenshotImageFilePath):
    screenshotImageBase64 = self.__imageUtils.getBase64Image(screenshotImageFilePath)
    #print(screenshotImageBase64)
    #print('--\n')
    
    if self.uploadedSourceArtifactFile:
      self.thread = self.client.beta.threads.create(
        messages = [
          {
            'role': 'user',
            'content': [
              {
                'type': 'text',
                'text': 'Tell me what is in the image in 20 words. Also tell me the first word in the attached file.'              
              }
              # TODO nope ,
              #{
              #  'type': 'image_file',
              #  'image_file': {
              #    'file_id': self.uploadedScreenshotFile.id
              #  }
              #}
              # TODO nope ,
              #{
              #  'type': 'image_url',
              #  'image_url': {
              #    'url': f'data:image/png;base64, {screenshotImageBase64}',
              #    'detail': 'auto'
              #  }
              #}
            ],
            # TODO attach image here? need to reference docs to know...
            'attachments': [
              {'file_id': self.uploadedSourceArtifactFile.id, 'tools': [{'type': 'file_search'}]}
            ],
          }
        ],
        tool_resources = {
          'file_search': {
            'vector_store_ids': [self.vectorStore.id]
          }
        }
      )

    else:
      print('Uploaded file not found.')

  def __createRun(self):
    if self.assistant and self.thread:
      run = self.client.beta.threads.runs.create_and_poll(thread_id = self.thread.id, assistant_id = self.assistant.id)
      messages = list(self.client.beta.threads.messages.list(thread_id = self.thread.id, run_id = run.id))

      messageContent = messages[0].content[0].text

      print(messageContent)
      #print(messages[0].content[1].image_url.url)

      annotations = messageContent.annotations
      citations = []
      for index, annotation in enumerate(annotations):
        messageContent.value = messageContent.value.replace(annotation.text, f' [{index}]')
        if fileCitation := getattr(annotation, 'file_citation', None):
          cited_file = self.client.files.retrieve(fileCitation.file_id)
          citations.append(f'[{index}] {cited_file.filename}')

      print('\n' + messageContent.value)
      print('\n'.join(citations))
    else:
      print('Assistant or thread not found.')