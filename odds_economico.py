"""
Cliente OTIMIZADO para economizar requisições
Usa apenas 1 casa de apostas como referência
"""
from odds_api_client import OddsAPIClient
from config_economia import CASA_PREFERIDA, REGIAO_UNICA, MERCADO_UNICO, CACHE_HORAS


class OddsEconomico:
    """Cliente otimizado que economiza requisições"""
    
    def __init__(self):
        self.client = OddsAPIClient()
        self.casa_preferida = CASA_PREFERIDA
        self.regiao = REGIAO_UNICA
        self.mercado = MERCADO_UNICO
        self.cache_horas = CACHE_HORAS
    
    def get_odds_economico(self, league_code: str):
        """
        Busca odds de forma econômica
        
        - Usa apenas 1 região
        - Usa apenas 1 mercado
        - Cache agressivo
        - Filtra apenas casa preferida
        
        Args:
            league_code: Código da liga (BSA, PL, etc)
        
        Returns:
            Lista de partidas com odds apenas da casa preferida
        """
        # Busca com configuração econômica
        odds_completas = self.client.get_odds_with_cache(
            self.client.LEAGUE_MAPPING.get(league_code),
            max_cache_age_hours=self.cache_horas,
            regions=self.regiao,
            markets=self.mercado
        )
        
        # Filtra apenas casa preferida
        odds_filtradas = []
        
        for match in odds_completas:
            # Cria cópia da partida
            match_filtrado = {
                'id': match['id'],
                'sport_key': match['sport_key'],
                'commence_time': match['commence_time'],
                'home_team': match['home_team'],
                'away_team': match['away_team'],
                'bookmakers': []
            }
            
            # Filtra apenas casa preferida
            for bookmaker in match.get('bookmakers', []):
                if bookmaker['key'] == self.casa_preferida:
                    match_filtrado['bookmakers'].append(bookmaker)
                    break
            
            # Se encontrou a casa, adiciona
            if match_filtrado['bookmakers']:
                odds_filtradas.append(match_filtrado)
        
        return odds_filtradas
    
    def get_odd_referencia(self, match):
        """
        Extrai a odd de referência da casa preferida
        
        Args:
            match: Dados da partida
        
        Returns:
            Dicionário com odds {casa, empate, fora}
        """
        if not match.get('bookmakers'):
            return None
        
        bookmaker = match['bookmakers'][0]
        
        odds = {'casa': None, 'empate': None, 'fora': None}
        
        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == match['home_team']:
                        odds['casa'] = outcome['price']
                    elif outcome['name'] == match['away_team']:
                        odds['fora'] = outcome['price']
                    else:
                        odds['empate'] = outcome['price']
        
        return odds
    
    def resumo_partidas(self, league_code: str):
        """
        Mostra resumo das partidas com odds da casa preferida
        
        Args:
            league_code: Código da liga
        """
        print("=" * 80)
        print(f"ODDS ECONÔMICAS - {league_code}")
        print("=" * 80)
        print(f"Casa de referência: {self.casa_preferida}")
        print(f"Região: {self.regiao}")
        print(f"Mercado: {self.mercado}")
        print(f"Cache: {self.cache_horas}h")
        print("=" * 80)
        
        odds = self.get_odds_economico(league_code)
        
        if not odds:
            print("\n⚠️ Nenhuma partida disponível no momento")
            print(f"\n💡 DICA: A casa '{self.casa_preferida}' pode não ter odds disponíveis")
            print("   Tente outra casa em config_economia.py")
            return
        
        print(f"\n✅ {len(odds)} partidas encontradas\n")
        
        for idx, match in enumerate(odds, 1):
            print(f"[{idx}] {match['home_team']} vs {match['away_team']}")
            
            odd = self.get_odd_referencia(match)
            
            if odd:
                if odd['casa']:
                    print(f"    Casa:   {odd['casa']:.2f}")
                if odd['empate']:
                    print(f"    Empate: {odd['empate']:.2f}")
                if odd['fora']:
                    print(f"    Fora:   {odd['fora']:.2f}")
            print()
    
    def comparar_com_modelo(self, league_code: str, home_prob: float, draw_prob: float, away_prob: float):
        """
        Compara odds da casa preferida com probabilidades do modelo
        
        Args:
            league_code: Código da liga
            home_prob: Probabilidade casa
            draw_prob: Probabilidade empate
            away_prob: Probabilidade fora
        
        Returns:
            Lista de value bets
        """
        odds = self.get_odds_economico(league_code)
        
        value_bets = []
        
        for match in odds:
            odd = self.get_odd_referencia(match)
            
            if not odd or not all([odd['casa'], odd['empate'], odd['fora']]):
                continue
            
            # Calcula odds implícitas do modelo
            model_odds = {
                'casa': 1 / home_prob if home_prob > 0 else 0,
                'empate': 1 / draw_prob if draw_prob > 0 else 0,
                'fora': 1 / away_prob if away_prob > 0 else 0
            }
            
            # Calcula value
            for resultado in ['casa', 'empate', 'fora']:
                market_odd = odd[resultado]
                model_odd = model_odds[resultado]
                
                if market_odd > 0 and model_odd > 0:
                    value = market_odd / model_odd
                    
                    if value >= 1.05:  # Mínimo 5% de value
                        value_bets.append({
                            'partida': f"{match['home_team']} vs {match['away_team']}",
                            'resultado': resultado,
                            'odd_mercado': market_odd,
                            'odd_modelo': model_odd,
                            'value': value,
                            'value_percent': (value - 1) * 100
                        })
        
        return value_bets


def main():
    """Exemplo de uso"""
    from config_economia import verificar_viabilidade
    
    print("\n")
    print("=" * 80)
    print("SISTEMA DE ODDS ECONÔMICO")
    print("=" * 80)
    print("\n📊 ANÁLISE DE VIABILIDADE:\n")
    
    cenarios = verificar_viabilidade()
    
    for nome, dados in cenarios.items():
        if dados['viavel']:
            print(f"✅ {nome.upper()}: {dados['custo']} req/mês (Sobra: {dados['sobra']})")
    
    print("\n" + "=" * 80)
    
    try:
        client = OddsEconomico()
        
        print(f"\n🎯 CONFIGURAÇÃO:")
        print(f"   Casa: {client.casa_preferida}")
        print(f"   Região: {client.regiao}")
        print(f"   Mercado: {client.mercado}")
        print(f"   Cache: {client.cache_horas}h")
        
        print("\n" + "=" * 80)
        print("TESTANDO BRASILEIRÃO (BSA)")
        print("=" * 80)
        
        client.resumo_partidas('BSA')
        
        print("\n💡 ECONOMIA:")
        print("   - Usando apenas 1 casa = Mais rápido")
        print("   - Usando apenas 1 região = 67% menos requisições")
        print("   - Usando apenas 1 mercado = 50% menos requisições")
        print("   - Cache de 12h = Análises ilimitadas")
        print("   - TOTAL: ~83% de economia!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Certifique-se de que ODDS_API_KEY está configurada no .env")


if __name__ == "__main__":
    main()

