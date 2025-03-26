import os, time
from datetime import datetime
import pygetwindow as gw

from recorder.userEvents.userEvent import UserEvent

class WindowEvents(UserEvent):
  __TK_TITLE = 'tk'
  __NO_ACTIVE_WINDOW = 'No Active Window'

  def __init__(self, outputFolder, noisy):
    super().__init__(outputFolder, noisy)
    self._EVENT_SUBFOLDER_PREFIX = 'window_events'
    self.__windowEventsFolder = super().getEventSubfolder(self._EVENT_SUBFOLDER_PREFIX)
  
  def saveWindowEventsFile(self, timestamp):
    filePath = os.path.join(self.__windowEventsFolder, f'window_event_{timestamp}.txt')
    
    with open(filePath, 'w', encoding = 'utf-8') as file:
      for windowTitle in self._events:
        file.write(f'{windowTitle}\n')
    
    self._events = []

  def logWindowTitleChange(self):
    self._lastActivityTime = time.time()
    lastWindowTimeStr = datetime.fromtimestamp(self._lastActivityTime).strftime(super()._EVENT_DATETIME_FORMAT)
    if (self._noisy):
      lastWindow = f'{lastWindowTimeStr} - {self.getActiveWindowTitle()}'
    else:
      lastWindow = f'{self.getActiveWindowTitle()}'

    self._events.append(lastWindow)
 
  def getActiveWindowTitle(self):
    try:
      window = gw.getActiveWindow()
      if window and window.title != self.__TK_TITLE and window.title != '':
        return window.title
      return self.__NO_ACTIVE_WINDOW
    except Exception as e:
      return f'Error: {e}'