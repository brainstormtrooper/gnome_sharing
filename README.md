# Intent-Type Content Sharing Between Applications With Dbus
This is a simple demo of how the sharing mechanism could work.
## Running the demo
Simply run in order in two consoles
1) receiver.py
2) sender.py

In sender.py, select "Foo Viewer" (com.example.GtkApplication) to send test content.

## Reasoning

Other platforms (especially mobile) provide a mechanism for sharing content and/or files between applications.
This is an intuitive and convenient way of distributing content.

## Proposal Basics

- Freedesktop applications provide for application Actions as defined in the desktop specification.
- Dbus activation as described in the desktop specification allows for an AtivateAction method to be called on any dbus activatable application.
- Applications can be associated with mime-types through the mime type specification.
- A draft (WIP) intent apps specification would allow applications to be associated with "intents".
- Intents could be anything, so Share could be an intent that could be associated with applications that could "share" content.
- Applications could implement a ReceiveShare action to handle incoming shared content.

## Proposed Workflow

Application A (on install?) → (Register handled mime-types and intents such as sharing) → Writes to config files

Application B User wants to share some content

Application B → Reads intentapps.list file(s) to find applications that share content (like Application A)

Application B → Reads mimeapps.list file(s) to find applications that handle the mime-type of the content te user wants to share.

Application B → Filter findings to get desktop entries of applications that have Share as an intent and  that handle the desired mime-type.

Application B → Reads .desktop files to get names of candidate applications in order to present the User with a list of applications.

User selects destination application Application A

Application B → (mime-type and base64 content string) → Application A using the dbus ActivateAction method

Application A treats the content as designed…
