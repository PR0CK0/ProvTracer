import time, os
from datetime import datetime
from pynput import mouse

from recorder.userEvents.userEvent import UserEvent

class MouseEvents(UserEvent):
  mouseListener = None
  
  def __init__(self, outputFolder, noisy):
    super().__init__(outputFolder, noisy)
    self.mouseEventsFolder = super().getEventSubfolder('mouse_events')
    
    self.mouseListener = mouse.Listener(on_click = self.onClick, on_scroll = self.onScroll, on_move = self.onMove)
    self.mouseListener.start()

  def saveMouseEventsFile(self, timestamp):
    filePath = os.path.join(self.mouseEventsFolder, f'mouse_event_{timestamp}.txt')
    
    with open(filePath, 'w', encoding = 'utf-8') as file:
      for mouseInput in self._events:
        file.write(f'{mouseInput}\n')
    
    self._events = []

  def logMouseEvent(self, event):
    lastMouseEventTimeStr = datetime.fromtimestamp(self._lastActivityTime).strftime(super()._EVENT_DATETIME_FORMAT)
    if (self._noisy):
      lastMouseEvent = f'{lastMouseEventTimeStr} - {event}'
    else:
      lastMouseEvent = f'{event}'
    self._events.append(lastMouseEvent)

  def onClick(self, x, y, button, pressed):
    self._lastActivityTime = time.time()
    if pressed:
      self.logMouseEvent(f'Mouse clicked at ({x}, {y}) with {button}')

  def onScroll(self, x, y, dx, dy):
    self._lastActivityTime = time.time()
    self.logMouseEvent(f'Mouse scrolled at ({x}, {y}) with delta ({dx}, {dy})')

  def onMove(self, x, y):
    self._lastActivityTime = time.time()
    self.logMouseEvent(f'Mouse moved to ({x}, {y})')