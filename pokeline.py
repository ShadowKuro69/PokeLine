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

def get_pokedex_entry(name):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{name.lower()}"
    response = requests.get(url)

    if response.status_code !=200:
        return "No Pokedex entry found"
    data = response.json()

    for entry in data["flavor_text_entries"]:
        if entry["language"]["name"] == "en":
            text = entry["flavor_text"]
            text = text.replace("\n", " ").replace("\f", " ")
            return text
        
    return "No Pokedex entry found"

def make_stat_bar(value, max_value=255):
    filled = int((value / max_value) * 20)
    empty = 20 - filled
    full = "\u2588"
    empty_char = "\u2591"
    bar = "[green]" + full * filled + "[/green]" + "[dim]" + empty_char * empty + "[/dim]"
    return bar


def get_type_weaknesses(types):
    weaknesses = {}
    for t in types:
        url = f"https://pokeapi.co/api/v2/type/{t}"
        data = requests.get(url).json()
        relations = data["damage_relations"]
        for weak in relations["double_damage_from"]:
            weaknesses[weak["name"]] = weaknesses.get(weak["name"], 1) * 2
        for resist in relations["half_damage_from"]:
            weaknesses[resist["name"]] = weaknesses.get(resist["name"], 1) * 0.5
        for immune in relations["no_damage_from"]:
            weaknesses[immune["name"]] = 0
    return weaknesses


def display_pokemon_panel(data, evolutions):
    name = data["name"].upper()
    xp = data["base_experience"]
    types = ", ".join(
        [t["type"]["name"].capitalize() for t in data["types"]]
    )
    type_list = [t["type"]["name"] for t in data["types"]]
    weaknesses = get_type_weaknesses(type_list)
    weak_text = " ".join([
        f"[red]{t}(x{v})[/red]" if v >= 2 else f"[green]{t}(x{v})[/green]"
        for t, v in weaknesses.items() if v != 1
        ])
    
    evo_text = " → ".join( 
        [e.capitalize() for e in evolutions]
    )

    stats = "\n".join([
        f"[cyan]{stat['stat']['name'].capitalize():15}[/cyan] {make_stat_bar(stat['base_stat'])} {stat['base_stat']}"
        for stat in data["stats"]
    ])

    pokedex_entry = get_pokedex_entry(data["name"])

    content = f"""
    [bold yellow]{name}[/bold yellow]

    [bold red]weaknesses:[/bold red] {weak_text}
    [cyan]Base XP:[/cyan] {xp} 
    [green]Type:[/green] {types}
    [bold blue]Evolution Line:[/bold blue] {evo_text}

    [bold magenta]Stats[/bold magenta]
    {stats}
    
    [bold white]Pokedex Entry[/bold white]
    "{pokedex_entry}"
    """

        
    panel = Panel(
        content,
        title="[bold red]POKEDEX[/bold red]",
        border_style="bright_blue",
        expand=False
    )
          
    console.print(panel)

def main():
    while True:
        name = input("\nEnter a Pokemon name: ")
        if name == "quit":
            break
        get_pokemon(name) 
if __name__ == "__main__":
    main()