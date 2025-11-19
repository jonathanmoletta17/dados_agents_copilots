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
        
        # Normalizar whitespace (mas manter quebras de linha se já processadas)
        # Se for texto cru, talvez queiramos remover tudo.
        # Aqui assumimos que pode ser usado após html_to_markdown, então cuidamos com \n
        
        return text.strip()
