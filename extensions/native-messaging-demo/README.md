# Native Messaging demo

A tiny Brave-on-Linux project showing shortcut → Python → browser communication.
It does not control music or change the existing YouTube Music extension.
No additional Python packages are needed. Keyboard settings are not changed
automatically.

## Two processes, one file

```text
Brave loads extension
        |
        v
connectNative() → Brave starts native-host.py (bridge, stays running)
                                       ^
                                       | private Unix socket
                                       |
Shortcut → native-host.py --toggle (sender, exits after reply)

bridge → Brave → extension → reply → Brave → bridge → socket → sender
```

`native-host.py` runs in two modes: without arguments it is the bridge started
by Brave; with `--toggle` it sends one request to that bridge. `host.py` supplies
the JSON framing functions imported by the bridge.

## Run

1. Keep this project in a permanent location.
2. Open `brave://extensions`, enable **Developer mode**, and choose
   **Load unpacked**. Select this project's `extension` folder.
3. Copy the ID shown on the **Communication Demo** card.
4. From this project folder, run:

   ```sh
   python3 register.py YOUR_EXTENSION_ID
   ```

   This registers the absolute path to `native-host.py` in Brave's user-level native
   messaging configuration. An existing demo registration is backed up first.
   Loading the extension before registration may produce an expected connection
   error; reload it after registration.

5. Click **Reload** on the extension card, then click its **service worker**
   link to inspect the console.

6. Run the sender from a terminal in this project folder:

   ```sh
   python3 native-host.py --toggle
   ```

   You should see the request and reply in the extension console. The terminal
   prints `Extension replied: {'ok': True, 'received': {'action': 'toggle'}}`.

7. For a keyboard trigger, add a GNOME custom shortcut under **Settings →
   Keyboard → View and Customize Shortcuts → Custom Shortcuts**. Use the
   absolute command printed by `register.py`, for example:

   ```text
   /usr/bin/python3 /absolute/path/native-messaging-demo/native-host.py --toggle
   ```

   Choose an unused key, such as **Win+Shift+F8** if available, rather than
   replacing your working music shortcut. Watch the extension console when
   pressing it; GNOME does not display the sender's terminal output.

Expected message exchange:

```text
Python sends:       {"action":"toggle"}
JavaScript replies: {"ok":true,"received":{"action":"toggle"}}
```

## Communication

- `background.js` opens `chrome.runtime.connectNative('com.local.demo')`.
- Brave finds the registration created by `register.py` and launches `native-host.py`.
- The shortcut launches a second Python process with `--toggle`. It sends a
  request over a private Unix socket to the bridge that Brave started.
- The bridge writes a four-byte length followed by JSON bytes to standard output.
- Brave delivers the request to JavaScript's `onMessage` listener.
- JavaScript acknowledges it with `postMessage`. Brave writes the framed reply
  to the bridge's standard input. The bridge forwards it to the shortcut sender.

Only protocol messages belong on the helper's standard output. Use standard
error for debugging in bridge mode. The sender prints its reply normally.
There is no network listener or internet traffic. The socket lives under
`$XDG_RUNTIME_DIR/native-messaging-demo/` (normally `/run/user/YOUR_UID/`).
The `toggle` message is just an example: the extension acknowledges it without
performing any action. Keep Brave and the extension running. Only one bridge
can own the demo socket. If you move the project, run registration again. On another laptop,
load the extension there and register its own ID; no browser profile is copied.

## Remove

Remove **Communication Demo** from `brave://extensions`, remove its custom
shortcut if added, and delete only this
demo's registration file:
`~/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts/com.local.demo.json`.
