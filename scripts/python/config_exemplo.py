#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURAÇÃO DE EXEMPLO - API GLPI
==================================

IMPORTANTE: 
1. Copie este arquivo para 'config.py'
2. Substitua os valores de exemplo pelos seus tokens reais
3. NUNCA commite o arquivo 'config.py' no Git!

"""

# ========================================
# CONFIGURAÇÕES DA API GLPI
# ========================================

# URL base da API GLPI (sem barra no final)
API_URL = "https://sua-instancia-glpi.com/apirest.php"

# Tokens de autenticação (SUBSTITUA pelos seus tokens reais)
APP_TOKEN = "seu_app_token_aqui_substitua_por_token_real"
USER_TOKEN = "seu_user_token_aqui_substitua_por_token_real"

# ========================================
# CONFIGURAÇÕES DE EXTRAÇÃO
# ========================================

# Limite de registros por requisição (não alterar sem necessidade)
RANGE_LIMIT = 1000

# Timeout para requisições (em segundos)
REQUEST_TIMEOUT = 30

# ========================================
# CONFIGURAÇÕES DE CACHE
# ========================================

# Habilitar cache de entidades/usuários/grupos
ENABLE_CACHE = True

# ========================================
# CONFIGURAÇÕES DE SAÍDA
# ========================================

# Diretório base para salvar dados
DADOS_DIR = "../dados"

# Formato de timestamp para arquivos
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# ========================================
# INSTRUÇÕES DE USO
# ========================================
"""
1. Para obter os tokens:
   - Acesse sua instância GLPI
   - Vá em Configurar > Geral > API
   - Gere um App Token
   - Vá em seu perfil de usuário
   - Gere um User Token

2. Substitua os valores acima pelos tokens reais

3. Salve como 'config.py' (sem '_exemplo')

4. Execute os scripts normalmente
"""