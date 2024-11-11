import gi
import os
import sys
import json
import configparser

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gio, Gtk

         

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        
        
        
    def on_receiveShare(self, action, parameter, app):
        """
        Handles the payload content boing shared
        See the receiver.py application for more code and documentation.
        """
        pass
        

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() 
        mybox = Gtk.Box()
        myListbox = Gtk.ListBox()
        
        #
        # Here we want to find the applications to/through which we can share our content 
        # We need to read the intentapps.list and mimeapps.list files
        # In reality, we would need to go through a heirarchy of folders and combine the found values.
        # For demo simplicity, I am just reading a fixed (fictitious) set from a demo subfolder.
        #
        config_intents = configparser.RawConfigParser()
        config_intents.read('./demo_home/config/intentapps.list')
        intent_dict = dict(config_intents.items('Added Associations'))
        config_mimes = configparser.RawConfigParser()
        config_mimes.read('./demo_home/config/mimeapps.list')
        mime_dict = dict(config_mimes.items('Added Associations'))
        
        sharing_apps = intent_dict['org.freedesktop.intent.sharing'].split(';')
        mime_apps = mime_dict['text/plain'].split(';')
        
        #
        # The sharing candidates are the entries in intentapps.list under the "share" intent key
        # that also have an entry in the mimeapps.list file under the correct mime-type key (text/plain for this demo)
        #
        registered_desktops = [d for d in sharing_apps if d in mime_apps]
        
        mystrings = []
        
        #
        # In orger to present the user of our application with a list of sharing candidates,
        # we need to get the application name from the .desktop file.
        #
        for d in registered_desktops:
                config_desktop = configparser.RawConfigParser()
                config_desktop.read(f"./demo_home/local/share/applications/{d}")
                desktop_dict = dict(config_desktop.items('Desktop Entry'))
                human_name = desktop_dict['name']
                bus_name = d.replace('.desktop', '')
                mystrings.append(json.dumps([human_name, bus_name]))
        
        print(mystrings)
        mymodel = Gtk.StringList(strings=mystrings)
        myListbox.bind_model(mymodel, self.create_item_for_list_box)
        mybox.append(myListbox)
        self.win.set_child(mybox)
        
        
    def on_list_item_activate(self, item):
        """
        Callback...
        Initiates share of demo content here.
        
        Args:
            item (widget): The selected list item representing the application to which we will send our content.
        """
        print(item.get_subtitle())
        
        #
        # Here we create a proxy for the destination (receiving) application
        # based on the application's id.
        #
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        myproxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            item.get_subtitle(),
            '/' + item.get_subtitle().replace('.','/'),
            'org.freedesktop.Application',
            None
        )  
        
        #
        # Here we create a payload with the mime-type of the content we are sharing
        # and a base64 encoded string of the content
        #
        bytestr = b"some text"
        payload = json.dumps({'mime_type': 'text/plain', 'contents': GLib.base64_encode(bytestr)})
        
        #
        # Here we call the ActivateAction dbus method with our action name and the payload we created.
        #
        variant = GLib.Variant('(sava{sv})', ('ReceiveShare', [GLib.Variant('(s)', (payload,))], {'key': GLib.Variant('(s)', ('value',))}))
        myproxy.call_sync('ActivateAction', variant, Gio.DBusCallFlags.NONE, -1, None)

    def create_item_for_list_box(self, list_item):
        """
        Just populates our list of applications to share to for the demo...
        """
        sl = json.loads(list_item.get_string())
        list_row = Adw.ActionRow(
            title=sl[0],
            subtitle=sl[1],
            activatable=True,
        )
        list_row.connect('activated', self.on_list_item_activate)
        return list_row
        




app = MyApp(application_id="com.example.GtkApplicationSender")
app.run(sys.argv)


