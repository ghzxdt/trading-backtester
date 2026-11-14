# Weekly trade simulation, run by the Windows scheduled task "Trading Backtester Weekly Run" (Saturdays 10:00 AM,
# or at the next sign-in if the laptop was off). It keeps exports/trade_simulation.json fresh for the research
# app, which cautions after 10 days and stops using the evidence after 45.
#
# Runs run_trades.py with the registered settings, then commits only the files a run writes (trial record,
# holdout ledger, report, export, trade list) and pushes main. Code changes in progress are never committed; if
# there are any, the run's record says "+dirty". Everything is logged to work\weekly_run.log.
$ErrorActionPreference = 'Continue'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $here '..\trading-research\.venv\Scripts\python.exe'
$git = 'C:\Program Files\Git\cmd\git.exe'
$log = Join-Path $here 'work\weekly_run.log'
New-Item -ItemType Directory -Force (Join-Path $here 'work') | Out-Null
if ((Test-Path $log) -and (Get-Item $log).Length -gt 512KB) { Move-Item -Force $log "$log.old" }

function Write-Log([string]$text) {
    Add-Content -Path $log -Encoding utf8 -Value ("{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $text)
}

function Invoke-Logged([string]$exe, [string[]]$arguments) {
    # Native output goes to the log line by line; returns the exit code.
    $output = & $exe @arguments 2>&1
    foreach ($line in $output) { Write-Log ("    " + $line) }
    return $LASTEXITCODE
}

Set-Location $here
$env:Path = 'C:\Program Files\Git\cmd;' + $env:Path  # so the run can name its commit
Write-Log 'Weekly trade simulation starting.'

$code = Invoke-Logged $python @('-B', 'run_trades.py')
if ($code -ne 0) {
    Write-Log "run_trades.py failed (exit $code); nothing committed."
    exit $code
}

$results = @('trials.jsonl', 'holdout_ledger.jsonl', 'exports', 'reports')
Invoke-Logged $git (@('add', '--') + $results) | Out-Null
& $git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Log 'Nothing new to commit.'
    exit 0
}
$message = "Weekly trade simulation, {0:yyyy-MM-dd}`n`nAutomatic run by run_weekly.ps1 (scheduled task 'Trading Backtester Weekly Run')." -f (Get-Date)
$code = Invoke-Logged $git @('commit', '-q', '-m', $message)
if ($code -ne 0) { Write-Log "git commit failed (exit $code)."; exit $code }
$code = Invoke-Logged $git @('push', '-q', 'origin', 'main')
if ($code -ne 0) { Write-Log "git push failed (exit $code); the commit is saved locally and goes up with the next push."; exit $code }
Write-Log 'Committed and pushed.'
exit 0
