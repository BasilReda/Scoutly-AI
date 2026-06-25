# start_podman.ps1

Write-Host "Creating podman network 'football-net'..." -ForegroundColor Cyan
podman network create football-net -d bridge 2>$null

Write-Host "Building MCP image..." -ForegroundColor Cyan
podman build -t football-mcp -f Containerfile.mcp .

Write-Host "Building Backend image..." -ForegroundColor Cyan
podman build -t football-backend -f Containerfile.backend .

Write-Host "Starting MCP server (port 8001)..." -ForegroundColor Cyan
# Remove existing container if it exists
podman rm -f football-mcp 2>$null
podman run -d --name football-mcp --network football-net -p 8001:8001 `
  --dns 8.8.8.8 `
  -v "$PWD/data:/app/data" `
  --env-file .env `
  football-mcp

Write-Host "Starting Backend server (port 8000)..." -ForegroundColor Cyan
# Remove existing container if it exists
podman rm -f football-backend 2>$null
podman run -d --name football-backend --network football-net -p 8000:8000 `
  --dns 8.8.8.8 `
  -v "$PWD/data:/app/data" `
  -v "$PWD/prompts:/app/prompts" `
  -v "$PWD/charts:/app/charts" `
  -v "$PWD/reports:/app/reports" `
  -e MCP_SERVER_HOST="football-mcp" `
  -e MCP_SERVER_PORT="8001" `
  --env-file .env `
  football-backend

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Servers are running in Podman!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000"
Write-Host "MCP Server:  http://localhost:8001"
Write-Host "To view logs: podman logs -f football-backend"
Write-Host "==========================================" -ForegroundColor Green
