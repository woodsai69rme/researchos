<# 
.SYNOPSIS
    ResearchOS Windows Installation Script
.DESCRIPTION
    Installs all prerequisites for ResearchOS on Windows 11 including Docker Desktop, WSL2, Python, Node.js, Git, Ollama, and LM Studio.
.NOTES
    Run as Administrator for best results.
    Some components require reboot after installation.
#>

param(
    [switch]$SkipDocker,
    [switch]$SkipWSL2,
    [switch]$SkipPython,
    [switch]$SkipNodeJS,
    [switch]$SkipGit,
    [switch]$SkipOllama,
    [switch]$SkipLMStudio,
    [switch]$SkipResearchOS,
    [string]$InstallPath = "C:\ResearchOS",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-Admin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Chocolatey {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Log "Chocolatey already installed"
        return
    }
    
    Write-Log "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
    Write-Log "Chocolatey installed successfully"
}

function Install-Docker {
    if ($SkipDocker) { Write-Log "Skipping Docker installation"; return }
    
    Write-Log "Installing Docker Desktop..."
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Log "Docker already installed"
        return
    }
    
    choco install docker-desktop -y
    Write-Log "Docker Desktop installed. A reboot may be required."
    Write-Log "After reboot, start Docker Desktop and enable WSL2 integration in Settings."
}

function Install-WSL2 {
    if ($SkipWSL2) { Write-Log "Skipping WSL2 installation"; return }
    
    Write-Log "Installing WSL2..."
    wsl --install -d Ubuntu
    Write-Log "WSL2 installed. A reboot is required."
}

function Install-Python {
    if ($SkipPython) { Write-Log "Skipping Python installation"; return }
    
    Write-Log "Installing Python 3.12..."
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $version = python --version 2>&1
        if ($version -like "*3.12*") {
            Write-Log "Python 3.12 already installed: $version"
            return
        }
    }
    
    choco install python --version=3.12.7 -y
    refreshenv
    Write-Log "Python installed: $(python --version)"
}

function Install-NodeJS {
    if ($SkipNodeJS) { Write-Log "Skipping Node.js installation"; return }
    
    Write-Log "Installing Node.js 20 LTS..."
    if (Get-Command node -ErrorAction SilentlyContinue) {
        $version = node --version
        if ($version -like "v20*") {
            Write-Log "Node.js 20 already installed: $version"
            return
        }
    }
    
    choco install nodejs-lts -y
    refreshenv
    Write-Log "Node.js installed: $(node --version)"
    Write-Log "npm version: $(npm --version)"
}

function Install-Git {
    if ($SkipGit) { Write-Log "Skipping Git installation"; return }
    
    Write-Log "Installing Git..."
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Log "Git already installed: $(git --version)"
        return
    }
    
    choco install git -y
    refreshenv
    Write-Log "Git installed: $(git --version)"
}

function Install-Ollama {
    if ($SkipOllama) { Write-Log "Skipping Ollama installation"; return }
    
    Write-Log "Installing Ollama..."
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Write-Log "Ollama already installed: $(ollama --version)"
        return
    }
    
    choco install ollama -y
    refreshenv
    
    # Start Ollama service
    Write-Log "Starting Ollama service..."
    Start-Service ollama -ErrorAction SilentlyContinue
    Start-Sleep 5
    
    Write-Log "Ollama installed: $(ollama --version)"
    Write-Log "Pulling essential models..."
    ollama pull ornith-1.0-9b:q4_k_m
    ollama pull qwen2.5-coder:latest
    ollama pull phi4-mini:latest
}

function Install-LMStudio {
    if ($SkipLMStudio) { Write-Log "Skipping LM Studio installation"; return }
    
    Write-Log "Installing LM Studio..."
    if (Test-Path "C:\Program Files\LM Studio\LM Studio.exe") {
        Write-Log "LM Studio already installed"
        return
    }
    
    choco install lm-studio -y
    Write-Log "LM Studio installed"
}

function Install-ResearchOS {
    if ($SkipResearchOS) { Write-Log "Skipping ResearchOS installation"; return }
    
    Write-Log "Installing ResearchOS to $InstallPath..."
    
    if (Test-Path $InstallPath) {
        if ($Force) {
            Write-Log "Removing existing installation..."
            Remove-Item $InstallPath -Recurse -Force
        } else {
            Write-Log "ResearchOS already exists at $InstallPath. Use -Force to overwrite."
            return
        }
    }
    
    # Clone repository
    git clone https://github.com/yourusername/ResearchOS.git $InstallPath
    
    # Copy environment file
    Copy-Item "$InstallPath\.env.example" "$InstallPath\.env"
    
    Write-Log "ResearchOS cloned to $InstallPath"
    Write-Log "Edit $InstallPath\.env to add your API keys"
}

function Verify-Installation {
    Write-Log "Verifying installation..."
    
    $checks = @{}
    
    $checks.Docker = (Get-Command docker -ErrorAction SilentlyContinue) -ne $null
    $checks.WSL2 = (wsl --list --verbose 2>$null) -ne $null
    $checks.Python = (Get-Command python -ErrorAction SilentlyContinue) -ne $null
    $checks.NodeJS = (Get-Command node -ErrorAction SilentlyContinue) -ne $null
    $checks.Git = (Get-Command git -ErrorAction SilentlyContinue) -ne $null
    $checks.Ollama = (Get-Command ollama -ErrorAction SilentlyContinue) -ne $null
    $checks.LMStudio = (Test-Path "C:\Program Files\LM Studio\LM Studio.exe")
    $checks.ResearchOS = (Test-Path "$InstallPath\docker-compose.yml")
    
    Write-Log "=== Installation Verification ==="
    foreach ($check in $checks.GetEnumerator()) {
        $status = if ($check.Value) { "✓ PASS" } else { "✗ FAIL" }
        Write-Log "$status - $($check.Name)"
    }
    
    $failed = $checks.Values | Where-Object { -not $_ } | Measure-Object | Select-Object -ExpandProperty Count
    if ($failed -gt 0) {
        Write-Log "$failed component(s) failed verification" "WARN"
    } else {
        Write-Log "All components verified successfully!"
    }
}

function Main {
    Write-Log "=== ResearchOS Windows Installation Started ==="
    Write-Log "Install path: $InstallPath"
    
    if (-not (Test-Admin)) {
        Write-Log "WARNING: Not running as Administrator. Some components may fail to install." "WARN"
    }
    
    # Install Chocolatey first
    Install-Chocolatey
    
    # Install prerequisites
    Install-WSL2
    Install-Docker
    Install-Python
    Install-NodeJS
    Install-Git
    Install-Ollama
    Install-LMStudio
    Install-ResearchOS
    
    # Verify
    Verify-Installation
    
    Write-Log "=== Installation Complete ==="
    Write-Log ""
    Write-Log "Next steps:"
    Write-Log "1. Reboot if prompted (required for WSL2/Docker)"
    Write-Log "2. Start Docker Desktop and enable WSL2 integration"
    Write-Log "3. Edit $InstallPath\.env with your API keys"
    Write-Log "4. Run: cd $InstallPath && .\start.ps1"
    Write-Log ""
    Write-Log "Access URLs after startup:"
    Write-Log "  - Web UI: http://localhost:3000"
    Write-Log "  - API: http://localhost:8000"
    Write-Log "  - API Docs: http://localhost:8000/docs"
}

Main