# Conan Exiles Enhanced Manager

A Windows desktop manager for **Conan Exiles Enhanced** mods, Steam Workshop modlists, local dedicated servers, hosted FTP/SFTP servers, profiles, backups, and recovery.

**GitHub:** https://github.com/Vercadi/conan-exiles-enhanced-manager  
**Support:** https://ko-fi.com/vercadi | https://www.patreon.com/cw/Vercadi

## What It Does

- Detects the Conan Exiles client, the Conan Exiles Dedicated Server Steam app, Steam build IDs, config folders, saves, logs, and Workshop content.
- Reads and writes `modlist.txt` safely for client, dedicated server, or both.
- Tracks local `.pak` entries and Steam Workshop items while preserving mod order.
- Scans `steamapps/workshop/content/440900` for downloaded Workshop files.
- Starts the local dedicated server only when explicitly requested.
- Supports hosted servers over SFTP or FTP for profile setup, path detection, modlist upload, optional local pak upload, and config backup.
- Provides named mod profiles, restore-to-vanilla workflows, backup snapshots, and an activity timeline.
- Includes Settings, Help, support diagnostics, and GitHub Releases update checks.

The app does not download Workshop items, edit `ServerSettings.ini`, delete `.pak` files, stop server processes, or restart hosted servers automatically.

## Download

Use the latest release from:

https://github.com/Vercadi/conan-exiles-enhanced-manager/releases

## Running From Source

### Prerequisites

- Windows 10/11
- Python 3.12+

### Setup

```bash
pip install -r requirements.txt
python app.py
```

### Run Tests

```bash
python -m pytest -q
```

## Building The Executable

```bash
python -m PyInstaller conan_exiles_enhanced_manager.spec --noconfirm
```

The packaged app stores its working data under `%LOCALAPPDATA%/ConanExilesEnhancedManager/`.

## Hosted Server Notes

Hosted support requires provider file access through SFTP or FTP.

You usually need:

- host or IP
- FTP/SFTP port
- username
- password or private key path
- remote server folder

FTP/SFTP ports are not Conan game, query, or RCON ports. If your provider only exposes a web file panel and does not offer FTP or SFTP access, use the app's provider-panel fallback instructions.

## Safety Model

- Existing `modlist.txt` files are backed up before writes.
- Config and save backups are stored in app-managed backup storage.
- Risky write, upload, restore, and vanilla workflows show previews before applying.
- Hosted secrets are redacted from support diagnostics.
- The app does not store plaintext hosted passwords after saving profiles.

## Project Layout

```text
app.py
requirements.txt
conan_exiles_enhanced_manager.spec
conan_manager/
  core/
  models/
  ui/
  utils/
tests/
```

## Known Limitations

- No automatic Steam Workshop downloads yet.
- No hosted control-panel APIs yet.
- No server config editing yet.
- No automatic hosted restart.
- Windows only.

## License

MIT License. See [LICENSE](LICENSE).

