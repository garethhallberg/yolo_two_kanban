# Start local development servers for Kanban application (Windows)

# Colors for output
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if required commands are available
function Test-Requirements {
    $missingCommands = @()
    
    # Check for Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        $missingCommands += "python"
    }
    
    # Check for Node.js
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        $missingCommands += "node"
    }
    
    # Check for npm
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        $missingCommands += "npm"
    }
    
    if ($missingCommands.Count -gt 0) {
        Write-Error "Missing required commands: $($missingCommands -join ', ')"
        Write-Info "Please install the missing dependencies and try again."
        exit 1
    }
    
    Write-Success "All requirements satisfied"
}

# Start backend server
function Start-Backend {
    Write-Info "Starting backend server..."
    
    # Check if backend is already running
    $backendProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*uvicorn*" -and $_.CommandLine -like "*8000*" }
    
    if ($backendProcess) {
        Write-Warning "Backend is already running on port 8000"
        return $backendProcess.Id
    }
    
    # Navigate to backend directory
    Set-Location backend
    
    # Install Python dependencies if needed
    if (-not (Test-Path ".venv") -and (Test-Path "pyproject.toml")) {
        Write-Info "Setting up Python virtual environment..."
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1
        pip install --upgrade pip
        pip install -e .
    } else {
        .\.venv\Scripts\Activate.ps1 -ErrorAction SilentlyContinue
    }
    
    # Start backend server
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        .\.venv\Scripts\Activate.ps1
        uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    }
    
    # Wait for backend to start
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "Backend server started successfully"
                return $backendJob.Id
            }
        } catch {
            # Continue waiting
        }
        
        Write-Info "Waiting for backend to start... (attempt $attempt/$maxAttempts)"
        Start-Sleep -Seconds 1
        $attempt++
    }
    
    Write-Error "Backend failed to start"
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

# Start frontend server
function Start-Frontend {
    Write-Info "Starting frontend server..."
    
    # Check if frontend is already running
    $frontendProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*next*" -or $_.CommandLine -like "*3000*" }
    
    if ($frontendProcess) {
        Write-Warning "Frontend is already running on port 3000"
        return $frontendProcess.Id
    }
    
    # Navigate to frontend directory
    Set-Location ../frontend
    
    # Install Node.js dependencies if needed
    if (-not (Test-Path "node_modules") -and (Test-Path "package.json")) {
        Write-Info "Installing Node.js dependencies..."
        npm install
    }
    
    # Start frontend server
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npm run dev
    }
    
    # Wait for frontend to start
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Success "Frontend server started successfully"
                return $frontendJob.Id
            }
        } catch {
            # Continue waiting
        }
        
        Write-Info "Waiting for frontend to start... (attempt $attempt/$maxAttempts)"
        Start-Sleep -Seconds 1
        $attempt++
    }
    
    Write-Warning "Frontend is taking longer than expected to start"
    return $frontendJob.Id
}

# Display startup information
function Show-Info {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "     Kanban Application Started" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Backend API:" -ForegroundColor White
    Write-Host "  URL:      http://localhost:8000" -ForegroundColor Gray
    Write-Host "  Health:   http://localhost:8000/api/health" -ForegroundColor Gray
    Write-Host "  Docs:     http://localhost:8000/api/docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Frontend:" -ForegroundColor White
    Write-Host "  URL:      http://localhost:3000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "API Endpoints:" -ForegroundColor White
    Write-Host "  Hello:    http://localhost:8000/api/hello" -ForegroundColor Gray
    Write-Host "  Echo:     http://localhost:8000/api/hello/echo/{message}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop the servers, run: .\scripts\stop-dev.ps1" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution
function Main {
    Write-Info "Starting Kanban application in development mode..."
    
    # Check requirements
    Test-Requirements
    
    # Store current directory
    $originalLocation = Get-Location
    
    try {
        # Start servers
        $backendJobId = Start-Backend
        Set-Location $originalLocation
        $frontendJobId = Start-Frontend
        
        # Show information
        Show-Info
        
        # Keep script running
        Write-Info "Press Ctrl+C to stop all servers"
        Write-Host ""
        
        # Wait for user to press Ctrl+C
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        # Cleanup on exit
        Set-Location $originalLocation
        Write-Info "Cleaning up..."
        
        if ($backendJobId) {
            Stop-Job $backendJobId -ErrorAction SilentlyContinue
        }
        
        if ($frontendJobId) {
            Stop-Job $frontendJobId -ErrorAction SilentlyContinue
        }
        
        Write-Success "All servers stopped"
    }
}

# Run main function
Main