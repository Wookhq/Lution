from modules.config.config_init import initConfig

initConfig()
import json

from modules.marketplace import MarketplaceHelper

mk = MarketplaceHelper()

print(json.dumps(mk.list_items(), indent=4))

mk.download_item("c9007043-ca0b-4e7e-8874-2ea7a3187416")
