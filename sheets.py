import os
from google.oauth2.service_account import Credentials
import gspread
from fuzzywuzzy import fuzz, process

SCOPES      = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN       = 'AIzaSyDUCTN9tPQDx_s8_7WzTuaYT0S1-65iLzc'
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
                return True, f"{name} is already on the list at row: {row}. Character already in Database."

        characters = self.worksheet.acell(f'O{row}').value + ", " + character
        self.worksheet.update_acell(f"O{row}", character)

        return True, f"{name} is already on the list at row: {row}. Added new character to database."

    # TODO:: Make more modular
    def CheckIfPresent(self, name, character):
        entries = self.worksheet.col_values(1)

        for row_num, entry in enumerate(self.worksheet.col_values(1), start=1):
            if entry == name:
                return self.AddNewCharacterInfo(name, character, row_num)

        return False

    def GetPlayerCharacters(self, name):
        entries = self.worksheet.col_values(1)

        for row_num, entry in enumerate(self.worksheet.col_values(1), start=1):
            if entry == name:
                return self.worksheet.acell(f'O{row_num}').value

        return f"{name} isn't found on the list."

    def AddAvoid(self, name):
        rows = self.avoids.col_values(1)

        if len(rows) < 1:
            self.avoids.update_acell(f"A2", name)
            print("yes")
            return

        # If rows 2-4 are all filled
        if len(rows) >= 4 and all(row for row in rows[2:4]):
            for i in range(2, 5):
                if i < len(rows):
                    self.avoids.update_cell(i, 1, rows[i])

            self.avoids.update_acell(f"A4", name)
        else:
            print('hello')
            row = len(rows) + 1
            self.avoids.update_acell(f"A{row}", name)


    def GetAvoids(self):
        names = self.avoids.col_values(1)
        names.remove("Player")

        if len(names) < 1:
            return

        results = [None] * len(names)

        for i in range(len(names)):
            results[i] = names[i]

        return results