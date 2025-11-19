$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $scriptDir '..\.env' | Resolve-Path | Select-Object -ExpandProperty Path
$envMap = @{}
Get-Content $envFile | ForEach-Object { if ($_ -match '=') { $k,$v = $_ -split '=',2; $envMap[$k]=$v } }
$glpiUrl = $envMap['GLPI_URL']
$appToken = $envMap['GLPI_APP_TOKEN']
$userToken = $envMap['GLPI_USER_TOKEN']
$headers = @{ 'App-Token'=$appToken; 'Authorization'="user_token $userToken" }
$session = Invoke-RestMethod -Method Post -Uri "$glpiUrl/initSession" -Headers $headers
$st = $session.session_token
$h = @{ 'App-Token'=$appToken; 'Session-Token'=$st }
$isDelId = 45
$dateModId = 19
$idId = 2
$nameId = 1
$contentId = 95

Write-Host "== GLPI validation =="
$urlActive = "$glpiUrl/search/Ticket?is_deleted=0&range=0-49"
if ($isDelId) { $urlActive += "&forcedisplay[]=$isDelId" }
if ($idId) { $urlActive += "&forcedisplay[]=$idId" }
if ($nameId) { $urlActive += "&forcedisplay[]=$nameId" }
$active = Invoke-RestMethod -Method Get -Uri $urlActive -Headers $h
Write-Host ("Active count={0} total={1}" -f $active.count,$active.totalcount)
$hasDeleted = $false
foreach ($row in ($active.data | Select-Object -First 50)) { if ($isDelId -and $row."$isDelId" -eq 1) { $hasDeleted = $true; break } }
Write-Host ("Active response contains is_deleted=1? {0}" -f $hasDeleted)
Write-Host "Sample active IDs and titles:"; ($active.data | Select-Object -First 5 | ForEach-Object { "id=" + $_."$idId" + " title=" + $_."$nameId" })

$urlDeleted = "$glpiUrl/search/Ticket?is_deleted=1&range=0-49"
if ($isDelId) { $urlDeleted += "&forcedisplay[]=$isDelId" }
if ($idId) { $urlDeleted += "&forcedisplay[]=$idId" }
if ($nameId) { $urlDeleted += "&forcedisplay[]=$nameId" }
$deleted = Invoke-RestMethod -Method Get -Uri $urlDeleted -Headers $h
Write-Host ("Deleted count={0} total={1}" -f $deleted.count,$deleted.totalcount)
Write-Host "Sample deleted IDs:"; ($deleted.data | Select-Object -First 5 | ForEach-Object { $_."$idId" })

$urlLatest = "$glpiUrl/search/Ticket?is_deleted=0&range=0-9"
if ($idId) { $urlLatest += "&forcedisplay[]=$idId" }
if ($nameId) { $urlLatest += "&forcedisplay[]=$nameId" }
if ($dateModId) { $urlLatest += "&forcedisplay[]=$dateModId&sort=$dateModId&order=DESC" }
$latest = Invoke-RestMethod -Method Get -Uri $urlLatest -Headers $h
Write-Host "Latest 5 by date_mod:"; ($latest.data | Select-Object -First 5 | ForEach-Object { "id=" + $_."$idId" + " date_mod=" + $_."$dateModId" + " title=" + $_."$nameId" })

Invoke-RestMethod -Method Post -Uri "$glpiUrl/killSession" -Headers $h | Out-Null