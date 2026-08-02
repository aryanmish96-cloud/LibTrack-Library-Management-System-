# autocommit.ps1
$Cwd = "c:\Users\aryan\Downloads\libtrack"
Set-Location $Cwd

$LogFile = Join-Path $Cwd "autocommit.log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] $Message"
    Write-Output $LogMessage
    Out-File -FilePath $LogFile -Append -InputObject $LogMessage -Encoding utf8
}

Write-Log "Auto-commit service started. Monitoring changes..."

while ($true) {
    # Check for unstaged/staged changes (excluding untracked files ignored by gitignore)
    $status = git status --porcelain
    if ($status) {
        Write-Log "Changes detected"
        
        # Add all tracked and new non-ignored files
        git add -A
        
        # Double check if anything got staged
        $stagedStatus = git status --porcelain
        if ($stagedStatus) {
            $date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            git commit -m "Auto-commit: $date"
            
            Write-Log "Pushing changes to GitHub..."
            # Capture stdout and stderr
            $pushResult = git push origin main 2>&1 | Out-String
            Write-Log "Git push output: $pushResult"
            Write-Log "Successfully committed and pushed."
        } else {
            Write-Log "No changes staged to commit."
        }
    }
    # Poll every 10 seconds
    Start-Sleep -Seconds 10
}
