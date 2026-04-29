import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from PIL import Image
import io
from PIL import ImageFilter, ImageEnhance
console = Console()

def get_evolution_chain(name):
     species_url = f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}"
     species_res = requests.get(species_url)
     if species_res.status_code == 404:
          return []
     evo_url = species_res.json()["evolution_chain"]["url"]
     evo_res = requests.get(evo_url)
     chain = evo_res.json()["chain"]
     evolutions = []
     while chain:
          evolutions.append(chain["species"]["name"])
          chain = chain["evolves_to"][0] if chain["evolves_to"] else None
     return evolutions
        

def show_pokemon_art(sprite_url):   
    from PIL import ImageEnhance
    response = requests.get(sprite_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGBA")
    img = img.resize((60, 60), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    for y in range(0, img.height - 1, 2):
        row = ""
        for x in range(img.width):
            r1, g1, b1, a1 = img.getpixel((x, y))
            r2, g2, b2, a2 = img.getpixel((x, y + 1))
            if a1 < 128 and a2 < 128:
                row += " "
            else:
                top = f"rgb({r1},{g1},{b1})" if a1 >= 128 else "black"
                bottom = f"rgb({r2},{g2},{b2})" if a2 >= 128 else "black"
                row += f"[{top} on {bottom}]▀[/]"
        console.print(row)
def get_pokemon(name):

    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}" 
    response = requests.get(url)
    if response.status_code == 404:
        console.print("[bold red]Pokemon not found![/bold red]")
        return
    data =  response.json() 
    
    sprite = data["sprites"]["other"]["official-artwork"]["front_default"]
    if sprite:
        show_pokemon_art(sprite)

    console.print(f"\n[bold yellow]{data['name'].upper()}[/bold yellow]")
    console.print(f"[cyan]Base XP:[/cyan] {data['base_experience']}")

    for t in data["types"]:
        console.print(f"[green]Type:[/green] {t['type']['name']}")
    evos = get_evolution_chain(name)
    console.print(f"[bold blue]Evolutions:[/bold blue] {' → '.join(evos)}")
    for stat in data["stats"]:
            console.print(f"[magenta]{stat['stat']['name']}[/magenta] : {stat['base_stat']}")

while True:
    name = input("Enter a Pokemon name: ")
    if name == "quit":
        break
    get_pokemon(name)    