import json
from modules.utils.logging import log

lg = log()

class crossover():
    def __init__(self):
        pass
    
    def crossover(self, data):
        content = json.loads(data)
        try:
            lg.info(f"Using crossover version {content['metadata']['crossoverVerison']}")
            lg.info(f"CROSSOVER : Platform {content['metadata']['roblox']}")
            
            fastflag = content['crossover']['fastflag']
            if fastflag == 'none':
                lg.info(f"CROSSOVER : Did not found fastflag")
            else :
                lg.info(f"CROSSOVER : Found fastflag path : {fastflag}")

            mod = content['crossover']['mod']
            if mod == 'none':
                lg.info(f"CROSSOVER : Did not found mod")
            else :
                lg.info(f"CROSSOVER : Found mod path : {mod}")

            lg.info(f"CROSSOVER : Crossing over!")



        except KeyError as e:
            lg.info(f"missing key: {e}")
            return f"Missing {e}"