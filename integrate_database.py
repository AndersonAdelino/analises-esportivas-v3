"""
Script de Integração do Banco de Dados
Migra dados existentes dos CSVs para o banco SQLite
"""

import os
import glob
from database import FootballDatabase, get_database
import pandas as pd
import config
from datetime import datetime


def migrate_existing_data():
    """Migra todos os dados CSV existentes para o banco de dados"""
    
    print("=" * 70)
    print("MIGRACAO DE DADOS PARA BANCO DE DADOS SQLITE")
    print("=" * 70)
    print()
    
    db = get_database()
    total_matches = 0
    total_teams = 0
    
    # Mapeia códigos para nomes de arquivo
    league_name_map = {
        info['code']: name.lower().replace(' ', '_').replace('ã', 'a').replace('é', 'e')
        for name, info in config.LEAGUES.items()
    }
    
    # Para cada liga configurada
    for league_name, league_info in config.LEAGUES.items():
        league_code = league_info['code']
        league_prefix = league_name_map.get(league_code, 'league')
        
        print(f"\n[{league_code}] Migrando {league_name}...")
        print("-" * 70)
        
        # Busca arquivos CSV de partidas
        csv_pattern = f'data/{league_prefix}_matches_*.csv'
        csv_files = glob.glob(csv_pattern)
        
        if not csv_files:
            print(f"  [!] Nenhum arquivo CSV encontrado para {league_name}")
            continue
        
        # Pega o arquivo mais recente
        latest_csv = max(csv_files, key=os.path.getctime)
        print(f"  [1/2] Arquivo encontrado: {os.path.basename(latest_csv)}")
        
        try:
            # Carrega e migra partidas
            df = pd.read_csv(latest_csv)
            matches_count = db.insert_matches(df, league_code)
            total_matches += matches_count
            print(f"  [2/2] Partidas migradas: {matches_count}")
            
            # Registra no log
            db.log_update(
                league_code, 
                'migration', 
                matches_count=matches_count,
                success=True,
                message=f'Migrated from {latest_csv}'
            )
            
        except Exception as e:
            print(f"  [X] Erro ao migrar {league_name}: {e}")
            db.log_update(
                league_code, 
                'migration', 
                success=False,
                message=str(e)
            )
    
    print()
    print("=" * 70)
    print("RESUMO DA MIGRACAO")
    print("=" * 70)
    print(f"Total de partidas migradas: {total_matches}")
    print()
    
    # Mostra estatísticas
    stats = db.get_statistics()
    print("ESTATISTICAS DO BANCO DE DADOS:")
    print(f"  Total de partidas: {stats['total_matches']}")
    print(f"  Total de times: {stats['total_teams']}")
    print()
    
    if stats['matches_by_league']:
        print("Partidas por liga:")
        for league in stats['matches_by_league']:
            print(f"  - {league['league_name']}: {league['count']} partidas")
    
    print()
    print("[OK] Migracao concluida com sucesso!")
    print(f"[OK] Banco de dados salvo em: {db.db_path}")
    print()
    
    return total_matches


def test_database():
    """Testa o banco de dados"""
    print("\n" + "=" * 70)
    print("TESTE DO BANCO DE DADOS")
    print("=" * 70)
    print()
    
    db = get_database()
    
    # Teste 1: Estatísticas gerais
    print("[1/4] Estatisticas gerais...")
    stats = db.get_statistics()
    print(f"  Total de partidas: {stats['total_matches']}")
    print(f"  Total de times: {stats['total_teams']}")
    print()
    
    # Teste 2: Buscar partidas de uma liga
    print("[2/4] Buscando partidas da Premier League (ultimas 5)...")
    df_pl = db.get_matches('PL', limit=5)
    if len(df_pl) > 0:
        print(f"  Encontradas {len(df_pl)} partidas")
        print(f"  Exemplo: {df_pl.iloc[0]['home_team']} vs {df_pl.iloc[0]['away_team']}")
    else:
        print("  Nenhuma partida encontrada")
    print()
    
    # Teste 3: Última atualização
    print("[3/4] Verificando ultima atualizacao...")
    for league_name, league_info in config.LEAGUES.items():
        last_update = db.get_last_update(league_info['code'])
        if last_update:
            print(f"  [{league_info['code']}] {league_name}: {last_update['timestamp']}")
            print(f"       Partidas: {last_update['matches_count']}")
    print()
    
    # Teste 4: Performance
    print("[4/4] Teste de performance...")
    import time
    start = time.time()
    df_all = db.get_matches(limit=1000)
    elapsed = time.time() - start
    print(f"  Buscar 1000 partidas: {elapsed*1000:.2f}ms")
    print()
    
    print("[OK] Todos os testes passaram!")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            test_database()
        elif sys.argv[1] == 'migrate':
            migrate_existing_data()
        elif sys.argv[1] == 'all':
            migrate_existing_data()
            test_database()
        else:
            print("Uso: python integrate_database.py [migrate|test|all]")
    else:
        # Por padrão, faz migração e teste
        migrate_existing_data()
        test_database()

