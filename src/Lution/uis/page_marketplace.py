import time
import requests

import gi
import json
import threading
import functools
import io
import cairo

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf

from modules.marketplace.downloadandinstall import MarketplaceManager
from github import Github as g
from github.GithubException import UnknownObjectException
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.config.genconfig import Config

def run_in_thread(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    return wrapper

@Gtk.Template(filename="uis/page_marketplace_layout.ui")
class PageMarketplace(Adw.PreferencesPage):
    __gtype_name__ = "PageMarketplace"

    # Template Children from the .ui file
    marketplace_group = Gtk.Template.Child()
    reload_button = Gtk.Template.Child()
    loading_spinner = Gtk.Template.Child()
    themes_expander = Gtk.Template.Child()
    themes_flowbox = Gtk.Template.Child()
    mods_expander = Gtk.Template.Child()
    mods_flowbox = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        log.info("Page : Marketplace")

        self.cf = Config()
        self.mm = MarketplaceManager()
        self.cache = self.load_cache()
        self.cache_invalidate_time = 3600 # 1 hour

        self.reload_button.connect("clicked", self.on_reload_button_clicked)

        self.provider = self.cf.Read("marketplace", "marketplaceprd")
        if self.provider is None:
            self.provider = "Wookhq/Lution-Marketplace"
            self.cf.Update("marketplace", "marketplaceprd", self.provider)
        
        self.themes_content = None
        self.mods_content = None

        self.load_marketplace_content_thread = threading.Thread(target=self.load_marketplace_content)
        self.load_marketplace_content_thread.daemon = True
        self.load_marketplace_content_thread.start()

    def load_cache(self):
        try:
            with open(".marketplace_cache.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self):
        with open(".marketplace_cache.json", "w") as f:
            json.dump(self.cache, f)

    def get_github_content(self, repo_name, item):
        """Fetches content from a GitHub repository."""
        cache_key = f"{repo_name}/{item}"
        if cache_key in self.cache and time.time() - self.cache[cache_key]['timestamp'] < self.cache_invalidate_time:
            return self.cache[cache_key]['content']

        try:
            repo = g().get_repo(repo_name)
            content = repo.get_contents(item)
            self.cache[cache_key] = {
                'content': content.decoded_content.decode(),
                'timestamp': time.time()
            }
            self.save_cache()
            return content.decoded_content.decode()
        except UnknownObjectException:
            log.error(f"GitHub object not found: {item} in repo {repo_name}")
            return None
        except Exception as e:
            log.error(f"Error fetching content from GitHub: {e}")
            return None
    
    @run_in_thread
    def load_marketplace_content(self, button=None):
        GLib.idle_add(self.loading_spinner.start)
        GLib.idle_add(self.reload_button.set_sensitive, False)
        
        GLib.idle_add(self.clear_flowbox, self.themes_flowbox)
        GLib.idle_add(self.clear_flowbox, self.mods_flowbox)

        themes_file = self.get_github_content(self.provider, "Assets/Themes/content.json")
        if themes_file:
            self.themes_content = json.loads(themes_file)
            GLib.idle_add(self.populate_flowbox, self.themes_flowbox, self.themes_content, "theme")
        else:
            GLib.idle_add(self.themes_expander.set_label, "Themes (Not Found)")
        
        mods_file = self.get_github_content(self.provider, "Assets/Mods/content.json")
        if mods_file:
            self.mods_content = json.loads(mods_file)
            GLib.idle_add(self.populate_flowbox, self.mods_flowbox, self.mods_content, "mod")
        else:
            GLib.idle_add(self.mods_expander.set_label, "Mods (Not Found)")
        
        GLib.idle_add(self.loading_spinner.stop)
        GLib.idle_add(self.reload_button.set_sensitive, True)

    def clear_flowbox(self, flowbox):
        """Clears all children from a Gtk.FlowBox."""
        children = []
        for child in flowbox:
            children.append(child)
        for child in children:
            flowbox.remove(child)

    def populate_flowbox(self, flowbox, contents, content_type):
        """Populates a Gtk.FlowBox with cards for each content item."""
        if not contents:
            return

        for item in contents:
            # Create a card for each item
            card = self.create_marketplace_card(item, content_type)
            flowbox.insert(card, -1)
            # card.connect("size-allocate", self.on_image_size_allocate)


    def create_marketplace_card(self, content, content_type):
        """
        Creates a custom card widget for a single marketplace item.
        The card's structure is defined in the .ui file's template.
        """
        builder = Gtk.Builder.new_from_file("uis/marketplace_card.ui")
        card = builder.get_object("MarketplaceCard")

        title_label = builder.get_object("title_label")
        body_label = builder.get_object("body_label")
        image_item = builder.get_object("image_item")
        version_label = builder.get_object("version_label")
        creator_label = builder.get_object("creator_label")
        badge_label = builder.get_object("badge_label")
        download_button = builder.get_object("download_button")
        install_button = builder.get_object("install_button")

        # Set content
        title_label.set_text(content.get('title', 'Untitled'))
        body_label.set_text(content.get("body", LANG["lution.marketplace.marketplace.nodescprovidered"]))
        version_label.set_text(f"WINDOWSPLAYERVERSION: {content.get('version', 'N/A')}")
        creator_label.set_text(f"By: {content.get('creator', 'Unknown')}")
        
        sb = content.get("sb", "unknown")
        if sb == "stable":
            badge_label.set_text(LANG["lution.marketplace.marketplace.badges.stable"])
        elif sb == "unstable":
            badge_label.set_text(LANG["lution.marketplace.marketplace.badges.unstable"])
        else:
            badge_label.set_text(LANG["lution.marketplace.marketplace.badges.unkown"])

        image_url = content.get("image", None)
        if image_url:
            self.load_image_from_url(image_item, image_url)
        
        download_button.connect("clicked", self.on_download_button_clicked, content.get('title'), content_type, download_button, install_button)
        install_button.connect("clicked", self.on_install_button_clicked, content.get('title'), content_type)

        installed_items = self.cf.Read("marketplace", f"Installed{content_type.capitalize()}s")
        if installed_items and content.get('title') in installed_items:
            download_button.set_visible(False)
            install_button.set_visible(True)

        return card

    @run_in_thread
    def load_image_from_url(self, image_widget, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            input_stream = Gio.MemoryInputStream.new_from_data(response.content, None)

            GdkPixbuf.Pixbuf.new_from_stream_async(input_stream, None, self.on_image_loaded, (image_widget,))
        except Exception as e:
            log.error(f"Failed to load image from {url}: {e}")
            GLib.idle_add(image_widget.set_from_icon_name, "image-missing")

    def on_image_loaded(self, source, result, user_data):
        image_widget, = user_data
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_finish(result)
            GLib.idle_add(image_widget.set_from_pixbuf, pixbuf)
        except Exception as e:
            log.error(f"Failed to create pixbuf from stream: {e}")
            GLib.idle_add(image_widget.set_from_icon_name, "image-missing")

    def on_image_size_allocate(self, card, allocation):
        image_item = card.get_first_child().get_first_child().get_next_sibling().get_next_sibling() #this is probably not the best way to do this
        pixbuf = image_item.get_pixbuf()
        if pixbuf:
            width = card.get_allocated_width()
            height = -1
            if width > 0:
                scaled_pixbuf = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
                image_item.set_from_pixbuf(scaled_pixbuf)

    # Signal handlers
    def on_reload_button_clicked(self, button):
        """Handler for the 'Reload Marketplace' button."""
        self.load_marketplace_content()

    @run_in_thread
    def on_download_button_clicked(self, button, item_title, content_type, download_button, install_button):
        """Handler for the 'Download' button on a marketplace item card."""
        log.info(f"Downloading {item_title} of type {content_type}")
        self.mm.DownloadMarketplace(item_title, type=content_type)
        
        GLib.idle_add(download_button.set_visible, False)
        GLib.idle_add(install_button.set_visible, True)

    def on_install_button_clicked(self, button, item_title, content_type):
        """Handler for the 'Install' button on a marketplace item card."""
        log.info(f"Installing {item_title} of type {content_type}")
        self.mm.ApplyMarketplace(item_title, type=content_type)
