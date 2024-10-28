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

# https://github.com/LEW21/pydbus/blob/master/examples/clientserver/server.py

from gi.repository import GLib
from pydbus import SessionBus
from pydbus.generic import signal

loop = GLib.MainLoop()
bus = SessionBus()

class ShareService(object):
    """
        <node>
            <interface name='com.brainstormtrooper.ShareService'>
                <signal name="ShareContentSignal">
                    <arg type='s'/>
                </signal>
                <signal name="PrivateMessageSignal">
                    <arg type='s'/>
                    <arg type='s'/>
                </signal>
                <method name='ShareContent'>
                    <arg type='s' name='text' direction='in'/>
                </method>
                <method name='GetSubscribers'>
                    <arg type='s' name='response' direction='out'/>
                </method>
                <method name='on_signal_subscribed'>
                    <arg type='s' name='subscriber_object_path' direction='in'/>
                </method>
                <method name='Quit'/>
            </interface>
        </node>
    """

    ShareContentSignal = signal()
    PrivateMessageSignal = signal()

    def __init__(self):
        self.subscribers = []

    def ShareContent(self, text):
        print("Received content to share:", text)
        self.emit_share_text_signal(text)
        self.SendPrivateMessage(self.subscribers[0], text)

    def emit_share_text_signal(self, text):
        print("Broadcasting content:", text)
        self.ShareContentSignal(text)

    def SendPrivateMessage(self, subscriber_object_path, message):
        if subscriber_object_path in self.subscribers:
            handler = bus.get(subscriber_object_path)
            # handler.on_private_signal(text)
            print("Received private message:", message)
            
            self.PrivateMessageSignal(message)
        else:
            print("Subscriber not found:", subscriber_object_path)

    def GetSubscribers(self):
        return self.subscribers

    def on_signal_subscribed(self, subscriber_object_path):
        if subscriber_object_path not in self.subscribers:
            self.subscribers.append(subscriber_object_path)
            print("New subscriber:", subscriber_object_path)
            
    def Quit(self):
        """removes this object from the DBUS connection and exits"""
        loop.quit()

# Create and start the share service

bus.publish("com.brainstormtrooper.ShareService", ShareService())
loop.run()
