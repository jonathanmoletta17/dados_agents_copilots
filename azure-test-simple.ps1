<#
.SYNOPSIS
    Script de Teste Azure - Validação de Conexão e Recursos
.DESCRIPTION
    Este script testa a conexão com Azure e demonstra comandos de validação
    sem necessidade de instalação de módulos grandes
#>

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    TESTE DE CONEXÃO E VALIDAÇÃO AZURE                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. Verificar se Azure CLI está instalado
Write-Host "`n1. Verificando Azure CLI..." -ForegroundColor Yellow
$azCli = Get-Command az -ErrorAction SilentlyContinue
if ($azCli) {
    Write-Host "✅ Azure CLI encontrado: $($azCli.Source)" -ForegroundColor Green
    
    # Testar versão
    Write-Host "`n2. Versão do Azure CLI:" -ForegroundColor Yellow
    & az --version | Select-Object -First 1
} else {
    Write-Host "❌ Azure CLI não encontrado" -ForegroundColor Red
    Write-Host "Por favor, instale o Azure CLI em: https://aka.ms/installazurecliwindows" -ForegroundColor Red
}

# 2. Verificar PowerShell Modules
Write-Host "`n3. Verificando módulos Azure PowerShell..." -ForegroundColor Yellow
$azModules = Get-Module -ListAvailable -Name Az* | Select-Object Name, Version | Sort-Object Name
if ($azModules) {
    Write-Host "✅ Módulos Azure PowerShell encontrados:" -ForegroundColor Green
    $azModules | Format-Table -AutoSize
} else {
    Write-Host "❌ Nenhum módulo Azure PowerShell encontrado" -ForegroundColor Red
    Write-Host "Para instalar, execute: Install-Module -Name Az -Force -AllowClobber -Scope CurrentUser" -ForegroundColor Yellow
}

# 3. Comandos de Validação que podem ser executados
Write-Host "`n4. Comandos de Validação Disponíveis:" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Yellow

$commands = @(
    @{
        Name = "Testar Login Azure"
        Command = "az login"
        Description = "Conectar ao Azure via CLI"
    },
    @{
        Name = "Listar Assinaturas"
        Command = "az account list"
        Description = "Mostrar todas as assinaturas disponíveis"
    },
    @{
        Name = "Listar Grupos de Recursos"
        Command = "az group list"
        Description = "Mostrar todos os grupos de recursos"
    },
    @{
        Name = "Validar Template ARM (exemplo)"
        Command = "az deployment group validate --resource-group NOME_DO_GRUPO --template-file TEMPLATE.json"
        Description = "Validar um template ARM antes da implantação"
    },
    @{
        Name = "Validar Template Bicep (exemplo)"
        Command = "az deployment group validate --resource-group NOME_DO_GRUPO --template-file TEMPLATE.bicep"
        Description = "Validar um template Bicep antes da implantação"
    }
)

foreach ($cmd in $commands) {
    Write-Host "`n📋 $($cmd.Name)" -ForegroundColor Cyan
    Write-Host "   Comando: $($cmd.Command)" -ForegroundColor White
    Write-Host "   Descrição: $($cmd.Description)" -ForegroundColor Gray
}

# 4. Criar template de exemplo para teste
Write-Host "`n5. Criando template de exemplo para testes..." -ForegroundColor Yellow

$exampleTemplate = @"
{
    "`$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "storageAccountName": {
            "type": "string",
            "defaultValue": "[concat('storage', uniqueString(resourceGroup().id))]",
            "metadata": {
                "description": "Nome da conta de armazenamento"
            }
        },
        "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Localização dos recursos"
            }
        }
    },
    "resources": [
        {
            "type": "Microsoft.Storage/storageAccounts",
            "apiVersion": "2021-04-01",
            "name": "[parameters('storageAccountName')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "Standard_LRS"
            },
            "kind": "StorageV2",
            "properties": {}
        }
    ],
    "outputs": {
        "storageAccountName": {
            "type": "string",
            "value": "[parameters('storageAccountName')]"
        }
    }
}
"@

$templatePath = "test-template.json"
$exampleTemplate | Out-File -FilePath $templatePath -Encoding UTF8
Write-Host "✅ Template de exemplo criado: $templatePath" -ForegroundColor Green

# 5. Instruções para teste
Write-Host "`n6. Próximos Passos:" -ForegroundColor Yellow
Write-Host "===================" -ForegroundColor Yellow
Write-Host "1. Conecte-se ao Azure: az login" -ForegroundColor White
Write-Host "2. Liste seus grupos de recursos: az group list" -ForegroundColor White
Write-Host "3. Crie um grupo de recursos para teste: az group create --name TestRG --location eastus" -ForegroundColor White
Write-Host "4. Valide o template: az deployment group validate --resource-group TestRG --template-file test-template.json" -ForegroundColor White
Write-Host "5. Se a validação passar, implante: az deployment group create --resource-group TestRG --template-file test-template.json" -ForegroundColor White

Write-Host "`n✨ Script concluído! Use os comandos acima para testar sua conexão com Azure." -ForegroundColor Green