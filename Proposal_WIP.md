# Existing Specifications

## Desktop file specification
here: https://specifications.freedesktop.org/desktop-entry-spec/latest/index.html#introduction

### Interfaces
https://specifications.freedesktop.org/desktop-entry-spec/latest/interfaces.html
Arbitrary "interfaces" implemented by the application.
Could be used to designate extra dbus interfaces implemented by an application if needed.
### Actions
https://specifications.freedesktop.org/desktop-entry-spec/latest/extra-actions.html
Allow access to extra application activation methods (similar to Exec)
### Dbus activation
https://specifications.freedesktop.org/desktop-entry-spec/latest/dbus.html
Dbus can activate a specific action using the ActivateAction method exposed by the application.
This could be used by sharing applications to access a ReceiveShare action and associated method in the receiving application.
### Mime types
https://specifications.freedesktop.org/desktop-entry-spec/latest/mime-types.html
Describes the mime-types handled by an application

## Mime-type specification
here: https://specifications.freedesktop.org/mime-apps-spec/latest/index.html#id-1.2
Describes how mime-types are associated with applications.
Configured by users/admins.
## Intent apps specification (WIP)
here: https://gitlab.freedesktop.org/xdg/xdg-specs/-/merge_requests/81,
https://gitlab.freedesktop.org/andyholmes/xdg-specs/-/blob/work/andyholmes/intent-app-spec/intent-apps/intent-apps-spec.xml
html output: https://andyholmes.ca/public/intent-apps/intent-apps-spec.html

Explains how to associate a given "intent" with a list of applications.
Eg.: Calendar: org.gnome.calendar...

I don't see how this could help share content.
org.exaple.share: some very long list of rather arbitrary applications?
### Proposition
Users, system administrators, application vendors and distributions can change associations between applications and intents by writing into a file called intentapps.list.
Indicating the default application for a given intent is done by writing into the group \[Default Applications\] in the file intentapps.list.
The suggested algorithm for determining the default application for a given intent is:
- get the list of desktop ids for the given intent under the "Default Applications" group in the first intentapps.list
- for each desktop ID in the list, attempt to load the named desktop file, using the normal rules
- if a valid desktop file is found, verify that it is associated with the intent
- if a valid association is found, we have found the default application
- if after all list items are handled, we have not yet found a default application, proceed to the next intentapps.list file in the search order and repeat
- if after all files are handled, we have not yet found a default application, we are free to choose how to pick one among the available implementations of the intent. This might include hardcoding a preferred default (e.g. from the same desktop environment / software stack), sorting available desktop files by desktop ID to pick the first, actually asking the user about their preference... In any case it should be consistent across runs rather than random (e.g. based on the order of an unsorted list of files from a directory).

# Proposed Workflow

### From current specifications
User of Application A want to share a picture with someone.
1) User clicks Share button on Application A interface.
2) Application A must read through the different intentapps.list files to build a list of possible receiving applications.
3) Application A must read through the different mimapps.list files to build a list of applications that handle the type of content being shared (a .jpg photo, for example).
4) Application A must find an (or several) application(s) that both handle the "sharing" intent, and accept the image/jpg mime type.
5) Application A must then read the desktop files for the found applications (even if just to get the icon to display in the sharing list UI)
6) Application A presents the user with a list of possible applications to share the content (picture) with/through.
7) User selects Application B from the list

We stop here, because the current draft does not describe how to hand the content off from Application A to Application B...

### Continuation based on my demo
The user of Application A has selected Application B to share some content (a .jpg photo) to/through...
8) Application A builds a dbus path to the expected ActivateAction method of Application B based on the id of Application B
9) Application A calls the dbus method and provides the mime-type (image/jpg), and the content of the photo being shared base64 encoded.
10) Application B will then present the User with the interface to handle the content received (edit, forward, whatever...)

# Requirements / Criteria
In order for this type of sharing to be possible, dbus must provide a pass-through sharing method and applications wanting to provide the Sharing intent must handle a ReceiveShare action.
Something like:
- Entry in mimeapps.list associating Application B (receiving application) with image/jpg (content mime-type).
- Entry in intentapps.list associating Application B (receiving application) with the Sharing intent.
- ReceiveShare action defined on Application B (.desktop file) and a method to handle the received content 
- org.freedesktop.intents.sharing.share method on dbus
# Current Hurdles / Obstacles
This type of implementation is not out of reach.
What is needed as far as I can see:
- Dbus method
	- Ownership and implementation?
- Inclusion of the ReceiveShare action and handler method in template/stater applications for the different desktop environments...
