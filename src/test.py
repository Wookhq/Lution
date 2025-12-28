from modules.config.sober_config import SoberConfig

cfg = SoberConfig()

pr = cfg.read_key("discord_rpc_show_join_button")

print(pr)

cfg.write_key("are oyu a chip", False)
