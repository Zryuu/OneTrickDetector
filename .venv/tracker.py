import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CURRENTSEASON = 0
SEASON_SUFFIX = '_11001_10'
MATCHES_URL   = 'https://api.tracker.gg/api/v2/marvel-rivals/standard/matches/'
PROFILE_URL   = f'https://api.tracker.gg/api/v2/marvel-rivals/standard/profile/ign/[Name]/segments/career?mode=competitive&season={CURRENTSEASON + 1}'
PUID_URL      = 'https://api.tracker.gg/api/v2/marvel-rivals/standard/search?platform=ign&query='



class Tracker:

    def __init__(self):
        options = Options()
        #options.add_argument('--headless')

        self.service = Service(executable_path='chromedriver.exe')
        self.driver = webdriver.Chrome(service=self.service, options=options)

    def GetProfileData(self, name, value):
        with open('test.json') as test:
            data = json.load(test)
            return data

        link = None
        if value.isnumeric():
            if value.len > 9:
                link = MATCHES_URL + f'{value}{SEASON_SUFFIX}'
            else:
                link = PUID_URL + f'{value}'
        else:
            link = PROFILE_URL.replace('[Name]', name)

        self.driver.get('google.com')

        try:
            pre_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'pre')))
            pre_text = pre_element.text
            return json.loads(pre_text)
        except Exception as e:
            print("failed")

    def GetProfileLink(self, name):
        return PROFILE_URL.replace('[Name]', name)

    def GetPlayedHeros(self, data):
        pass

    def GetProfileFromMatch(self, name, matchID):
        pass

    def GetPlayedHero(self, data):

        heros = []

        for hero in data:
            store_details = {"hero": None, "timePlayed": None}
            store_details["hero"] = hero["hero"]
            store_details["timePlayed"] = hero["timePlayed"]
            heros.append(store_details)

        print(heros)
