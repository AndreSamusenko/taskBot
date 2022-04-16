import requests
from threading import Thread
from time import sleep
from config import ConfigData

config_data = ConfigData()


class Gist:
    GITHUB_API = 'https://api.github.com/gists'
    GIST_TOKEN = config_data.GIST_TOKEN
    headers = {'Authorization': f'token {GIST_TOKEN}'}
    MAX_GISTS = 100

    def __init__(self):
        self.gists = None
        self.gists_by_lan = {}
        th = Thread(target=self.update)
        th.start()

    def __update__(self):
        self.get_all_gists()
        self.gists_by_lan = {}
        self.filter_by_language()

    def update(self):
        while True:
            self.__update__()
            print("UPDATING GISTS....")
            sleep(3600 * 4)

    def get_all_gists(self):
        self.gists = requests.get(self.GITHUB_API,
                                  headers=self.headers,
                                  params={"per_page": self.MAX_GISTS}).json()[::-1]
        print()
        return self.gists

    def get_languages(self):
        return list(self.gists_by_lan.keys())

    def get_gists_by_language(self, lang):
        return self.gists_by_lan.get(lang, [])

    def filter_by_language(self):
        for gist in self.gists:
            for file in gist["files"]:
                lang = gist["files"][file]["language"]
                name = gist['description'] if gist['description'] else file

                if self.gists_by_lan.get(lang):
                    self.gists_by_lan[lang].append({"name": name, "link": gist['html_url']})
                else:
                    self.gists_by_lan[lang] = [{"name": name, "link": gist['html_url']}]




