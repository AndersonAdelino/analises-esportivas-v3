"""
Script para buscar dados históricos das últimas partidas de uma liga
Suporta: Premier League, Brasileirão Série A
"""
import json
import os
from datetime import datetime
from api_client import FootballDataClient
from config import PREMIER_LEAGUE_CODE, DEFAULT_LIMIT, LEAGUES
import pandas as pd


def create_data_directory():
    """Cria diretório para armazenar os dados"""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Diretorio 'data' criado")


def save_json(data: dict, filename: str):
    """Salva dados em formato JSON"""
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK - Dados JSON salvos em: {filepath}")


def save_csv(df: pd.DataFrame, filename: str):
    """Salva DataFrame em formato CSV"""
    filepath = os.path.join('data', filename)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"OK - Dados CSV salvos em: {filepath}")


def parse_matches_to_dataframe(matches_data: dict) -> pd.DataFrame:
    """
    Converte dados de partidas em um DataFrame do Pandas
    
    Args:
        matches_data: Dados brutos das partidas da API
        
    Returns:
        DataFrame com informações das partidas
    """
    matches = matches_data.get('matches', [])
    
    parsed_data = []
    for match in matches:
        parsed_match = {
            'match_id': match['id'],
            'data': match['utcDate'],
            'status': match['status'],
            'rodada': match.get('matchday', 'N/A'),
            'estadio': match.get('venue', 'N/A'),
            'time_casa': match['homeTeam']['name'],
            'time_casa_id': match['homeTeam']['id'],
            'time_visitante': match['awayTeam']['name'],
            'time_visitante_id': match['awayTeam']['id'],
            'gols_casa': match['score']['fullTime']['home'],
            'gols_visitante': match['score']['fullTime']['away'],
            'vencedor': match['score']['winner'],
            'temporada': match['season']['startDate'][:4],
        }
        parsed_data.append(parsed_match)
    
    return pd.DataFrame(parsed_data)


def get_league_historical_data(limit: int = DEFAULT_LIMIT, league_code: str = None):
    """
    Busca dados históricos das últimas partidas de uma liga
    
    Args:
        limit: Número de partidas a buscar (padrão: 20)
        league_code: Código da liga (ex: 'PL', 'BSA'). Se None, usa PREMIER_LEAGUE_CODE
    """
    if league_code is None:
        league_code = PREMIER_LEAGUE_CODE
    
    # Obtém nome da liga
    league_display = [name for name, info in LEAGUES.items() if info['code'] == league_code][0]
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a') 
                      for name, info in LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'league')
    
    print("=" * 60)
    print(f"ANALISE ESPORTIVA - {league_display.upper()}")
    print("=" * 60)
    print(f"Iniciando busca de dados historicos da {league_display}...")
    print(f"Buscando ultimas {limit} partidas finalizadas\n")
    
    # Cria diretório de dados
    create_data_directory()
    
    try:
        # Inicializa o cliente da API
        client = FootballDataClient()
        
        # 1. Busca partidas finalizadas da liga
        print("[1/4] Buscando partidas finalizadas...")
        matches_data = client.get_competition_matches(
            competition_code=league_code,
            status='FINISHED',
            limit=limit
        )
        
        # Salva dados brutos em JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f'{league_prefix}_matches_{timestamp}.json'
        save_json(matches_data, json_filename)
        
        # 2. Converte para DataFrame e salva em CSV
        print("\n[2/4] Processando dados...")
        df_matches = parse_matches_to_dataframe(matches_data)
        csv_filename = f'{league_prefix}_matches_{timestamp}.csv'
        save_csv(df_matches, csv_filename)
        
        # 3. Mostra estatísticas básicas
        print("\n" + "="*60)
        print("[3/4] RESUMO DOS DADOS COLETADOS")
        print("="*60)
        print(f"Total de partidas: {len(df_matches)}")
        print(f"Período: {df_matches['data'].min()[:10]} até {df_matches['data'].max()[:10]}")
        print(f"Temporadas: {df_matches['temporada'].unique()}")
        print(f"\nPrimeiras 5 partidas:")
        print(df_matches[['data', 'time_casa', 'gols_casa', 'gols_visitante', 'time_visitante']].head())
        
        # 4. Busca times da liga
        print(f"\n[4/4] Buscando lista de times da {league_display}...")
        teams_data = client.get_competition_teams(league_code)
        
        teams_json = f'{league_prefix}_teams_{timestamp}.json'
        save_json(teams_data, teams_json)
        
        teams_list = teams_data.get('teams', [])
        print(f"OK - {len(teams_list)} times encontrados")
        
        print("\n" + "="*60)
        print("SUCESSO! Dados coletados com sucesso!")
        print("="*60)
        print(f"\nProximo passo: Use os dados em 'data/' para suas analises")
        
        return df_matches, teams_data
        
    except ValueError as e:
        print(f"\nERRO de configuracao: {e}")
        print("\nComo obter sua API Key:")
        print("1. Acesse: https://www.football-data.org/client/register")
        print("2. Registre-se gratuitamente")
        print("3. Copie sua API Key")
        print("4. Crie um arquivo .env na raiz do projeto")
        print("5. Adicione: FOOTBALL_DATA_API_KEY=sua_chave_aqui")
        
    except Exception as e:
        print(f"\nERRO ao buscar dados: {e}")


def get_premier_league_historical_data(limit: int = DEFAULT_LIMIT):
    """
    Função legacy - mantida para compatibilidade
    Busca dados históricos das últimas partidas da Premier League
    
    Args:
        limit: Número de partidas a buscar (padrão: 20)
    """
    return get_league_historical_data(limit=limit, league_code='PL')


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("COLETA DE DADOS - ESCOLHA A LIGA")
    print("=" * 70)
    
    # Menu de seleção de liga
    print("\nLigas disponíveis:")
    for idx, (name, info) in enumerate(LEAGUES.items(), 1):
        print(f"{idx}. {info['flag']} {name} ({info['code']})")
    print(f"{len(LEAGUES) + 1}. Todas as ligas")
    
    # Lê escolha do usuário
    try:
        choice = input(f"\nEscolha a liga (1-{len(LEAGUES) + 1}) [1]: ").strip() or "1"
        choice_num = int(choice)
        
        if choice_num == len(LEAGUES) + 1:
            # Coletar todas as ligas
            for league_name, league_info in LEAGUES.items():
                print(f"\n{'='*70}")
                print(f"Coletando {league_name}...")
                print(f"{'='*70}\n")
                get_league_historical_data(limit=20, league_code=league_info['code'])
                print("\n")
        else:
            # Liga específica
            league_name = list(LEAGUES.keys())[choice_num - 1]
            league_code = LEAGUES[league_name]['code']
            get_league_historical_data(limit=20, league_code=league_code)
    except (ValueError, IndexError):
        print("Opção inválida. Usando Premier League por padrão.")
        get_league_historical_data(limit=20, league_code='PL')

