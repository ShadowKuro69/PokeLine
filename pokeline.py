import requests 



def get_pokemon(name):
        url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
        response = requests.get(url)
        data = response.json()
        print(data["name"])
        print(data["base_experience"])

        for t in data["types"]:
            print("Type:", t["type"]["name"])

        for stat in data["stats"]:
            print(stat["stat"]["name"], ":", stat["base_stat"])

while True:

    


        name = input("Enter a Pokemon name: ")
        if name == "quit":
            break
        get_pokemon(name)