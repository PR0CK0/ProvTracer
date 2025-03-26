import time, os, threading
from datetime import datetime
import pyperclip

from recorder.userEvents.userEvent import UserEvent

class ClipboardEvents(UserEvent):
  __lastActivityTime = time.time()
  __SLEEP_TIME_SECONDS = 0.5

  def __init__(self, outputFolder, noisy):
    super().__init__(outputFolder, noisy)
    self.__clipboardEventsFolder = super().getEventSubfolder('clipboard_events')
      
    try:
      self.__initial_clipboard = pyperclip.paste()
    except Exception:
      self.__initial_clipboard = ''
    self.__recentValue = self.__initial_clipboard
    
    self.startMonitoringThread()

  def startMonitoringThread(self):
    self.monitoring_thread = threading.Thread(target = self.startClipboardCapture)
    self.monitoring_thread.daemon = True
    self.monitoring_thread.start()

  def saveClipboardEventsFile(self, timestamp):
    filePath = os.path.join(self.__clipboardEventsFolder, f'clipboard_event_{timestamp}.txt')
    
    with open(filePath, 'w', encoding = 'utf-8') as file:
      for clipboardEvent in self._events:
        file.write(f'{clipboardEvent}\n\n\n')
    
    self._events = []

  def logClipboardEvent(self, event):
    lastActivityTimeStr = datetime.fromtimestamp(self.__lastActivityTime).strftime(super()._EVENT_DATETIME_FORMAT)
    if (self._noisy):
      lastActivity = f'{lastActivityTimeStr} - Clipboard changed:\n{event}\n\n\n'
    else:
      lastActivity = f'Clipboard changed:\n{event}\n\n\n'
    self._events.append(lastActivity)

  def startClipboardCapture(self):    
    while True: 
      try:
        clipboardValue = pyperclip.paste()
        
        if clipboardValue != self.__recentValue:
          self.__recentValue = clipboardValue
          self.__lastActivityTime = time.time()
          self.logClipboardEvent(f'{self.__recentValue}')
        
        time.sleep(self.__SLEEP_TIME_SECONDS)
      
      except Exception as e:
        print(f'Warning: {e}')