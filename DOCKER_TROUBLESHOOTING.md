# 🔧 Guia Rápido: Docker Troubleshooting

## 🚨 Problema: Alterações no código não aparecem

### ⚡ Solução Rápida (Copie e Cole)

**Para SIS Smart Search:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\sis-smart-search"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para DTIC Smart Search:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\glpi-smart-search"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para DTIC Dashboard:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\06-dtic-dashboard"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para SIS Dashboard:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\06.1.1-sis-dashboard"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para Carregadores:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\06.1.1-sis-carregadores-dashboard"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para Backend (GLPI Data Service):**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau\glpi-data-service"; docker-compose -f docker-compose.dev.yml down; docker-compose -f docker-compose.dev.yml up --build -d
```

**Para TODOS os containers:**
```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau"; ./dev-down.ps1; ./dev-up.ps1
```

---

## 🔍 Checklist de Validação

Use esta checklist quando o modelo aplicar uma correção:

- [ ] **1. Confirmar alteração no código**
  ```powershell
  cat "caminho\do\arquivo\modificado"
  ```

- [ ] **2. Forçar rebuild do container** (usar comando acima)

- [ ] **3. Aguardar inicialização** (15 segundos)
  ```powershell
  Start-Sleep -Seconds 15
  ```

- [ ] **4. Limpar cache do navegador** (`Ctrl + Shift + R`)

- [ ] **5. Testar funcionalidade** na aplicação

- [ ] **6. Se ainda não funcionar:** Verificar logs
  ```powershell
  docker-compose -f docker-compose.dev.yml logs --tail=50 frontend
  ```

---

## 📋 Prompt para o Modelo

**Copie e cole este texto quando precisar que o modelo force um rebuild:**

```
A alteração que você aplicou não está aparecendo na aplicação. Por favor:

1. Visualize o arquivo modificado para confirmar que a alteração foi salva
2. Force a reconstrução do container executando:
   cd "[CAMINHO_DA_APLICAÇÃO]"
   docker-compose -f docker-compose.dev.yml down
   docker-compose -f docker-compose.dev.yml up --build -d
3. Aguarde 15 segundos
4. Teste novamente no navegador com hard refresh (Ctrl+Shift+R)
5. Confirme que a alteração agora está visível

Aplicação: [nome da aplicação]
URL: http://localhost:[porta]
```

---

## 🎯 Exemplos de Uso

### Exemplo 1: SIS Smart Search não mostra correção
```
A alteração no ResultRow.tsx não está aparecendo em http://localhost:3004. 
Por favor, visualize o arquivo e depois force rebuild do SIS Smart Search.
```

### Exemplo 2: Todos os dashboards precisam de rebuild
```
Fiz alterações em múltiplos componentes compartilhados. 
Por favor, execute ./dev-down.ps1 e ./dev-up.ps1 para reconstruir tudo.
```

---

## 💡 Dicas

- O flag `--build` força o Docker a reconstruir a imagem ignorando cache
- O `-d` executa em background (detached mode)
- Sempre faça hard refresh no navegador (`Ctrl + Shift + R`) após rebuild
- Se o problema persistir, verifique os logs com `docker-compose logs`
