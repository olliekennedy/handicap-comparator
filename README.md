# Handicap Comparator

This tool allows you compare the handicaps held for players in Master Scoreboard and England Golf

### Installation:
**Windows**
- Clone this repo
- Get the [latest Python 3](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5)
- Create a copy of both config.py.example and names_mapping.py.example, removing the .example file extensions
  - This should leave you with config.py and names_mapping.py
  - Change each of the values to your own according to the instructions in the files
- Double click ***setup.bat***

**Mac**
- Clone this repo
- Install python3 if you don't have the command line developer tools installed
- Create a copy of both config.py.example and names_mapping.py.example, removing the .example file extensions
  - This should leave you with config.py and names_mapping.py
  - Change each of the values to your own according to the instructions in the files
- `cd` to the project in terminal and `pip install -r .\requirements.txt`

### Usage:
- **Windows** - double click ***run_report.bat***
- **Mac** - `cd` to the project in terminal and `python3 create_handicap_report.py`

---

### Dealing with players who have different names in Master and EG

You will see an error message in the output such as:

    WARNING: failed to find player with name Smith, Johnny  on England Golf

This either means they don't exist on England Golf, or the name they use on Master is different to EG
  - Go to MyEG and use the member search tool to find the player - they will most likely be listed under a different name/nickname
  - If it turns out the names in the two systems are different, such as 'Smith, Johnny ' and 'Smith, John':
  - Add a row in 'names_mapping.py', formatted exactly the same as the others, with their name as it appears in Master on the left, and as it appears on EG on the right
  - This should remove the WARNING for that player from the output
  - If they don't exist on EG then there's nothing you can do
