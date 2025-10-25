"""
Sistema de Apostas Múltiplas (Bingo)

Analisa palpites do dia e gera UMA cartela otimizada com 3-5 jogos,
selecionando automaticamente os melhores palpites com base em EV e probabilidade.
"""

from datetime import datetime, date
from itertools import combinations
import numpy as np


class BingoAnalyzer:
    """Analisador de apostas múltiplas - Gera a MELHOR cartela do dia"""
    
    def __init__(self):
        """Inicializa o analisador com cache vazio"""
        self.cache = []
        self.cache_date = None
        
    def add_analysis(self, match_info, bet_type, analysis):
        """
        Adiciona uma análise ao cache do dia
        
        Args:
            match_info: Dict com informações da partida (home_team, away_team, date, match_id)
            bet_type: Tipo de aposta (ex: "🏠 Vitória Casa", "📈 Over 2.5")
            analysis: Dict com análise completa do betting_tools.analyze_bet()
        """
        # Verifica se é um novo dia (limpa cache)
        today = date.today()
        if self.cache_date != today:
            self.cache = []
            self.cache_date = today
        
        # Adiciona ao cache
        bet_entry = {
            'match_info': match_info,
            'bet_type': bet_type,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        self.cache.append(bet_entry)
        
    def get_cached_analyses(self):
        """
        Retorna todas as análises em cache do dia
        
        Returns:
            Lista de análises
        """
        # Verifica se é um novo dia
        today = date.today()
        if self.cache_date != today:
            self.cache = []
            self.cache_date = today
        
        return self.cache
    
    def get_unique_matches(self):
        """
        Retorna lista de partidas únicas no cache
        
        Returns:
            Lista de match_ids únicos
        """
        matches = set()
        for bet in self.cache:
            match_id = bet['match_info'].get('match_id', 
                                            f"{bet['match_info']['home_team']}_vs_{bet['match_info']['away_team']}")
            matches.add(match_id)
        return list(matches)
    
    def generate_best_cartela(self, min_bets=3, max_bets=5, min_ev_percent=3.0, 
                             min_prob_percent=35.0, stake=100.0):
        """
        Gera A MELHOR cartela possível do dia
        
        Estratégia:
        1. Filtra palpites que atendem critérios mínimos
        2. Seleciona o melhor palpite de cada partida
        3. Gera TODAS as combinações possíveis de N jogos
        4. Calcula métricas de cada combinação
        5. Ranqueia e retorna a TOP 1
        
        Args:
            min_bets: Mínimo de jogos na cartela (3-5)
            max_bets: Máximo de jogos na cartela (3-5)
            min_ev_percent: EV% mínimo de cada palpite
            min_prob_percent: Probabilidade% mínima de cada palpite
            stake: Valor a apostar na cartela
            
        Returns:
            Dict com a melhor cartela ou None se não encontrar
        """
        # Validação
        if len(self.get_unique_matches()) < min_bets:
            return None
        
        # Filtrar palpites que atendem critérios
        filtered_bets = self._filter_bets(min_ev_percent, min_prob_percent)
        
        if not filtered_bets:
            return None
        
        # Selecionar melhor palpite de cada partida
        best_per_match = self._filter_best_bet_per_match(filtered_bets)
        
        if len(best_per_match) < min_bets:
            return None
        
        # Gerar todas as combinações possíveis
        all_cartelas = []
        
        for num_bets in range(min_bets, min(max_bets + 1, len(best_per_match) + 1)):
            combos = combinations(best_per_match, num_bets)
            
            for combo in combos:
                cartela = self._calculate_cartela_metrics(list(combo), stake)
                cartela['bets'] = list(combo)
                all_cartelas.append(cartela)
        
        if not all_cartelas:
            return None
        
        # Ranquear cartelas e retornar a melhor
        all_cartelas.sort(key=lambda c: c['quality_score'], reverse=True)
        best_cartela = all_cartelas[0]
        
        # Adicionar info de quantas combinações foram analisadas
        best_cartela['total_combinations_analyzed'] = len(all_cartelas)
        
        return best_cartela
    
    def _filter_bets(self, min_ev_percent, min_prob_percent):
        """
        Filtra palpites que atendem critérios mínimos
        
        Args:
            min_ev_percent: EV% mínimo
            min_prob_percent: Probabilidade% mínima
            
        Returns:
            Lista de palpites filtrados
        """
        filtered = []
        
        for bet in self.cache:
            ev_percent = bet['analysis']['ev']['ev_percent']
            prob_percent = bet['analysis']['prob_real'] * 100
            
            if ev_percent >= min_ev_percent and prob_percent >= min_prob_percent:
                # Adiciona score ao palpite
                bet['score'] = self._calculate_bet_score(bet)
                filtered.append(bet)
        
        return filtered
    
    def _calculate_bet_score(self, bet):
        """
        Calcula score de qualidade do palpite
        
        Score = (EV% * 0.6) + (Prob% * 0.4)
        Balanceia value com confiabilidade
        
        Args:
            bet: Dict com palpite
            
        Returns:
            Score numérico
        """
        ev_percent = bet['analysis']['ev']['ev_percent']
        prob_percent = bet['analysis']['prob_real'] * 100
        
        score = (ev_percent * 0.6) + (prob_percent * 0.4)
        return score
    
    def _filter_best_bet_per_match(self, bets_list):
        """
        Para cada partida, seleciona apenas o MELHOR palpite
        
        Args:
            bets_list: Lista de palpites filtrados
            
        Returns:
            Lista com melhor palpite de cada partida
        """
        # Agrupa por partida
        matches_dict = {}
        
        for bet in bets_list:
            match_id = bet['match_info'].get('match_id',
                                            f"{bet['match_info']['home_team']}_vs_{bet['match_info']['away_team']}")
            
            if match_id not in matches_dict:
                matches_dict[match_id] = []
            
            matches_dict[match_id].append(bet)
        
        # Seleciona o melhor de cada partida (maior score)
        best_bets = []
        for match_id, bets in matches_dict.items():
            best_bet = max(bets, key=lambda b: b['score'])
            best_bets.append(best_bet)
        
        return best_bets
    
    def _calculate_cartela_metrics(self, bets_list, stake):
        """
        Calcula métricas de uma cartela
        
        Args:
            bets_list: Lista de palpites da cartela
            stake: Valor apostado
            
        Returns:
            Dict com métricas calculadas
        """
        # Odds multiplicadas
        odd_total = 1.0
        for bet in bets_list:
            odd_total *= bet['analysis']['odds']
        
        # Probabilidade combinada (produto)
        prob_combined = 1.0
        for bet in bets_list:
            prob_combined *= bet['analysis']['prob_real']
        
        # Retorno e lucro potencial
        potential_return = stake * odd_total
        potential_profit = potential_return - stake
        
        # Expected profit (EV da múltipla)
        expected_profit = (prob_combined * potential_return) - stake
        
        # EV% e ROI%
        ev_percent = (expected_profit / stake) * 100
        roi_percent = ev_percent
        
        # Quality score
        # Score = (EV% * 0.5) + (Prob% * 30) + (NumJogos * 2)
        # Favorece bom EV, probabilidade razoável, mais jogos
        quality_score = (ev_percent * 0.5) + (prob_combined * 100 * 0.3) + (len(bets_list) * 2)
        
        return {
            'num_bets': len(bets_list),
            'odd_total': odd_total,
            'prob_combined': prob_combined,
            'stake': stake,
            'potential_return': potential_return,
            'potential_profit': potential_profit,
            'expected_profit': expected_profit,
            'ev_percent': ev_percent,
            'roi_percent': roi_percent,
            'quality_score': quality_score
        }
    
    def clear_cache(self):
        """Limpa o cache (usado para testes ou reset manual)"""
        self.cache = []
        self.cache_date = None


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SISTEMA DE APOSTAS MÚLTIPLAS (BINGO) - TESTE")
    print("=" * 80)
    
    # Criar analyzer
    analyzer = BingoAnalyzer()
    
    # Simular algumas análises
    from betting_tools import analyze_bet
    
    print("\nSimulando análises de 4 partidas...")
    
    # Partida 1: Arsenal vs Chelsea
    match1 = {
        'home_team': 'Arsenal FC',
        'away_team': 'Chelsea FC',
        'date': '2025-10-26',
        'match_id': 'arsenal_vs_chelsea'
    }
    analysis1 = analyze_bet(prob_win=0.55, odds_decimal=2.10, bankroll=1000, kelly_fraction=0.25)
    analyzer.add_analysis(match1, '🏠 Vitória Casa', analysis1)
    
    # Partida 2: Liverpool vs Man City
    match2 = {
        'home_team': 'Liverpool FC',
        'away_team': 'Manchester City FC',
        'date': '2025-10-26',
        'match_id': 'liverpool_vs_mancity'
    }
    analysis2 = analyze_bet(prob_win=0.65, odds_decimal=1.75, bankroll=1000, kelly_fraction=0.25)
    analyzer.add_analysis(match2, '📈 Over 2.5', analysis2)
    
    # Partida 3: Tottenham vs Brighton
    match3 = {
        'home_team': 'Tottenham Hotspur FC',
        'away_team': 'Brighton & Hove Albion FC',
        'date': '2025-10-26',
        'match_id': 'tottenham_vs_brighton'
    }
    analysis3 = analyze_bet(prob_win=0.60, odds_decimal=1.90, bankroll=1000, kelly_fraction=0.25)
    analyzer.add_analysis(match3, '✅ BTTS Sim', analysis3)
    
    # Partida 4: Newcastle vs Wolves
    match4 = {
        'home_team': 'Newcastle United FC',
        'away_team': 'Wolverhampton Wanderers FC',
        'date': '2025-10-26',
        'match_id': 'newcastle_vs_wolves'
    }
    analysis4 = analyze_bet(prob_win=0.50, odds_decimal=2.20, bankroll=1000, kelly_fraction=0.25)
    analyzer.add_analysis(match4, '🏠 Vitória Casa', analysis4)
    
    print(f"OK - {len(analyzer.get_cached_analyses())} analises adicionadas ao cache")
    print(f"OK - {len(analyzer.get_unique_matches())} partidas diferentes")
    
    # Gerar a melhor cartela
    print("\nGerando a MELHOR cartela...")
    cartela = analyzer.generate_best_cartela(
        min_bets=3,
        max_bets=4,
        min_ev_percent=5.0,
        min_prob_percent=40.0,
        stake=100.0
    )
    
    if cartela:
        print("\n" + "=" * 80)
        print("MELHOR CARTELA DO DIA")
        print("=" * 80)
        print(f"\nMETRICAS:")
        print(f"  Numero de jogos:        {cartela['num_bets']}")
        print(f"  Odd total:              {cartela['odd_total']:.2f}")
        print(f"  Probabilidade:          {cartela['prob_combined']*100:.2f}%")
        print(f"  Score de qualidade:     {cartela['quality_score']:.2f}")
        
        print(f"\nFINANCEIRO:")
        print(f"  Investimento:           R$ {cartela['stake']:.2f}")
        print(f"  Retorno potencial:      R$ {cartela['potential_return']:.2f}")
        print(f"  Lucro potencial:        R$ {cartela['potential_profit']:.2f}")
        print(f"  Lucro esperado (EV):    R$ {cartela['expected_profit']:+.2f}")
        print(f"  EV%:                    {cartela['ev_percent']:+.2f}%")
        print(f"  ROI esperado:           {cartela['roi_percent']:+.2f}%")
        
        print(f"\nPALPITES ({len(cartela['bets'])} jogos):")
        for idx, bet in enumerate(cartela['bets'], 1):
            print(f"\n  {idx}. {bet['match_info']['home_team']} vs {bet['match_info']['away_team']}")
            # Remove emojis do bet_type para display no terminal
            bet_type_clean = bet['bet_type'].encode('ascii', 'ignore').decode('ascii')
            print(f"     Palpite: {bet_type_clean}")
            print(f"     Odd: {bet['analysis']['odds']:.2f}")
            print(f"     Probabilidade: {bet['analysis']['prob_real']*100:.1f}%")
            print(f"     EV%: {bet['analysis']['ev']['ev_percent']:+.1f}%")
            print(f"     Score: {bet['score']:.2f}")
        
        print(f"\nANALISE:")
        print(f"  Combinacoes analisadas: {cartela['total_combinations_analyzed']}")
        
        print("\n" + "=" * 80)
        print("CARTELA GERADA COM SUCESSO!")
        print("=" * 80 + "\n")
    else:
        print("\nERRO: Nao foi possivel gerar cartela com os filtros especificados.")

