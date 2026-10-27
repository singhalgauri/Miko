# Installing Miko as a Windows Background Service

> Owner: Person 2  
> Purpose: Instructions and PowerShell script templates for registering Miko as an always-on Windows service  
> Status: Placeholder

---

## 1. Using NSSM (Non-Sucking Service Manager)

1. Download NSSM and extract `nssm.exe`.
2. Open PowerShell as Administrator and run:
   ```powershell
   nssm install MikoBackend "C:\Users\<User>\AppData\Local\Programs\Python\Python311\python.exe" "-m uvicorn app.main:app --host 127.0.0.1 --port 8000"
   nssm set MikoBackend AppDirectory "F:\Miko\backend"
   nssm set MikoBackend Start SERVICE_AUTO_START
   nssm start MikoBackend
   ```

## 2. Using Windows Task Scheduler (Startup Catch-up)

- Create a basic task triggered at user logon.
- Action: Start Program `powershell.exe` with arguments running `scripts/dev.ps1`.
