import sys, os, time, threading
from datetime import datetime
from PyQt6.QtWidgets import QApplication

base = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base, 'recorder/ui/'))
sys.path.append(os.path.join(base, 'recorder/'))
sys.path.append(os.path.join(base, 'tracer/'))

from recorder.ui.disclaimerWindow import DisclaimerWindow
from recorder.ui.primerWindow import PrimerWindow
from recorder.userEvents.nullEvent import NullEvent
from recorder.userEvents.screenshotter import Screenshotter
from recorder.userEvents.windowEvents import WindowEvents
from recorder.userEvents.mouseEvents import MouseEvents
from recorder.userEvents.keyboardEvents import KeyboardEvents
from recorder.userEvents.clipboardEvents import ClipboardEvents
from tracer.fileWatcher import FileWatcher

__SLOWDOWN_TIME_SECONDS = 0.1
__INACTIVE_TIME_SECONDS = 60
__DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

__OUTPUT_FOLDER = 'outputs/'
outputFolderBase = os.path.join(os.path.dirname(os.path.abspath(__file__)), __OUTPUT_FOLDER)
sessionStartTimestamp = datetime.now().strftime(__DATETIME_FORMAT)
sessionStartFolder = os.path.join(outputFolderBase, sessionStartTimestamp)
os.makedirs(outputFolderBase, exist_ok = True)
os.makedirs(sessionStartFolder, exist_ok = True)

__screenshotter = None
__windowEvents = None
__mouseEvents = None
__keyboardEvents = None
__clipboardEvents = None
__pauseEvent = None
__fileWatcher = None
__disclaimerWindow = None

def provenanceCaptureLoop():
  lastScreenshotTime = time.time()
  lastWindowTitle = __windowEvents.getActiveWindowTitle()

  while True:
    __pauseEvent.wait()
    currentTime = time.time()
    activeWindowTitle = __windowEvents.getActiveWindowTitle()

    if activeWindowTitle != lastWindowTitle:
      lastWindowTitle = activeWindowTitle
      __windowEvents.logWindowTitleChange()

    if __disclaimerWindow.lazyTerminate:
      continue

    if currentTime - lastScreenshotTime >= __primerWindow.selectedTimesliceInterval:
      timestamp = datetime.now().strftime(__DATETIME_FORMAT)
      __screenshotter.takeScreenshot(timestamp)
      __windowEvents.saveWindowEventsFile(timestamp) 
      __mouseEvents.saveMouseEventsFile(timestamp)
      __keyboardEvents.saveKeyEventsFile(timestamp)
      __clipboardEvents.saveClipboardEventsFile(timestamp)
      lastScreenshotTime = currentTime

    time.sleep(__SLOWDOWN_TIME_SECONDS)

__app = QApplication(sys.argv)
__primerWindow = PrimerWindow(sessionStartFolder)

def onPrimerClosed():
  global sessionStartFolder, __screenshotter, __windowEvents, __mouseEvents, __keyboardEvents, __clipboardEvents, __pauseEvent, __fileWatcher, __disclaimerWindow

  if __primerWindow.contexts.sessionName != '':
    newSessionStartFolder = os.path.join(outputFolderBase, f'{sessionStartTimestamp}_{__primerWindow.contexts.sessionName}')
    os.rename(sessionStartFolder, newSessionStartFolder)
    sessionStartFolder = newSessionStartFolder

  __screenshotter = Screenshotter(sessionStartFolder)
  __windowEvents = WindowEvents(sessionStartFolder, __primerWindow.timestampsIncluded) if __primerWindow.contexts.areWindowEventsEnabled else NullEvent()
  __mouseEvents = MouseEvents(sessionStartFolder, __primerWindow.timestampsIncluded) if __primerWindow.contexts.areMouseEventsEnabled else NullEvent()
  __keyboardEvents = KeyboardEvents(sessionStartFolder, __primerWindow.timestampsIncluded) if __primerWindow.contexts.areKeyboardEventsEnabled else NullEvent()
  __clipboardEvents = ClipboardEvents(sessionStartFolder, __primerWindow.timestampsIncluded) if __primerWindow.contexts.areClipboardEventsEnabled else NullEvent()

  __pauseEvent = threading.Event()
  __pauseEvent.set()

  __fileWatcher = FileWatcher(os.path.join(sessionStartFolder, 'screenshots'), __primerWindow.contexts, __primerWindow.apiKey, __primerWindow.selectedNumberOfThreads, __pauseEvent)

  fileWatcherThread = threading.Thread(target = __fileWatcher.startFileWatch)
  fileWatcherThread.daemon = True
  fileWatcherThread.start()

  __disclaimerWindow = DisclaimerWindow(sessionStartFolder, __fileWatcher, __primerWindow.contexts, __pauseEvent)
  __disclaimerWindow.show()

  provenanceThread = threading.Thread(target = provenanceCaptureLoop)
  provenanceThread.daemon = True
  provenanceThread.start()

__primerWindow.closed.connect(onPrimerClosed)
__primerWindow.show()
sys.exit(__app.exec())

try:
  sys.exit(__app.exec())

except KeyboardInterrupt:
  print('Script terminated by user!')

finally:
  __mouseEvents.mouseListener.stop()
  __keyboardEvents.keyListener.stop()

  if not os.listdir(sessionStartFolder):
    os.rmdir(sessionStartFolder)