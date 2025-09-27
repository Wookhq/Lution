from modules.crossover import crossover


cr = crossover()


with open('/home/chip/Documents/random/crossover/crossover.json', 'r') as f :
    content = f.read()
    cr.crossover(content)