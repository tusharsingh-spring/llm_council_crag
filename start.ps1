# LLM Council - Windows Start Script

Write-Host "Starting LLM Council..." -ForegroundColor Green

# Add uv to PATH
$env:Path = "C:\Users\Aryan Shivatare\.local\bin;$env:Path"

# Start backend in background
Write-Host "`nStarting backend on http://localhost:8001..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\llmcouncill; `$env:Path = 'C:\Users\Aryan Shivatare\.local\bin;`$env:Path'; uv run python -m backend.main"

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend..." -ForegroundColor Cyan
cd d:\llmcouncill\frontend
npm run dev -- --host

Write-Host "`nPress Ctrl+C to stop" -ForegroundColor Yellow
