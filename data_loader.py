"""
Carregador Universal de Dados com Persistência
Busca do banco SQLite primeiro, fallback para CSV se necessário
"""

import pandas as pd
import os
from glob import glob
from datetime import datetime
import config


def load_match_data(league_code=None):
    """
    Carrega dados de partidas com sistema de persistência
    
    Ordem de prioridade:
    1. CSV Persistente (data/persistent/*.csv) - Sobrevive a reboots ✅
    2. Banco SQLite (data/cache/*.db) - Cache rápido se disponível
    3. CSV Temporário (data/*.csv) - Fallback antigo
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
        
    Returns:
        DataFrame com colunas: time_casa, time_visitante, gols_casa, gols_visitante, data
    """
    if league_code is None:
        league_code = config.PREMIER_LEAGUE_CODE
    
    # Obtém nome da liga para exibição
    league_display = [name for name, info in config.LEAGUES.items() if info['code'] == league_code][0]
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a').replace('é', 'e')
                      for name, info in config.LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'league')
    
    # PRIORIDADE 1: CSV Persistente (commitado no Git - SEMPRE disponível após deploy!)
    persistent_csv = f'data/persistent/{league_prefix}_latest.csv'
    if os.path.exists(persistent_csv):
        try:
            df = pd.read_csv(persistent_csv)
            
            # Verifica se tem as colunas necessárias
            if all(col in df.columns for col in ['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data']):
                df_matches = df[['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data']].copy()
                df_matches['data'] = pd.to_datetime(df_matches['data'])
                df_matches = df_matches.sort_values('data', ascending=False).reset_index(drop=True)
                
                print(f"[PERSISTENT] Carregados {len(df_matches)} jogos de {league_display} (dados permanentes)")
                return df_matches
        except Exception as e:
            print(f"[!] Aviso: Erro ao carregar CSV persistente: {e}")
    
    # PRIORIDADE 2: Tentar buscar do banco de dados (cache rápido se disponível)
    try:
        from database import get_database
        db = get_database()
        df = db.get_matches(league_code=league_code)
        
        if len(df) > 0:
            # Mapeia colunas do banco para o formato esperado pelos modelos
            df_matches = pd.DataFrame({
                'time_casa': df['home_team'],
                'time_visitante': df['away_team'],
                'gols_casa': df['home_goals'],
                'gols_visitante': df['away_goals'],
                'data': pd.to_datetime(df['date'])
            })
            
            print(f"[CACHE] Carregados {len(df_matches)} jogos de {league_display} do cache local")
            return df_matches
            
    except Exception as e:
        print(f"[!] Aviso: Cache local nao disponivel: {e}")
    
    # PRIORIDADE 3: Fallback para CSV temporário (método antigo)
    
    csv_pattern = f'data/{league_prefix}_matches_*.csv'
    csv_files = glob(csv_pattern)
    
    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum dado encontrado para {league_display}.\n"
            f"Execute 'python get_team_matches.py' primeiro ou use COLETAR_DADOS.bat"
        )
    
    # Pega o arquivo CSV mais recente
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"[CSV] Carregando de {os.path.basename(latest_csv)}...")
    
    df = pd.read_csv(latest_csv)
    
    # Processa dados dependendo do formato do CSV
    if 'time_casa' in df.columns:
        # Formato direto (já processado)
        df_matches = df[['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data']].copy()
    else:
        # Formato bruto (de get_team_matches.py) - precisa processar
        matches_list = []
        
        for _, row in df.iterrows():
            # Identifica se foi jogo em casa ou fora
            if row['local'] == 'Casa':
                time_casa = row['time']
                time_visitante = row['adversario']
                gols_casa = row['gols_marcados']
                gols_visitante = row['gols_sofridos']
            else:  # Fora
                time_casa = row['adversario']
                time_visitante = row['time']
                gols_casa = row['gols_sofridos']
                gols_visitante = row['gols_marcados']
            
            # Filtra apenas jogos da liga desejada
            if row.get('competicao_code') == league_code:
                matches_list.append({
                    'time_casa': time_casa,
                    'time_visitante': time_visitante,
                    'gols_casa': gols_casa,
                    'gols_visitante': gols_visitante,
                    'data': row['data']
                })
        
        df_matches = pd.DataFrame(matches_list)
        
        # Remove duplicatas (mesma partida pode aparecer 2 vezes)
        df_matches = df_matches.drop_duplicates(
            subset=['time_casa', 'time_visitante', 'data'],
            keep='first'
        )
    
    # Converte data para datetime
    df_matches['data'] = pd.to_datetime(df_matches['data'])
    
    # Ordena por data (mais recente primeiro)
    df_matches = df_matches.sort_values('data', ascending=False).reset_index(drop=True)
    
    print(f"[CSV] Carregados {len(df_matches)} jogos de {league_display}")
    
    return df_matches


def load_team_history(team_name, league_code=None, limit=50):
    """
    Carrega histórico de um time específico
    
    Args:
        team_name: Nome do time
        league_code: Código da liga
        limit: Número máximo de jogos
        
    Returns:
        DataFrame com histórico do time
    """
    # Carrega todos os dados
    df_all = load_match_data(league_code)
    
    # Filtra jogos do time (casa ou fora)
    df_team = df_all[
        (df_all['time_casa'] == team_name) |
        (df_all['time_visitante'] == team_name)
    ].copy()
    
    # Limita resultados
    if limit and len(df_team) > limit:
        df_team = df_team.head(limit)
    
    return df_team


def get_data_info(league_code=None):
    """
    Retorna informações sobre os dados disponíveis
    
    Args:
        league_code: Código da liga
        
    Returns:
        Dict com informações (fonte, quantidade, última atualização, etc)
    """
    if league_code is None:
        league_code = config.PREMIER_LEAGUE_CODE
    
    info = {
        'league_code': league_code,
        'source': None,
        'total_matches': 0,
        'last_update': None,
        'teams_count': 0
    }
    
    # Tenta banco primeiro
    try:
        from database import get_database
        db = get_database()
        
        df = db.get_matches(league_code=league_code)
        if len(df) > 0:
            info['source'] = 'database'
            info['total_matches'] = len(df)
            
            # Última atualização
            last_update = db.get_last_update(league_code)
            if last_update:
                info['last_update'] = last_update['timestamp']
            
            # Conta times únicos
            teams = set(df['home_team'].unique()) | set(df['away_team'].unique())
            info['teams_count'] = len(teams)
            
            return info
    except:
        pass
    
    # Fallback para CSV
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a').replace('é', 'e')
                      for name, info in config.LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'league')
    
    csv_files = glob(f'data/{league_prefix}_matches_*.csv')
    
    if csv_files:
        latest_csv = max(csv_files, key=os.path.getctime)
        info['source'] = 'csv'
        
        df = pd.read_csv(latest_csv)
        info['total_matches'] = len(df)
        
        # Timestamp do arquivo
        file_time = datetime.fromtimestamp(os.path.getctime(latest_csv))
        info['last_update'] = file_time.isoformat()
    
    return info

