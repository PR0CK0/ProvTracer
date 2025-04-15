import os, shutil, time, re
from PyQt6.QtWidgets import (
  QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QDialog,
  QCheckBox, QRadioButton, QTextEdit, QLineEdit, QSlider, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPixmap, QIcon
from recorder.contexts import Contexts
from recorder.ui.window import Window
from helperz import fileUtils
from tracer.LLMs import LLMConfig

class PrimerWindow(QWidget, Window):
  __WINDOW_TITLE = 'ProvTracer - Session Primer'
  __WINDOW_MIN_WIDTH = 720
  __WINDOW_MIN_HEIGHT = 480
  __MSG_HELP = [
    'Primer Context: Tell the LLM what your planned work is about.',
    'Mouse Events: Adds mouse clicks since last screenshot.',
    'Keyboard Events: Adds keyboard strokes since last screenshot.',
    'Window Events: Adds window title changes since last screenshot.',
    'Clipboard Events: Adds clipboard changes since last screenshot.',
    'Side-by-Side: Planned work is split into source and working artifact.',
    'Open-Ended: Work may involve multiple artifacts without a strict layout.'
  ]
  __MSG_DESCRIPTION = 'ProvTracer is a system developed to automatically capture digital artifact provenance by utilizing a multi-modal large language model (MLLM) and knowledge graph serialization.'
  __MSG_OTHER = 'Click the Pause button or press Ctrl + Shift + P to pause ProvTracer at any time.'

  __WINDOW_TITLE_DISCLAIMER = 'DISCLAIMER'
  __MSG_DISCLAIMER = """You are beginning a ProvTracer session. The entirety of your screen will be screenshotted on a set interval. These screenshots, and any elected context sources, will be sent to a large language model for analysis and serialization as a knowledge graph. You consent to the possible collection and interpretation of your personal data, e.g., usernames, passwords, files, emails, etc. You may pause ProvTracer at any time. Do you wish to continue?
"""

  __PRIMER_SKIPPED_MESSAGE = 'NO CONTEXT'
  __EMPTY_SESSION_NAME = 'unnamed'

  __WINDOW_TITLE_SAVED = 'Success'
  __WINDOW_TITLE_HELP = 'ProvTracer - Help'
  __WINDOW_TITLE_QUIT = 'Quit'

  __HELP_WINDOW_HEIGHT = 500
  __HELP_WINDOW_WIDTH = 400

  __LABEL_SESSION_NAME = 'Enter a name for this session:'
  __LABEL_CHECKBOXES = 'What context do you want to include?'
  __LABEL_PRIMER_CONTEXT = 'Primer Context - What is the purpose of this session? Describe your work:'
  __LABEL_PRIMER_CONTEXT_PLACEHOLDER = 'Type here...'
  __LABEL_WORK_MODE = 'Select Work Mode:'
  __LABEL_OPEN_ENDED = 'Open-Ended'
  __LABEL_SIDE_BY_SIDE = 'Side-by-Side'
  __LABEL_TIMESLICE_INTERVAL = 'Screenshot Interval (seconds): '
  __LABEL_THREAD_COUNT = 'Number of Threads: '
  __LABEL_LLM = 'Select GPT Model:' 
  __LABEL_BUTTON_HELP = 'Help'
  __LABEL_BUTTON_SAVE = 'Save Context'
  __LABEL_BUTTON_SKIP = 'Skip Context'
  __LABEL_BUTTON_RECORD_ONLY = 'Record Only'
  __LABEL_BUTTON_OK = 'OK'
  __LABEL_CHARACTERS_REMAINING = 'Characters remaining: '
  __LABEL_PRIMER_CONTEXT_SAVED = 'Primer context saved!'
  __LABEL_QUIT = 'Are you sure you want to quit?'

  __LOGO_IMAGE = 'provtracer.png'
  __PRIMER_CONTEXT_FILE = 'primer_context.txt'

  SHUTDOWN_DELAY_SECS = 0.5
  __CHAR_LIMIT_SESSION_NAME = 30
  __PRIMER_CHAR_LIMIT = 350
  # not used currently
  __PRIMER_CHAR_MIN = 20
  __GPT_FILESIZE_LIMIT_BYTES = 512 * 1_048_576
  closed = pyqtSignal()

  __isAPIKeyValid = 'sk-(proj-[A-Za-z0-9-_]+|[A-Za-z0-9-_]{20,100})'

  def __init__(self, folderPath):
    super().__init__()
    self.contexts = Contexts()
    self.selectedTimesliceInterval = 5
    self.selectedNumberOfThreads = os.cpu_count()
    self.timestampsIncluded = False
    self.apiKey = ''
    self.__folderPath = folderPath
    self.initUI()

  def initUI(self):
    self.initWindow()
    layout = QVBoxLayout()
    self.setLayout(layout)
    
    self.initSessionNameWidget(layout)
    self.initCheckboxWidget(layout)
    self.initPrimerContextWidget(layout)
    self.initWorkModeWidget(layout)
    self.initScreenshotIntervalWidget(layout)
    self.initThreadCountWidget(layout)
    self.initLLMWidget(layout)
    self.initButtonWidget(layout)
    
    self.togglePrimerTextField()

  def initWindow(self):
    self.setWindowTitle(self.__WINDOW_TITLE)
    self.setMinimumSize(self.__WINDOW_MIN_WIDTH, self.__WINDOW_MIN_HEIGHT)
    self.setWindowFlags(Qt.WindowType.Window)
    self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), self.__LOGO_IMAGE)))
    screen = QGuiApplication.primaryScreen().geometry()
    centerX = (screen.width() - self.__WINDOW_MIN_WIDTH) // 2

  def initSessionNameWidget(self, layout):
    self.sessionLabel = QLabel(self.__LABEL_SESSION_NAME)
    self.sessionInput = QLineEdit()
    self.sessionInput.setMaxLength(self.__CHAR_LIMIT_SESSION_NAME)
    self.sessionInput.textChanged.connect(lambda: self.saveSessionName(self.sessionInput.text()))
    self.sessionInput.textChanged.connect(self.updateContextSelection)
    layout.addWidget(self.sessionLabel)
    layout.addWidget(self.sessionInput)

  def initCheckboxWidget(self, layout):
    self.checkboxLabel = QLabel(self.__LABEL_CHECKBOXES)
    layout.addWidget(self.checkboxLabel)
    self.contextOptions = ['Primer Context', 'Mouse Events', 'Keyboard Events', 'Window Events', 'Clipboard Events']
    self.checkboxes = []
    for option in self.contextOptions:
      checkbox = QCheckBox(option)
      checkbox.stateChanged.connect(self.updateContextSelection)
      layout.addWidget(checkbox)
      self.checkboxes.append(checkbox)
    self.checkboxes[0].stateChanged.connect(self.togglePrimerTextField) 

  def initPrimerContextWidget(self, layout):
    self.primerLabel = QLabel(self.__LABEL_PRIMER_CONTEXT)
    self.primerInput = QTextEdit()
    self.primerInput.setPlaceholderText(self.__LABEL_PRIMER_CONTEXT_PLACEHOLDER)
    self.primerInput.textChanged.connect(self.updatePrimerContextLength)
    layout.addWidget(self.primerLabel)
    layout.addWidget(self.primerInput)
    self.counterLabel = QLabel(f'{self.__LABEL_CHARACTERS_REMAINING}{self.__PRIMER_CHAR_LIMIT}')
    layout.addWidget(self.counterLabel)

  def initWorkModeWidget(self, layout):
    self.workModeLabel = QLabel(self.__LABEL_WORK_MODE)
    self.openEndedRadio = QRadioButton(self.__LABEL_OPEN_ENDED)
    self.sideBySideRadio = QRadioButton(self.__LABEL_SIDE_BY_SIDE)
    self.openEndedRadio.setChecked(True)
    self.openEndedRadio.toggled.connect(self.toggleWorkModes)
    workModeLayout = QHBoxLayout()
    workModeLayout.addWidget(self.workModeLabel)
    workModeLayout.addWidget(self.openEndedRadio)
    workModeLayout.addWidget(self.sideBySideRadio)
    layout.addLayout(workModeLayout)

  def initScreenshotIntervalWidget(self, layout):
    self.screenshotIntervalLabel = QLabel(f'{self.__LABEL_TIMESLICE_INTERVAL}{self.selectedTimesliceInterval}')
    self.screenshotSlider = QSlider(Qt.Orientation.Horizontal)
    self.screenshotSlider.setMinimum(1)
    self.screenshotSlider.setMaximum(10)
    self.screenshotSlider.setValue(self.selectedTimesliceInterval)
    self.screenshotSlider.valueChanged.connect(self.updateScreenshotInterval)
    intervalLayout = QHBoxLayout()
    intervalLayout.addWidget(self.screenshotIntervalLabel)
    intervalLayout.addWidget(self.screenshotSlider)
    layout.addLayout(intervalLayout)

  def initThreadCountWidget(self, layout):
    self.threadCountLabel = QLabel(f'{self.__LABEL_THREAD_COUNT}{self.selectedNumberOfThreads}')
    self.threadSlider = QSlider(Qt.Orientation.Horizontal)
    self.threadSlider.setMinimum(1)
    self.threadSlider.setMaximum(self.selectedNumberOfThreads)
    self.threadSlider.setValue(self.selectedNumberOfThreads)
    self.threadSlider.valueChanged.connect(self.updateThreadCount)
    threadsLayout = QHBoxLayout()
    threadsLayout.addWidget(self.threadCountLabel)
    threadsLayout.addWidget(self.threadSlider)
    layout.addLayout(threadsLayout)

  def initLLMWidget(self, layout):
    self.gptLabel = QLabel(self.__LABEL_LLM)
    self.gptDropdown = QComboBox()
    self.gptDropdown.addItems(LLMConfig.LLMS_AVAILABLE)
    self.gptDropdown.currentTextChanged.connect(self.updateSelectedLLM)
    default_model = LLMConfig.getDefaultLLM()
    if default_model in LLMConfig.LLMS_AVAILABLE:
      self.gptDropdown.setCurrentText(default_model)
    gptLayout = QHBoxLayout()
    gptLayout.addWidget(self.gptLabel)
    gptLayout.addWidget(self.gptDropdown)
    layout.addLayout(gptLayout)

  def initButtonWidget(self, layout):
    apiKeyLayout = QHBoxLayout()
    self.apiKeyLabel = QLabel('Enter GPT API Key:')
    self.apiKeyInput = QLineEdit()
    self.apiKeyInput.setPlaceholderText('Paste API Key here...')
    self.apiKeyInput.textChanged.connect(self.updateAPIKeyStatus)
    apiKeyLayout.addWidget(self.apiKeyLabel)
    apiKeyLayout.addWidget(self.apiKeyInput)
    layout.addLayout(apiKeyLayout)
  
    buttonLayout = QHBoxLayout()
    self.helpButton = QPushButton(self.__LABEL_BUTTON_HELP)
    self.helpButton.clicked.connect(self.showHelp)
    buttonLayout.addWidget(self.helpButton)
    self.saveButton = QPushButton(self.__LABEL_BUTTON_SAVE)
    self.saveButton.setEnabled(False)
    self.saveButton.clicked.connect(lambda: self.savePrimerContext(False))
    self.skipButton = QPushButton(self.__LABEL_BUTTON_SKIP)
    self.skipButton.setEnabled(False)
    self.skipButton.clicked.connect(lambda: self.savePrimerContext(True))
    self.recordButton = QPushButton(self.__LABEL_BUTTON_RECORD_ONLY)
    self.recordButton.setStyleSheet('background-color: #BB9D99;')
    self.recordButton.clicked.connect(self.setRecordOnly)
    buttonLayout.addWidget(self.saveButton)
    buttonLayout.addWidget(self.skipButton)
    buttonLayout.addWidget(self.recordButton)
    layout.addLayout(buttonLayout)		

  def showHelp(self):
    helpWindow = QDialog(self)
    helpWindow.setWindowTitle(self.__WINDOW_TITLE_HELP)
    helpWindow.setModal(True)
    helpWindow.setFixedSize(self.__HELP_WINDOW_HEIGHT, self.__HELP_WINDOW_WIDTH)

    layout = QVBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(2)

    logoLabel = QLabel()
    logoPath = os.path.join(os.path.dirname(__file__), self.__LOGO_IMAGE)
    pixmap = QPixmap(logoPath)
    logoLabel.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(logoLabel)

    descriptionLabel = QLabel(self.__MSG_DESCRIPTION)
    descriptionLabel.setWordWrap(True)
    layout.addWidget(descriptionLabel)

    for msg in self.__MSG_HELP:
      label = QLabel(f'• {msg}')
      label.setWordWrap(True)
      layout.addWidget(label)

    otherLabel = QLabel(self.__MSG_OTHER)
    otherLabel.setWordWrap(True)
    layout.addWidget(otherLabel)

    okButton = QPushButton(self.__LABEL_BUTTON_OK)
    okButton.clicked.connect(helpWindow.accept)
    okButton.setFixedWidth(80)

    buttonLayout = QHBoxLayout()
    buttonLayout.addWidget(okButton, alignment = Qt.AlignmentFlag.AlignCenter)

    layout.addLayout(buttonLayout)

    helpWindow.setLayout(layout)
    helpWindow.exec()

  def updateContextSelection(self):
    isAPIKeyValid = bool(re.fullmatch(self.__isAPIKeyValid, self.apiKey))
    sessionNameValid = self.sessionInput.text().strip() != ''
    anyOptionSelected = any(cb.isChecked() for cb in self.checkboxes)
    primerContextChecked = self.checkboxes[0].isChecked()
    primerContextValid = self.primerInput.toPlainText().strip() != ''

    allowSave = isAPIKeyValid and (
        sessionNameValid or 
        anyOptionSelected or 
        (primerContextChecked and primerContextValid)
    )
    self.saveButton.setEnabled(allowSave)
    self.skipButton.setEnabled(isAPIKeyValid)

    self.contexts.isPrimerContextEnabled = self.checkboxes[0].isChecked()
    self.contexts.areMouseEventsEnabled = self.checkboxes[1].isChecked()
    self.contexts.areKeyboardEventsEnabled = self.checkboxes[2].isChecked()
    self.contexts.areWindowEventsEnabled = self.checkboxes[3].isChecked()
    self.contexts.areClipboardEventsEnabled = self.checkboxes[4].isChecked()

  def togglePrimerTextField(self):
    isChecked = self.checkboxes[0].isChecked()
    self.primerInput.setEnabled(isChecked)
    self.primerInput.setStyleSheet('background-color: white;' if isChecked else 'background-color: lightgray;')

  def toggleWorkModes(self):
    self.contexts.setOpenEnded(self.openEndedRadio.isChecked())
    self.contexts.setSideBySide(self.sideBySideRadio.isChecked())

  def updatePrimerContextLength(self):
    currentText = self.primerInput.toPlainText()
    remainingChars = self.__PRIMER_CHAR_LIMIT - len(currentText)
    self.counterLabel.setText(f'{self.__LABEL_CHARACTERS_REMAINING}{max(0, remainingChars)}')

  def updateScreenshotInterval(self):
    self.selectedTimesliceInterval = self.screenshotSlider.value()
    self.screenshotIntervalLabel.setText(f'{self.__LABEL_TIMESLICE_INTERVAL}{self.selectedTimesliceInterval}')

  def updateThreadCount(self):
    self.selectedNumberOfThreads = self.threadSlider.value()
    self.threadCountLabel.setText(f'{self.__LABEL_THREAD_COUNT}{self.selectedNumberOfThreads}')

  def updateSelectedLLM(self, value):
    LLMConfig.setLLMChosen(value)

  def saveSessionName(self, text):
    self.contexts.setSessionName(fileUtils.cleanText(text, 'filename'))

  def updateAPIKeyStatus(self):
    self.apiKey = self.apiKeyInput.text().strip()
    isValid = bool(re.fullmatch(self.__isAPIKeyValid, self.apiKey))
    self.saveButton.setEnabled(isValid)
    self.skipButton.setEnabled(isValid)
    self.recordButton.setEnabled(isValid)

    if not isValid:
        self.apiKeyInput.setStyleSheet('border: 2px solid red;')
    else:
        self.apiKeyInput.setStyleSheet('')
        self.updateContextSelection()

  def savePrimerContext(self, isSkipped = False):
    if not self.isUserProvidingConsent():
      return
    outputFile = os.path.join(self.__folderPath, 'contexts', self.__PRIMER_CONTEXT_FILE)
    os.makedirs(os.path.dirname(outputFile), exist_ok = True)
    if not isSkipped:
      uncleanTextFieldContent = self.primerInput.toPlainText().strip()
      cleanedTextFieldContent = fileUtils.cleanText(uncleanTextFieldContent, 'filecontent')
      self.contexts.setPrimerContext(cleanedTextFieldContent)
      with open(outputFile, 'w', encoding = 'utf-8') as file:
        file.write(self.contexts.primerContext)
      QMessageBox.information(self, self.__WINDOW_TITLE_SAVED, self.__LABEL_PRIMER_CONTEXT_SAVED)
    else:
      with open(outputFile, 'w', encoding = 'utf-8') as file:
        file.write(self.__PRIMER_SKIPPED_MESSAGE)
    if self.contexts.sessionName == '':
      self.contexts.setSessionName(self.__EMPTY_SESSION_NAME)
    self.closed.emit()
    self.hide()

  def setRecordOnly(self):
    if not self.isUserProvidingConsent():
      return
    self.contexts.setRecordOnly(True)
    self.closed.emit()
    self.hide()

  def isUserProvidingConsent(self):
    return QMessageBox.question(
      self, self.__WINDOW_TITLE_DISCLAIMER, self.__MSG_DISCLAIMER, 
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    ) == QMessageBox.StandardButton.Yes

  def closeEvent(self, event):
    reply = QMessageBox.question(
      self, self.__WINDOW_TITLE_QUIT, self.__LABEL_QUIT, 
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
      self.cleanup()
      QApplication.quit()
    else:
      event.ignore()

  def cleanup(self):
    time.sleep(self.SHUTDOWN_DELAY_SECS)
    try:
      shutil.rmtree(self.__folderPath, ignore_errors = True)
    except Exception as e:
      print(f'Failed to clean up: {e}')
