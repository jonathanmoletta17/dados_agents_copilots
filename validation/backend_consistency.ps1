$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $scriptDir '..\.env' | Resolve-Path | Select-Object -ExpandProperty Path
$envMap = @{}
Get-Content $envFile | ForEach-Object { if ($_ -match '=') { $k,$v = $_ -split '=',2; $envMap[$k]=$v } }
$glpiUrl = $envMap['GLPI_URL']
$appToken = $envMap['GLPI_APP_TOKEN']
$userToken = $envMap['GLPI_USER_TOKEN']
$base = 'http://127.0.0.1:8099'

$headers = @{ 'App-Token'=$appToken; 'Authorization'="user_token $userToken" }
$session = Invoke-RestMethod -Method Post -Uri "$glpiUrl/initSession" -Headers $headers
$st = $session.session_token
$h = @{ 'App-Token'=$appToken; 'Session-Token'=$st }

$latest = Invoke-RestMethod -Method Get -Uri ("$glpiUrl/search/Ticket?is_deleted=0&range=0-19&forcedisplay[]=2&forcedisplay[]=19&sort=19&order=DESC") -Headers $h
$latestIds = @($latest.data | Select-Object -First 10 | ForEach-Object { $_.'2' })
$deleted = Invoke-RestMethod -Method Get -Uri ("$glpiUrl/search/Ticket?is_deleted=1&range=0-199") -Headers $h
$deletedIds = @($deleted.data | ForEach-Object { $_.id })

$backendRows = Invoke-RestMethod -Method Get -Uri ("$base/search?q=&size=50&sort=recent")
$backendIds = @($backendRows | ForEach-Object { $_.id })

$overlapDel = $backendIds | Where-Object { $_ -in $deletedIds }
$presentLatest = $latestIds | Where-Object { $_ -in $backendIds }

Write-Host "Backend rows: $($backendIds.Count)"
Write-Host "Deleted overlap: $($overlapDel.Count)"
Write-Host "Latest present in backend: $($presentLatest.Count) of $($latestIds.Count)"

$sample = $backendIds | Select-Object -First 5
foreach ($id in $sample) {
  $check = Invoke-RestMethod -Method Get -Uri ("$glpiUrl/Ticket/$id") -Headers $h
  Write-Host ("id={0} is_deleted={1} status={2}" -f $id, $check.is_deleted, $check.status)
}

Invoke-RestMethod -Method Post -Uri "$glpiUrl/killSession" -Headers $h | Out-Null