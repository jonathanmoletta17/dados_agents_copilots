# BD CAU - Sistema Integrado

Este repositório contém os microsserviços e frontends do ecossistema BD CAU.

## 🚀 Como Executar

A ordem de execução é importante: **primeiro o Backend, depois os Frontends.**

### 1. Backend (Obrigatório)

O `glpi-data-service` é a API central que serve dados para todas as aplicações.

```bash
cd glpi-data-service
docker-compose up -d --build
```
*Porta: 8000*

---

### 2. Frontends (Aplicações)

Execute os comandos abaixo em terminais separados ou conforme a necessidade.

#### GLPI Smart Search (Busca Inteligente DTIC)
```bash
cd glpi-smart-search
docker-compose up -d --build
```
*Porta: 3003*

#### SIS Smart Search (Busca Inteligente SIS)
```bash
cd sis-smart-search
docker-compose up -d --build
```
*Porta: 3004*

#### DTIC Dashboard
```bash
cd 06-dtic-dashboard
docker-compose up -d --build
```
*Porta: 3000*

#### SIS Dashboard
```bash
cd 06.1-sis-dashboard
docker-compose up -d --build
```
*Porta: 3001*

---

### 🛠️ Scripts Úteis

Na raiz do projeto, existem scripts para facilitar o gerenciamento de todos os serviços de uma vez (Windows PowerShell):

*   **Iniciar Tudo**: `.\start_all.ps1`
*   **Parar Tudo**: `.\stop_all.ps1`