# -*- coding: utf-8 -*-
"""
Módulo de Processamento de Texto para GLPI
==========================================

Focado em limpar e estruturar textos HTML vindos do GLPI para
formato Markdown/Texto Rico, ideal para consumo por Agentes de IA.
"""

import re
import html

class TextProcessor:
    @staticmethod
    def html_to_markdown(html_content):
        """
        Converte HTML básico do GLPI para Markdown.
        Preserva estrutura de listas, negrito e quebras de linha.
        """
        if not html_content:
            return ""
        
        text = str(html_content)
        text = html.unescape(text)
        
        # Substituições básicas
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</div>', '\n', text, flags=re.IGNORECASE)
        
        # Negrito / Itálico
        text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE)
        text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE)
        text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE)
        text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE)
        
        # Listas
        text = re.sub(r'<ul>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</ul>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<li>', '- ', text, flags=re.IGNORECASE)
        text = re.sub(r'</li>', '\n', text, flags=re.IGNORECASE)
        
        # Links
        text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', text, flags=re.IGNORECASE)
        
        # Remover tags restantes
        text = re.sub(r'<[^>]+>', '', text)
        
        # Limpeza final
        text = re.sub(r'\n\s+\n', '\n\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text

    @staticmethod
    def clean_text(text):
        """
        Limpeza geral de texto (remove caracteres invisíveis, normaliza espaços).
        """
        if not text:
            return ""
        
        text = str(text)
        # Remover caracteres de controle invisíveis
        text = re.sub(r'[\u200b-\u200f\u2028-\u202f\u205f-\u206f]', '', text)
        
        return text.strip()

    @staticmethod
    def extract_form_description(text):
        """
        Extrai apenas o campo "Descrição" de formulários estruturados do GLPI.
        
        Formulários do GLPI SIS têm estrutura como:
        **1) Este atendimento é para quem? : **Para mim
        **2) Localização : **...
        **7) Descrição : **TEXTO DA DESCRIÇÃO
        **8) Anexar Arquivo : **...
        
        Esta função extrai apenas o conteúdo do campo "Descrição" (geralmente campo 7),
        removendo todos os outros campos do formulário.
        
        Se o texto não tiver padrão de formulário, retorna o texto original.
        
        Args:
            text: Texto potencialmente contendo estrutura de formulário
            
        Returns:
            String contendo apenas a descrição, ou texto original se não for formulário
            
        Examples:
            >>> text = "**7) Descrição : **Solicito um mensageiro **8) Anexar : **Nenhum"
            >>> extract_form_description(text)
            'Solicito um mensageiro'
        """
        if not text:
            return text
        
        text_str = str(text)
        
        # Limpar HTML entities primeiro
        cleaned = re.sub(r'&nbsp;', ' ', text_str)
        cleaned = re.sub(r'&#\d+;', '', cleaned)
        cleaned = re.sub(r'&[a-z]+;', '', cleaned)
        
        # Estratégia 1: Regex otimizado para padrão **N) Descrição : **TEXTO
        # Procura por qualquer número seguido de ") Descrição :"
        pattern = r'\*\*\d+\)\s*Descri[çc][ãa]o\s*:\s*\*\*(.+?)(?:\*\*\d+\)|$)'
        match = re.search(pattern, cleaned, re.IGNORECASE | re.DOTALL)
        
        if match:
            desc = match.group(1).strip()
            # Limpar marcadores Markdown residuais
            desc = re.sub(r'\*\*\s*$', '', desc)
            # Normalizar espaços em branco
            desc = re.sub(r'\s+', ' ', desc)
            return desc.strip()
        
        # Estratégia 2: Fallback com split por campos
        # Mais robusto para variações de formato
        fields = re.split(r'\*\*\d+\)', cleaned)
        for field in fields:
            # Procurar por campo "Descrição"
            if re.search(r'Descri[çc][ãa]o\s*:', field, re.IGNORECASE):
                match = re.search(r'Descri[çc][ãa]o\s*:\s*\*\*(.+)', field, re.IGNORECASE | re.DOTALL)
                if match:
                    desc = match.group(1).strip()
                    desc = re.sub(r'\*\*\s*$', '', desc)
                    desc = re.sub(r'\s+', ' ', desc)
                    return desc.strip()
        
        # Se não encontrar padrão de formulário, retorna texto original
        # Isso garante compatibilidade com descrições que não são formulários
        return text_str

