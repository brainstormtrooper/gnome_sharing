import gi
import os
import sys
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gio, Gtk


bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
proxy = Gio.DBusProxy.new_sync(
    bus,
    Gio.DBusProxyFlags.NONE,
    None,
    'com.brainstormtrooper.ShareService',
    '/com/brainstormtrooper/ShareService',
    'com.brainstormtrooper.ShareService',
    None
)        
    
interface_xml = """
<node>
  <interface name='com.example.GtkApplicationSender.sharing'>
    <method name='share_content'>
      <arg type='s' name='content' direction='in'/>
      <arg type='s' name='response' direction='out'/>
    </method>
  </interface>
</node>
"""        
        

         

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.object_path = "/com/brainstormtrooper/ShareService"
        self.interface_name = "com.brainstormtrooper.ShareService"
        reg = {
            'human_name': 'Sending app',
            'bus_name': 'com.example.GtkApplicationSender',
            'share_types': [ 'text/plain' ],
            'share_files': True
        }
        result = proxy.register_sharing('(s)', json.dumps(reg))
        Gio.DBusConnection.register_object(
            bus,
            '/com/example/GtkApplicationSender/sharing',
            Gio.DBusNodeInfo.new_for_xml(interface_xml).interfaces[0],
            self.do_handle_incoming_share
        )

        
        
    def do_handle_incoming_share(self, c, i, path, interface, method, payload, invocation):
        print(payload)
        

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() 
        mybox = Gtk.Box()
        myListbox = Gtk.ListBox()
        
        registered = proxy.get_sharing_apps('(s)', 'text/plain')
        print(registered)
        mystrings = [json.dumps([item['human_name'], item['bus_name']]) for item in json.loads(registered)]
        print(mystrings)
        mymodel = Gtk.StringList(strings=mystrings)
        myListbox.bind_model(mymodel, self.create_item_for_list_box)
        mybox.append(myListbox)
        self.win.set_child(mybox)
        
        
    def on_share_text_signal(self, sender, object, iface, signal, text):
        print("Received shared text:", text)
        # Process the shared text here
        
    def on_list_item_activate(self, item):
        print(item.get_subtitle())
        
        myproxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            item.get_subtitle(),
            '/' + item.get_subtitle().replace('.','/')  + '/sharing',
            item.get_subtitle() + '.sharing',
            None
        )  
        payload = {'mime_type': 'text/plain', 'contents': GLib.base64_encode(b'some text')}
        res = myproxy.share_content('(s)', json.dumps(payload))
        print(res)

    def create_item_for_list_box(self, list_item):
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


