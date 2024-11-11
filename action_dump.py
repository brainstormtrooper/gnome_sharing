from gi.repository import Gio, GLib

def on_activate(app):
    print("Application activated")

def on_my_action(action, parameter, app):
    print("My action was called!")

def main():
    # Create a GApplication instance
    app = Gio.Application.new("org.example.MyApp", Gio.ApplicationFlags.FLAGS_NONE)
    
    # Connect the 'activate' signal
    app.connect('activate', on_activate)
    
    # Create and add an action
    action = Gio.SimpleAction.new("my-action", None)
    action.connect('activate', on_my_action, app)
    app.add_action(action)
    
    # Activate the action
    app.activate_action("my-action", None)
    
    # Run the application
    app.run(None)

if __name__ == "__main__":
    main()
