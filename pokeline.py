import requests
from rich.console import Console
from rich.live import Live
from PIL import Image, ImageEnhance
import io
import time
from rich.panel import Panel

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

def get_pokemon_art(sprite_url, padding=0):
    response = requests.get(sprite_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGBA")
    img = img.resize((38, 30), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.8)
    CHARS = " ░▒▓█"
    lines = "\n" * padding  
    for y in range(img.height):
        row = ""
        for x in range(img.width):  
            r, g, b, a = img.getpixel((x, y))
            if a < 128:
                row += "  "
                continue
            brightness = (r + g + b) // 3
            char = CHARS[int(brightness / 255 * (len(CHARS) - 1))]
            row += f"[rgb({r},{g},{b})]{char} [/rgb({r},{g},{b})]"
        lines += row + "\n"
    return lines

def get_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)
    if response.status_code == 404:
        console.print("[bold red]Pokemon not found![/bold red]")
        return
    data = response.json()

    sprite = data["sprites"]["other"]["official-artwork"]["front_default"]
    if sprite:
        console.print(get_pokemon_art(sprite))

    evos = get_evolution_chain(name)
    display_pokemon_panel(data, evos)
def test_panel():
    panel = Panel(
        "This is my first pokedex panel",
        title="POKEDEX",
        border_style="blue"
    )

    console.print(panel) 


def display_pokemon_panel(data, evolutions):
    name = data["name"].upper()
    xp = data["base_experience"]

    types = ", ".join(
        [t["type"]["name"].capitalize() for t in data["types"]]
    )

    evo_text = " → ".join(
        [e.capitalize() for e in evolutions]
    )

    stats = "\n".join([
        f"{stat['stat']['name'].capitalize():15} : {stat['base_stat']}"
        for stat in data["stats"]
    ])

    content = f"""
    [bold yellow]{name}[/bold yellow]


    [cyan]Base XP:[/cyan] {xp}
    [green]Type:[/green] {types}
    [bold blue]Evolution Line:[/bold blue] {evo_text}

    [bold magenta]Stats[/bold magenta]
    {stats}
    """

        
    panel = Panel(
        content,
        title="[bold red]POKEDEX[/bold red]",
        border_style="bright_blue",
        expand=False
    )
          
    console.print(panel)


while True:
    name = input("\nEnter a Pokemon name: ")
    if name == "quit":
        break
    get_pokemon(name) 