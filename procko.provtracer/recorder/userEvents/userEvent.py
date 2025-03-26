import os, time

class UserEvent:
  CONTEXTS_SUBFOLDER_STRING = 'contexts'
  _EVENT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

  def __init__(self, outputFolder, noisy = False):
    self._outputFolder = outputFolder
    self._EVENT_SUBFOLDER_PREFIX = ''
    self._lastActivityTime = time.time()
    self._events = []
    self._noisy = noisy

  def getEventSubfolder(self, eventSubfolderPrefix):
    eventSubfolder = os.path.join(self._outputFolder, self.CONTEXTS_SUBFOLDER_STRING, eventSubfolderPrefix)
    os.makedirs(eventSubfolder, exist_ok = True)
    return eventSubfolder