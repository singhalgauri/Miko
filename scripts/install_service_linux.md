# Installing Miko as a Linux systemd User Service

> Owner: Person 2  
> Purpose: Instructions for managing Miko via systemd user services  
> Status: Placeholder

---

## 1. Systemd Service Unit

Create `~/.config/systemd/user/miko.service`:

```ini
[Unit]
Description=Miko Local-First AI Agent Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/miko/backend
ExecStart=/usr/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PROVIDER=local
Environment=OLLAMA_HOST=http://127.0.0.1:11434

[Install]
WantedBy=default.target
```

Enable and start the service:
```bash
systemctl --user daemon-reload
systemctl --user enable --now miko.service
systemctl --user status miko.service
```
