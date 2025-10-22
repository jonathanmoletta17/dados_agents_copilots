# 🔧 CONFIGURAÇÃO INICIAL DO PROJETO

## 🚀 Primeiros Passos

### 1. Clone o Repositório
```bash
git clone [URL_DO_REPOSITORIO]
cd bd_cau
```

### 2. 🔒 Configure as Credenciais (OBRIGATÓRIO)

**⚠️ IMPORTANTE: Este passo é essencial para o funcionamento do sistema!**

```bash
cd scripts/python
cp config_exemplo.py config.py
```

Edite o arquivo `config.py` e substitua pelos seus tokens reais:

```python
# Substitua pelos seus tokens reais da API GLPI
API_URL = "https://sua-instancia-glpi.com/apirest.php"
APP_TOKEN = "seu_app_token_real_aqui"
USER_TOKEN = "seu_user_token_real_aqui"
```

### 3. 📋 Como Obter os Tokens

**App Token:**
1. Acesse sua instância GLPI
2. Vá em **Configurar** → **Geral** → **API**
3. Gere um novo **App Token**

**User Token:**
1. Acesse seu perfil de usuário no GLPI
2. Vá na aba **Configurações**
3. Gere um novo **Token de API**

### 4. 🐍 Instale as Dependências

```bash
pip install requests pandas pyyaml
```

### 5. ✅ Teste a Configuração

```bash
python extrair_dados_api_glpi_com_filtro_data.py --help
```

Se aparecer a mensagem "✅ Configurações carregadas de config.py", está tudo funcionando!

## 🔒 SEGURANÇA

### ❌ O que NÃO fazer:
- **NUNCA** commite o arquivo `config.py`
- **NUNCA** compartilhe seus tokens
- **NUNCA** coloque credenciais diretamente no código

### ✅ O que está protegido:
- `config.py` - Arquivo com credenciais (no .gitignore)
- `scripts/dados/` - Todos os dados extraídos (no .gitignore)
- Relatórios e métricas geradas (no .gitignore)

### 🛡️ Arquivos seguros para commit:
- Código-fonte dos scripts
- Documentação (README, etc.)
- `config_exemplo.py` (apenas exemplo, sem credenciais reais)

## 🎯 Uso do Sistema

### Extração de Dados:
```bash
# Extrair últimos 3 meses
python extrair_dados_api_glpi_com_filtro_data.py --periodo ultimos_3_meses

# Extrair período específico
python extrair_dados_api_glpi_com_filtro_data.py --data-inicial 01/01/2024 --data-final 31/01/2024
```

### Análise de Métricas:
```bash
python analisar_metricas_tickets.py
```

## 🆘 Problemas Comuns

### "Arquivo config.py não encontrado"
- Certifique-se de ter copiado `config_exemplo.py` para `config.py`
- Verifique se está no diretório `scripts/python`

### "Erro de autenticação na API"
- Verifique se os tokens estão corretos
- Confirme se a URL da API está correta
- Teste os tokens diretamente na interface GLPI

### "Módulo não encontrado"
- Instale as dependências: `pip install requests pandas pyyaml`

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique este arquivo de configuração
2. Consulte os READMEs específicos em `scripts/python/`
3. Verifique os logs de erro gerados pelos scripts