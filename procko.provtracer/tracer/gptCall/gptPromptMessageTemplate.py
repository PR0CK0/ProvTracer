class GPTPromptMessageTemplate():
  __message = []

  def __init__(self, text, image): 
    self.__message = [
      {
        'role': 'user',
        'content': [
          {
            'type': 'text',
            'text': text
          },
          {
            'type': 'image_url',
            'image_url': {
              'url': f'data:image/png;base64, {image}',
              'detail': 'auto'
            }
          }
        ]
      }
    ]
    
  def getMessage(self):
    return self.__message