const { app, BrowserWindow, screen, Tray, Menu, nativeImage, ipcMain } = require("electron");
const path = require("path");

const ICON =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAC1ElEQVR42uWbS2/bMAzHScOftUnXHrquw3bYmgfaJrk0yTpg26dlD4ET2ZViPfjwHF4SIQ6gHyn+RUow/rglIDgZIbQsMKbE56PGBABQNsbU/9cJ8MQJKwAPgE5gIp1RR0yOuGGF4EPOwHPPVyOFd8cU+v2QAoo5bgDfjKmbFg1gdQHwH9LiCIiOAyRhBwIPXXifBtAFwJM7ri4M/qgJ5zRg9MvepwFmRc7rxgyeYuoA8ciDUeR9GqAO/7o5fG7XNvDNCrBrbMAu8k0aVEMQPLCBBxENyIIHG3h2DUiZbJP3je1W+vCsdUBp5MEAnq0XyIoc8KRBCTyLBuTA79Z+8P2LLnyxBpRuXSVpwAFfpAEi8KALn60BJfC71XnwX8968FkaIB15UIRP1gCWchXy0kACPkkDuFvWIcBHawAX/P4lDv7tSQc+SgO0I/9hFQivBHz4QiQJv19Bsd08yjmj5QAO+B0DcJ9dz/icUXPAb9egan8Wp+/TeZkz6hz47QYGY3/n7fFkkeaMOuX09n+wf7PT96tlvzPq2Mh//hY+zBiSTZYZGpCa83ff22MN4QsCL/I1gAAA7x+IOPf52GKnxKaLcvU/boP3X4kkr6fenhm2vTlvHeAWPkcHaNzV/X5K3OsFKkDqdJ2VxcVlSkssCX9ohxXhb37GL3kN+EMzpH1FbdAIheBb5wGaV9RDgVfRgFR4UIQX1wDf5D499uzxcz14UQ3om6x15EU1IBsedOFFNCBmstezcImrCc+uAamTt4w8uwaUwoMBPJsG5ERuWniSwwHPogGlRYtV5F0NQHN4sIEHAKys4MkePl8DuOAnS+fw0gDe1QBUj3yGBjDDY3IdIHE9FXN0LRF5Xx2A2vBWy54cyq4G4CXBR9UBI4OP6gVwxPDY/b0ORB59LxiNZdn31gHOZHDM8N67Qc/kEAIvHQ4cHmOerxMED7svHA0QHlP//w69hPESjp7DkAAAAABJRU5ErkJggg==";

const SIDE_WIDTH = 420;
let win;
let tray;

function goFull() {
  win.setAlwaysOnTop(false);
  win.maximize();
  win.focus();
}

function goSide() {
  const { workArea } = screen.getPrimaryDisplay();
  win.unmaximize();
  win.setBounds({
    x: workArea.x + workArea.width - SIDE_WIDTH,
    y: workArea.y,
    width: SIDE_WIDTH,
    height: workArea.height,
  });
  win.setAlwaysOnTop(true);
  win.focus();
}

function createWindow() {
  win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 360,
    autoHideMenuBar: true,
    title: "Sovereign Agent",
    backgroundColor: "#0f1424",
    icon: nativeImage.createFromDataURL(ICON),
    webPreferences: { preload: path.join(__dirname, "preload.cjs") },
  });

  win.on("page-title-updated", (e) => e.preventDefault());
    if (app.isPackaged) {
    win.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  } else {
    win.loadURL("http://localhost:5173");
  }
  win.maximize();
}

function createTray() {
  tray = new Tray(nativeImage.createFromDataURL(ICON).resize({ width: 16, height: 16 }));
  tray.setToolTip("Sovereign Agent");
  tray.setContextMenu(
    Menu.buildFromTemplate([
      { label: "Open full screen", click: () => { win.show(); goFull(); } },
      { label: "Dock to the side", click: () => { win.show(); goSide(); } },
      { type: "separator" },
      { label: "Quit", click: () => app.quit() },
    ])
  );
  tray.on("click", () => { win.show(); win.focus(); });
}

ipcMain.on("set-mode", (_event, mode) => {
  if (mode === "side") goSide();
  else goFull();
});

app.whenReady().then(() => {
  createWindow();
  createTray();
});

app.on("window-all-closed", () => app.quit());