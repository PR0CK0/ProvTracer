import sys
import os
from PyQt6.QtWidgets import (
  QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QEvent, QPoint
from PyQt6.QtGui import QGuiApplication
from grapher.provGraphBuilder import ProvGraphBuilder

class DisclaimerWindow(QWidget):
  WINDOW_TITLE = 'ProvTracer'
  WINDOW_DESC = 'You are being recorded'
  WINDOW_DESC_PAUSED = 'Paused'
  WINDOW_DESC_LAZY_TERMINATE = 'Waiting and Terminating'
  LABEL_TERMINATE_BUTTON = 'Terminate Now'
  LABEL_LAZY_TERMINATE_BUTTON = 'Wait and Terminate'
  LABEL_PAUSE_BUTTON = 'Pause'
  LABEL_RESUME_BUTTON = 'Resume'
  LABEL_TOTAL_COUNT = 'Total: '
  LABEL_PROCESSED_COUNT = 'Processed: '

  CONFIRM_TERMINATE_WINDOW_TITLE = 'Terminate Now'
  CONFIRM_TERMINATE_WINDOW_MSG = 'Are you sure you want to terminate now?'

  CONFIRM_LAZY_TERMINATE_WINDOW_TITLE = 'Wait and Terminate'
  CONFIRM_LAZY_TERMINATE_WINDOW_MSG = 'Are you sure you want to wait and terminate?\n(Finish processing files?)'

  WINDOW_EXIT_MSG = 'Session terminating...'

  WINDOW_WIDTH = 500
  WINDOW_HEIGHT = 150

  WINDOW_OFFSET_Y = 10

  WINDOW_NO_HOVER_ALPHA = 0.5
  WINDOW_HOVER_ALPHA = 1.0

  UPDATE_DELAY_MS = 250

  def __init__(self, sessionStartFolder, fileWatcher, contexts, pauseEvent):
    super().__init__()

    self.sessionStartFolder = sessionStartFolder
    self.fileWatcher = fileWatcher
    self.contexts = contexts
    self.pauseEvent = pauseEvent
    self.lazyTerminate = False
    self.isPaused = False

    self.dragging = False
    self.drag_position = QPoint()

    self.initUI()
    self.updateFileCounts()

  def initUI(self):
    self.setWindowTitle(self.WINDOW_TITLE)
    self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

    screen = QGuiApplication.primaryScreen().geometry()
    centerX = (screen.width() - self.WINDOW_WIDTH) // 2
    centerY = self.WINDOW_OFFSET_Y
    self.move(centerX, centerY)

    layout = QVBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)
    self.setLayout(layout)

    self.titleBar = QLabel(self.WINDOW_TITLE)
    self.titleBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.titleBar.setStyleSheet('font-size: 18px; font-weight: bold; background-color: #DDD; color: black; padding: 5px;')
    self.titleBar.setFixedHeight(30)
    layout.addWidget(self.titleBar)

    self.statusLabel = QLabel(self.WINDOW_DESC)
    self.statusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.statusLabel.setStyleSheet('color: red; font-size: 14px; font-weight: bold;')
    layout.addWidget(self.statusLabel)

    buttonLayout = QHBoxLayout()
    self.pauseButton = QPushButton(self.LABEL_PAUSE_BUTTON)
    self.pauseButton.clicked.connect(self.togglePauseResume)
    buttonLayout.addWidget(self.pauseButton)

    if not self.contexts.recordOnly:
      self.lazyTerminateButton = QPushButton(self.LABEL_LAZY_TERMINATE_BUTTON)
      self.lazyTerminateButton.setEnabled(False)
      self.lazyTerminateButton.clicked.connect(self.confirmLazyTerminate)
      buttonLayout.addWidget(self.lazyTerminateButton)

    self.terminateButton = QPushButton(self.LABEL_TERMINATE_BUTTON)
    self.terminateButton.setStyleSheet('background-color: #BB9D99;')
    self.terminateButton.clicked.connect(self.confirmTerminate)
    buttonLayout.addWidget(self.terminateButton)
    layout.addLayout(buttonLayout)

    countLayout = QHBoxLayout()

    self.totalCountLabel = QLabel(f'{self.LABEL_TOTAL_COUNT}0')
    alignment = Qt.AlignmentFlag.AlignCenter if self.contexts.recordOnly else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    self.totalCountLabel.setAlignment(alignment)
    countLayout.addWidget(self.totalCountLabel)

    if not self.contexts.recordOnly:
      countLayout.addStretch()
      self.processedCountLabel = QLabel(f'{self.LABEL_PROCESSED_COUNT}0')
      self.processedCountLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
      countLayout.addWidget(self.processedCountLabel)

    layout.addLayout(countLayout)

    self.setWindowOpacity(self.WINDOW_NO_HOVER_ALPHA)
    self.installEventFilter(self)

    self.timer = QTimer(self)
    self.timer.timeout.connect(self.updateFileCounts)
    self.timer.start(self.UPDATE_DELAY_MS)

  def eventFilter(self, obj, event):
    if event.type() == QEvent.Type.Enter:
      self.setWindowOpacity(self.WINDOW_HOVER_ALPHA)
    elif event.type() == QEvent.Type.Leave:
      self.setWindowOpacity(self.WINDOW_NO_HOVER_ALPHA)
    return super().eventFilter(obj, event)

  def togglePauseResume(self):
    if self.isPaused:
      self.resume()
      self.pauseButton.setText(self.LABEL_PAUSE_BUTTON)
      self.statusLabel.setText(self.WINDOW_DESC)
    else:
      self.pause()
      self.pauseButton.setText(self.LABEL_RESUME_BUTTON)
      self.statusLabel.setText(self.WINDOW_DESC_PAUSED)

  def confirmTerminate(self):
    reply = QMessageBox.question(
      self, self.CONFIRM_TERMINATE_WINDOW_TITLE, self.CONFIRM_TERMINATE_WINDOW_MSG,
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
      self.onClose()
      sys.exit(0)

  def confirmLazyTerminate(self):
    reply = QMessageBox.question(
      self, self.CONFIRM_LAZY_TERMINATE_WINDOW_TITLE, self.CONFIRM_LAZY_TERMINATE_WINDOW_MSG,
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
      self.setLazyTerminate()

  def setLazyTerminate(self):
    self.lazyTerminate = True
    self.terminateButton.setEnabled(True)
    self.pauseButton.setEnabled(False)
    self.lazyTerminateButton.setEnabled(False)
    self.statusLabel.setText(self.WINDOW_DESC_LAZY_TERMINATE)
    self.resume()

  def pause(self):
    self.isPaused = True
    self.pauseEvent.clear()

  def resume(self):
    self.isPaused = False
    self.pauseEvent.set()

  def onClose(self):
    print(self.WINDOW_EXIT_MSG)
    builder = ProvGraphBuilder(self.sessionStartFolder)
    builder.buildGraph()

  def updateFileCounts(self):
    total = self.fileWatcher.getFilesEncountered()
    self.totalCountLabel.setText(f'{self.LABEL_TOTAL_COUNT}{total}')

    if not self.contexts.recordOnly:
      processed = self.fileWatcher.getFilesProcessed()
      self.processedCountLabel.setText(f'{self.LABEL_PROCESSED_COUNT}{processed}')

      if not self.isPaused and not self.lazyTerminate and total >= 1:
        self.lazyTerminateButton.setEnabled(True)

      if self.lazyTerminate and total == processed:
        self.onClose()
        sys.exit(0)

  def keyPressEvent(self, event):
    if not self.lazyTerminate and event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) and event.key() == Qt.Key.Key_P:
      self.togglePauseResume()

  def mousePressEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= self.titleBar.height():
      self.dragging = True
      self.drag_position = event.globalPosition().toPoint()

  def mouseMoveEvent(self, event):
    if self.dragging:
      new_pos = event.globalPosition().toPoint() - self.drag_position + self.pos()
      screen = QGuiApplication.primaryScreen().geometry()
      new_pos.setX(max(0, min(new_pos.x(), screen.width() - self.width())))
      new_pos.setY(max(0, min(new_pos.y(), screen.height() - self.height())))
      self.move(new_pos)
      self.drag_position = event.globalPosition().toPoint()

  def mouseReleaseEvent(self, event):
    if event.button() == Qt.MouseButton.LeftButton:
      self.dragging = False
