import string, random, os

#############################################################################

def reverseString(s):
  return s[::-1]

def toUppercase(s):
  return s.upper()

def toLowercase(s):
  return s.lower()

def replaceSubstring(s):
  old = input('Substring to replace: ')
  new = input('Replace with: ')
  return s.replace(old, new)

def removeWhitespace(s):
  return ''.join(s.split())

def capitalizeWords(s):
  return s.title()

def shiftCharacters(s):
  return ''.join(chr(ord(c) + 1) if c.isascii() else c for c in s)

def reverseWords(s):
  return ' '.join(s.split()[::-1])

def removePunctuation(s):
  return ''.join(c for c in s if not c in string.punctuation)

def duplicateString(s):
  return s + s

def alternateCase(s):
  return ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(s))

def toBinary(s):
  return ' '.join(format(ord(c), '08b') for c in s)

def maskDigits(s):
  return ''.join('#' if c.isdigit() else c for c in s)

def trimWhitespace(s):
  return s.strip()

def addPrefixSuffix(s):
  prefix = input('Prefix: ')
  suffix = input('Suffix: ')
  return f'{prefix}{s}{suffix}'

def replaceRandomChar(s):
  if not s:
    return s
  pos = random.randint(0, len(s) - 1)
  newChar = random.choice(string.ascii_letters + string.punctuation + string.digits)
  return s[:pos] + newChar + s[pos + 1:]

def shiftCharactersBack(s):
  return ''.join(chr(ord(c) - 1) if c.isascii() else c for c in s)

def scrambleString(s):
  chars = list(s)
  random.shuffle(chars)
  return ''.join(chars)

def removeVowels(s):
  return ''.join(c for c in s if c.lower() not in 'aeiou')

def doubleCharacters(s):
  return ''.join(c * 2 for c in s)

def insertDashes(s):
  return '-'.join(s)

def mirrorString(s):
  return s + s[::-1]

#############################################################################

options = {
  '1': ('Reverse string', reverseString),
  '2': ('To uppercase', toUppercase),
  '3': ('To lowercase', toLowercase),
  '4': ('Replace substring', replaceSubstring),
  '5': ('Remove whitespace', removeWhitespace),
  '6': ('Capitalize words', capitalizeWords),
  '7': ('Shift characters by +1', shiftCharacters),
  '8': ('Reverse word order', reverseWords),
  '9': ('Remove punctuation', removePunctuation),
  '10': ('Duplicate string', duplicateString),
  '11': ('Alternate character case', alternateCase),
  '12': ('Convert to binary', toBinary),
  '13': ('Replace digits with #', maskDigits),
  '14': ('Trim whitespace', trimWhitespace),
  '15': ('Add prefix/suffix', addPrefixSuffix),
  '16': ('Replace random character with another', replaceRandomChar),
  '17': ('Shift characters by -1', shiftCharactersBack),
  '18': ('Scramble characters', scrambleString),
  '19': ('Remove all vowels', removeVowels),
  '20': ('Double every character', doubleCharacters),
  '21': ('Insert dashes between characters', insertDashes),
  '22': ('Mirror the string (append reverse)', mirrorString),
}

#############################################################################

def main():
  currentString = input('Enter a string to begin: ')
  history = [currentString]

  while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Current string:', currentString)
    print('\nChoose an operation:')
    for k, (desc, _) in sorted(options.items(), key = lambda x: int(x[0])):
      print(f'{k}. {desc}')
    print('P. Print string evolution to file')
    print('Q. Quit')

    choice = input('Your choice: ').strip().lower()

    if choice =='q':
      break
    elif choice == 'p':
      filename = input('Enter filename, e.g., output.txt')
      with open(filename, 'w') as f:
        for i, val in enumerate(history):
          f.write(f'[{i}] {val}\n')
      print(f'Saved to {filename}')
      continue

    methodTuple = options.get(choice)
    if methodTuple:
      method = methodTuple[1]
      result = method(currentString)
      currentString = result
      history.append(currentString)
      print('Updated string: ', currentString)
    else:
      print('Invalid choice!')

if __name__ == '__main__':
  main()