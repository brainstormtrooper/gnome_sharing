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

    @dbus.service.method("com.brainstormtrooper.ShareService", in_signature='s')
    def ShareContent(self, text):
        print("Received content to share:", text)
        try:
            dest = json.loads(self.GetSubscribers())[0]['bus_name']
            print(dest)
            dpath = '/' + dest.replace('.', '/')
        
            # a = self.PrivateMessageSignal(text, dest[0])
            self.service = self.bus.get_object(dest, f"{dpath}/shareSomething")
            _message = self.service.get_dbus_method('shareSomething', f"{dest}.shareSomething")
            payload = {'mime_type': 'text/plain', 'contents': GLib.base64_encode(b'text')}
            _message(json.dumps(payload))
        except Exception as e:
            print(e)
        
        b = self.ShareContentSignal(text)

    @dbus.service.signal("com.brainstormtrooper.ShareService", signature='s')
    def ShareContentSignal(self, text):
        print("Broadcasting content:", text)
        # self.bus.emit_signal(self.object_path, self.interface_name, "ShareContentSignal", text)
        return True

    @dbus.service.method("com.brainstormtrooper.ShareService", in_signature='s', out_signature='s')
    def get_sharing_apps(self, mime):
        res = []
        for s in self.subscribers:
            match = False
            for shareable in s['share_types']:
                if mime == shareable or (shareable.split('/')[1] == '*' and shareable.split('/')[0] == mime.split('/')[0]):
                    match = True
            if match:
                res.append(s)
        return json.dumps(res)
        # return json.dumps([s for s in self.subscribers if mime in s['share_types']])
    
    @dbus.service.method("com.brainstormtrooper.ShareService", in_signature='s', out_signature='s')
    def register_sharing(self, ob):
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
# service.bus.add_signal_receiver(service.on_signal_subscribed, "ShareContentSignal", service.interface_name, None, service.object_path)
loop = GLib.MainLoop()
loop.run()
