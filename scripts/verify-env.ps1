# Frontend Environment Variable Configuration Verification Script
# Verify frontend environment variable configuration

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Frontend Environment Verification" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = Split-Path -Parent $PSScriptRoot
$frontendDir = Join-Path $rootDir "frontend"

# Check project directory
if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Cannot find frontend directory" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Project directory: $rootDir" -ForegroundColor Green
Write-Host ""

# 1. Check .env.example files
Write-Host "1. Check .env.example files..." -ForegroundColor Yellow
$frontendEnvExample = Join-Path $frontendDir ".env.example"
$rootEnvExample = Join-Path $rootDir ".env.example"

if (Test-Path $frontendEnvExample) {
    Write-Host "  [OK] frontend/.env.example exists" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] frontend/.env.example not found" -ForegroundColor Red
}

if (Test-Path $rootEnvExample) {
    Write-Host "  [OK] .env.example exists" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] .env.example not found" -ForegroundColor Red
}
Write-Host ""

# 2. Check .env files
Write-Host "2. Check .env files..." -ForegroundColor Yellow
$frontendEnv = Join-Path $frontendDir ".env"
$rootEnv = Join-Path $rootDir ".env"

if (Test-Path $frontendEnv) {
    Write-Host "  [OK] frontend/.env exists" -ForegroundColor Green
    Write-Host "  Content:" -ForegroundColor Cyan
    Get-Content $frontendEnv | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
} else {
    Write-Host "  [WARN] frontend/.env not found (needed for local dev)" -ForegroundColor Yellow
    Write-Host "     Run: cd frontend && cp .env.example .env" -ForegroundColor White
}
Write-Host ""

if (Test-Path $rootEnv) {
    Write-Host "  [OK] .env exists (for Docker)" -ForegroundColor Green
} else {
    Write-Host "  [WARN] .env not found (needed for Docker)" -ForegroundColor Yellow
    Write-Host "     Run: cp .env.example .env" -ForegroundColor White
}
Write-Host ""

# 3. Check vite.config.ts
Write-Host "3. Check vite.config.ts..." -ForegroundColor Yellow
$viteConfig = Join-Path $frontendDir "vite.config.ts"

if (Test-Path $viteConfig) {
    $content = Get-Content $viteConfig -Raw
    if ($content -match "loadEnv") {
        Write-Host "  [OK] vite.config.ts configured with loadEnv" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] vite.config.ts missing loadEnv" -ForegroundColor Red
    }
} else {
    Write-Host "  [FAIL] vite.config.ts not found" -ForegroundColor Red
}
Write-Host ""

# 4. Check Dockerfile
Write-Host "4. Check Dockerfile..." -ForegroundColor Yellow
$dockerfile = Join-Path $frontendDir "Dockerfile"

if (Test-Path $dockerfile) {
    $content = Get-Content $dockerfile -Raw
    if ($content -match "ARG VITE_API_URL") {
        Write-Host "  [OK] Dockerfile configured with build args" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Dockerfile missing ARG declarations" -ForegroundColor Red
    }
} else {
    Write-Host "  [FAIL] Dockerfile not found" -ForegroundColor Red
}
Write-Host ""

# 5. Check docker-compose.yml
Write-Host "5. Check docker-compose.yml..." -ForegroundColor Yellow
$dockerCompose = Join-Path $rootDir "docker-compose.yml"

if (Test-Path $dockerCompose) {
    $content = Get-Content $dockerCompose -Raw
    if ($content -match "args:") {
        Write-Host "  [OK] docker-compose.yml configured with build args" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] docker-compose.yml missing build args" -ForegroundColor Red
    }
} else {
    Write-Host "  [FAIL] docker-compose.yml not found" -ForegroundColor Red
}
Write-Host ""

# 6. Check port availability
Write-Host "6. Check port availability..." -ForegroundColor Yellow
$ports = @(9101, 8000, 80)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        Write-Host "  [WARN] Port $port is in use" -ForegroundColor Yellow
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "     Process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Gray
        }
    } else {
        Write-Host "  [OK] Port $port is available" -ForegroundColor Green
    }
}
Write-Host ""

# 7. Check Node.js and npm
Write-Host "7. Check development environment..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  [OK] Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Node.js not installed" -ForegroundColor Red
}

try {
    $npmVersion = npm --version 2>&1
    Write-Host "  [OK] npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] npm not installed" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Verification Complete" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start Guide:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Local Development:" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   cp .env.example .env" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Docker Environment:" -ForegroundColor White
Write-Host "   cp .env.example .env" -ForegroundColor Gray
Write-Host "   docker-compose up --build" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation: frontend/ENV_SETUP.md" -ForegroundColor Cyan
Write-Host ""
