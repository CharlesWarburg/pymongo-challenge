import requests
from pymongo import MongoClient


def get_starships():
    res = requests.get("https://swapi.info/api/starships")
    res.raise_for_status()
    return res.json()


def connect_to_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    return client["starwars"]


def get_pilot_object_ids(pilot_urls, people_collection):
    pilot_ids = []

    for pilot_url in pilot_urls:
        response = requests.get(pilot_url)
        response.raise_for_status()

        pilot_data = response.json()
        pilot_name = pilot_data["name"]

        pilot = people_collection.find_one({"name": pilot_name})

        if pilot:
            pilot_ids.append(pilot["_id"])
        else:
            print(f"Pilot not found: {pilot_name}")

    return pilot_ids


def transform_starships(starships, people_collection):
    for starship in starships:
        starship["pilots"] = get_pilot_object_ids(
            starship["pilots"],
            people_collection
        )

    return starships


def insert_starships(starships, starships_collection):
    starships_collection.delete_many({})
    starships_collection.insert_many(starships)


db = connect_to_mongo()

people_collection = db["people"]
starships_collection = db["starships"]

starships = get_starships()

transformed_starships = transform_starships(
    starships,
    people_collection
)

insert_starships(
    transformed_starships,
    starships_collection
)

# basic testing

print(starships_collection.count_documents({}))

millennium_falcon = starships_collection.find_one({
    "name": "Millennium Falcon"
})

print(millennium_falcon)