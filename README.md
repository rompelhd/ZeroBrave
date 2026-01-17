# ZeroBrave **v1.2.0**

Privacy-focused policy configurator for **Brave Browser**. Disables telemetry, AI features (Leo), and other privacy-invasive settings automatically.

## Features

- Disables Brave AI (Leo), Gemini, and all generative AI features
- Blocks third-party cookies and Privacy Sandbox
- Disables all telemetry and metrics reporting
- Turns off payment methods and autofill
- Prevents sync and browser sign-in
- Performance optimizations (memory saver, reduced cache)
- Multi-platform support (Linux, Windows, macOS)
- **Interactive TUI with profiles and help system**

## Quick Start

```bash
# Linux/macOS - launches interactive TUI by default
sudo python3 src/main.py

# Windows (Run as Administrator)
python src\main.py
```

Running without arguments automatically launches the interactive TUI:

```
 ███████╗███████╗██████╗  ██████╗ ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗
 ╚══███╔╝██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝
   ███╔╝ █████╗  ██████╔╝██║   ██║██████╔╝██████╔╝███████║██║   ██║█████╗  
  ███╔╝  ██╔══╝  ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  
 ███████╗███████╗██║  ██║╚██████╔╝██████╔╝██║  ██║██║  ██║ ╚████╔╝ ███████╗
 ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝
```

### TUI Commands

| Key | Action |
|-----|--------|
| `1-8` | Toggle policy category |
| `S` | Strict profile (all ON) |
| `B` | Balanced profile |
| `M` | Minimal profile |
| `?` | Help |
| `P` | Preview JSON |
| `ENTER` | Apply policies |
| `Q` | Quit |

## CLI Mode

For scripts and automation, use CLI arguments:

```bash
# Preview changes without applying
python3 src/main.py --dry-run

# Create backup before applying
sudo python3 src/main.py --backup

# Restore previous backup
sudo python3 src/main.py --restore

# Use local policies file
sudo python3 src/main.py --local ./my-policies.json
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Force interactive TUI |
| `-n, --dry-run` | Show what would be done without making changes |
| `-b, --backup` | Create backup of existing policies |
| `-r, --restore` | Restore the most recent backup |
| `-l, --local FILE` | Use a local JSON file instead of downloading |
| `--skip-checks` | Skip permission and installation checks |
| `-q, --quiet` | Suppress non-error output |
| `--debug` | Enable debug logging |
| `-v, --version` | Show version |

## Policy Categories

<details>
<summary><b>AI Features (all disabled)</b></summary>

- `BraveAIChatEnabled`: Leo AI
- `HelpMeWriteSettings`: AI writing assistant
- `GeminiSettings`: Google Gemini integration
- `GenAiDefaultSettings`: General AI features
- `LensOverlaySettings`: Google Lens

</details>

<details>
<summary><b>Privacy</b></summary>

- Third-party cookie blocking
- Privacy Sandbox disabled
- WebRTC IP leak protection
- DNS-over-HTTPS off (set to auto if you don't have a custom DoH/DoQ/DoT server)
- QUIC/HTTP3 enabled (better privacy and performance)
- Certificate Transparency enabled (prevents MITM attacks)

</details>

<details>
<summary><b>Telemetry (all disabled)</b></summary>

- `MetricsReportingEnabled`
- `UrlKeyedAnonymizedDataCollectionEnabled`
- `CloudReportingEnabled`
- All report data settings

</details>

<details>
<summary><b>Permissions (all blocked by default)</b></summary>

- Geolocation
- Notifications  
- Bluetooth
- USB
- File system access
- Sensors
- Serial

</details>

## 📁 Policy Locations

| OS | Path |
|----|------|
| Linux | `/etc/brave/policies/managed/policies.json` |
| Windows | `C:\Program Files\BraveSoftware\Brave-Browser\Application\policy\managed\policies.json` |
| macOS | `~/Library/Application Support/BraveSoftware/Brave-Browser/policies/managed/policies.json` |

## ⚠️ Notes

- **Restart Brave** after applying policies for changes to take effect
- Policies are **enforced** - users cannot override them in browser settings
- Check the [CHANGELOG](CHANGELOG.md) for changes between versions
- You can view applied policies at `brave://policy`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

Apache 2.0 - See [LICENSE](LICENSE) for details.
