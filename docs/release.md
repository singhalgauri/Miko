# GitHub Release and Test Installers Guide

> Owner: Person 4  
> Purpose: Procedure for packaging, tagging, and attaching pre-built installers to GitHub Releases  
> TODO(person4): Automate release asset bundling via GitHub Actions workflow

---

## 1. Versioning Strategy

Miko follows [Semantic Versioning (SemVer)](https://semver.org/):
- **Alpha / Hackathon Pre-releases:** `v0.1.0-alpha.1`, `v0.1.0-rc.1`
- **Stable Releases:** `v0.1.0`, `v0.2.0`

---

## 2. Building Installers Locally

### Desktop Installers (Tauri)
From the `apps/desktop` directory:
```bash
# Windows (.msi and .exe installer)
npm run tauri build

# macOS (.dmg and .app bundle)
npm run tauri build

# Linux (.deb, .AppImage)
npm run tauri build
```
Built binaries will be located under `apps/desktop/src-tauri/target/release/bundle/`.

### Web Standalone Bundle
```bash
cd apps/web
npm run build
tar -czvf miko-web-bundle.tar.gz dist/
```

---

## 3. Creating a GitHub Release

1. **Tag the Commit:**
   ```bash
   git checkout main
   git pull origin main
   git tag -a v0.1.0-alpha.1 -m "Release v0.1.0-alpha.1: Nebius x NVIDIA Hackathon Preview"
   git push origin v0.1.0-alpha.1
   ```

2. **Draft Release via GitHub CLI or Web UI:**
   ```bash
   gh release create v0.1.0-alpha.1 \
     --title "Miko v0.1.0-alpha.1 (Hackathon Preview)" \
     --notes-file docs/release-notes-template.md \
     --prerelease
   ```

3. **Attach Test Installer Assets:**
   Attach the following compiled assets:
   - `Miko_0.1.0_x64_en-US.msi` (Windows Installer)
   - `Miko_0.1.0_x64.dmg` (macOS Installer)
   - `miko_0.1.0_amd64.AppImage` (Linux Portable)
   - `miko-web-bundle.tar.gz` (Static Web Distribution)

4. **Verify SHA-256 Checksums:**
   Generate and attach `checksums.txt`:
   ```bash
   sha256sum * > checksums.txt
   gh release upload v0.1.0-alpha.1 checksums.txt
   ```
