# Intent-Type Content Sharing Between Applications With Dbus

## Reasoning

Other platforms (especially mobile) provide a mechanism for sharing content and/or files between applications.
This is an intuitive and convenient way of distributing content.

## Proposal Basics

- Dbus could be used to handle intent registration and informing sharing applications of which receiving applications are available.
- Each application would be responsible for registering any sharing intent with Dbus. This could be done at install or update, or event on application launch. The application should also be able to update the list of mime-types it shares (when a new version is installed, for example).
- Applications could ask Dbus for a list of other Applications that would accept a given mime-type.
- Dbus would keep the register in the file system (shared between User ans System level).
- Applications could implement a simple Dbus interface to receive shared content.

## Proposed Workflow

Application A (at launch or Install/Update) → (Register Accepted mime-types) → Dbus

Application B (at launch or Install/Update) → (Register Accepted mime-types) → Dbus (Dbus does not keep duplicates)

Application B User wants to share some content

Application B → (mime-type) → Dbus to get list of possible destination applications

Dbus → (list of Name and ID of applications) → Application B

User selects destination application Application A

Application B → (mime-type and base64 content string) → Application A

Application A → (ACK message w/status code) → Application B

Application A treats the content as designed…
