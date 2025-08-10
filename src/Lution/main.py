import gi
import sys
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

from uis.page_fflags import PageFFlags
from uis.page_mods import PageMods
from uis.page_appear import PageAppearance
from uis.page_marketplace import PageMarketplace
from uis.page_installed import PageInstalled

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hb = Adw.HeaderBar()
        self.set_titlebar(hb)

        # lazy add about btn
        about_btn = Gtk.Button.new_from_icon_name("help-about-symbolic")
        about_btn.set_tooltip_text("About")
        about_btn.connect("clicked", self.show_about)
        hb.pack_end(about_btn)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        stack = Adw.ViewStack(vexpand=True)
        container.append(stack)
        self.set_default_size(600, 900)

        try: stack.add_titled(PageFFlags(), "fflags", "Feature Flags")
        except Exception as e: print(f"Error loading PageFFlags: {e}")

        try: stack.add_titled(PageMods(), "mods", "Mods")
        except Exception as e: print(f"Error loading PageMods: {e}")

        try: stack.add_titled(PageAppearance(), "appearance", "Appearance")
        except Exception as e: print(f"Error loading PageAppearance: {e}")

        try: stack.add_titled(PageMarketplace(), "marketplace", "Marketplace")
        except Exception as e: print(f"Error loading PageMarketplace: {e}")

        try: stack.add_titled(PageInstalled(), "installed", "Installed")
        except Exception as e: print(f"Error loading PageInstalled: {e}")

        c = Adw.ViewSwitcherBar()
        c.set_stack(stack)
        c.set_reveal(True)
        container.append(c)

        self.set_child(container)

    def show_about(self, button):
        icon_path = os.path.join(os.path.dirname(__file__), "files", "lution1.png")
        
        about = Adw.AboutWindow(
            application_name="LUTION BETA",
            application_icon=icon_path,
            developer_name="Wookhq",
            version="1.7.8",
            comments="just a few cats and coffee",
            license="MIT",
            website="https://wookhq.github.io/lution",
            issue_url="https://github.com/Wookhq/Lution/issues",
            license_type=Gtk.License.MIT_X11,
            developers=["Chip", "gio-exe"],
        )

      

        about.present()

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = MainWindow(application=app)
        win.present()

def main():
    app = MyApp()
    return app.run(sys.argv)

if __name__ == '__main__':
    main()
