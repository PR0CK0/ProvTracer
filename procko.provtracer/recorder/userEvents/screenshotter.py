import sys, os
import pyautogui

from helperz.imageUtils import ImageUtils

class Screenshotter():
  __IMAGE_QUALITY_PERCENT = 80
  __OUTPUT_SUBFOLDER_NAME = 'screenshots'
    
  def __init__(self, outputFolder):
    self.outputFolder = os.path.join(outputFolder, self.__OUTPUT_SUBFOLDER_NAME)
    os.makedirs(self.outputFolder, exist_ok = True)
  
  def takeScreenshot(self, timestamp):
    imageUtils = ImageUtils()
    
    filePath = os.path.join(self.outputFolder, f'screenshot_{timestamp}.png')
    screenshot = pyautogui.screenshot()
    screenshot.save(filePath)
    
    if imageUtils.isBadImage(filePath):
      os.remove(filePath)
      print(f'Deleted image due to verification issue: {filePath}')
    else:
      imageUtils.compressImage(filePath, self.__IMAGE_QUALITY_PERCENT)
      print(os.path.splitext(os.path.basename(filePath))[0])