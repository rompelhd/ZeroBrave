# Changelog

All notable changes to ZeroBrave will be documented in this file.

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
