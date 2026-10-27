# Owner: Person 4
# Purpose: Start Miko backend (FastAPI) and frontend (Vite) on Windows PowerShell
# TODO(person4): Add background process monitoring and automatic port conflict check

Write-Host "Starting Miko in development mode (Windows PowerShell)..." -ForegroundColor Cyan

if (-not $env:PROVIDER) {
    $env:PROVIDER = "mock"
}

Write-Host "Active Provider: $env:PROVIDER" -ForegroundColor Green

# Start Backend in a separate process
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -PassThru
Write-Host "Backend process spawned (PID: $($backendJob.Id)) on http://127.0.0.1:8000" -ForegroundColor Yellow

# Start Frontend
Write-Host "Starting Frontend on http://127.0.0.1:5173..." -ForegroundColor Yellow
cd apps/web
npm.cmd run dev
