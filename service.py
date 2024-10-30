#!/usr/bin/env python3
#
#  service.py
#  
#  Copyright 2024 Rick Opper <rick@localhost.localdomain>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


import dbus
import dbus.service
import json
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


class ShareService(dbus.service.Object):
    def __init__(self):
        
        self.bus = dbus.SessionBus()
        self.object_path = "/com/brainstormtrooper/ShareService"
        self.interface_name = "com.brainstormtrooper.ShareService"

        self.subscribers = []
        
        dbus.service.Object.__init__(self, self.bus, self.object_path)
        # self.bus.publish(self.object_path, self.interface_name, self)


    @dbus.service.method("com.brainstormtrooper.ShareService", in_signature='s', out_signature='s')
    def get_sharing_apps(self, mime):
        """
        Provides a list of registered applications that share the given mime-type.
        Mime-types can be wild-card sub typed suh as img/* for all image formats.
        
        Args:
            mime (string): The mime-type the caller wants to share
            
        Returns:
            string: JSON list of objects describing registered applications.
        """
        res = []
        for s in self.subscribers:
            match = False
            for shareable in s['share_types']:
                if mime == shareable or (shareable.split('/')[1] == '*' and shareable.split('/')[0] == mime.split('/')[0]):
                    match = True
            if match:
                res.append(s)
        return json.dumps(res)
        
    
    @dbus.service.method("com.brainstormtrooper.ShareService", in_signature='s', out_signature='s')
    def register_sharing(self, ob):
        """
        Registers an application as accepting to share certain mime-types
        
        Args:
            ob (string): JSON object describing the application (id, name, accepted mime-types).
            
        Returns:
            string: JSON object with status code and message.
        """
        myob = json.loads(ob)
        if myob not in self.subscribers:
            self.subscribers.append(myob)
            print("New subscriber:", myob['human_name'])
            res = '{“status_code”: 202, “message”: “Registration created”}'
        else:
            res = '{“status_code”: 200, “message”: “Already registered”}'
        return res

# Create and start the share service
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
service = ShareService()
name = dbus.service.BusName("com.brainstormtrooper.ShareService", service.bus)
loop = GLib.MainLoop()
loop.run()
