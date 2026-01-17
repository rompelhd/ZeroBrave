# ZeroBrave - Future Roadmap

Ideas and features planned for future versions.

## v1.2.0 - Interactive TUI ✅ COMPLETED

### Terminal User Interface
- [x] Create interactive TUI using `rich`
- [x] TUI launches by default (auto-detection)
- [x] 8 policy categories with toggle controls (1-8)
- [x] Visual preview of changes before applying (P)
- [x] Keyboard navigation with simple commands
- [x] Works over SSH and headless servers
- [x] 3D ASCII banner with animations
- [x] Intro/exit animations
- [x] Predefined profiles: Strict (S), Balanced (B), Minimal (M)
- [x] Contextual help system (? and ?1-8)
- [x] Change indicator
- [x] NO_COLOR environment variable support

### New Policies Added
- [x] Camera access blocked
- [x] Microphone access blocked
- [x] Screen capture blocked
- [x] Brave Talk disabled

### Dependencies
- `rich>=13.0.0` - For styled terminal output

---

## v1.3.0 - Advanced Features (planned)

- [ ] Custom profile saving/loading to JSON
- [ ] Export/import policy configurations
- [ ] Policy diff: compare current vs proposed
- [ ] Undo last change
- [ ] Auto-detect Brave version for compatible policies

## v2.0.0 - Distribution (planned)

- [ ] Publish to PyPI (`pip install zerobrave`)
- [ ] Create AUR package for Arch Linux
- [ ] Create `.deb` package for Debian/Ubuntu
- [ ] Create `.rpm` package for Fedora/RHEL
- [ ] GitHub Actions CI/CD
- [ ] Automatic releases
