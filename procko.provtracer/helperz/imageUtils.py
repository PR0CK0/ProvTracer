import base64
from PIL import Image

class ImageUtils:
  def __init__(self):
    return
  
  def compressImage(self, imagePath, quality):
    with Image.open(imagePath) as img:
      img.save(imagePath, optimize = True, quality = quality)
    
  def isBadImage(self, imagePath):
    try:
      with Image.open(imagePath) as img:
        img.verify()  
      return False
    except (IOError, SyntaxError, Image.DecompressionBombError, OSError) as e:
      print('Bad image encountered. Deleting %s' %imagePath)
      return True
  
  def getBase64Image(self, imagePath):
    with open(imagePath, 'rb') as imageFile:
      base64Image = base64.b64encode(imageFile.read()).decode('utf-8')
    return base64Image