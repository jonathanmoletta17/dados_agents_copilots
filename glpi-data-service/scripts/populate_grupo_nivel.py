#!/usr/bin/env python3
"""
Script simples para popular grupo_nivel
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.postgres_manager import get_db_manager
from src.db.models import Ticket


def extract_nivel(grupo_text: str) -> str:
    """Extrai nível (N1-N4) do campo grupo."""
    if not grupo_text:
        return None
    
    # Divide por quebra de linha
    grupos = grupo_text.split('\n')
    
    # Prioridade: N1 > N2 > N3 > N4
    for nivel in ['N1', 'N2', 'N3', 'N4']:
        if nivel in grupos:
            return nivel
    
    return None


def populate_context(context: str, dry_run: bool = False):
    """Popula grupo_nivel para um contexto."""
    print(f"\n{'='*60}")
    print(f"📊 Contexto: {context.upper()}")
    print(f"{'='*60}\n")
    
    db_manager = get_db_manager(context)
    
    with db_manager.get_session() as session:
        # Busca todos os tickets
        tickets = session.query(Ticket).filter(Ticket.is_deleted == False).all()
        
        print(f"Total de tickets: {len(tickets):,}\n")
        
        # Estatísticas
        stats = {
            'N1': 0,
            'N2': 0,
            'N3': 0,
            'N4': 0,
            'SEM_NIVEL': 0
        }
        
        updated = 0
        
        for ticket in tickets:
            nivel = extract_nivel(ticket.grupo)
            
            if nivel:
                stats[nivel] += 1
                if ticket.grupo_nivel != nivel and not dry_run:
                    ticket.grupo_nivel = nivel
                    updated += 1
            else:
                stats['SEM_NIVEL'] += 1
        
        if not dry_run:
            session.commit()
            print(f"✅ Atualizados: {updated:,} tickets\n")
        else:
            print("⚠️  DRY RUN - Nenhuma alteração feita\n")
        
        # Mostra distribuição
        print("📊 Distribuição por nível:\n")
        for nivel, count in stats.items():
            print(f"  {nivel}: {count:,}")
        
        print(f"\n{'='*60}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', choices=['dtic', 'sis', 'all'], default='all')
    parser.add_argument('--dry-run', action='store_true')
    
    args = parser.parse_args()
    
    contexts = ['dtic', 'sis'] if args.context == 'all' else [args.context]
    
    for context in contexts:
        try:
            populate_context(context, dry_run=args.dry_run)
        except Exception as e:
            print(f"❌ Erro: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
