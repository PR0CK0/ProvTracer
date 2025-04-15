# String Manipulation CLI Tool
A full-featured command-line application that allows users to interactively transform strings using over 20 unique operations. Designed as a testbed for provenance trace recording via the ProvTracer system, this script also serves as a flexible utility for experimenting with string processing code.

## Table of Contents

- [String Manipulation CLI Tool](#string-manipulation-cli-tool)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Available Operations](#available-operations)
    - [Basic String Mutations](#basic-string-mutations)
    - [Word Structure Mutations](#word-structure-mutations)
    - [Character-Level Mutations](#character-level-mutations)
    - [Miscellaneous Mutations](#miscellaneous-mutations)
  - [Output Logging](#output-logging)
  - [Example](#example)
  - [Implementation Notes](#implementation-notes)
  - [Limitations](#limitations)
  - [System Requirements](#system-requirements)
  - [License](#license)
  - [Author](#author)


## Features
- CLI-based interface that updates after each mutation
- 22 distinct string manipulation functions
- Ability to track and export string evolution to a file
- Modular function design
- Useful for testing string algorithms and waltkthroughs

## Installation
Clone the repo or copy the Python file directly. Ensure you're using Python 3.6 or higher. No outside libraries required.

## Usage
Run the script in your terminal: ```python string_manipulator.py```

Follow the prompts:
1. Enter a starting string, e.g., 'hello world'
2. Choose from the 22 available operations
3. View the transformed output
4. Repeat as desired
5. Type 'p' to save your session and 'q' to exit

## Available Operations

### Basic String Mutations
| Option | Description |
|--------|-------------|
|1|Reverse the string|
|2|Convert to uppercase|
|3|Convert to lowercase|
|4|Replace one substring with another|
|5|Remove all whitespace|
|6|Capitalize the first letter of each word|

### Word Structure Mutations
| Option | Description |
|--------|-------------|
|8|Reverse word order|
|10|Duplicate the entire string|
|14|Trim leading and trailing whitespace|
|22|Mirror the string (append reverse)|

### Character-Level Mutations
| Option | Description |
|--------|-------------|
|7|Shift each character by +1|
|11|Alternate cases (upper/lower)|
|16|Replace one random character|
|17|Shift each character by -1|
|18|Scramble all characters|
|20|Double every character|
|21|Insert dashes between all characters|

### Miscellaneous Mutations
| Option | Description |
|--------|-------------|
|9|Remove punctuation|
|12|Replace all digits with '#'|
|13|Remove all vowels|
|19|Convert string to binary (ASCII)|
|25|Add a custom prefix and suffix|

## Output Logging
At any point, type 'p' to export your full string history to a file. You will be promtped to enter a filename, e.g., word.txt, and the code will log each mutation step, e.g.,

```
[0] hello world
[1] HELLO WORLD
[2] H-E-L-L-O- -W-O-R-L-D
[3] D-L-R-O-W- -O-L-L-E-H
```

## Example

**Simple reversal and case flip:**

```
Enter a string to begin: hello world
Choose an operation:
1. Reverse string
Current string: dlrow olleh

Choose an operation:
2. To uppercase
Current string: DLROW OLLEH
```

## Implementation Notes
- All mutations are applied iterative and destructively to the current string state
- The input string is preserved in history even after multiple rewrites
- Functions that require user input, e.g., substring replacement, prefix/suffix, handle prompting inline

## Limitations
- No undo functionality
- Binary conversion outputs a space-separated ASCII binary stream that may be long and hard to read
- Non-ASCII characters may result in inconsistent outputs when shifted
  
## System Requirements
- Python 3.6+
- Works on Windows, macOS, and Linux
- Uses built-in os, random, and string libraries

## License
MIT License. You are free to use, fork, and modify this tool for educational or experimental use.

## Author
Tyler Procko
https://github.com/PR0CK0
Built to test the ProvTracer system's ability to capture semantic trace link generation from live work sessions.