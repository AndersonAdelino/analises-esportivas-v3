"""
Script de TESTE para buscar os últimos jogos de alguns times da Premier League
Este script busca apenas 3 times para teste rápido
"""
import json
import os
from datetime import datetime
from api_client import FootballDataClient
from config import PREMIER_LEAGUE_CODE
import pandas as pd
import time


def load_teams_from_json():
    """Carrega times do JSON mais recente ou busca da API"""
    # Procura o arquivo JSON de times mais recente
    data_dir = 'data'
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) if f.startswith('premier_league_teams_') and f.endswith('.json')]
        if json_files:
            latest_file = max([os.path.join(data_dir, f) for f in json_files], key=os.path.getctime)
            print(f"Carregando times do arquivo: {latest_file}")
            with open(latest_file, 'r', encoding='utf-8') as f:
                teams_data = json.load(f)
                return teams_data.get('teams', [])
    
    # Se não encontrou, busca da API
    print("Buscando times da Premier League da API...")
    client = FootballDataClient()
    teams_data = client.get_competition_teams(PREMIER_LEAGUE_CODE)
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


def get_teams_matches_test(teams_to_test=3, limit_per_team=20):
    """
    VERSAO DE TESTE - Busca últimas partidas de alguns times da Premier League
    
    Args:
        teams_to_test: Número de times para testar
        limit_per_team: Número de partidas a buscar por time
    """
    print("=" * 70)
    print("TESTE - COLETA DE DADOS DE ALGUNS TIMES")
    print("=" * 70)
    print(f"Buscando ultimas {limit_per_team} partidas de {teams_to_test} times da Premier League")
    print("(em todas as competicoes)\n")
    
    # Cria diretório de dados se não existir
    if not os.path.exists('data'):
        os.makedirs('data')
    
    try:
        # Carrega times da Premier League
        print("[1/3] Carregando times da Premier League...")
        all_teams = load_teams_from_json()
        
        # Seleciona apenas os primeiros N times para teste
        teams = all_teams[:teams_to_test]
        print(f"OK - Testando com {len(teams)} times: {', '.join([t['name'] for t in teams])}\n")
        
        # Inicializa cliente da API
        client = FootballDataClient()
        
        # Estrutura para armazenar todos os dados
        all_teams_data = {}
        all_matches_df = []
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print(f"[2/3] Buscando partidas de cada time...")
        print("-" * 70)
        
        for idx, team in enumerate(teams, 1):
            team_id = team['id']
            team_name = team['name']
            
            print(f"[{idx:2d}/{len(teams)}] {team_name:40s}", end=' ', flush=True)
            
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
                
                # Pausa entre requisições para respeitar limites da API
                if idx < len(teams):
                    time.sleep(6)
                
            except Exception as e:
                print(f"ERRO: {e}")
                continue
        
        print("\n[3/3] Salvando dados...")
        print("-" * 70)
        
        # Salva dados brutos em JSON
        json_filename = f'test_teams_matches_{timestamp}.json'
        save_json(all_teams_data, json_filename)
        
        # Combina todos os DataFrames e salva em CSV
        if all_matches_df:
            df_combined = pd.concat(all_matches_df, ignore_index=True)
            csv_filename = f'test_teams_matches_{timestamp}.csv'
            csv_filepath = os.path.join('data', csv_filename)
            df_combined.to_csv(csv_filepath, index=False, encoding='utf-8')
            print(f"  -> Salvo: {csv_filepath}")
            
            # Estatísticas resumidas
            print("\n" + "=" * 70)
            print("RESUMO DOS DADOS COLETADOS")
            print("=" * 70)
            print(f"Total de times testados: {len(teams)}")
            print(f"Total de partidas coletadas: {len(df_combined)}")
            print(f"Competicoes envolvidas: {df_combined['competicao'].nunique()}")
            print(f"\nCompeticoes:")
            for comp in df_combined['competicao'].unique():
                count = len(df_combined[df_combined['competicao'] == comp])
                print(f"  - {comp}: {count} partidas")
            
            # Mostra exemplo de dados por time
            print(f"\nDados por time:")
            for time in df_combined['time'].unique():
                df_time = df_combined[df_combined['time'] == time]
                vitorias = len(df_time[df_time['resultado'] == 'Vitoria'])
                empates = len(df_time[df_time['resultado'] == 'Empate'])
                derrotas = len(df_time[df_time['resultado'] == 'Derrota'])
                print(f"  {time}: {len(df_time)} jogos - {vitorias}V {empates}E {derrotas}D")
            
            print(f"\nExemplo (primeiras 10 partidas):")
            print(df_combined[['data', 'time', 'local', 'adversario', 'placar', 'resultado', 'competicao']].head(10).to_string())
            
            print("\n" + "=" * 70)
            print("SUCESSO! Teste concluido com sucesso!")
            print("=" * 70)
            print("\nPara buscar todos os 20 times, execute: python get_team_matches.py")
            
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
    # Busca últimas 20 partidas de apenas 3 times para teste
    get_teams_matches_test(teams_to_test=3, limit_per_team=20)

