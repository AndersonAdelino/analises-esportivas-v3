"""
Script para coletar dados do Brasileirão Série A
"""
from get_team_matches import get_all_teams_matches
from get_historical_data import get_league_historical_data

if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("COLETA DE DADOS - BRASILEIRÃO SÉRIE A")
    print("=" * 70)
    print("\n")
    
    # Coleta histórico de partidas
    print("Coletando histórico de partidas...")
    get_league_historical_data(limit=20, league_code='BSA')
    
    print("\n")
    print("=" * 70)
    print("\n")
    
    # Coleta partidas por time
    print("Coletando partidas de cada time...")
    get_all_teams_matches(limit_per_team=20, league_code='BSA')
    
    print("\n")
    print("=" * 70)
    print("DADOS DO BRASILEIRÃO COLETADOS COM SUCESSO!")
    print("=" * 70)
    print("\n")

