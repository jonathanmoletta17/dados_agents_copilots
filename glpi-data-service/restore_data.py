#!/usr/bin/env python3
"""
Script para forçar sincronização completa dos dados via RealtimeSyncWorker
"""
import asyncio
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workers.realtime_sync_worker import RealtimeSyncWorker

async def main():
    print("=" * 70)
    print("SINCRONIZAÇÃO COMPLETA - Restaurando Dados DTIC e SIS")
    print("=" * 70)
    
    worker = RealtimeSyncWorker()
    
    # Sincroniza DTIC
    print("\n🔄 [1/2] Sincronizando DTIC (aprox. 11k tickets)...")
    try:
        await worker.full_sync("dtic")
        print("✅ DTIC sincronizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar DTIC: {e}")
    
    # Sincroniza SIS
    print("\n🔄 [2/2] Sincronizando SIS (aprox. 5k tickets)...")
    try:
        await worker.full_sync("sis")
        print("✅ SIS sincronizado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar SIS: {e}")
    
    print("\n" + "=" * 70)
    print("Sincronização concluída!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
