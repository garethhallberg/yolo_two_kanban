# Stop local development servers for Kanban application (Windows)

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

# Stop process by port
function Stop-ProcessByPort {
    param(
        [int]$Port,
        [string]$ProcessName
    )
    
    Write-Info "Stopping $ProcessName on port $Port..."
    
    # Find processes using the port
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($processes) {
        foreach ($pid in $processes) {
            try {
                $process = Get-Process -Id $pid -ErrorAction Stop
                Write-Info "  Stopping process: $($process.ProcessName) (PID: $pid)"
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Info "  Process stopped"
            } catch {
                Write-Warning "  Could not stop process $pid: $_"
            }
        }
        Write-Success "$ProcessName stopped"
    } else {
        Write-Info "$ProcessName is not running on port $Port"
    }
}

# Clean up temporary files
function Cleanup-TempFiles {
    Write-Info "Cleaning up temporary files..."
    
    # Remove Python cache files
    Get-ChildItem -Path . -Recurse -Include "__pycache__" -Directory -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Get-ChildItem -Path . -Recurse -Include "*.pyc", "*.pyo", "*.pyd" -File -ErrorAction SilentlyContinue | 
        Remove-Item -Force -ErrorAction SilentlyContinue
    
    # Remove Node.js cache files
    Get-ChildItem -Path . -Recurse -Include ".next" -Directory -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Success "Temporary files cleaned up"
}

# Display stopped information
function Show-StoppedInfo {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "     Kanban Application Stopped" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "All development servers have been stopped." -ForegroundColor White
    Write-Host ""
    Write-Host "Ports freed:" -ForegroundColor White
    Write-Host "  Port 8000: Backend API" -ForegroundColor Gray
    Write-Host "  Port 3000: Frontend" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To start again, run: .\scripts\start-dev.ps1" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution
function Main {
    Write-Info "Stopping Kanban development servers..."
    
    # Stop processes by ports
    Stop-ProcessByPort -Port 8000 -ProcessName "Backend server"
    Stop-ProcessByPort -Port 3000 -ProcessName "Frontend server"
    
    # Also stop any Python uvicorn processes
    $uvicornProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*uvicorn*" }
    
    if ($uvicornProcesses) {
        Write-Info "Stopping remaining uvicorn processes..."
        $uvicornProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    # Also stop any Node.js processes
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    
    if ($nodeProcesses) {
        Write-Info "Stopping remaining Node.js processes..."
        $nodeProcesses | Where-Object { 
            $_.CommandLine -like "*next*" -or 
            $_.CommandLine -like "*dev*" 
        } | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    # Clean up
    Cleanup-TempFiles
    
    # Show information
    Show-StoppedInfo
}

# Run main function
Main