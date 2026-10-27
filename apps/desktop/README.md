# Miko Desktop Shell (Tauri)

> Owner: Person 3  
> Purpose: Native desktop shell wrapping the `apps/web` Vite React build with system tray support  
> Product Name: Miko

---

## Architecture

The desktop application wraps the compiled frontend (`apps/web/dist`) and connects to the background FastAPI server on `127.0.0.1:8000`.

### Supported Platforms
- **Windows:** MSI installer & portable exe
- **macOS:** DMG package & universal app bundle
- **Linux:** AppImage & Debian package

---

## Development & Build

### Prerequisites
- [Rust toolchain](https://www.rust-lang.org/) (`cargo`, `rustc`)
- Platform C++ build tools (Visual Studio C++ build tools on Windows, Xcode on macOS)

### Running in Dev Mode
```bash
cd apps/desktop
npm install
npm run dev
```

### Packaging Production Installers
```bash
npm run build
```
Built binaries are emitted to `src-tauri/target/release/bundle/`.
