import time

class NullEvent:
  def __init__(self):
    self.__lastActivityTime = time.time()

  def getActiveWindowTitle(self):
    return None

  def logWindowTitleChange(self):
    pass

  def saveWindowEventsFile(self, timestamp):
    pass

  def saveMouseEventsFile(self, timestamp):
    pass

  def saveKeyEventsFile(self, timestamp):
    pass

  def saveClipboardEventsFile(self, timestamp):
    pass