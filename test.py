import polars as pl
import json
big_mac = pl.read_csv('data/big-mac-source-data-v2.csv')
print(big_mac)

countries = pl.read_json('data/countries.json')
print(countries)

with open('data/countries.json') as file:
  countries = json.load(file)
countries_code_mapping = {country["cca"]: country["name"]["common"] for country in countries}