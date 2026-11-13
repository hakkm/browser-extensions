# YouTube Music Only

Win+Shift+K toggles only existing `music.youtube.com` tabs. Regular YouTube
videos and other sites are never targeted. If several music tabs are playing,
all are paused. When none are playing, only the most recently accessed loaded
music tab resumes. The toolbar button performs the same action.

## Install in Brave

1. Restore this bundle, which installs the extension files at
   `~/.local/share/youtube-music-control`, registers the native messaging helper
   with Brave, and adds the GNOME Win+Shift+K shortcut.
2. Open `brave://extensions`, enable Developer mode, and choose **Load unpacked**.
3. Select `~/.local/share/youtube-music-control`. If already loaded, click its
   **Reload** button after restoring an update.
4. With a song loaded in YouTube Music and a regular YouTube video playing,
   press Win+Shift+K. Only the music should pause. Press again to resume.
   Repeat from another application to check desktop-wide operation.

Brave must remain running. GNOME handles the Win key; Brave extension shortcut
declarations do not support Super on Linux. The native helper uses a private
Unix socket in the logged-in user's runtime directory, not a network listener.
If the extension is missing, the shortcut shows a desktop notification.
The shortcut persists in GNOME and the extension reconnects when Brave starts.
Only one Brave profile can own the helper connection at a time.
Loading an unpacked extension is a separate browser step on each new device.
Restoring the files does not install or enable the extension in a browser profile.

The extension requests script access only to `https://music.youtube.com/*`
and native messaging access to its locally registered helper. Its manifest key
is public, keeps the extension ID stable, and is not an account credential.
It makes no network requests, stores no account data, and does not change
Win+Alt+K or the existing GNOME media shortcuts.
