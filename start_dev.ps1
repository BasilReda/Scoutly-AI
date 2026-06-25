Write-Host "Starting backend servers..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList '-NoExit', '-Command', 'conda activate agentic; python -m backend.mcp_server.server' -WindowStyle Normal

Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList '-NoExit', '-Command', 'conda activate agentic; python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload' -WindowStyle Normal

Write-Host "Both servers launched." -ForegroundColor Green
