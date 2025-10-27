"""
Script para buscar os últimos jogos de cada time de uma liga
Suporta: Premier League, Brasileirão Série A
"""
import json
import os
from datetime import datetime
from api_client import FootballDataClient
from config import PREMIER_LEAGUE_CODE, LEAGUES, DEFAULT_LEAGUE
import pandas as pd
import time


def load_teams_from_json(league_code=None):
    """
    Carrega times do JSON mais recente ou busca da API
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA'). Se None, usa PREMIER_LEAGUE_CODE
    """
    if league_code is None:
        league_code = PREMIER_LEAGUE_CODE
    
    # Mapeia code para nome da liga
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a') 
                       for name, info in LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'premier_league')
    
    # Procura o arquivo JSON de times mais recente
    data_dir = 'data'
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) 
                      if f.startswith(f'{league_prefix}_teams_') and f.endswith('.json')]
        if json_files:
            latest_file = max([os.path.join(data_dir, f) for f in json_files], key=os.path.getctime)
            print(f"Carregando times do arquivo: {latest_file}")
            with open(latest_file, 'r', encoding='utf-8') as f:
                teams_data = json.load(f)
                return teams_data.get('teams', [])
    
    # Se não encontrou, busca da API
    league_display = [name for name, info in LEAGUES.items() if info['code'] == league_code][0]
    print(f"Buscando times da {league_display} da API...")
    client = FootballDataClient()
    teams_data = client.get_competition_teams(league_code)
    return teams_data.get('teams', [])


def save_json(data: dict, filename: str):
    """Salva dados em formato JSON"""
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  -> Salvo: {filepath}")


def parse_team_matches_to_dataframe(team_name: str, matches_data: dict) -> pd.DataFrame:
    """
    Converte dados de partidas de um time em DataFrame
    
    Args:
        team_name: Nome do time
        matches_data: Dados das partidas da API
        
    Returns:
        DataFrame com informações das partidas
    """
    matches = matches_data.get('matches', [])
    
    parsed_data = []
    for match in matches:
        # Identifica se o time jogou em casa ou fora
        is_home = match['homeTeam']['name'] == team_name
        opponent = match['awayTeam']['name'] if is_home else match['homeTeam']['name']
        venue = 'Casa' if is_home else 'Fora'
        
        # Gols marcados e sofridos
        if is_home:
            gols_marcados = match['score']['fullTime']['home']
            gols_sofridos = match['score']['fullTime']['away']
        else:
            gols_marcados = match['score']['fullTime']['away']
            gols_sofridos = match['score']['fullTime']['home']
        
        # Resultado
        winner = match['score']['winner']
        if winner == 'DRAW':
            resultado = 'Empate'
        elif (is_home and winner == 'HOME_TEAM') or (not is_home and winner == 'AWAY_TEAM'):
            resultado = 'Vitoria'
        else:
            resultado = 'Derrota'
        
        parsed_match = {
            'match_id': match['id'],
            'data': match['utcDate'][:10],
            'competicao': match['competition']['name'],
            'competicao_code': match['competition']['code'],
            'status': match['status'],
            'time': team_name,
            'adversario': opponent,
            'local': venue,
            'gols_marcados': gols_marcados,
            'gols_sofridos': gols_sofridos,
            'placar': f"{match['score']['fullTime']['home']}-{match['score']['fullTime']['away']}",
            'resultado': resultado,
            'temporada': match['season']['startDate'][:4],
        }
        parsed_data.append(parsed_match)
    
    return pd.DataFrame(parsed_data)


def get_all_teams_matches(limit_per_team: int = 20, league_code: str = None):
    """
    Busca últimas partidas de todos os times de uma liga
    
    Args:
        limit_per_team: Número de partidas a buscar por time
        league_code: Código da liga (ex: 'PL', 'BSA'). Se None, usa PREMIER_LEAGUE_CODE
    """
    if league_code is None:
        league_code = PREMIER_LEAGUE_CODE
    
    # Obtém nome da liga
    league_display = [name for name, info in LEAGUES.items() if info['code'] == league_code][0]
    
    print("=" * 70)
    print("COLETA DE DADOS - ULTIMAS PARTIDAS POR TIME")
    print("=" * 70)
    print(f"Liga: {league_display}")
    print(f"Buscando ultimas {limit_per_team} partidas de cada time")
    print("(em todas as competicoes)\n")
    
    # Cria diretório de dados se não existir
    if not os.path.exists('data'):
        os.makedirs('data')
    
    try:
        # Carrega times da liga
        print(f"[1/3] Carregando times da {league_display}...")
        teams = load_teams_from_json(league_code)
        print(f"OK - {len(teams)} times encontrados\n")
        
        # Inicializa cliente da API
        client = FootballDataClient()
        
        # Estrutura para armazenar todos os dados
        all_teams_data = {}
        all_matches_df = []
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Nome do arquivo baseado na liga
        league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a') 
                          for name, info in LEAGUES.items()}
        league_prefix = league_name_map.get(league_code, 'league')
        
        print(f"[2/3] Buscando partidas de cada time...")
        print("-" * 70)
        
        for idx, team in enumerate(teams, 1):
            team_id = team['id']
            team_name = team['name']
            
            print(f"[{idx:2d}/{len(teams)}] {team_name:40s}", end=' ')
            
            try:
                # Busca últimas partidas do time (finalizadas)
                matches_data = client.get_team_matches(
                    team_id=team_id,
                    status='FINISHED',
                    limit=limit_per_team
                )
                
                num_matches = len(matches_data.get('matches', []))
                print(f"- {num_matches} partidas")
                
                # Armazena dados brutos
                all_teams_data[team_name] = matches_data
                
                # Converte para DataFrame
                if num_matches > 0:
                    df_team = parse_team_matches_to_dataframe(team_name, matches_data)
                    all_matches_df.append(df_team)
                
                # Pausa entre requisições para respeitar limites da API (10 req/min)
                # Com 20 times, fazemos ~6 segundos entre cada requisição
                if idx < len(teams):
                    import time as time_module
                    time_module.sleep(6)
                
            except Exception as e:
                print(f"ERRO: {e}")
                continue
        
        print("\n[3/3] Salvando dados...")
        print("-" * 70)
        
        # Salva dados brutos em JSON (todos os times)
        json_filename = f'{league_prefix}_teams_matches_{timestamp}.json'
        save_json(all_teams_data, json_filename)
        
        # Combina todos os DataFrames e salva em CSV
        if all_matches_df:
            df_combined = pd.concat(all_matches_df, ignore_index=True)
            csv_filename = f'{league_prefix}_matches_{timestamp}.csv'
            csv_filepath = os.path.join('data', csv_filename)
            df_combined.to_csv(csv_filepath, index=False, encoding='utf-8')
            print(f"  -> Salvo CSV: {csv_filepath}")
            
            # NOVO: Salvar também no banco de dados
            try:
                from database import get_database
                db = get_database()
                db_count = db.insert_matches(df_combined, league_code)
                db.log_update(
                    league_code,
                    'api_fetch',
                    matches_count=db_count,
                    success=True,
                    message=f'Collected {db_count} matches from API'
                )
                print(f"  -> Salvo DB:  {db_count} partidas persistidas no banco")
            except Exception as e:
                print(f"  [!] Aviso: Nao foi possivel salvar no banco: {e}")
            
            # Estatísticas resumidas
            print("\n" + "=" * 70)
            print("RESUMO DOS DADOS COLETADOS")
            print("=" * 70)
            print(f"Total de times: {len(teams)}")
            print(f"Total de partidas coletadas: {len(df_combined)}")
            print(f"Competicoes envolvidas: {df_combined['competicao'].nunique()}")
            print(f"\nCompeticoes:")
            for comp in df_combined['competicao'].unique():
                count = len(df_combined[df_combined['competicao'] == comp])
                print(f"  - {comp}: {count} partidas")
            
            # Mostra exemplo de dados
            print(f"\nExemplo de dados (primeiras 5 partidas):")
            print(df_combined[['data', 'time', 'local', 'adversario', 'placar', 'resultado']].head())
            
            print("\n" + "=" * 70)
            print("SUCESSO! Dados coletados com sucesso!")
            print("=" * 70)
            
            return df_combined, all_teams_data
        else:
            print("AVISO: Nenhuma partida foi coletada")
            return None, all_teams_data
            
    except ValueError as e:
        print(f"\nERRO de configuracao: {e}")
        print("Verifique se sua API Key esta configurada corretamente no arquivo .env")
        
    except Exception as e:
        print(f"\nERRO ao buscar dados: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
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
            print("\n")
            print("IMPORTANTE: Coletando dados de TODAS as ligas")
            print(f"Aproximadamente {len(LEAGUES) * 20} requisições à API")
            print("Com plano gratuito (10 req/min), levará ~4-6 minutos")
            print("=" * 70)
            print("\n")
            
            for league_name, league_info in LEAGUES.items():
                print(f"\n{'='*70}")
                print(f"Coletando {league_name}...")
                print(f"{'='*70}\n")
                get_all_teams_matches(limit_per_team=20, league_code=league_info['code'])
                print("\n")
        else:
            # Liga específica
            league_name = list(LEAGUES.keys())[choice_num - 1]
            league_code = LEAGUES[league_name]['code']
            
            print("\n")
            print("IMPORTANTE: Este script fará aproximadamente 20 requisições à API")
            print("Com plano gratuito (10 req/min), levará cerca de 2-3 minutos")
            print("=" * 70)
            print("\n")
            
            get_all_teams_matches(limit_per_team=20, league_code=league_code)
    except (ValueError, IndexError):
        print("Opção inválida. Usando Premier League por padrão.")
        get_all_teams_matches(limit_per_team=20, league_code='PL')

