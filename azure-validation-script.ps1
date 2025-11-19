<#
.SYNOPSIS
    Script de Validação de Implantação Azure ARM/Bicep
.DESCRIPTION
    Este script automatiza a validação de templates ARM e Bicep no Azure
    com detecção automática de recursos e validação completa
#>

param(
    [string]$ResourceGroupName = "",
    [string]$TemplateFile = "",
    [string]$ParameterFile = "",
    [switch]$Interactive = $true,
    [switch]$ConnectAzure = $true
)

# Configuração de cores para melhor visualização
$Colors = @{
    Success = "Green"
    Warning = "Yellow" 
    Error = "Red"
    Info = "Cyan"
    Default = "White"
}

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] " -NoNewline -ForegroundColor Gray
    Write-Host $Message -ForegroundColor $Colors[$Type]
}

function Test-AzureConnection {
    Write-StatusMessage "Verificando conexão com Azure..." "Info"
    
    try {
        $context = Get-AzContext -ErrorAction Stop
        if ($context) {
            Write-StatusMessage "Conectado ao Azure como: $($context.Account.Id)" "Success"
            Write-StatusMessage "Assinatura: $($context.Subscription.Name) ($($context.Subscription.Id))" "Success"
            return $true
        } else {
            Write-StatusMessage "Não conectado ao Azure" "Warning"
            return $false
        }
    } catch {
        Write-StatusMessage "Erro ao verificar conexão: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Connect-ToAzure {
    Write-StatusMessage "Conectando ao Azure..." "Info"
    
    try {
        Connect-AzAccount -ErrorAction Stop
        Write-StatusMessage "Conexão estabelecida com sucesso!" "Success"
        return $true
    } catch {
        Write-StatusMessage "Erro ao conectar ao Azure: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Get-AzureResourceGroups {
    Write-StatusMessage "Buscando grupos de recursos disponíveis..." "Info"
    
    try {
        $rgs = Get-AzResourceGroup -ErrorAction Stop | Select-Object ResourceGroupName, Location, Tags
        
        if ($rgs.Count -eq 0) {
            Write-StatusMessage "Nenhum grupo de recursos encontrado" "Warning"
            return $null
        }
        
        Write-StatusMessage "Encontrados $($rgs.Count) grupos de recursos" "Success"
        return $rgs
    } catch {
        Write-StatusMessage "Erro ao buscar grupos de recursos: $($_.Exception.Message)" "Error"
        return $null
    }
}

function Select-ResourceGroup {
    param([array]$ResourceGroups)
    
    Write-Host "`nGrupos de Recursos Disponíveis:" -ForegroundColor $Colors.Info
    Write-Host "================================" -ForegroundColor $Colors.Info
    
    for ($i = 0; $i -lt $ResourceGroups.Count; $i++) {
        $rg = $ResourceGroups[$i]
        Write-Host "[$($i+1)] $($rg.ResourceGroupName) - Localização: $($rg.Location)"
    }
    
    Write-Host "[0] Criar novo grupo de recursos" -ForegroundColor $Colors.Warning
    Write-Host "[X] Sair" -ForegroundColor $Colors.Error
    
    $choice = Read-Host "`nSelecione um grupo de recursos (número ou nome)"
    
    if ($choice -eq "X" -or $choice -eq "x") {
        exit
    }
    
    if ($choice -eq "0") {
        return Create-NewResourceGroup
    }
    
    # Verificar se é um número
    if ($choice -match '^\d+$') {
        $index = [int]$choice - 1
        if ($index -ge 0 -and $index -lt $ResourceGroups.Count) {
            return $ResourceGroups[$index].ResourceGroupName
        }
    }
    
    # Verificar se é um nome válido
    $rg = $ResourceGroups | Where-Object { $_.ResourceGroupName -eq $choice }
    if ($rg) {
        return $rg.ResourceGroupName
    }
    
    Write-StatusMessage "Seleção inválida" "Error"
    return $null
}

function Create-NewResourceGroup {
    $name = Read-Host "Nome do novo grupo de recursos"
    $location = Read-Host "Localização (ex: eastus, westeurope, brazilsouth)"
    
    try {
        Write-StatusMessage "Criando grupo de recursos '$name' em '$location'..." "Info"
        $rg = New-AzResourceGroup -Name $name -Location $location -ErrorAction Stop
        Write-StatusMessage "Grupo de recursos criado com sucesso!" "Success"
        return $name
    } catch {
        Write-StatusMessage "Erro ao criar grupo de recursos: $($_.Exception.Message)" "Error"
        return $null
    }
}

function Find-TemplateFiles {
    Write-StatusMessage "Buscando arquivos de template..." "Info"
    
    $templates = @()
    
    # Buscar templates ARM JSON
    $jsonTemplates = Get-ChildItem -Path . -Recurse -Filter "*.json" -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -like "*template*" -or $_.Name -like "*deploy*" -or $_.Name -like "*azure*" }
    
    # Buscar templates Bicep
    $bicepTemplates = Get-ChildItem -Path . -Recurse -Filter "*.bicep" -ErrorAction SilentlyContinue
    
    $templates += $jsonTemplates
    $templates += $bicepTemplates
    
    if ($templates.Count -eq 0) {
        Write-StatusMessage "Nenhum arquivo de template encontrado" "Warning"
        
        # Criar um template de exemplo
        Write-StatusMessage "Criando template de exemplo..." "Info"
        Create-ExampleTemplate
        
        # Buscar novamente
        $templates = Get-ChildItem -Path . -Filter "example-template.json" -ErrorAction SilentlyContinue
    }
    
    Write-StatusMessage "Encontrados $($templates.Count) arquivos de template" "Success"
    return $templates
}

function Create-ExampleTemplate {
    $exampleTemplate = @{
        '$schema' = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
        contentVersion = "1.0.0.0"
        parameters = @{
            storageAccountName = @{
                type = "string"
                defaultValue = "[concat('storage', uniqueString(resourceGroup().id))]"
                metadata = @{
                    description = "Nome da conta de armazenamento"
                }
            }
            location = @{
                type = "string"
                defaultValue = "[resourceGroup().location]"
                metadata = @{
                    description = "Localização dos recursos"
                }
            }
        }
        resources = @(
            @{
                type = "Microsoft.Storage/storageAccounts"
                apiVersion = "2021-04-01"
                name = "[parameters('storageAccountName')]"
                location = "[parameters('location')]"
                sku = @{
                    name = "Standard_LRS"
                }
                kind = "StorageV2"
                properties = @{}
            }
        )
        outputs = @{
            storageAccountName = @{
                type = "string"
                value = "[parameters('storageAccountName')]"
            }
        }
    }
    
    $exampleTemplate | ConvertTo-Json -Depth 10 | Out-File -FilePath "example-template.json" -Encoding UTF8
    Write-StatusMessage "Template de exemplo criado: example-template.json" "Success"
}

function Select-TemplateFile {
    param([array]$Templates)
    
    Write-Host "`nArquivos de Template Disponíveis:" -ForegroundColor $Colors.Info
    Write-Host "=================================" -ForegroundColor $Colors.Info
    
    for ($i = 0; $i -lt $Templates.Count; $i++) {
        $template = $Templates[$i]
        $type = if ($template.Extension -eq ".bicep") { "Bicep" } else { "ARM" }
        Write-Host "[$($i+1)] $($template.Name) ($type) - $($template.DirectoryName)"
    }
    
    Write-Host "[0] Especificar caminho manualmente" -ForegroundColor $Colors.Warning
    Write-Host "[X] Sair" -ForegroundColor $Colors.Error
    
    $choice = Read-Host "`nSelecione um template (número)"
    
    if ($choice -eq "X" -or $choice -eq "x") {
        exit
    }
    
    if ($choice -eq "0") {
        $manualPath = Read-Host "Digite o caminho completo do template"
        if (Test-Path $manualPath) {
            return $manualPath
        } else {
            Write-StatusMessage "Arquivo não encontrado: $manualPath" "Error"
            return $null
        }
    }
    
    if ($choice -match '^\d+$') {
        $index = [int]$choice - 1
        if ($index -ge 0 -and $index -lt $Templates.Count) {
            return $Templates[$index].FullName
        }
    }
    
    Write-StatusMessage "Seleção inválida" "Error"
    return $null
}

function Test-TemplateValidation {
    param(
        [string]$ResourceGroup,
        [string]$TemplatePath,
        [string]$ParameterPath = ""
    )
    
    Write-StatusMessage "Iniciando validação do template..." "Info"
    Write-StatusMessage "Grupo de Recursos: $ResourceGroup" "Info"
    Write-StatusMessage "Template: $TemplatePath" "Info"
    
    if ($ParameterPath) {
        Write-StatusMessage "Parâmetros: $ParameterPath" "Info"
    }
    
    try {
        $validationParams = @{
            ResourceGroupName = $ResourceGroup
            TemplateFile = $TemplatePath
            ErrorAction = "Stop"
        }
        
        if ($ParameterPath -and (Test-Path $ParameterPath)) {
            $validationParams.TemplateParameterFile = $ParameterPath
        }
        
        Write-StatusMessage "Executando validação..." "Info"
        $result = Test-AzResourceGroupDeployment @validationParams
        
        if ($result) {
            Write-StatusMessage "Validação concluída com sucesso!" "Success"
            
            # Analisar detalhes da validação
            if ($result.Code) {
                Write-StatusMessage "Código: $($result.Code)" "Info"
            }
            if ($result.Message) {
                Write-StatusMessage "Mensagem: $($result.Message)" "Info"
            }
            
            return $true
        } else {
            Write-StatusMessage "Template válido - nenhum erro encontrado" "Success"
            return $true
        }
        
    } catch {
        Write-StatusMessage "Erro na validação: $($_.Exception.Message)" "Error"
        
        # Tentar obter mais detalhes do erro
        if ($_.Exception.InnerException) {
            Write-StatusMessage "Detalhes: $($_.Exception.InnerException.Message)" "Error"
        }
        
        return $false
    }
}

function Show-ValidationResults {
    param([bool]$IsValid)
    
    Write-Host "`n" + ("="*50) -ForegroundColor $Colors.Info
    
    if ($IsValid) {
        Write-Host "✅ VALIDAÇÃO BEM-SUCEDIDA!" -ForegroundColor $Colors.Success
        Write-Host "O template pode ser implantado com segurança." -ForegroundColor $Colors.Success
    } else {
        Write-Host "❌ VALIDAÇÃO FALHOU!" -ForegroundColor $Colors.Error
        Write-Host "Corrija os erros antes de prosseguir com a implantação." -ForegroundColor $Colors.Error
    }
    
    Write-Host ("="*50) -ForegroundColor $Colors.Info
}

# ===== FUNÇÃO PRINCIPAL =====
function Main {
    Clear-Host
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║    VALIDADOR DE TEMPLATES AZURE ARM/BICEP v1.0             ║
║                                                              ║
║  Este script valida templates antes da implantação         ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan
    
    # Verificar/Instalar módulos Azure
    Write-StatusMessage "Verificando módulos Azure PowerShell..." "Info"
    
    $requiredModules = @("Az.Accounts", "Az.Resources")
    foreach ($module in $requiredModules) {
        if (!(Get-Module -ListAvailable -Name $module)) {
            Write-StatusMessage "Instalando módulo $module..." "Warning"
            try {
                Install-Module -Name $module -Force -AllowClobber -Scope CurrentUser
                Write-StatusMessage "Módulo $module instalado com sucesso" "Success"
            } catch {
                Write-StatusMessage "Erro ao instalar $module : $($_.Exception.Message)" "Error"
                return
            }
        }
    }
    
    Import-Module Az.Accounts
    Import-Module Az.Resources
    
    # Conectar ao Azure se necessário
    if ($ConnectAzure) {
        $connected = Test-AzureConnection
        if (!$connected) {
            $connected = Connect-ToAzure
            if (!$connected) {
                Write-StatusMessage "Não foi possível conectar ao Azure. Saindo..." "Error"
                return
            }
        }
    }
    
    # Obter ou selecionar grupo de recursos
    $resourceGroup = $ResourceGroupName
    if ([string]::IsNullOrEmpty($resourceGroup)) {
        $rgs = Get-AzureResourceGroups
        if ($rgs) {
            if ($Interactive) {
                $resourceGroup = Select-ResourceGroup -ResourceGroups $rgs
            } else {
                $resourceGroup = $rgs[0].ResourceGroupName
                Write-StatusMessage "Usando grupo de recursos: $resourceGroup" "Info"
            }
        }
        
        if ([string]::IsNullOrEmpty($resourceGroup)) {
            Write-StatusMessage "Nenhum grupo de recursos selecionado. Saindo..." "Error"
            return
        }
    }
    
    # Obter ou selecionar template
    $templatePath = $TemplateFile
    if ([string]::IsNullOrEmpty($templatePath)) {
        $templates = Find-TemplateFiles
        if ($templates) {
            if ($Interactive) {
                $templatePath = Select-TemplateFile -Templates $templates
            } else {
                $templatePath = $templates[0].FullName
                Write-StatusMessage "Usando template: $templatePath" "Info"
            }
        }
        
        if ([string]::IsNullOrEmpty($templatePath)) {
            Write-StatusMessage "Nenhum template selecionado. Saindo..." "Error"
            return
        }
    }
    
    # Verificar se o template existe
    if (!(Test-Path $templatePath)) {
        Write-StatusMessage "Template não encontrado: $templatePath" "Error"
        return
    }
    
    # Validar template
    $isValid = Test-TemplateValidation -ResourceGroup $resourceGroup -TemplatePath $templatePath -ParameterPath $ParameterFile
    
    # Mostrar resultados
    Show-ValidationResults -IsValid $isValid
    
    # Opções adicionais
    if ($Interactive -and $isValid) {
        Write-Host "`nOpções:" -ForegroundColor $Colors.Info
        Write-Host "[1] Implantar template agora" -ForegroundColor $Colors.Success
        Write-Host "[2] Validar outro template" -ForegroundColor $Colors.Info
        Write-Host "[3] Sair" -ForegroundColor $Colors.Default
        
        $choice = Read-Host "`nEscolha uma opção"
        
        switch ($choice) {
            "1" {
                Write-StatusMessage "Para implantar, execute: New-AzResourceGroupDeployment -ResourceGroupName '$resourceGroup' -TemplateFile '$templatePath'" "Info"
            }
            "2" {
                & $PSCommandPath -ResourceGroupName $resourceGroup -Interactive $true
            }
            default {
                Write-StatusMessage "Script concluído. Até logo!" "Success"
            }
        }
    }
}

# Executar script principal
Main