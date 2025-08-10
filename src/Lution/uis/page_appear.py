import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GObject

from modules.utils.files import FilesFunctions
from modules.utils.lang import LANG
from modules.utils.logging import log

@Gtk.Template(filename="uis/page_appear.ui")
class PageAppearance(Adw.PreferencesPage):
    __gtype_name__ = "PageAppearance"

    # btn_upload_font now refers to a GtkButton in the .ui file
    btn_upload_font = Gtk.Template.Child()
    btn_apply_font = Gtk.Template.Child()
    combo_cursor_style = Gtk.Template.Child()
    btn_apply_cursor = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        log.info("Page : Appearance")
        self.ff = FilesFunctions()

        # Connect the "clicked" signal of the new button to our new method
        self.btn_upload_font.connect("clicked", self.on_upload_font_clicked)
        # You'll also want to connect the other buttons here
        # self.btn_apply_font.connect("clicked", self.on_apply_font_clicked)
        # self.btn_apply_cursor.connect("clicked", self.on_apply_cursor_clicked)


    def on_upload_font_clicked(self, button):
        """
        Handler for the 'Upload Custom Font' button.
        This method will create and show a GtkFileDialog.
        """
        dialog = Gtk.FileDialog(title="Choose a Font File")

        # Create a filter for font files
        font_filter = Gtk.FileFilter(name="Font Files")
        font_filter.add_mime_type("font/ttf")
        font_filter.add_mime_type("font/otf")

        # The set_filters method expects a Gio.ListModel, not a list.
        # We must create a Gio.ListStore and add our filter to it.
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(font_filter)
        dialog.set_filters(filters)

        # Present the dialog and handle the response
        dialog.open(self.get_root(), None, self.on_font_file_selected)


    def on_font_file_selected(self, dialog, result):
        """
        Callback for when a file is selected from the dialog.
        """
        try:
            file_path = dialog.open_finish(result)
            if file_path:
                print(f"Selected font file: {file_path.get_path()}")
                # You can now process the selected file path
                # self.ff.copy_file(file_path.get_path(), "destination/path")
        except GObject.GError as err:
            # Handle the case where the user canceled the dialog
            print(f"Error opening file dialog: {err.message}")
