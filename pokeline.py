import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
console = Console()


def get_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)
    if response.status_code == 404:
        console.print("[bold red]Pokemon not found![/bold red]")
        return
    data =  response.json()

    console.print(f"\n[bold yellow]{data['name'].upper()}[/bold yellow]")
    console.print(f"[cyan]Base XP:[/cyan] {data['base_experience']}")

    for t in data["types"]:
        console.print(f"[green]Type:[/green] {t['type']['name']}")
    for stat in data["stats"]:
            console.print(f"[magenta]{stat['stat']['name']}[/magenta] : {stat['base_stat']}")

while True:
    name = input("Enter a Pokemon name: ")
    if name == "quit":
        break
    get_pokemon(name)