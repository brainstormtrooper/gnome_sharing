import gi
import os
import sys
import json

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gio, Gtk    
        

         

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Things will go here

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        
        # Create and add an action
        action = Gio.SimpleAction.new("ReceiveShare", GLib.VariantType.new('(s)'))
        action.connect('activate', self.on_receiveShare, self)
        self.add_action(action)
        
        
    def on_receiveShare(self, action, parameter, app):
        """
        Handles the payload content being shared and returns a status
        
        Args (the ones of interest for the demo):
            parameter (string variant): JSON encoded object describing what is being shared. Includes mime-type and base64 encoded content
        """
        print(parameter)
        
        content = GLib.base64_decode(json.loads(parameter.unpack()[0])['contents'])
        self.label.set_label(f"You shared: {content.decode('utf-8')}")
        
        

    def on_activate(self, app):
        box = Gtk.Box()
        self.label = Gtk.Label(label='Waiting for message')
        box.append(self.label)
        self.win = MainWindow(application=app)
        self.win.set_child(box)
        self.win.present() 
        
        



app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)


