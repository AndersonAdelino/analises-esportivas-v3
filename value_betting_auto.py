"""
Sistema Automático de Value Betting
Integra modelos preditivos com odds da Bet365
"""
from odds_api_client import OddsAPIClient
from ensemble import EnsembleModel
from config_economia import CASA_PREFERIDA, REGIAO_UNICA, MERCADOS_COMPLETOS, CACHE_HORAS
from config import LEAGUES
import pandas as pd
from datetime import datetime


class ValueBettingAuto:
    """Sistema automático de detecção de value bets"""
    
    def __init__(self, casa='bet365'):
        self.odds_client = OddsAPIClient()
        self.casa_preferida = casa
        self.regiao = REGIAO_UNICA
        self.mercados = MERCADOS_COMPLETOS
        self.cache_horas = CACHE_HORAS
    
    def buscar_odds_liga(self, league_code: str):
        """
        Busca odds de uma liga específica
        
        Args:
            league_code: Código da liga (BSA, PL, etc)
        
        Returns:
            Lista de partidas com odds
        """
        sport_key = self.odds_client.LEAGUE_MAPPING.get(league_code)
        
        if not sport_key:
            return []
        
        try:
            odds = self.odds_client.get_odds_with_cache(
                sport_key,
                max_cache_age_hours=self.cache_horas,
                regions=self.regiao,
                markets=self.mercados
            )
            return odds
        except Exception as e:
            print(f"Erro ao buscar odds de {league_code}: {e}")
            return []
    
    def extrair_odds_bet365(self, match):
        """
        Extrai odds da Bet365 de uma partida
        
        Args:
            match: Dados da partida
        
        Returns:
            Dicionário com odds
        """
        odds_resultado = {
            'casa': None,
            'empate': None,
            'fora': None,
            'over_2_5': None,
            'under_2_5': None,
            'btts_yes': None,
            'btts_no': None
        }
        
        # Busca Bet365 nos bookmakers
        for bookmaker in match.get('bookmakers', []):
            if bookmaker['key'] == self.casa_preferida or 'bet365' in bookmaker['key'].lower():
                
                for market in bookmaker.get('markets', []):
                    market_key = market['key']
                    
                    # 1X2
                    if market_key == 'h2h':
                        for outcome in market['outcomes']:
                            if outcome['name'] == match['home_team']:
                                odds_resultado['casa'] = outcome['price']
                            elif outcome['name'] == match['away_team']:
                                odds_resultado['fora'] = outcome['price']
                            else:
                                odds_resultado['empate'] = outcome['price']
                    
                    # Over/Under
                    elif market_key == 'totals':
                        for outcome in market['outcomes']:
                            point = outcome.get('point', 0)
                            if abs(point - 2.5) < 0.1:
                                if outcome['name'] == 'Over':
                                    odds_resultado['over_2_5'] = outcome['price']
                                elif outcome['name'] == 'Under':
                                    odds_resultado['under_2_5'] = outcome['price']
                    
                    # BTTS
                    elif market_key == 'btts':
                        for outcome in market['outcomes']:
                            if outcome['name'] == 'Yes':
                                odds_resultado['btts_yes'] = outcome['price']
                            elif outcome['name'] == 'No':
                                odds_resultado['btts_no'] = outcome['price']
                
                break
        
        return odds_resultado
    
    def calcular_probabilidades_modelo(self, home_team: str, away_team: str, league_code: str):
        """
        Calcula probabilidades usando os modelos
        
        NOTA: Esta é uma versão simplificada
        Em produção, você deve:
        1. Buscar dados históricos dos times
        2. Treinar o modelo com dados recentes
        3. Fazer predição real
        
        Args:
            home_team: Time da casa
            away_team: Time fora
            league_code: Liga
        
        Returns:
            Dicionário com probabilidades
        """
        # SIMULAÇÃO: Probabilidades fictícias
        # Em produção, substitua por cálculo real do modelo
        
        # Exemplo de como deveria ser:
        # model = EnsembleModel()
        # model.treinar_com_dados_historicos(league_code)
        # probs = model.predict(home_team, away_team)
        
        # Por enquanto, retorna probabilidades balanceadas
        import random
        
        home_prob = random.uniform(0.35, 0.50)
        away_prob = random.uniform(0.25, 0.35)
        draw_prob = 1 - home_prob - away_prob
        
        # Ajusta para somar 1
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # Over/Under 2.5 (simplificado)
        over_2_5_prob = random.uniform(0.45, 0.60)
        under_2_5_prob = 1 - over_2_5_prob
        
        # BTTS (simplificado)
        btts_yes_prob = random.uniform(0.45, 0.60)
        btts_no_prob = 1 - btts_yes_prob
        
        return {
            'home': home_prob,
            'draw': draw_prob,
            'away': away_prob,
            'over_2_5': over_2_5_prob,
            'under_2_5': under_2_5_prob,
            'btts_yes': btts_yes_prob,
            'btts_no': btts_no_prob
        }
    
    def calcular_value_bet(self, odd_mercado: float, prob_modelo: float, min_value: float = 1.05):
        """
        Calcula se há value bet
        
        Args:
            odd_mercado: Odd do mercado
            prob_modelo: Probabilidade do modelo
            min_value: Mínimo de value para considerar (1.05 = 5%)
        
        Returns:
            Dict com análise ou None se não houver value
        """
        if odd_mercado is None or prob_modelo is None or prob_modelo <= 0:
            return None
        
        odd_modelo = 1 / prob_modelo
        value = odd_mercado / odd_modelo
        
        if value >= min_value:
            ev = (odd_mercado * prob_modelo) - 1
            
            return {
                'odd_mercado': odd_mercado,
                'odd_modelo': odd_modelo,
                'prob_modelo': prob_modelo * 100,
                'value': value,
                'value_percent': (value - 1) * 100,
                'ev': ev * 100,
                'kelly': max(0, prob_modelo - (1 / odd_mercado)),
                'tem_value': True
            }
        
        return None
    
    def analisar_partida(self, match, league_code: str):
        """
        Analisa uma partida completa
        
        Args:
            match: Dados da partida
            league_code: Código da liga
        
        Returns:
            Lista de value bets encontrados
        """
        home_team = match['home_team']
        away_team = match['away_team']
        
        # Busca odds da Bet365
        odds = self.extrair_odds_bet365(match)
        
        # Se não tem odds, pula
        if not any(odds.values()):
            return []
        
        # Calcula probabilidades do modelo
        probs = self.calcular_probabilidades_modelo(home_team, away_team, league_code)
        
        # Analisa cada mercado
        value_bets = []
        
        # 1X2
        mercados_1x2 = [
            ('Casa', 'casa', 'home'),
            ('Empate', 'empate', 'draw'),
            ('Fora', 'fora', 'away')
        ]
        
        for nome, odd_key, prob_key in mercados_1x2:
            if odds[odd_key]:
                resultado = self.calcular_value_bet(odds[odd_key], probs[prob_key])
                if resultado:
                    value_bets.append({
                        'partida': f"{home_team} vs {away_team}",
                        'liga': league_code,
                        'data': match['commence_time'],
                        'mercado': '1X2',
                        'tipo': nome,
                        **resultado
                    })
        
        # Over/Under 2.5
        mercados_totals = [
            ('Over 2.5', 'over_2_5', 'over_2_5'),
            ('Under 2.5', 'under_2_5', 'under_2_5')
        ]
        
        for nome, odd_key, prob_key in mercados_totals:
            if odds[odd_key]:
                resultado = self.calcular_value_bet(odds[odd_key], probs[prob_key])
                if resultado:
                    value_bets.append({
                        'partida': f"{home_team} vs {away_team}",
                        'liga': league_code,
                        'data': match['commence_time'],
                        'mercado': 'Over/Under',
                        'tipo': nome,
                        **resultado
                    })
        
        # BTTS
        mercados_btts = [
            ('BTTS Sim', 'btts_yes', 'btts_yes'),
            ('BTTS Não', 'btts_no', 'btts_no')
        ]
        
        for nome, odd_key, prob_key in mercados_btts:
            if odds[odd_key]:
                resultado = self.calcular_value_bet(odds[odd_key], probs[prob_key])
                if resultado:
                    value_bets.append({
                        'partida': f"{home_team} vs {away_team}",
                        'liga': league_code,
                        'data': match['commence_time'],
                        'mercado': 'BTTS',
                        'tipo': nome,
                        **resultado
                    })
        
        return value_bets
    
    def analisar_todas_ligas(self, league_codes: list = None):
        """
        Analisa todas as ligas configuradas
        
        Args:
            league_codes: Lista de códigos de ligas (None = todas)
        
        Returns:
            DataFrame com todos os value bets
        """
        if league_codes is None:
            league_codes = list(LEAGUES.keys())
        
        todos_value_bets = []
        
        for league_name in league_codes:
            league_code = LEAGUES[league_name]['code']
            
            print(f"Analisando {league_name}...")
            
            # Busca odds
            matches = self.buscar_odds_liga(league_code)
            
            # Analisa cada partida
            for match in matches:
                value_bets = self.analisar_partida(match, league_code)
                todos_value_bets.extend(value_bets)
        
        if not todos_value_bets:
            return pd.DataFrame()
        
        # Cria DataFrame
        df = pd.DataFrame(todos_value_bets)
        
        # Ordena por EV (maior primeiro)
        df = df.sort_values('ev', ascending=False)
        
        return df


def main():
    """Teste do sistema"""
    print("=" * 80)
    print("SISTEMA AUTOMÁTICO DE VALUE BETTING")
    print("=" * 80)
    print(f"Casa: {CASA_PREFERIDA}")
    print(f"Região: {REGIAO_UNICA}")
    print(f"Mercados: {MERCADOS_COMPLETOS}")
    print("=" * 80)
    
    vb = ValueBettingAuto()
    
    # Analisa Brasileirão
    df = vb.analisar_todas_ligas(['Brasileirão Série A'])
    
    if len(df) > 0:
        print(f"\n✅ {len(df)} value bets encontrados!\n")
        print(df[['partida', 'mercado', 'tipo', 'odd_mercado', 'prob_modelo', 'value_percent', 'ev']].head(10))
    else:
        print("\n⚠️ Nenhum value bet encontrado no momento")


if __name__ == "__main__":
    main()

