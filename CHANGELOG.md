# Changelog

All notable changes to ZeroBrave will be documented in this file.

## [1.2.0] - 2026-01-17 (by @vodtinker)

### Added
- **Interactive TUI** with `rich` library - now launches by default!
- Auto-detection: TUI starts automatically in interactive terminals
- 3D ASCII banner with intro/exit animations
- 8 policy categories with toggle controls (keys 1-8)
- **Predefined profiles**: Strict (S), Balanced (B), Minimal (M)
- Contextual help system (? for general, ?1-8 for category-specific)
- Live preview of JSON policies before applying (P)
- Change indicator showing modifications in current session
- `NO_COLOR` environment variable support for accessibility
- New policies: Camera, Microphone, ScreenCapture, BraveTalk

### Changed
- New dependency: `rich>=13.0.0`
- 61 total policies (up from 57)

## [1.1.2] - 2026-01-17 (by @vodtinker)

### Added
- Type validation for known policy configurations (prevents runtime errors)
- Explicit `PermissionError` handling for better error messages
- 5 new unit tests for type validation

### Fixed
- Changed incorrect symbol "X" to "→" in success message
- Corrected `requires-python` from `>=3.8` to `>=3.9` (type hints require 3.9+)
- Fixed `pyproject.toml` entry point for proper package installation
- Fixed `.gitignore` backup pattern (`*.backup` → `*.backup_*`)
- Fixed invalid `CookiesSessionOnlyForUrls` pattern (`[*.]*` → `*`)
- Removed unused `MagicMock` import in tests

## [1.1.0] - 2026-01-16 (by @vodtinker)

### Added
- Full CLI with arguments: `--dry-run`, `--backup`, `--restore`, `--local`
- macOS support
- Backup/restore functionality
- Permission validation (sudo/admin check)
- Brave installation detection
- Comprehensive logging system
- Unit tests (11 tests)

### Changed
- `QuicAllowed` → `true` (better privacy & performance)
- `SafeBrowsingProtectionLevel` → `2` (Enhanced, was incorrectly set to 1)
- `DiskCacheSize` → 100MB (was 1MB, too restrictive)
- `ComponentUpdatesEnabled` → `true` (security)

### Removed
- `CertificateTransparencyEnforcementDisabledForUrls` (security risk)

### Fixed
- JSON comments causing parse errors (JSONC now properly formatted)

## [1.0.0] - Initial Release (by @rompelhd)

### Added
- Basic policy application for Linux and Windows
- Privacy-focused default policies
- AI features disabled (Leo, Gemini, Lens)
- Telemetry completely disabled
- Third-party cookies blocked
