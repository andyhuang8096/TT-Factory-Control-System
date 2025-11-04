# Create Pull Request using GitHub API
# Requires GitHub Personal Access Token

param(
    [string]$GitHubToken = "",
    [string]$RepoOwner = "andyhuang8096",
    [string]$RepoName = "TT_PPID_CS",
    [string]$BaseBranch = "main",
    [string]$HeadBranch = "feature/ppid-migration-complete",
    [string]$Title = "feat: Complete DPK to PPID migration and related tool scripts",
    [string]$Body = ""
)

# If no token provided, try to get from environment variable
if ([string]::IsNullOrEmpty($GitHubToken)) {
    $GitHubToken = $env:GITHUB_TOKEN
}

if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Host "Error: GitHub Personal Access Token required" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please choose one of the following:" -ForegroundColor Yellow
    Write-Host "1. Set environment variable: `$env:GITHUB_TOKEN = 'your_token'" -ForegroundColor Cyan
    Write-Host "2. Run script with parameter: .\create_pr.ps1 -GitHubToken 'your_token'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "How to create GitHub Token:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "2. Click 'Generate new token' -> 'Generate new token (classic)'" -ForegroundColor Cyan
    Write-Host "3. Select scopes: repo (need repo permission)" -ForegroundColor Cyan
    Write-Host "4. Generate and copy token" -ForegroundColor Cyan
    exit 1
}

# If no Body provided, use default content
if ([string]::IsNullOrEmpty($Body)) {
    $Body = @"
## Changes

- Migrated all DPK references to PPID
  - Updated data model: DPKRecord -> PPIDRecord
  - Updated database table names and SQL statements
  - Updated UI display text
  - Updated all scripts and configuration files
  - Updated documentation

- Database migration scripts
  - Created migrate_dpk_to_ppid.py for table migration
  - Created migrate_dpk_to_ppid.sql SQL migration script

- Added GitHub push helper tools
  - PowerShell script
  - Bash script
  - Push guide documentation

## Testing

- [x] Database migration script tested
- [x] Database connection tested
- [x] All tables created/migrated correctly

## Related Changes

- Code updates: 69 files, 7417 lines of code
- Database migration: DPKRecord -> PPIDRecord
- UI updates: All DPK related display text updated to PPID
"@
}

# API endpoint
$apiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/pulls"

# Request body
$requestBody = @{
    title = $Title
    body = $Body
    head = $HeadBranch
    base = $BaseBranch
} | ConvertTo-Json

# Request headers
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Accept" = "application/vnd.github.v3+json"
    "User-Agent" = "PowerShell"
}

Write-Host "Creating Pull Request..." -ForegroundColor Cyan
Write-Host "  Repository: $RepoOwner/$RepoName" -ForegroundColor Gray
Write-Host "  From: $HeadBranch" -ForegroundColor Gray
Write-Host "  To: $BaseBranch" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $requestBody -ContentType "application/json"
    
    Write-Host "Pull Request created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "PR Link: $($response.html_url)" -ForegroundColor Cyan
    Write-Host "PR Number: #$($response.number)" -ForegroundColor Cyan
    Write-Host "Status: $($response.state)" -ForegroundColor Cyan
    
    # Open browser
    Write-Host ""
    $openBrowser = Read-Host "Open PR in browser? (Y/N)"
    if ($openBrowser -eq "Y" -or $openBrowser -eq "y") {
        Start-Process $response.html_url
    }
    
} catch {
    Write-Host "Failed to create Pull Request" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "Details: $($errorDetails.message)" -ForegroundColor Red
    }
    
    exit 1
}

