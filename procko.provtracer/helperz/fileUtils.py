import os, re

__FILE_NAME_REGEX = re.compile(r'[^a-zA-Z0-9_]')
__FILE_CONTENT_REGEX = re.compile(r'[^a-zA-Z0-9_\s#.,:;?!()\\]')

def writeFile(filePath, content):
  with open(filePath, 'w', encoding = 'utf-8') as file:
    file.write(content)

def readFile(filePath):
  with open(filePath, 'r') as file:
    content = file.read()
  return content

def cleanText(inputText, kind):
  if kind == 'filename':
    pattern = __FILE_NAME_REGEX
  elif kind == 'filecontent':
    pattern = __FILE_CONTENT_REGEX
    
  cleanedText = pattern.sub('', inputText)
  return cleanedText

class ContextFileUtils():
  def getContextFile(self, screenshotFilePath, context):
    
    parentFolder = os.path.dirname(os.path.dirname(screenshotFilePath))
    contextFolder = os.path.join(parentFolder, 'contexts', context)
    
    nonPluralContext = context[:-1]
    fileTimestamp = os.path.splitext(os.path.basename(screenshotFilePath))[0].replace('screenshot_', nonPluralContext + '_')
      
    contextFileName = fileTimestamp + '.txt'
    contextFilePath = os.path.join(contextFolder, contextFileName)
    return contextFilePath