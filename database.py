"""
Sistema de Banco de Dados para Persistência de Dados das Ligas
Resolve o problema de perda de dados ao reiniciar o sistema
"""

import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import config


class FootballDatabase:
    """Gerenciador de banco de dados SQLite para dados de futebol"""
    
    def __init__(self, db_path='data/football_data.db'):
        """
        Inicializa conexão com o banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        # Garante que o diretório existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Estabelece conexão com o banco de dados"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        cursor = self.conn.cursor()
        
        # Tabela de partidas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER UNIQUE,
                league_code TEXT NOT NULL,
                league_name TEXT,
                season TEXT,
                date TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_goals INTEGER NOT NULL,
                away_goals INTEGER NOT NULL,
                winner TEXT,
                competition TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de times
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                short_name TEXT,
                tla TEXT,
                league_code TEXT NOT NULL,
                founded INTEGER,
                venue TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de atualizações (log de quando dados foram coletados)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS updates_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                league_code TEXT NOT NULL,
                update_type TEXT NOT NULL,
                matches_count INTEGER,
                teams_count INTEGER,
                success BOOLEAN,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Índices para melhorar performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_matches_league 
            ON matches(league_code)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_matches_date 
            ON matches(date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_teams_league 
            ON teams(league_code)
        """)
        
        self.conn.commit()
    
    def insert_matches(self, df, league_code):
        """
        Insere ou atualiza partidas no banco de dados
        
        Args:
            df: DataFrame com dados das partidas
            league_code: Código da liga (ex: 'PL', 'BSA')
            
        Returns:
            Número de partidas inseridas/atualizadas
        """
        cursor = self.conn.cursor()
        count = 0
        
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO matches 
                    (match_id, league_code, league_name, season, date, home_team, away_team, 
                     home_goals, away_goals, winner, competition, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    row.get('match_id'),
                    league_code,
                    self._get_league_name(league_code),
                    row.get('temporada', row.get('season')),
                    row.get('data', row.get('date')),
                    row.get('time_casa', row.get('home_team', row.get('time'))),
                    row.get('time_visitante', row.get('away_team', row.get('adversario'))),
                    int(row.get('gols_casa', row.get('home_goals', row.get('gols_marcados', 0)))),
                    int(row.get('gols_visitante', row.get('away_goals', row.get('gols_sofridos', 0)))),
                    row.get('winner', row.get('resultado')),
                    row.get('competicao', row.get('competition')),
                    row.get('status', 'FINISHED')
                ))
                count += 1
            except Exception as e:
                print(f"Erro ao inserir partida {row.get('match_id')}: {e}")
                continue
        
        self.conn.commit()
        return count
    
    def insert_teams(self, teams_data, league_code):
        """
        Insere ou atualiza times no banco de dados
        
        Args:
            teams_data: Lista de dicionários com dados dos times
            league_code: Código da liga
            
        Returns:
            Número de times inseridos/atualizados
        """
        cursor = self.conn.cursor()
        count = 0
        
        for team in teams_data:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO teams 
                    (team_id, name, short_name, tla, league_code, founded, venue, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    team.get('id'),
                    team.get('name'),
                    team.get('shortName'),
                    team.get('tla'),
                    league_code,
                    team.get('founded'),
                    team.get('venue')
                ))
                count += 1
            except Exception as e:
                print(f"Erro ao inserir time {team.get('name')}: {e}")
                continue
        
        self.conn.commit()
        return count
    
    def log_update(self, league_code, update_type, matches_count=0, teams_count=0, 
                   success=True, message=''):
        """
        Registra uma atualização no log
        
        Args:
            league_code: Código da liga
            update_type: Tipo de atualização (ex: 'api_fetch', 'manual_import')
            matches_count: Número de partidas atualizadas
            teams_count: Número de times atualizados
            success: Se a atualização foi bem-sucedida
            message: Mensagem adicional
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO updates_log 
            (league_code, update_type, matches_count, teams_count, success, message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (league_code, update_type, matches_count, teams_count, success, message))
        self.conn.commit()
    
    def get_matches(self, league_code=None, limit=None, as_dataframe=True):
        """
        Recupera partidas do banco de dados
        
        Args:
            league_code: Código da liga (None para todas)
            limit: Limite de resultados
            as_dataframe: Se True, retorna DataFrame; se False, retorna lista de dicts
            
        Returns:
            DataFrame ou lista de partidas
        """
        query = "SELECT * FROM matches"
        params = []
        
        if league_code:
            query += " WHERE league_code = ?"
            params.append(league_code)
        
        query += " ORDER BY date DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if as_dataframe:
            return pd.read_sql_query(query, self.conn, params=params if params else None)
        else:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_teams(self, league_code=None, as_dataframe=True):
        """
        Recupera times do banco de dados
        
        Args:
            league_code: Código da liga (None para todos)
            as_dataframe: Se True, retorna DataFrame
            
        Returns:
            DataFrame ou lista de times
        """
        query = "SELECT * FROM teams"
        params = []
        
        if league_code:
            query += " WHERE league_code = ?"
            params.append(league_code)
        
        query += " ORDER BY name"
        
        if as_dataframe:
            return pd.read_sql_query(query, self.conn, params=params if params else None)
        else:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_last_update(self, league_code):
        """
        Retorna informações da última atualização de uma liga
        
        Args:
            league_code: Código da liga
            
        Returns:
            Dict com informações da última atualização ou None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM updates_log 
            WHERE league_code = ? AND success = 1
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (league_code,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_statistics(self, league_code=None):
        """
        Retorna estatísticas gerais do banco de dados
        
        Args:
            league_code: Código da liga (None para todas)
            
        Returns:
            Dict com estatísticas
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total de partidas
        if league_code:
            cursor.execute("SELECT COUNT(*) FROM matches WHERE league_code = ?", (league_code,))
        else:
            cursor.execute("SELECT COUNT(*) FROM matches")
        stats['total_matches'] = cursor.fetchone()[0]
        
        # Total de times
        if league_code:
            cursor.execute("SELECT COUNT(*) FROM teams WHERE league_code = ?", (league_code,))
        else:
            cursor.execute("SELECT COUNT(*) FROM teams")
        stats['total_teams'] = cursor.fetchone()[0]
        
        # Última atualização
        if league_code:
            cursor.execute("""
                SELECT MAX(timestamp) FROM updates_log 
                WHERE league_code = ? AND success = 1
            """, (league_code,))
        else:
            cursor.execute("SELECT MAX(timestamp) FROM updates_log WHERE success = 1")
        
        last_update = cursor.fetchone()[0]
        stats['last_update'] = last_update
        
        # Partidas por liga
        cursor.execute("""
            SELECT league_code, league_name, COUNT(*) as count 
            FROM matches 
            GROUP BY league_code, league_name
        """)
        stats['matches_by_league'] = [dict(row) for row in cursor.fetchall()]
        
        return stats
    
    def import_from_csv(self, csv_path, league_code):
        """
        Importa dados de um arquivo CSV existente
        
        Args:
            csv_path: Caminho para o arquivo CSV
            league_code: Código da liga
            
        Returns:
            Número de registros importados
        """
        try:
            df = pd.read_csv(csv_path)
            count = self.insert_matches(df, league_code)
            self.log_update(
                league_code, 
                'csv_import', 
                matches_count=count, 
                success=True,
                message=f'Imported from {csv_path}'
            )
            return count
        except Exception as e:
            self.log_update(
                league_code, 
                'csv_import', 
                success=False,
                message=f'Error importing from {csv_path}: {str(e)}'
            )
            raise
    
    def _get_league_name(self, league_code):
        """Helper para pegar nome da liga pelo código"""
        for name, info in config.LEAGUES.items():
            if info['code'] == league_code:
                return info['name']
        return league_code


# Instância global do banco de dados
_db_instance = None

def get_database():
    """
    Retorna instância única do banco de dados (Singleton)
    
    Returns:
        FootballDatabase instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = FootballDatabase()
    return _db_instance


# Funções de conveniência
def save_matches_to_db(df, league_code):
    """Salva partidas no banco de dados"""
    db = get_database()
    return db.insert_matches(df, league_code)


def get_matches_from_db(league_code=None, limit=None):
    """Recupera partidas do banco de dados"""
    db = get_database()
    return db.get_matches(league_code, limit)


def get_last_update_info(league_code):
    """Retorna informações da última atualização"""
    db = get_database()
    return db.get_last_update(league_code)

