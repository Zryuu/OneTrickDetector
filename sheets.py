import os
from google.oauth2.service_account import Credentials
import gspread
from fuzzywuzzy import fuzz, process

SCOPES      = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN       = os.environ['sheets_token']
SHEETS_ID   = '1mz-b8zojmVwpVQ8qdL9Y-5YCB1Jly62Jn60f7gS-HDc'

validCharacters = ['Adam Warlock',
'Black Panther',
'Black Widow',
'Captain America',
'Cloak & Dagger',
'Docter Strange',
'Groot',
'Hawkeye',
'Hela',
'Hulk',
'Invisible Woman',
'Iron Fist',
'Iron Man',
'Jeff',
'Loki',
'Luna',
'Mister Fantastic',
'Magik',
'Magneto',
'Mantis',
'Moon Knight',
'Namor',
'Peni',
'Psylocke',
'Rocket',
'Scarlet Witch',
"Spiderman",
'Squirrel Girl',
'Starlord',
"Storm",
"Punisher",
"Thor",
"Venom",
'Winter Soldier',
"Wolverine"]

class Sheets:
    def __init__(self):
        self.sheet = None
        try:
            creds           = Credentials.from_service_account_file("token.json", scopes=SCOPES)
            client          = gspread.authorize(creds)
            self.sheet      = client.open_by_key(SHEETS_ID)
            self.worksheet  = self.sheet.worksheet("Player Tracker")
            self.avoids     = self.sheet.worksheet("Current Avoids")
        except Exception as e:
            print(f"An error occurred in sheets::init -- {e}")
    def hasNum(self, str):
        return any(char.isdigit() for char in str)

    def GetLastRow(self):
        try:
            rows =  self.worksheet.col_values(1)
            if rows:
                last_row = len(rows) + 1
                return last_row
            else:
                print("No data found.")

        except Exception as e:
            print(f"An error occurred in sheets::GetLastRow -- {e}")

    def AddInfo(self, name, character, date):
        row = self.GetLastRow()
        matchID = character
        validCharacter = ""

        print(self.hasNum(character))

        # Check if using Character or MatchID (for players with non-ascii names)
        if self.hasNum(character):
            columns = ['A', 'D', 'G']
            values = [name, date, matchID]
        else:
            validCharacter = process.extractOne(character, validCharacters)
            regular = self.CheckIfPresent(name, validCharacter[0])

            if regular:
                return  regular
            columns = ['A', 'D', 'K', 'O']
            values = [name, date, validCharacter[0], validCharacter[0]]

        # Push data to sheet.
        try:
            for column, value in zip(columns, values):
                self.worksheet.update_acell(f"{column}{row}", value)
            return True, f"{name} has been added to the list."

        except Exception as e:
            print(f"An error occurred in sheets::addInfo::tryCatch::foreach -- {e}")
            return False, "Something broke, yell at Zryu."

    def AddNewCharacterInfo(self, name, character, row):

        characters = self.worksheet.acell(f'O{row}').value

        for char in characters:
            if char == character:
                return True, f"{name} is already on the list at row {row}. Character already in Database."

        characters = self.worksheet.acell(f'O{row}').value + ", " + character
        self.worksheet.update_acell(f"O{row}", character)

        return True, f"{name} is already on the list at row {row}. Added new character to database."

    # TODO:: Make more modular
    def CheckIfPresent(self, name, character):
        entries = self.worksheet.col_values(1)

        for row_num, entry in enumerate(self.worksheet.col_values(1), start=1):
            if entry == name:
                return self.AddNewCharacterInfo(name, character, row_num)

        return False

    def GetPlayerCharacters(self, name):
        entries = self.worksheet.col_values(1)

        validName, score = process.extractOne(name, entries)

        if score >= 80:
            for row_num, entry in enumerate(self.worksheet.col_values(1), start=1):
                if entry == validName:
                    return f'{validName}: ' + self.worksheet.acell(f'O{row_num}').value

        return f"{name} isn't found on the list."

    def AddAvoid(self, name, channel):
        col_index = 0
        row_index = 0

        # Finds column and row containing Channel name.
        for i in range(1, 2):
            chan_rows = self.avoids.row_values(i * 5)

            for index, chan in enumerate(chan_rows):
                if chan == channel:
                    print(f'{index + 1}: {chan}')
                    col_index = index + 1
                    row_index = i * 5
                    break
            if col_index != 0:
                break

        if col_index == 0:
            return False

        # gets rows above channel name.
        rows = [self.avoids.cell(row, col_index).value for row in range(row_index - 3, row_index)]

        # removes empty entries
        rows = [row for row in rows if row is not None]

        # if no current avoids.
        if len(rows) < 1:
            self.avoids.update_acell(f"{chr(64+col_index)}{row_index - 3}", name)
            return True

        # If rows 2-4 are all filled
        if len(rows) >= 3 and all(row for row in rows):
            for i in range(2, 5):
                if i < len(rows):
                    self.avoids.update_cell(i, col_index, rows[i])
            self.avoids.update_acell(f"{chr(64+col_index)}{row_index-1}", name)
        else: # if not all full
            self.avoids.update_acell(f"{chr(64+col_index)}{(row_index - 3) + len(rows)}", name)

        return True

    def GetAvoids(self, channel):
        col_index = 0
        row_index = 0

        # TODO:: make more modular.
        # finds column and row containing Channel name.
        for i in range(1, 2):
            rows = self.avoids.row_values(i * 5)

            for index, chan in enumerate(rows):
                if chan == channel:
                    col_index = index + 1
                    row_index = i * 5
                    break
            if col_index != 0:
                break

        if col_index == 0:
            return "Error: Can't find channel."

        # Init return list
        results = [None]

        # Gets values in rows channel - 3 to channel - 1 (3 above to 1 above streamer's name). Skips empty entries.
        for i in range(row_index - 3, row_index):
            results.append(self.avoids.cell(i, col_index).value)

        results = [r for r in results if r]
        return results