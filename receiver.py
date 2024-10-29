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
  <interface name='com.example.GtkApplication.sharing'>
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
            'human_name': 'example app',
            'bus_name': 'com.example.GtkApplication',
            'share_types': [ 'text/plain' ],
            'share_files': True
        }
        result = proxy.register_sharing('(s)', json.dumps(reg))
        Gio.DBusConnection.register_object(
            bus,
            '/com/example/GtkApplication/sharing',
            Gio.DBusNodeInfo.new_for_xml(interface_xml).interfaces[0],
            self.do_handle_incoming_share
        )

        
        
    def do_handle_incoming_share(self, c, i, path, interface, method, payload, invocation):
        print(payload)
        response = '{"status_code": 200, "message": "Accepted"}'
        self.label.set_label(payload.unpack()[0])
        invocation.return_value(GLib.Variant('(s)', (response,)))
        

    def on_activate(self, app):
        box = Gtk.Box()
        self.label = Gtk.Label(label='Waiting for message')
        box.append(self.label)
        self.win = MainWindow(application=app)
        self.win.set_child(box)
        self.win.present() 
        
        registered = proxy.get_sharing_apps('(s)', 'text/plain')
        print(registered)
        
    def on_share_text_signal(self, sender, object, iface, signal, text):
        print("Received shared text:", text)
        # Process the shared text here
        


        




app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)


