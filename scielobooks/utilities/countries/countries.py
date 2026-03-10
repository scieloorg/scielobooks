# coding: utf-8
import json
import os
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(CURRENT_PATH, 'countries.json')

class Countries(object):
    with open(DATA_FILE, encoding="utf-8") as countries_file:
        __countries = json.load(countries_file)

    def __init__(self, language):
        self.__localized_countries = {code: country[language] for code, country in self.__countries.items()}

    def __getitem__(self, key):
        return self.__localized_countries[key]

    def __iter__(self):
        sorted_codes = sorted(self.__localized_countries, key= lambda country: self.__localized_countries[country])
        return (code for code in sorted_codes)

    def items(self):
        return ((code, self[code]) for code in self)
