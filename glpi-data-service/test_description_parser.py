#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste: Parser de Descrições de Formulário do GLPI
============================================================

Este script testa diferentes estratégias para extrair apenas o campo "Descrição"
dos textos de formulário estruturados do GLPI SIS.

NÃO ALTERA CÓDIGO DE PRODUÇÃO - apenas teste e validação.
"""

import re

# Exemplo real de descrição do GLPI conforme mostrado nas imagens
SAMPLE_DESCRIPTION_1 = """Dados do formulárioDados Gerais**1) Este atendimento é para quem? : **Para mim **2) Localização : **Carregadores e Mensageiros &#62; Casa Civil 1005 &#62; 1° Andar **3) Telefone de Contato : **32104437 **4) Urgência : **Muito Alta &nbsp; Detalhamento**5) Tipo : **Conservação &#62; Mensageria &#62; Movimentação Documentos **6) Assunto : **LEVAR DOCUMENTO PARA SGT BITTENCOURT **7) Descrição : **Solicito um mensageiro para levar documento para o Sargento Bittencourt. **8) Anexar Arquivo : **Nenhum documento anexado"""

SAMPLE_DESCRIPTION_2 = """Dados do Formulário **1) Localização : **Locais &#62; Palácio Piratini &#62; Galpão Crioulo **2) Este atendimento é para quem? : **Para mim **3) Telefone de Contato : **42155 **5)Setor Solicitante: ** Admin Detalhamento**4) Tipo : **Conservação &#62; Limpeza **5) Assunto : **Limpeza - Limpeza para festa **7) Descrição : **Solicito limpeza urgente do galpão para evento de sexta-feira"""

SAMPLE_DESCRIPTION_3 = """Dados do formulárioDados Gerais**1) Localização : **SPGG **2) Este atendimento é para quem? : **Para outra pessoa **3) Telefone de Contato : **3210-1234 Detalhamento**5) Tipo : **Suporte de TI **6) Assunto : **Instalação de Software **7) Descrição : **Preciso instalar o pacote office 2021 em 3 máquinas do setor financeiro. **8) Observações : **Máquinas novas sem office instalado"""


def extract_description_v1_regex_numbered(text):
    """
    Estratégia 1: Buscar padrão "7) Descrição : **TEXTO"
    Funciona se o campo sempre for numerado como 7)
    """
    if not text:
        return None
    
    # Procura por "7) Descrição : **" e captura até o próximo campo numerado
    pattern = r'\*\*7\)\s*Descri[çc][ãa]o\s*:\s*\*\*(.+?)(?:\*\*\d+\)|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        desc = match.group(1).strip()
        # Remove possíveis tags HTML residuais
        desc = re.sub(r'&[a-z]+;', '', desc)
        desc = re.sub(r'&#\d+;', '', desc)
        return desc
    
    return None


def extract_description_v2_regex_flexible(text):
    """
    Estratégia 2: Buscar padrão "\d+) Descrição : **TEXTO"
    Mais flexível, funciona independente do número
    """
    if not text:
        return None
    
    # Procura por qualquer número seguido de ") Descrição : **"
    pattern = r'\*\*\d+\)\s*Descri[çc][ãa]o\s*:\s*\*\*(.+?)(?:\*\*\d+\)|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        desc = match.group(1).strip()
        # Limpar HTML entities
        desc = re.sub(r'&[a-z]+;', ' ', desc)
        desc = re.sub(r'&#\d+;', ' ', desc)
        # Normalizar espaços
        desc = re.sub(r'\s+', ' ', desc)
        desc = desc.strip()
        # Remove "**" residual no final
        desc = re.sub(r'\*\*\s*$', '', desc)
        return desc
    
    return None


def extract_description_v3_split(text):
    """
    Estratégia 3: Split por campos e procurar especificamente "Descrição"
    Mais robusto para variações de formato
    """
    if not text:
        return None
    
    # Primeiro, limpar HTML entities
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'&[a-z]+;', '', text)
    
    # Split por padrão "**número)"
    fields = re.split(r'\*\*\d+\)', text)
    
    for field in fields:
        # Procurar por "Descrição :"
        if re.search(r'Descri[çc][ãa]o\s*:', field, re.IGNORECASE):
            # Extrair o conteúdo após os dois pontos
            match = re.search(r'Descri[çc][ãa]o\s*:\s*\*\*(.+)', field, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                # Limpar "**" do final
                desc = re.sub(r'\*\*\s*$', '', desc)
                # Normalizar espaços
                desc = re.sub(r'\s+', ' ', desc)
                return desc.strip()
    
    return None


def extract_description_v4_comprehensive(text):
    """
    Estratégia 4: Combinação de v2 e v3 - mais robusta
    Primeiro tenta regex específico, depois fallback para split
    """
    # Tenta v2 primeiro (mais rápido)
    result = extract_description_v2_regex_flexible(text)
    if result:
        return result
    
    # Fallback para v3 (mais robusto)
    return extract_description_v3_split(text)


def test_extraction_methods():
    """
    Testa todos os métodos de extração com amostras reais
    """
    samples = [
        ("Amostra 1 (Mensageiro)", SAMPLE_DESCRIPTION_1),
        ("Amostra 2 (Limpeza)", SAMPLE_DESCRIPTION_2),
        ("Amostra 3 (TI)", SAMPLE_DESCRIPTION_3),
    ]
    
    methods = [
        ("V1: Regex Numerado (7)", extract_description_v1_regex_numbered),
        ("V2: Regex Flexível", extract_description_v2_regex_flexible),
        ("V3: Split por Campos", extract_description_v3_split),
        ("V4: Combinado", extract_description_v4_comprehensive),
    ]
    
    print("=" * 80)
    print("TESTE DE ESTRATÉGIAS DE EXTRAÇÃO DE DESCRIÇÃO")
    print("=" * 80)
    
    for sample_name, sample_text in samples:
        print(f"\n{'─' * 80}")
        print(f"📋 {sample_name}")
        print(f"{'─' * 80}")
        print(f"\n📄 Texto Original (truncado):")
        print(f"{sample_text[:150]}...")
        print("\n")
        
        for method_name, method_func in methods:
            result = method_func(sample_text)
            print(f"🔹 {method_name}:")
            if result:
                print(f"   ✅ '{result}'")
            else:
                print(f"   ❌ Não extraiu")
            print()
    
    print("=" * 80)
    print("RECOMENDAÇÃO")
    print("=" * 80)
    print("""
A estratégia V4 (Combinado) é a mais robusta pois:
1. Tenta primeiro o regex otimizado (V2) - mais rápido
2. Faz fallback para split (V3) - mais robusto para formatos variados
3. Limpa HTML entities (&#62;, &nbsp;, etc)
4. Normaliza espaços em branco
5. Remove marcadores Markdown residuais (**)

Próximo passo: Integrar esta função no TextProcessor do backend.
    """)


if __name__ == "__main__":
    test_extraction_methods()
    
    # Teste adicional: mostrar resultado esperado vs atual
    print("\n" + "=" * 80)
    print("COMPARAÇÃO: ATUAL vs PROPOSTO")
    print("=" * 80)
    
    sample = SAMPLE_DESCRIPTION_1
    
    print("\n📊 ATUAL (mostrando tudo):")
    print(f"{sample}")
    
    print("\n📊 PROPOSTO (apenas campo 7 - Descrição):")
    clean_desc = extract_description_v4_comprehensive(sample)
    print(f"{clean_desc}")
    
    print(f"\n💾 Redução de tamanho: {len(sample)} → {len(clean_desc)} caracteres")
    print(f"   ({(1 - len(clean_desc)/len(sample))*100:.1f}% menor)")
