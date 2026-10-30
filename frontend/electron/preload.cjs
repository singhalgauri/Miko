const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("agent", {
  setMode: (mode) => ipcRenderer.send("set-mode", mode),
}); 