from gi.repository import Gio, GLib

def call_action(app_id, action_name, parameter=None):
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    proxy = Gio.DBusProxy.new_sync(
        bus,
        Gio.DBusProxyFlags.NONE,
        None,
        app_id,
        '/org/gtk/Application',
        'org.gtk.Application',
        None
    )
    
    if parameter is not None:
        variant = GLib.Variant('(sav)', (action_name, [parameter]))
    else:
        variant = GLib.Variant('(sav)', (action_name, []))
    
    proxy.call_sync('ActivateAction', variant, Gio.DBusCallFlags.NONE, -1, None)

# Example usage
call_action('org.gnome.Gedit', 'new-window')
