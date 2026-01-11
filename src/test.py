from modules.config.config_init import initConfig
initConfig()
from modules.marketplace import MarketplaceHelper
import json

mk = MarketplaceHelper()

print(json.dumps(mk.list_items(), indent=4))