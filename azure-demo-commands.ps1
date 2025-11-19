# DEMONSTRAÇÃO: Comandos de Validação Azure (Sem Instalação)
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "    DEMONSTRAÇÃO DE COMANDOS AZURE PARA VALIDAÇÃO          " -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

Write-Host "`n⚠️  AZURE CLI NÃO ENCONTRADO!" -ForegroundColor Yellow
Write-Host "Por favor, instale o Azure CLI primeiro:" -ForegroundColor Yellow
Write-Host "https://aka.ms/installazurecliwindows" -ForegroundColor Cyan

Write-Host "`n📋 PASSO A PASSO PARA VALIDAÇÃO DE TEMPLATES:" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green

# Passo 1: Instalação
Write-Host "`n1️⃣ INSTALAÇÃO DO AZURE CLI:" -ForegroundColor Cyan
Write-Host "   - Acesse: https://aka.ms/installazurecliwindows" -ForegroundColor White
Write-Host "   - Baixe e execute o instalador" -ForegroundColor White
Write-Host "   - Reinicie o PowerShell após instalação" -ForegroundColor White

# Passo 2: Conexão
Write-Host "`n2️⃣ CONECTAR AO AZURE:" -ForegroundColor Cyan
Write-Host "   Comando: az login" -ForegroundColor Yellow
Write-Host "   Descrição: Abrirá uma janela do navegador para autenticação" -ForegroundColor Gray

# Passo 3: Verificar recursos
Write-Host "`n3️⃣ VERIFICAR RECURSOS DISPONÍVEIS:" -ForegroundColor Cyan
Write-Host "   Comando: az account list" -ForegroundColor Yellow
Write-Host "   Descrição: Lista todas as assinaturas disponíveis" -ForegroundColor Gray

Write-Host "   Comando: az group list" -ForegroundColor Yellow
Write-Host "   Descrição: Lista todos os grupos de recursos" -ForegroundColor Gray

# Passo 4: Criar grupo de teste
Write-Host "`n4️⃣ CRIAR GRUPO DE RECURSOS DE TESTE:" -ForegroundColor Cyan
Write-Host "   Comando: az group create --name TestRG --location eastus" -ForegroundColor Yellow
Write-Host "   Descrição: Cria um grupo de recursos para testes" -ForegroundColor Gray
Write-Host "   Nota: Você pode usar 'brazilsouth' para localização no Brasil" -ForegroundColor Green

# Passo 5: Validar template
Write-Host "`n5️⃣ VALIDAR TEMPLATE ARM:" -ForegroundColor Cyan
Write-Host "   Comando: az deployment group validate --resource-group TestRG --template-file test-template.json" -ForegroundColor Yellow
Write-Host "   Descrição: Valida o template antes da implantação" -ForegroundColor Gray

Write-Host "`n📄 TEMPLATE DE EXEMPLO CRIADO:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Arquivo: test-template.json" -ForegroundColor White
Write-Host "Tipo: ARM Template (JSON)" -ForegroundColor White
Write-Host "Recurso: Conta de Armazenamento" -ForegroundColor White

Write-Host "`n🔍 COMANDOS ÚTEIS ADICIONAIS:" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`nVerificar status de implantação:" -ForegroundColor White
Write-Host "az deployment group list --resource-group TestRG" -ForegroundColor Yellow

Write-Host "`nVer logs de uma implantação:" -ForegroundColor White
Write-Host "az deployment group show --resource-group TestRG --name TestDeployment" -ForegroundColor Yellow

Write-Host "`nExcluir grupo de recursos (limpar testes):" -ForegroundColor White
Write-Host "az group delete --name TestRG --yes" -ForegroundColor Yellow

Write-Host "`n📊 VALIDAÇÃO COM POWERSHELL (Alternativa):" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

Write-Host "`nSe você preferir usar Azure PowerShell:" -ForegroundColor White
Write-Host "1. Instale o módulo: Install-Module -Name Az -Force" -ForegroundColor Yellow
Write-Host "2. Conecte: Connect-AzAccount" -ForegroundColor Yellow
Write-Host "3. Valide: Test-AzResourceGroupDeployment -ResourceGroupName 'TestRG' -TemplateFile 'test-template.json'" -ForegroundColor Yellow

Write-Host "`n⚡ PRÓXIMOS PASSOS:" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta
Write-Host "1. Instale o Azure CLI" -ForegroundColor White
Write-Host "2. Execute 'az login' para conectar" -ForegroundColor White
Write-Host "3. Use os comandos acima para validar seus templates" -ForegroundColor White
Write-Host "4. O script criará recursos de teste automaticamente" -ForegroundColor White

Write-Host "`n✅ SCRIPT CONCLUÍDO!" -ForegroundColor Green
Write-Host "Todos os comandos necessários foram demonstrados acima." -ForegroundColor Green