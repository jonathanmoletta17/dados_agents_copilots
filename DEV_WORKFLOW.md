# 🚀 Guia de Desenvolvimento Diário

## TL;DR - Quick Start

```powershell
# Início do dia
cd bd_cau
.\scripts\dev-up.ps1

# Durante desenvolvimento: apenas edite e salve
# Hot-reload funciona automaticamente em 1-3s

# Fim do dia
.\scripts\dev-down.ps1
```

---

## 📋 Início do Dia

### 1. Limpar Conflitos de Porta (IMPORTANTE)

**Por que:** Processos antigos (wslrelay, node, python) podem causar comportamento aleatório.

```powershell
cd "c:\Users\jonathan-moletta\OneDrive - Governo do Estado do Rio Grande do Sul\Área de Trabalho\BD_cau_sis\bd_cau"
.\scripts\cleanup-ports.ps1
```

**Saída esperada:**
- ✅ "No port conflicts found!" → Continuar para passo 2
- ⚠️ Lista de conflitos → Confirmar com `y` para matar processos

### 2. Iniciar Ambiente de Desenvolvimento

```powershell
.\scripts\dev-up.ps1
```

**⏱️ Tempo:** ~10-15 segundos (modo rápido, sem rebuild)

**Containers iniciados:**
- GLPI Data Service (PostgreSQL + API Backend) - http://localhost:8000
- DTIC Dashboard - http://localhost:3000
- SIS Dashboard - http://localhost:3001  
- SIS Carregadores Dashboard - http://localhost:3005
- DTIC Smart Search - http://localhost:3003
- SIS Smart Search - http://localhost:3004

---

## 💻 Durante o Desenvolvimento

### Como Funciona o Hot-Reload

1. **Abrir arquivo** no VS Code
2. **Fazer mudanças** no código
3. **Salvar (`Ctrl+S`)**
4. **Aguardar 1-3 segundos**
5. **Ver mudança automaticamente** no browser

**NÃO precisa:**
- ❌ Dar F5 no browser
- ❌ Reiniciar container
- ❌ Rodar `docker-compose up` novamente

### ✅ Hot-Reload Funcionando (Normal)

**Frontend:**
- Vite mostra "page reload" ou "hmr update"
- Mudança aparece em 1-3 segundos
- Browser NÃO precisa refresh manual

**Backend:**
- Logs mostram: `Detected file change, reloading...`
- API recarrega automaticamente
- Endpoints refletem mudanças imediatamente

### ❌ Se Hot-Reload NÃO Funcionar

**Sintomas:**
- Mudanças não aparecem após salvar
- Browser mostra versão antiga
- Precisa dar F5 constantemente

**Diagnóstico:**

```powershell
# 1. Verificar container rodando
docker ps | Select-String "carregadores"

# 2. Ver logs do frontend
docker logs sis-carregadores-frontend-dev --tail 50

# 3. Verificar conflitos de porta
.\scripts\cleanup-ports.ps1

# 4. Se persistir, restart específico
cd 06.1.1-sis-carregadores-dashboard
docker-compose -f docker-compose.dev.yml restart
cd ..
```

---

## 🔨 Quando Usar `-Rebuild`

### USE `-Rebuild` APENAS quando:

**Mudanças em dependências:**
- ✅ Instalou pacote npm: `npm install <pacote>`
- ✅ Instalou pacote Python: `pip install <pacote>`
- ✅ Mudou `package.json` diretamente
- ✅ Mudou `requirements.txt`

**Mudanças em configuração Docker:**
- ✅ Editou `Dockerfile.dev`
- ✅ Editou `docker-compose.dev.yml`

**Comando:**
```powershell
.\scripts\dev-up.ps1 -Rebuild
```

**⏱️ Tempo:** ~2-3 minutos (rebuilda todas as imagens)

### NÃO use `-Rebuild` para:

**Mudanças normais de código:**
- ❌ Editou arquivos `.tsx`, `.ts`, `.py`
- ❌ Mudou CSS, HTML
- ❌ Editou `vite.config.ts`
- ❌ Mudou lógica de negócio

**Por que não:** Hot-reload já traz essas mudanças automaticamente!

---

## 🚨 Troubleshooting

### Problema: "App rodando antes de subir container"

**Causa:** Processo antigo (wslrelay) usando mesma porta

**Solução:**
```powershell
.\scripts\cleanup-ports.ps1
.\scripts\dev-down.ps1
.\scripts\dev-up.ps1
```

### Problema: "Mudanças aparecem às vezes sim, às vezes não"

**Causa:** Conflito de portas - browser acessa versão errada aleatoriamente

**Solução:**
```powershell
# Ver quem está usando porta 3005 (exemplo)
Get-NetTCPConnection -LocalPort 3005 -State Listen | 
    ForEach-Object { Get-Process -Id $_.OwningProcess }

# Limpar conflitos
.\scripts\cleanup-ports.ps1
```

### Problema: "wslrelay usando portas"

**Causa:** Docker Desktop cache

**Solução:**
1. Fechar Docker Desktop
2. Aguardar 10 segundos
3. Reabrir Docker Desktop
4. Rodar `.\scripts\dev-up.ps1`

### Problema: "Port already in use"

**Solução automática:**
```powershell
.\scripts\cleanup-ports.ps1
```

**Solução manual:**
```powershell
# Encontrar processo
Get-NetTCPConnection -LocalPort <PORTA> -State Listen

# Matar processo
Stop-Process -Id <PID> -Force
```

---

## 🎯 Fim do Dia

### Parar Todos os Containers

```powershell
.\scripts\dev-down.ps1
```

**Tempo:** ~10 segundos

### Opcional: Deixar Rodando

Se você vai continuar trabalhando amanhã cedo:
- ✅ Pode deixar containers rodando
- ✅ Economiza tempo de startup (~15s)
- ⚠️ Consome memória/CPU durante a noite

---

## 📊 Como Verificar o Estado

### Containers Rodando

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

**Esperado:** 8 containers (6 apps + postgres + pgadmin)

### Portas em Uso

```powershell
Get-NetTCPConnection -LocalPort 3000,3001,3005,8000 -State Listen | 
    Select-Object LocalPort, OwningProcess | 
    Format-Table -AutoSize
```

**Esperado:** Apenas 1 processo (Docker) por porta

### Logs em Tempo Real

```powershell
# Frontend específico
docker logs sis-carregadores-frontend-dev -f

# Backend
docker logs glpi-service-dev -f

# Todos (precisa terminal separado para cada)
```

---

## ⚡ Comandos Rápidos

```powershell
# Iniciar ambiente
.\scripts\dev-up.ps1

# Iniciar com rebuild  
.\scripts\dev-up.ps1 -Rebuild

# Limpar conflitos de porta
.\scripts\cleanup-ports.ps1

# Parar tudo
.\scripts\dev-down.ps1

# Ver containers rodando
docker ps

# Restart específico (exemplo: carregadores)
cd 06.1.1-sis-carregadores-dashboard
docker-compose -f docker-compose.dev.yml restart
cd ..
```

---

## ✅ Checklist de Boas Práticas

**SEMPRE:**
- ✅ Rodar `cleanup-ports.ps1` no início do dia
- ✅ Usar `.\scripts\dev-up.ps1` centralizado
- ✅ Salvar (`Ctrl+S`) e aguardar hot-reload
- ✅ Verificar logs se algo parecer estranho

**NUNCA:**
- ❌ Rodar `npm run dev` direto nas pastas
- ❌ Rodar `python scripts/start_service.py` direto
- ❌ Rebuildar sem necessidade
- ❌ Ignorar warnings de port conflict

---

## 🎓 Conceitos Importantes

**Hot-Reload:** Mudanças refletem automaticamente sem restart
**Volume Mount:** Código local montado no container (Docker lê seu disco)
**Watch Polling:** Vite verifica mudanças ativamente a cada 1s
**Port Conflict:** Múltiplos processos na mesma porta = comportamento aleatório
**wslrelay:** Proxy do Docker Desktop (pode cachear versões antigas)

---

## 📞 Se Tudo Falhar

**Reset Completo:**

```powershell
# 1. Parar tudo
.\scripts\dev-down.ps1

# 2. Limpar portas
.\scripts\cleanup-ports.ps1 -Force

# 3. Reiniciar Docker Desktop
# (Fechar e abrir manualmente)

# 4. Rebuild completo
.\scripts\dev-up.ps1 -Rebuild
```

**Verificar sucesso:**
```powershell
docker ps  # Deve mostrar 8 containers
Get-NetTCPConnection -LocalPort 3005 -State Listen  # Apenas 1 processo
```

Abrir http://localhost:3005 → Fazer mudança → Ver em 1-3s ✅
