---
description: Forçar reconstrução de containers quando alterações não se refletem
---

# Workflow: Forçar Reconstrução de Containers Docker

Use este workflow quando você fizer alterações no código mas elas não aparecerem no container em execução.

## Comandos por Aplicação

### SIS Smart Search
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\sis-smart-search"
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build -d
```

### DTIC Smart Search (GLPI Smart Search)
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\glpi-smart-search"
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build -d
```

### Carregadores Dashboard
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\carregadores-dashboard"
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build -d
```

### GLPI Data Service (Backend)
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\glpi-data-service"
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up --build -d
```

## Reconstruir TODAS as aplicações de uma vez
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau"
./dev-down.ps1
./dev-up.ps1
```

---

## Procedimento de Troubleshooting

### 1. Confirmar que o código foi alterado
```powershell
# Verifique o conteúdo do arquivo modificado
cat "caminho\do\arquivo\modificado.tsx"
```

### 2. Forçar reconstrução do container específico
Use os comandos acima da aplicação afetada.

### 3. Aguardar inicialização (10-15 segundos)
```powershell
Start-Sleep -Seconds 15
```

### 4. Verificar logs do container
```powershell
docker-compose -f docker-compose.dev.yml logs --tail=30 frontend
```

### 5. Limpar cache do navegador
- Pressione `Ctrl + Shift + R` para hard refresh
- Ou abra DevTools (F12) e clique com botão direito no botão de atualizar → "Limpar cache e atualizar"

### 6. Testar novamente
Abra a aplicação no navegador e valide as mudanças.

---

## Prompt Template para o Modelo

Quando as alterações não se refletirem, envie este prompt:

```
As alterações que você aplicou no código não estão aparecendo na aplicação em execução. 

Por favor:
1. Confirme que o arquivo [NOME_DO_ARQUIVO] foi realmente modificado visualizando o código atual
2. Force a reconstrução do container da aplicação [NOME_DA_APLICAÇÃO] usando:
   - docker-compose -f docker-compose.dev.yml down
   - docker-compose -f docker-compose.dev.yml up --build -d
3. Aguarde 15 segundos para o container inicializar
4. Teste novamente a funcionalidade no navegador para confirmar que as mudanças foram aplicadas

Aplicação afetada: [SIS Smart Search | DTIC Smart Search | Carregadores Dashboard | etc]
URL de teste: http://localhost:[PORTA]
```

---

## Quando usar este workflow?

✅ Use quando:
- Você fez alterações no código mas a aplicação ainda mostra o comportamento antigo
- O hot-reload não funcionou automaticamente
- Você alterou arquivos de configuração ou dependências
- Você suspeita que o Docker está usando cache antigo

❌ Não precisa usar quando:
- A aplicação já não está rodando
- Você ainda não fez nenhuma alteração no código
- O erro é de sintaxe/compilação (apareceria nos logs)
