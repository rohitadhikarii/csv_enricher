import csv
import requests
import json
import datetime

API_KEY = '02721966b26d1024cebd3d4bf7640511'
#Geocoding - returns lat/lon based on city and country code
def geocode(city, country_code):

    geo_response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&country={country_code}&count=1", timeout = 10)
    output = geo_response.json()
    results = output.get('results', []) #make sure to return an empty list if doesnt exist
    if not results:
        return None, None
    return results[0].get('latitude'), results[0].get('longitude')

#returns temperature and windspeed based on lat/lon of geocode function
def weather(lat, lon):
    weather_response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true", timeout = 10)
    output = weather_response.json()
    results = output.get('current_weather', {}) #make sure to return an empty dict if doesnt exist
    return results.get('temperature'), results.get('windspeed')

#returns the conversion rate and converted amount
def fx_rate(local_currency, amount):
    fx_response = requests.get(f"https://api.exchangerate.host/convert?access_key={API_KEY}&from={local_currency}&to=USD&amount={amount}", timeout = 10)
    output = fx_response.json()
    return output['result'], output['info']['quote']

output_data = []

with open('input.csv') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader: #converts the csv to a workable dictionary 
        city = row['city']
        country_code = row['country_code']
        local_currency = row['local_currency']
        amount = float(row['amount'])

    #call the api functions
        lat, lon = geocode(city, country_code)
        temperature, windspeed = weather(lat, lon) 
        usd_amount, fx_rate_val = fx_rate(local_currency, amount)

    #feeding desired output
        output_row = {
            "city": city,
            "country_code": country_code,
            "local_currency": local_currency,
            "amount_local": amount,
            "fx_rate_to_usd": round(fx_rate_val,5),
            "Amount_usd": round((amount*fx_rate_val),2),
            "latitude": lat,
            "longitude": lon,
            "temperature_c": temperature,
            "wind_speed_mps": windspeed,
            "retreived_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        output_data.append(output_row)

columns = output_row.keys()

with open('output.csv', 'w', newline = '') as outputfile:
    csvwriter = csv.DictWriter(outputfile, fieldnames=columns)
    csvwriter.writeheader()
    for row in output_data:
        csvwriter.writerow(row)

with open('output_file_json', 'w') as jsonfile:
    json.dump(output_data, jsonfile, indent=4)