# Hledání nejkratší cesty v bludišti

## Popis

Tento projekt se zabývá řešením (hledáním nejkratší cesty) a také základním generováním bludišť. Základním vstupem bude bludiště $n\times n$ z csv souboru, přičemž vstup do bludiště bude vždy levý horní roh a výstup bude vždy pravý dolní roh. Z jedné buňky do druhé se lze dostat pouze přes společnou hranu (nikoliv přes roh).

Nahrané bludiště se pak načte jako Numpy matice s hodnotami true/false, kde true = průchozí cesta, false = stěna.

Výstup je ve formě obrázku (černá = stěna, bílá = průchozí cesta, červená = nejkratší cesta ven).

## Funcionality

- Načítání bludiště z CSV souboru
- Hledání nejkratší cesty (mezi levým horním rohem a pravým dolním rohem) za použití incidenční matice a Dijkstrova algoritmu
- Vykreslení bludiště a nalezenou cestu do černobílého obrázku, kde cesta bude vyznačena červeně
- Generování bludiště tak, aby mělo řešení (tj. aby existovala cesta mezi levým horním a pravým dolním rohem)
  - funkce začne s nějakou předdefinovanou šablonou a poté bude zaplňovat bludiště v náhodných místech a kontrolovat, zda je stále průchozí

## Třída a metody

- V kódu je definována třída Maze, která má následující atributy:
  - grid: bludiště ve formě matice
  - shortest_path: nejkratší cesta ve formě seznamu

- Třída má tyto metody:
  - from_csv
    - Vstup: "cesta k csv souboru bludiště"
    - Nahraje bludiště jako objekt třídy

  - find_shortest_path
    - Najde nejkratší cestu z bludiště

  - generate_maze
    - Vstup: celočíselný rozměr, "název šablony", celočícelý počet přidání náhodných stěn
    - Výchozí hodnoty: šablona = "empty", náhodé stěny = 50
    - šablony na výběr: empty, slalom, X, +, mrizka
    - při napsání špatného názvu šablony se napíše chybová hláška

  - save_to_image(self, output_path: str = "saved_maze.png", scale: int = 20)
    - Vstup: "cesta a název obrázku", škála
    - Výchozí hodnoty: název obrázku "saved_maze.png" ve složce s projektem, škála = 20
