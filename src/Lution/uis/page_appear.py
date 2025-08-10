import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GObject

from modules.utils.files import FilesFunctions
from modules.utils.lang import LANG
from modules.utils.logging import log

@Gtk.Template(filename="files/uis/page_appear.ui")
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

        font_filter = Gtk.FileFilter(name="Font Files")
        font_filter.add_mime_type("font/ttf")
        font_filter.add_mime_type("font/otf")


        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(font_filter)
        dialog.set_filters(filters)

        dialog.open(self.get_root(), None, self.on_font_file_selected)


    def on_font_file_selected(self, dialog, result):
        """
        Callback for when a file is selected from the dialog.
        """
        try:
            file_path = dialog.open_finish(result)
            if file_path:
                print(f"Selected font file: {file_path.get_path()}")
                self.ff.ApplyFont(file_path.get_path())
        except GObject.GError as err:
            print(f"Error opening file dialog: {err.message}")
