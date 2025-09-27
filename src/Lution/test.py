from modules.crossover import crossover
from pathlib import Path

co = crossover()

folder = Path("~/Documents/dock").expanduser()

co.create(folder)

crossover_file = co.pack(folder)

co.unpack(crossover_file)

co.crossover(folder)
