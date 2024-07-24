import json

from fuzzywuzzy import process

#https://www.goat.com/web-api/v1/countries
#https://www.goat.com/web-api/v1/currencies

def get_rate(scraper, currency):
  currencies = scraper.get("https://www.goat.com/web-api/v1/currencies")
  currencies = json.loads(currencies.text)
  curr = currencies['currencies']
  for i in curr:
    if i['isoCode'] == currency:
      return i['rate']
  return 1

def get_country_info_v3(scraper, country):
  countries = scraper.get("https://www.goat.com/web-api/v1/countries")
  countriesJson = json.loads(countries.text)['countries']
  if countriesJson is not None:
    countriesList = {countriesJson[i]['name']:i for i in range(len(countriesJson))}
    rightName = process.extractOne(country, countriesList.keys())
    if rightName is not None:
      index = countriesList[rightName[0]]
      return countriesJson[index]['isoCode'], countriesJson[index]['currency']
  return "EE", "EUR"

def get_country_info_v2(scraper, country):
  countries = scraper.get("https://www.goat.com/web-api/v1/countries")
  countriesJson = json.loads(countries.text)['countries']
  countriesList = {countriesJson[i]['isoCode']:i for i in range(len(countriesJson))}
  rightName = process.extractOne(country, countriesList.keys())
  if rightName is not None:
    index = countriesList[rightName[0]]
    rate = get_rate(scraper, countriesJson[index]["currency"])
    return rate 
  return None

def get_core_data(scraper, query, result=0):
  list = scraper.get(f"https://ac.cnstrc.com/search/{query.replace(' ','%20')}?c=ciojs-client-2.35.2&key=key_XT7bjdbvjgECO5d8&i=bbde1232-e0be-41e3-a7da-04909b345282&s=2&")
  initial = json.loads(list.text)["response"]["results"]
  if result < len(initial):
    shoe = initial[result]
    return shoe["data"]["id"], shoe["data"]["slug"], shoe["value"], shoe['data']["image_url"]
  return None, None, None, None
