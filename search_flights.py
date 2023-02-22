#!python3
# search_flights.py
# requires API_KEY for KIWI and AIRLABS

import requests
from datetime import datetime
import os

KIWI_ENDPOINT = "https://api.tequila.kiwi.com/"
headers = {
    "apikey": os.environ["KIWI_API"],
}

air_labs_endpoint = "https://airlabs.co/api/v9/"


def identify_airport(city_name):
    id_endpoint = f"{KIWI_ENDPOINT}locations/query"
    id_params = {
        "term": city_name,
        "locale": "en-US",
        "location_types": "airport",
        "active_only": True,
    }
    id_response = requests.get(
        url=id_endpoint, params=id_params, headers=headers
    ).json()
    return id_response["locations"][0]["city"]["code"]


def identify_airline(code):
    airline_endpoint = f"{air_labs_endpoint}airlines"
    air_labs_params = {
        "api_key": os.environ["AIR_LABS_API"],
        "iata_code": code,
    }
    airline_response = requests.get(url=airline_endpoint, params=air_labs_params).json()
    return airline_response["response"][0]["name"]


def airport_code(code):
    airline_endpoint = f"{air_labs_endpoint}airports"
    air_labs_params = {
        "api_key": os.environ["AIR_LABS_API"],
        "iata_code": code,
    }
    airline_response = requests.get(url=airline_endpoint, params=air_labs_params).json()
    return airline_response["response"][0]["name"]


def search_flights(
    fly_from, fly_to, date_from, date_to, currency="EUR", limit="5", max_stopovers="2"
):
    search_endpoint = f"{KIWI_ENDPOINT}v2/search"
    search_params = {
        "fly_from": identify_airport(fly_from),
        "fly_to": identify_airport(fly_to),
        "date_from": date_from,
        "date_to": date_to,
        "curr": currency,
        "locale": "en",
        "limit": limit,
        "max_stopovers": max_stopovers,
    }

    data = requests.get(
        url=search_endpoint, params=search_params, headers=headers
    ).json()
    print(
        f"\nFlights from {data['data'][0]['cityFrom']} to {data['data'][0]['cityTo']}:"
    )

    for flight in data["data"]:
        price = flight["price"]
        currency = data["currency"]
        fly_from = airport_code(flight["flyFrom"])
        fly_to = airport_code(flight["flyTo"])
        routes = flight["route"]

        print(f"\nFlight for {price} {currency}")
        print(f"Route from {fly_from} to {fly_to}:")

        for route in routes:
            airport_from = airport_code(route["flyFrom"])
            airport_to = airport_code(route["flyTo"])
            airline = identify_airline(route["airline"])
            print(
                f"From {airport_from} to {airport_to} by {airline} "
                f"at {route['local_departure'].split('T')[1].split('Z')[0].split('.000')[0]} "
                f"in {route['local_departure'].split('T')[0]}"
            )


def main():
    today = datetime.today().strftime("%d/%m/%Y")
    fly_from = input("\nFlight from: ")
    fly_to = input("Flight to: ")
    date_from = input("Date from (dd/mm/yyyy): ") or today
    date_to = input("Date to (dd/mm/yyyy): ")
    currency = input("Currency (e.g. USD, EUR, PLN): ") or "EUR"
    limit = input("Search limit: ") or "4"
    max_stopovers = input("Max number of stopovers (0 for direct flights): ") or "2"

    search_flights(fly_from, fly_to, date_from, date_to, currency, limit, max_stopovers)


if __name__ == "__main__":
    main()
