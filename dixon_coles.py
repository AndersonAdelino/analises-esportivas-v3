"""
Implementação do modelo Dixon-Coles para predição de resultados de futebol

O modelo Dixon-Coles é uma extensão do modelo de Poisson que considera:
- Força de ataque e defesa dos times
- Vantagem de jogar em casa
- Correlação entre gols baixos (parâmetro rho)

Referência: Dixon, M. J., & Coles, S. G. (1997). Modelling Association Football Scores 
and Inefficiencies in the Football Betting Market.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson
from datetime import datetime
from glob import glob
import os


class DixonColesModel:
    """Modelo Dixon-Coles para predição de resultados de futebol"""
    
    def __init__(self, xi=0.0):
        """
        Inicializa o modelo Dixon-Coles
        
        Args:
            xi: Fator de decaimento temporal (0 = sem decaimento)
        """
        self.xi = xi
        self.params = None
        self.teams = None
        self.home_advantage = None
        
    def rho_correction(self, home_goals, away_goals, lambda_home, lambda_away, rho):
        """
        Calcula a correção rho para resultados baixos (0-0, 1-0, 0-1, 1-1)
        
        Args:
            home_goals: Gols do time da casa
            away_goals: Gols do time visitante
            lambda_home: Lambda esperado (casa)
            lambda_away: Lambda esperado (fora)
            rho: Parâmetro de correlação
            
        Returns:
            Fator de correção tau
        """
        if home_goals == 0 and away_goals == 0:
            return 1 - lambda_home * lambda_away * rho
        elif home_goals == 0 and away_goals == 1:
            return 1 + lambda_home * rho
        elif home_goals == 1 and away_goals == 0:
            return 1 + lambda_away * rho
        elif home_goals == 1 and away_goals == 1:
            return 1 - rho
        else:
            return 1.0
    
    def dc_log_likelihood(self, params, home_teams, away_teams, home_goals, away_goals, weights=None):
        """
        Calcula a log-verossimilhança negativa para otimização
        
        Args:
            params: Parâmetros do modelo [home_adv, rho, attack_params..., defense_params...]
            home_teams: Índices dos times da casa
            away_teams: Índices dos times visitantes
            home_goals: Gols marcados pelo time da casa
            away_goals: Gols marcados pelo time visitante
            weights: Pesos temporais (opcional)
            
        Returns:
            Log-verossimilhança negativa
        """
        n_teams = len(self.teams)
        home_advantage = params[0]
        rho = params[1]
        
        attack_params = params[2:2+n_teams]
        defense_params = params[2+n_teams:]
        
        # Normalização: média de ataque = média de defesa = 0
        attack_params = attack_params - np.mean(attack_params)
        defense_params = defense_params - np.mean(defense_params)
        
        if weights is None:
            weights = np.ones(len(home_teams))
        
        # Calcula lambdas esperados
        lambda_home = np.exp(home_advantage + attack_params[home_teams] - defense_params[away_teams])
        lambda_away = np.exp(attack_params[away_teams] - defense_params[home_teams])
        
        # Log-verossimilhança de Poisson
        log_lik_home = poisson.logpmf(home_goals, lambda_home)
        log_lik_away = poisson.logpmf(away_goals, lambda_away)
        
        # Aplica correção rho
        rho_corr = np.array([
            self.rho_correction(hg, ag, lh, la, rho)
            for hg, ag, lh, la in zip(home_goals, away_goals, lambda_home, lambda_away)
        ])
        
        log_lik = weights * (log_lik_home + log_lik_away + np.log(rho_corr))
        
        return -log_lik.sum()
    
    def fit(self, df, time_decay=True):
        """
        Treina o modelo Dixon-Coles
        
        Args:
            df: DataFrame com colunas ['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data']
            time_decay: Se True, aplica decaimento temporal aos dados
            
        Returns:
            self
        """
        # Prepara dados
        df = df.copy()
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        
        # Lista de times únicos
        self.teams = sorted(list(set(df['time_casa'].unique()) | set(df['time_visitante'].unique())))
        team_to_idx = {team: idx for idx, team in enumerate(self.teams)}
        
        # Converte times para índices
        home_teams = df['time_casa'].map(team_to_idx).values
        away_teams = df['time_visitante'].map(team_to_idx).values
        home_goals = df['gols_casa'].values
        away_goals = df['gols_visitante'].values
        
        # Calcula pesos temporais se time_decay=True
        weights = None
        if time_decay and self.xi > 0:
            max_date = df['data'].max()
            days_diff = (max_date - df['data']).dt.days
            weights = np.exp(-self.xi * days_diff / 365.25)
        
        # Chute inicial para parâmetros
        n_teams = len(self.teams)
        init_params = np.concatenate([
            [0.3],  # home advantage
            [0.0],  # rho
            np.random.normal(0, 0.1, n_teams),  # attack
            np.random.normal(0, 0.1, n_teams)   # defense
        ])
        
        # Otimização
        print("Treinando modelo Dixon-Coles...")
        print(f"- Times: {n_teams}")
        print(f"- Partidas: {len(df)}")
        print(f"- Decaimento temporal: {time_decay} (xi={self.xi})")
        
        options = {'maxiter': 100, 'disp': False}
        
        result = minimize(
            self.dc_log_likelihood,
            init_params,
            args=(home_teams, away_teams, home_goals, away_goals, weights),
            method='BFGS',
            options=options
        )
        
        if result.success:
            print("Otimizacao concluida com sucesso!")
        else:
            print(f"AVISO: Otimizacao nao convergiu completamente: {result.message}")
        
        # Extrai parâmetros otimizados
        self.params = result.x
        self.home_advantage = result.x[0]
        self.rho = result.x[1]
        
        attack_params = result.x[2:2+n_teams]
        defense_params = result.x[2+n_teams:]
        
        # Normaliza
        attack_params = attack_params - np.mean(attack_params)
        defense_params = defense_params - np.mean(defense_params)
        
        self.attack = {team: attack_params[idx] for team, idx in team_to_idx.items()}
        self.defense = {team: defense_params[idx] for team, idx in team_to_idx.items()}
        
        print(f"- Home advantage: {self.home_advantage:.3f}")
        print(f"- Rho (correlacao): {self.rho:.3f}")
        
        return self
    
    def predict_goals(self, home_team, away_team):
        """
        Prediz lambdas esperados para uma partida
        
        Args:
            home_team: Nome do time da casa
            away_team: Nome do time visitante
            
        Returns:
            (lambda_home, lambda_away)
        """
        if home_team not in self.teams or away_team not in self.teams:
            raise ValueError(f"Time nao encontrado no modelo: {home_team} ou {away_team}")
        
        lambda_home = np.exp(
            self.home_advantage + 
            self.attack[home_team] - 
            self.defense[away_team]
        )
        
        lambda_away = np.exp(
            self.attack[away_team] - 
            self.defense[home_team]
        )
        
        return lambda_home, lambda_away
    
    def predict_score_probabilities(self, home_team, away_team, max_goals=10):
        """
        Calcula probabilidades para todos os placares até max_goals
        
        Args:
            home_team: Time da casa
            away_team: Time visitante
            max_goals: Número máximo de gols a considerar
            
        Returns:
            Matriz de probabilidades [gols_casa][gols_fora]
        """
        lambda_home, lambda_away = self.predict_goals(home_team, away_team)
        
        # Matriz de probabilidades
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob_poisson = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
                tau = self.rho_correction(i, j, lambda_home, lambda_away, self.rho)
                prob_matrix[i, j] = prob_poisson * tau
        
        # Normaliza
        prob_matrix = prob_matrix / prob_matrix.sum()
        
        return prob_matrix
    
    def predict_match(self, home_team, away_team, max_goals=10):
        """
        Gera predições completas para uma partida
        
        Args:
            home_team: Time da casa
            away_team: Time visitante
            max_goals: Número máximo de gols
            
        Returns:
            Dicionário com todas as probabilidades
        """
        lambda_home, lambda_away = self.predict_goals(home_team, away_team)
        prob_matrix = self.predict_score_probabilities(home_team, away_team, max_goals)
        
        # Probabilidades de resultado (1X2)
        prob_home_win = np.tril(prob_matrix, -1).sum()  # Casa ganha
        prob_draw = np.trace(prob_matrix)  # Empate
        prob_away_win = np.triu(prob_matrix, 1).sum()  # Fora ganha
        
        # Over/Under 2.5 gols
        prob_under_2_5 = sum([prob_matrix[i, j] 
                              for i in range(max_goals + 1) 
                              for j in range(max_goals + 1) 
                              if i + j < 2.5])
        prob_over_2_5 = 1 - prob_under_2_5
        
        # Ambos marcam (BTTS)
        prob_btts_yes = sum([prob_matrix[i, j] 
                             for i in range(1, max_goals + 1) 
                             for j in range(1, max_goals + 1)])
        prob_btts_no = 1 - prob_btts_yes
        
        # Placares mais prováveis
        top_scores = []
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                top_scores.append(((i, j), prob_matrix[i, j]))
        top_scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'lambda_home': lambda_home,
            'lambda_away': lambda_away,
            'expected_goals_home': lambda_home,
            'expected_goals_away': lambda_away,
            'prob_home_win': prob_home_win,
            'prob_draw': prob_draw,
            'prob_away_win': prob_away_win,
            'prob_over_2_5': prob_over_2_5,
            'prob_under_2_5': prob_under_2_5,
            'prob_btts_yes': prob_btts_yes,
            'prob_btts_no': prob_btts_no,
            'top_scores': top_scores[:10],  # Top 10 placares
            'prob_matrix': prob_matrix
        }
    
    def get_team_strengths(self):
        """
        Retorna força de ataque e defesa de todos os times
        
        Returns:
            DataFrame com estatísticas dos times
        """
        data = []
        for team in self.teams:
            data.append({
                'Time': team,
                'Ataque': self.attack[team],
                'Defesa': self.defense[team],
                'Forca_Total': self.attack[team] - self.defense[team]
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values('Forca_Total', ascending=False).reset_index(drop=True)
        return df


def print_prediction(prediction):
    """Imprime predição de forma formatada"""
    print("=" * 80)
    print(f"{prediction['home_team']} vs {prediction['away_team']}")
    print("=" * 80)
    
    print(f"\nGols Esperados:")
    print(f"  {prediction['home_team']}: {prediction['expected_goals_home']:.2f}")
    print(f"  {prediction['away_team']}: {prediction['expected_goals_away']:.2f}")
    
    print(f"\nProbabilidades de Resultado (1X2):")
    print(f"  Vitoria {prediction['home_team']}: {prediction['prob_home_win']*100:.1f}%")
    print(f"  Empate: {prediction['prob_draw']*100:.1f}%")
    print(f"  Vitoria {prediction['away_team']}: {prediction['prob_away_win']*100:.1f}%")
    
    print(f"\nOver/Under 2.5 Gols:")
    print(f"  Over 2.5: {prediction['prob_over_2_5']*100:.1f}%")
    print(f"  Under 2.5: {prediction['prob_under_2_5']*100:.1f}%")
    
    print(f"\nAmbas Equipes Marcam (BTTS):")
    print(f"  Sim: {prediction['prob_btts_yes']*100:.1f}%")
    print(f"  Nao: {prediction['prob_btts_no']*100:.1f}%")
    
    print(f"\nPlacares Mais Provaveis:")
    for i, ((home_goals, away_goals), prob) in enumerate(prediction['top_scores'][:10], 1):
        print(f"  {i:2d}. {home_goals}-{away_goals}: {prob*100:.2f}%")
    
    print("=" * 80)


def load_match_data_from_api(league_code=None):
    """
    Carrega dados de partidas diretamente da API
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
    
    Returns:
        DataFrame com colunas: time_casa, time_visitante, gols_casa, gols_visitante, data
    """
    from api_client import FootballDataClient
    from config import PREMIER_LEAGUE_CODE
    
    if league_code is None:
        league_code = PREMIER_LEAGUE_CODE
    
    try:
        client = FootballDataClient()
        # Busca partidas finalizadas (últimos 90 dias tem mais dados)
        matches_data = client.get_competition_matches(league_code, status='FINISHED', limit=100)
        
        matches_list = []
        for match in matches_data.get('matches', []):
            if match['status'] != 'FINISHED':
                continue
                
            score = match.get('score', {}).get('fullTime', {})
            if score.get('home') is None or score.get('away') is None:
                continue
            
            matches_list.append({
                'time_casa': match['homeTeam']['name'],
                'time_visitante': match['awayTeam']['name'],
                'gols_casa': score['home'],
                'gols_visitante': score['away'],
                'data': match['utcDate'][:10]  # YYYY-MM-DD
            })
        
        if not matches_list:
            raise ValueError(f"Nenhuma partida finalizada encontrada para {league_code}")
        
        return pd.DataFrame(matches_list)
    
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados da API: {e}")


def load_match_data(league_code=None):
    """
    Carrega dados de partidas do arquivo mais recente ou da API
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA'). Se None, carrega Premier League
    
    Returns:
        DataFrame com colunas: time_casa, time_visitante, gols_casa, gols_visitante, data
    """
    from config import LEAGUES, PREMIER_LEAGUE_CODE
    
    if league_code is None:
        league_code = PREMIER_LEAGUE_CODE
    
    # Mapeia code para nome do arquivo
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a') 
                      for name, info in LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'league')
    
    # Busca arquivos da liga específica
    csv_files = glob(f'data/{league_prefix}_matches_*.csv')
    
    # Se não encontrou arquivos específicos, tenta o formato antigo
    if not csv_files:
        csv_files = glob('data/all_teams_matches_*.csv')
    
    if not csv_files:
        # Sem arquivos locais, tenta buscar da API
        print(f"Nenhum arquivo local encontrado. Buscando dados da API...")
        return load_match_data_from_api(league_code)
    
    csv_file = max(csv_files, key=os.path.getctime)
    print(f"Carregando dados de: {csv_file}")
    
    df = pd.read_csv(csv_file)
    
    # Ajusta para considerar o local (casa/fora)
    # Separa jogos em casa e fora
    df_fora = df[df['local'] == 'Fora'].copy()
    df_casa = df[df['local'] == 'Casa'].copy()
    
    # Para jogos fora, inverte casa/visitante (pois o time jogou fora)
    df_fora_adjusted = df_fora.copy()
    df_fora_adjusted['time_casa'] = df_fora['adversario']
    df_fora_adjusted['time_visitante'] = df_fora['time']
    df_fora_adjusted['gols_casa'] = df_fora['gols_sofridos']
    df_fora_adjusted['gols_visitante'] = df_fora['gols_marcados']
    
    # Para jogos em casa, o time é o mandante
    df_casa_adjusted = df_casa.copy()
    df_casa_adjusted['time_casa'] = df_casa['time']
    df_casa_adjusted['time_visitante'] = df_casa['adversario']
    df_casa_adjusted['gols_casa'] = df_casa['gols_marcados']
    df_casa_adjusted['gols_visitante'] = df_casa['gols_sofridos']
    
    # Combina tudo
    df_final = pd.concat([df_casa_adjusted, df_fora_adjusted], ignore_index=True)
    
    # Filtra pela liga específica
    league_full_name = [info['name'] for name, info in LEAGUES.items() if info['code'] == league_code][0]
    if 'competicao' in df_final.columns:
        # Tenta filtrar pelo nome completo da liga
        df_final = df_final[df_final['competicao'].str.contains(league_full_name.split()[0], na=False, case=False)]
    
    return df_final[['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data']]


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("MODELO DIXON-COLES - PREDICAO DE RESULTADOS DE FUTEBOL")
    print("=" * 80)
    print("\n")
    
    # Carrega dados
    df = load_match_data()
    print(f"Total de partidas carregadas: {len(df)}")
    print(f"Times unicos: {len(set(df['time_casa'].unique()) | set(df['time_visitante'].unique()))}")
    print()
    
    # Treina modelo
    model = DixonColesModel(xi=0.003)  # Pequeno decaimento temporal
    model.fit(df, time_decay=True)
    
    print("\n")
    print("=" * 80)
    print("FORCAS DOS TIMES")
    print("=" * 80)
    strengths = model.get_team_strengths()
    print(strengths.to_string(index=False))
    
    print("\n")
    print("=" * 80)
    print("EXEMPLOS DE PREDICOES")
    print("=" * 80)
    print("\n")
    
    # Exemplos de predições
    matches_to_predict = [
        ('Arsenal FC', 'Manchester City FC'),
        ('Liverpool FC', 'Chelsea FC'),
        ('Manchester United FC', 'Tottenham Hotspur FC'),
    ]
    
    for home, away in matches_to_predict:
        try:
            prediction = model.predict_match(home, away)
            print_prediction(prediction)
            print("\n")
        except ValueError as e:
            print(f"Erro ao prever {home} vs {away}: {e}\n")
    
    print("=" * 80)
    print("MODELO TREINADO COM SUCESSO!")
    print("=" * 80)
    print("\nPara fazer suas proprias predicoes, use:")
    print("  from dixon_coles import DixonColesModel, load_match_data")
    print("  df = load_match_data()")
    print("  model = DixonColesModel(xi=0.003)")
    print("  model.fit(df)")
    print("  prediction = model.predict_match('Time Casa', 'Time Visitante')")
    print()

