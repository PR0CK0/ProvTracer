import os, time
from datetime import datetime
from pynput import keyboard

from recorder.userEvents.userEvent import UserEvent

class KeyboardEvents(UserEvent):
  keyListener = None
    
  def __init__(self, outputFolder, noisy):
    super().__init__(outputFolder, noisy)
    self.keyEventsFolder = super().getEventSubfolder('keyboard_events')
    
    self.keyListener = keyboard.Listener(on_press = self.onPress, on_release = self.onRelease)
    self.keyListener.start()

  def saveKeyEventsFile(self, timestamp):
    filePath = os.path.join(self.keyEventsFolder, f'keyboard_event_{timestamp}.txt')
    
    with open(filePath, 'w', encoding = 'utf-8') as file:
      for keyInput in self._events:
        file.write(f'{keyInput}\n')
        
    self._events.clear()

  def logKeyboardEvent(self, event):
    lastKeyboardEventTimeStr = datetime.fromtimestamp(self._lastActivityTime).strftime(super()._EVENT_DATETIME_FORMAT)
    if (self._noisy):
      lastKeyboardEvent = f'{lastKeyboardEventTimeStr} - {event}'
    else:
      lastKeyboardEvent = f'{event}'
    self._events.append(lastKeyboardEvent)

  def onPress(self, key):
    self._lastActivityTime = time.time()
    self.logKeyboardEvent(f'Key pressed: {key}')

  def onRelease(self, key):
    self._lastActivityTime = time.time()
    self.logKeyboardEvent(f'Key released: {key}')