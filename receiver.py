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
        
        #
        # This is the registration object
        # It describes the application and what it accepts to share
        #
        reg = {
            'human_name': 'example app',
            'bus_name': 'com.example.GtkApplication',
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
        # using the interface XML created above.
        # This is the function interface that will be called by the sending application.
        # This should probably be moved...
        #
        Gio.DBusConnection.register_object(
            bus,
            '/com/example/GtkApplication/sharing',
            Gio.DBusNodeInfo.new_for_xml(interface_xml).interfaces[0],
            self.do_handle_incoming_share
        )

        
        
    def do_handle_incoming_share(self, c, i, path, interface, method, payload, invocation):
        """
        Handles the payload content being shared and returns a status
        
        Args (the ones of interest for the demo):
            payload (string): JSON object describing what is being shared. Includes mime-type and base64 encoded content
            invocation (invocation): Used to return the response to the calling application
        
        Returns: 
            string: JSON object with status code and message
        """
        print(payload)
        
        #
        # Here is a sample response 
        #
        response = '{"status_code": 200, "message": "Accepted"}'
        
        self.label.set_label(payload.unpack()[0])
        
        #
        # Here we handle the response through the invocation object
        #
        invocation.return_value(GLib.Variant('(s)', (response,)))
        

    def on_activate(self, app):
        box = Gtk.Box()
        self.label = Gtk.Label(label='Waiting for message')
        box.append(self.label)
        self.win = MainWindow(application=app)
        self.win.set_child(box)
        self.win.present() 
        
        #
        # Here we ask dbus what applications are registered as accepting 
        # what we want to share (text/plain in this example).
        #
        registered = proxy.get_sharing_apps('(s)', 'text/plain')
        print(registered)
        



app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)


