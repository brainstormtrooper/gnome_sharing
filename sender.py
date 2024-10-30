import gi
import os
import sys
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gio, Gtk

#
# Connect to session bus and create a proxy to execute functions
#
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

#
# This is the description of our interface for accepting shared content
# It is used below to create the actual interface on the bus.
#    
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


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.object_path = "/com/brainstormtrooper/ShareService"
        self.interface_name = "com.brainstormtrooper.ShareService"
        
        #
        # This is the registration object
        # It describes the application and what it accepts to share
        #
        reg = {
            'human_name': 'Sending app',
            'bus_name': 'com.example.GtkApplicationSender',
            'share_types': [ 'text/plain' ],
            'share_files': True
        }
        
        #
        # Here we call the sharing service and register what the application will accept
        # using the proxy we created above.
        #
        result = proxy.register_sharing('(s)', json.dumps(reg))
        
        #
        # Here we create the interface for the application to accept shared content
        # This should probably be moved...
        #
        Gio.DBusConnection.register_object(
            bus,
            '/com/example/GtkApplicationSender/sharing',
            Gio.DBusNodeInfo.new_for_xml(interface_xml).interfaces[0],
            self.do_handle_incoming_share
        )

        
        
    def do_handle_incoming_share(self, c, i, path, interface, method, payload, invocation):
        """
        Handles the payload content boing shared
        See the receiver.py application for more code and documentation.
        """
        print(payload)
        

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present() 
        mybox = Gtk.Box()
        myListbox = Gtk.ListBox()
        
        #
        # Here we ask dbus what applications are registered as accepting 
        # what we want to share (text/plain in this example).
        #
        registered = proxy.get_sharing_apps('(s)', 'text/plain')
        print(registered)
        mystrings = [json.dumps([item['human_name'], item['bus_name']]) for item in json.loads(registered)]
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
        myproxy = Gio.DBusProxy.new_sync(
            bus,
            Gio.DBusProxyFlags.NONE,
            None,
            item.get_subtitle(),
            '/' + item.get_subtitle().replace('.','/')  + '/sharing',
            item.get_subtitle() + '.sharing',
            None
        )  
        
        #
        # Here we create a payload with the mime-type of the content we are sharing
        # and a base64 encoded string of the content
        #
        payload = {'mime_type': 'text/plain', 'contents': GLib.base64_encode(b'some text')}
        
        #
        # Here we call the share_content function on our receiving application with the payload we created.
        # In response, we should get a status code and message (see receiver.py for example)
        #
        res = myproxy.share_content('(s)', json.dumps(payload))
        print(res)

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


