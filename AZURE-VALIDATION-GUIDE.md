# GUIA COMPLETO: Validação de Implantação Azure com PowerShell

## 📋 VISÃO GERAL
Este guia demonstra como usar PowerShell para validar templates ARM/Bicep antes da implantação no Azure.

## 🔧 PRÉ-REQUISITOS

### 1. Azure CLI (Recomendado)
```powershell
# Verificar se Azure CLI está instalado
az --version

# Se não estiver instalado, baixe em: https://aka.ms/installazurecliwindows
```

### 2. Azure PowerShell Module (Opcional, mas útil)
```powershell
# Instalar módulo Azure PowerShell
Install-Module -Name Az -Force -AllowClobber -Scope CurrentUser

# Importar módulos
Import-Module Az.Accounts
Import-Module Az.Resources
```

## 🔐 CONEXÃO COM AZURE

### Opção 1: Azure CLI (Mais Rápido)
```powershell
# Conectar ao Azure
az login

# Listar assinaturas
az account list --output table

# Selecionar assinatura (se necessário)
az account set --subscription "NOME_DA_ASSINATURA"
```

### Opção 2: Azure PowerShell
```powershell
# Conectar ao Azure
Connect-AzAccount

# Verificar contexto atual
Get-AzContext
```

## 📁 GESTÃO DE GRUPOS DE RECURSOS

### Listar Grupos de Recursos Existentes
```powershell
# Azure CLI
az group list --output table

# Azure PowerShell
Get-AzResourceGroup | Select-Object ResourceGroupName, Location | Format-Table
```

### Criar Novo Grupo de Recursos
```powershell
# Azure CLI
az group create --name MeuGrupoDeTeste --location eastus

# Azure PowerShell
New-AzResourceGroup -Name "MeuGrupoDeTeste" -Location "eastus"
```

## 🔍 VALIDAÇÃO DE TEMPLATES

### Template ARM (JSON)
```powershell
# Validar template ARM
az deployment group validate `
  --resource-group MeuGrupoDeTeste `
  --template-file template.json `
  --parameters @params.json

# PowerShell equivalente
Test-AzResourceGroupDeployment `
  -ResourceGroupName "MeuGrupoDeTeste" `
  -TemplateFile "template.json" `
  -TemplateParameterFile "params.json"
```

### Template Bicep
```powershell
# Validar template Bicep
az deployment group validate `
  --resource-group MeuGrupoDeTeste `
  --template-file template.bicep

# PowerShell equivalente (requer módulo Bicep)
Test-AzResourceGroupDeployment `
  -ResourceGroupName "MeuGrupoDeTeste" `
  -TemplateFile "template.bicep"
```

### Validação com Parâmetros Inline
```powershell
# Azure CLI
az deployment group validate `
  --resource-group MeuGrupoDeTeste `
  --template-file template.json `
  --parameters storageAccountName=mystorageaccount location=eastus

# PowerShell
Test-AzResourceGroupDeployment `
  -ResourceGroupName "MeuGrupoDeTeste" `
  -TemplateFile "template.json" `
  -storageAccountName "mystorageaccount" `
  -location "eastus"
```

## 🚨 TRATAMENTO DE ERROS

### Verificar Logs de Validação
```powershell
# Azure CLI com saída detalhada
az deployment group validate `
  --resource-group MeuGrupoDeTeste `
  --template-file template.json `
  --debug

# Capturar erros em variável
$validation = az deployment group validate `
  --resource-group MeuGrupoDeTeste `
  --template-file template.json | ConvertFrom-Json

if ($validation.error) {
    Write-Host "Erro: $($validation.error.message)" -ForegroundColor Red
    Write-Host "Código: $($validation.error.code)" -ForegroundColor Red
}
```

## 📊 COMANDOS ÚTEIS ADICIONAIS

### Verificar Implantações Anteriores
```powershell
# Listar implantações recentes
az deployment group list --resource-group MeuGrupoDeTeste --output table

# Ver detalhes de uma implantação específica
az deployment group show `
  --resource-group MeuGrupoDeTeste `
  --name NomeDaImplantacao

# Ver operações de uma implantação
az deployment operation group list `
  --resource-group MeuGrupoDeTeste `
  --name NomeDaImplantacao
```

### Testar Conectividade
```powershell
# Verificar se pode acessar Azure Resource Manager
Test-NetConnection -ComputerName management.azure.com -Port 443

# Verificar endpoints do Azure
az cloud list --output table
```

## 📝 EXEMPLO COMPLETO DE SCRIPT

```powershell
# Script de Validação Completo
param(
    [string]$ResourceGroupName = "TestRG",
    [string]$TemplateFile = "template.json",
    [string]$Location = "eastus"
)

# Conectar ao Azure
Write-Host "Conectando ao Azure..."
az login

# Criar grupo de recursos se não existir
$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq "false") {
    Write-Host "Criando grupo de recursos $ResourceGroupName..."
    az group create --name $ResourceGroupName --location $Location
}

# Validar template
Write-Host "Validando template $TemplateFile..."
$validation = az deployment group validate `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile | ConvertFrom-Json

if ($validation.error) {
    Write-Host "VALIDAÇÃO FALHOU!" -ForegroundColor Red
    Write-Host "Erro: $($validation.error.message)" -ForegroundColor Red
    exit 1
} else {
    Write-Host "VALIDAÇÃO BEM-SUCEDIDA!" -ForegroundColor Green
    Write-Host "Template pode ser implantado com segurança." -ForegroundColor Green
}
```

## 🎯 COMANDOS PARA TESTAR AGORA

1. **Verificar Azure CLI**: `az --version`
2. **Conectar ao Azure**: `az login`
3. **Listar assinaturas**: `az account list`
4. **Criar grupo de teste**: `az group create --name TestRG --location eastus`
5. **Testar validação**: Use o template `test-template.json` criado anteriormente

## 📚 RECURSOS ADICIONAIS

- [Documentação Azure CLI](https://docs.microsoft.com/cli/azure/)
- [Templates ARM Reference](https://docs.microsoft.com/azure/templates/)
- [Azure PowerShell Reference](https://docs.microsoft.com/powershell/azure/)
- [Bicep Documentation](https://docs.microsoft.com/azure/azure-resource-manager/bicep/)

## ⚡ DICAS RÁPIDAS

- Use `--debug` para mais detalhes em erros
- Use `--what-if` para pré-visualizar mudanças antes da implantação
- Valide sempre antes de implantar em produção
- Mantenha templates em controle de versão (Git)
- Use grupos de recursos separados para teste e produção