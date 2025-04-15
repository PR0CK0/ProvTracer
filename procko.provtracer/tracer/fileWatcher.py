import sys, os, time, threading
from queue import Queue

from tracer.llmPrompter import LLMPrompter

class FileWatcher():
  __FILE_WATCH_SLEEP_TIME_SECONDS = 1
  __NUMBER_OF_THREADS = 5
  __IMAGE_EXTENSIONS = {'.png'}

  def __init__(self, directoryToWatch, contexts, apiKey, numThreads, pauseEvent):
    self.__WATCH_DIRECTORY = directoryToWatch
    self.__NUMBER_OF_THREADS = numThreads
    self.__pauseEvent = pauseEvent

    self.__llm = LLMPrompter(contexts, apiKey)

    self.__processedFiles = set()
    self.__fileQueue = Queue()
    self.__filesEncountered = 0
    self.__filesProcessed = 0
    self.__lock = threading.Lock()
        
  def startFileWatch(self):
    watcherThread = threading.Thread(target = self.watchDirectory, daemon = True)
    watcherThread.start()
    
    for _ in range(self.__NUMBER_OF_THREADS):
      workerThread = threading.Thread(target = self.worker, daemon = True)
      workerThread.start()

  def watchDirectory(self):
    while True:
      files = set(os.listdir(self.__WATCH_DIRECTORY))
      newFiles = files - self.__processedFiles
      for fileName in newFiles:
        file_path = os.path.join(self.__WATCH_DIRECTORY, fileName)
        if os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in self.__IMAGE_EXTENSIONS:
          self.__fileQueue.put(file_path)
          with self.__lock:
            self.__processedFiles.add(fileName)
            self.__filesEncountered += 1
      time.sleep(self.__FILE_WATCH_SLEEP_TIME_SECONDS)

  def worker(self):
    while True:
      filePath = self.__fileQueue.get()
      if filePath:
        time.sleep(self.__FILE_WATCH_SLEEP_TIME_SECONDS * 2)
        self.__llm.promptLLM(filePath)
        self.__pauseEvent.wait()
        self.__fileQueue.task_done()
        with self.__lock:
          self.__filesProcessed += 1

  def getFilesEncountered(self):
    with self.__lock:
      return self.__filesEncountered

  def getFilesProcessed(self):
    with self.__lock:
      return self.__filesProcessed