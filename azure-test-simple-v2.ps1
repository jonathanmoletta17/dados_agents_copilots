# Script de Teste Azure - Validação de Conexão e Recursos
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

Write-Host "`n📋 Testar Login Azure" -ForegroundColor Cyan
Write-Host "   Comando: az login" -ForegroundColor White
Write-Host "   Descrição: Conectar ao Azure via CLI" -ForegroundColor Gray

Write-Host "`n📋 Listar Assinaturas" -ForegroundColor Cyan
Write-Host "   Comando: az account list" -ForegroundColor White
Write-Host "   Descrição: Mostrar todas as assinaturas disponíveis" -ForegroundColor Gray

Write-Host "`n📋 Listar Grupos de Recursos" -ForegroundColor Cyan
Write-Host "   Comando: az group list" -ForegroundColor White
Write-Host "   Descrição: Mostrar todos os grupos de recursos" -ForegroundColor Gray

Write-Host "`n📋 Validar Template ARM (exemplo)" -ForegroundColor Cyan
Write-Host "   Comando: az deployment group validate --resource-group NOME_DO_GRUPO --template-file TEMPLATE.json" -ForegroundColor White
Write-Host "   Descrição: Validar um template ARM antes da implantação" -ForegroundColor Gray

Write-Host "`n📋 Validar Template Bicep (exemplo)" -ForegroundColor Cyan
Write-Host "   Comando: az deployment group validate --resource-group NOME_DO_GRUPO --template-file TEMPLATE.bicep" -ForegroundColor White
Write-Host "   Descrição: Validar um template Bicep antes da implantação" -ForegroundColor Gray

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