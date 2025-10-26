"""
Cliente para The Odds API
https://the-odds-api.com/
"""
import requests
from typing import Dict, List, Optional
import time
import json
import os
from datetime import datetime, timedelta
from config import ODDS_API_KEY


class OddsAPIClient:
    """Cliente para interagir com The Odds API"""
    
    # Mapeamento de ligas
    LEAGUE_MAPPING = {
        'BSA': 'soccer_brazil_campeonato',  # Brasileirão
        'PL': 'soccer_epl',  # Premier League
        'LaLiga': 'soccer_spain_la_liga',
        'SerieA': 'soccer_italy_serie_a',
        'Bundesliga': 'soccer_germany_bundesliga',
        'Ligue1': 'soccer_france_ligue_one',
        'Champions': 'soccer_uefa_champs_league',
    }
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o cliente da API
        
        Args:
            api_key: Chave da API (se não fornecida, usa a configuração)
        """
        self.api_key = api_key or ODDS_API_KEY
        self.base_url = 'https://api.the-odds-api.com/v4'
        
        # Cache directory
        self.cache_dir = 'data/odds_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        
        if not self.api_key:
            raise ValueError(
                "API Key do The Odds API não configurada. "
                "Configure ODDS_API_KEY no arquivo .env"
            )
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz uma requisição à API
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da query string
            
        Returns:
            Resposta da API em formato JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        # Adiciona API key aos parâmetros
        if params is None:
            params = {}
        params['apiKey'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Mostra uso da quota
            remaining = response.headers.get('x-requests-remaining')
            used = response.headers.get('x-requests-used')
            last = response.headers.get('x-requests-last')
            
            if remaining:
                print(f"📊 Quota API: {used} usadas | {remaining} restantes | {last} último custo")
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("AVISO: Limite de taxa atingido. Aguardando 60 segundos...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif response.status_code == 401:
                raise ValueError(
                    "API Key inválida. "
                    "Verifique sua chave em https://the-odds-api.com/account/"
                )
            else:
                raise Exception(f"Erro na requisição: {e}\nResposta: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na conexão: {e}")
    
    def get_sports(self, all_sports: bool = False) -> List[Dict]:
        """
        Lista todos os esportes disponíveis
        
        Args:
            all_sports: Se True, retorna também esportes fora de temporada
            
        Returns:
            Lista de esportes
        """
        endpoint = "/sports"
        params = {}
        
        if all_sports:
            params['all'] = 'true'
        
        return self._make_request(endpoint, params)
    
    def get_soccer_leagues(self, active_only: bool = True) -> List[Dict]:
        """
        Lista apenas ligas de futebol
        
        Args:
            active_only: Se True, retorna apenas ligas ativas
            
        Returns:
            Lista de ligas de futebol
        """
        all_sports = self.get_sports(all_sports=not active_only)
        
        # Filtra apenas futebol
        soccer_leagues = [
            sport for sport in all_sports 
            if 'soccer' in sport.get('key', '')
        ]
        
        return soccer_leagues
    
    def get_odds(
        self,
        sport_key: str,
        regions: str = 'us,uk,eu',
        markets: str = 'h2h,totals',
        odds_format: str = 'decimal'
    ) -> List[Dict]:
        """
        Busca odds de uma liga específica
        
        Args:
            sport_key: Chave da liga (ex: 'soccer_brazil_campeonato')
            regions: Regiões das casas (us,uk,eu,au)
            markets: Mercados desejados (h2h,totals,btts)
            odds_format: Formato das odds (decimal, american)
            
        Returns:
            Lista de partidas com odds
        """
        endpoint = f"/sports/{sport_key}/odds"
        
        params = {
            'regions': regions,
            'markets': markets,
            'oddsFormat': odds_format
        }
        
        return self._make_request(endpoint, params)
    
    def get_odds_by_league_code(
        self,
        league_code: str,
        regions: str = 'us,uk,eu',
        markets: str = 'h2h,totals'
    ) -> List[Dict]:
        """
        Busca odds usando código de liga do projeto (BSA, PL, etc)
        
        Args:
            league_code: Código da liga (BSA, PL, LaLiga, etc)
            regions: Regiões das casas
            markets: Mercados desejados
            
        Returns:
            Lista de partidas com odds
        """
        sport_key = self.LEAGUE_MAPPING.get(league_code)
        
        if not sport_key:
            raise ValueError(
                f"Liga '{league_code}' não mapeada. "
                f"Ligas disponíveis: {list(self.LEAGUE_MAPPING.keys())}"
            )
        
        return self.get_odds(sport_key, regions, markets)
    
    def get_match_odds(
        self,
        home_team: str,
        away_team: str,
        sport_key: str
    ) -> Optional[Dict]:
        """
        Busca odds de uma partida específica
        
        Args:
            home_team: Nome do time da casa
            away_team: Nome do time visitante
            sport_key: Chave da liga
            
        Returns:
            Dados da partida com odds ou None
        """
        matches = self.get_odds(sport_key)
        
        # Busca partida
        for match in matches:
            if (self._normalize_team_name(match['home_team']) == self._normalize_team_name(home_team) and 
                self._normalize_team_name(match['away_team']) == self._normalize_team_name(away_team)):
                return match
        
        return None
    
    def get_best_odds(self, match: Dict) -> Dict:
        """
        Extrai as melhores odds de uma partida
        
        Args:
            match: Dados da partida da API
            
        Returns:
            Dicionário com melhores odds por mercado
        """
        best = {
            'home': {'value': 0, 'bookmaker': ''},
            'draw': {'value': 0, 'bookmaker': ''},
            'away': {'value': 0, 'bookmaker': ''},
            'over_2_5': {'value': 0, 'bookmaker': ''},
            'under_2_5': {'value': 0, 'bookmaker': ''},
            'btts_yes': {'value': 0, 'bookmaker': ''},
            'btts_no': {'value': 0, 'bookmaker': ''}
        }
        
        home_team = match['home_team']
        away_team = match['away_team']
        
        for bookmaker in match.get('bookmakers', []):
            bookmaker_name = bookmaker['title']
            
            for market in bookmaker.get('markets', []):
                market_key = market['key']
                
                # Mercado 1X2
                if market_key == 'h2h':
                    for outcome in market['outcomes']:
                        odd_value = outcome['price']
                        
                        if outcome['name'] == home_team:
                            if odd_value > best['home']['value']:
                                best['home'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                        elif outcome['name'] == away_team:
                            if odd_value > best['away']['value']:
                                best['away'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                        else:  # Draw
                            if odd_value > best['draw']['value']:
                                best['draw'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                
                # Mercado Over/Under
                elif market_key == 'totals':
                    for outcome in market['outcomes']:
                        point = outcome.get('point', 0)
                        
                        # Foca em 2.5 gols
                        if abs(point - 2.5) < 0.1:
                            odd_value = outcome['price']
                            
                            if outcome['name'] == 'Over':
                                if odd_value > best['over_2_5']['value']:
                                    best['over_2_5'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                            elif outcome['name'] == 'Under':
                                if odd_value > best['under_2_5']['value']:
                                    best['under_2_5'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                
                # Mercado BTTS (Both Teams To Score)
                elif market_key == 'btts':
                    for outcome in market['outcomes']:
                        odd_value = outcome['price']
                        
                        if outcome['name'] == 'Yes':
                            if odd_value > best['btts_yes']['value']:
                                best['btts_yes'] = {'value': odd_value, 'bookmaker': bookmaker_name}
                        elif outcome['name'] == 'No':
                            if odd_value > best['btts_no']['value']:
                                best['btts_no'] = {'value': odd_value, 'bookmaker': bookmaker_name}
        
        return best
    
    def save_odds_to_cache(self, sport_key: str, odds_data: List[Dict]) -> str:
        """
        Salva odds em cache local
        
        Args:
            sport_key: Chave da liga
            odds_data: Dados das odds
            
        Returns:
            Caminho do arquivo salvo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sport_key}_{timestamp}.json"
        filepath = os.path.join(self.cache_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(odds_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Odds salvas em: {filepath}")
        return filepath
    
    def load_odds_from_cache(
        self,
        sport_key: str,
        max_age_hours: int = 24
    ) -> Optional[List[Dict]]:
        """
        Carrega odds do cache se disponíveis e recentes
        
        Args:
            sport_key: Chave da liga
            max_age_hours: Idade máxima em horas para considerar válido
            
        Returns:
            Dados das odds ou None
        """
        # Lista arquivos do cache para esta liga
        cache_files = [
            f for f in os.listdir(self.cache_dir)
            if f.startswith(sport_key) and f.endswith('.json')
        ]
        
        if not cache_files:
            return None
        
        # Ordena por timestamp (mais recente primeiro)
        cache_files.sort(reverse=True)
        latest_file = cache_files[0]
        filepath = os.path.join(self.cache_dir, latest_file)
        
        # Verifica idade do arquivo
        file_time = os.path.getmtime(filepath)
        file_age = (time.time() - file_time) / 3600  # em horas
        
        if file_age > max_age_hours:
            print(f"⏰ Cache expirado ({file_age:.1f}h). Buscando novos dados...")
            return None
        
        # Carrega do cache
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📦 Usando cache ({file_age:.1f}h atrás): {latest_file}")
        return data
    
    def get_odds_with_cache(
        self,
        sport_key: str,
        max_cache_age_hours: int = 6,
        **kwargs
    ) -> List[Dict]:
        """
        Busca odds usando cache quando possível
        
        Args:
            sport_key: Chave da liga
            max_cache_age_hours: Idade máxima do cache em horas
            **kwargs: Argumentos para get_odds
            
        Returns:
            Lista de partidas com odds
        """
        # Tenta carregar do cache
        cached_data = self.load_odds_from_cache(sport_key, max_cache_age_hours)
        
        if cached_data:
            return cached_data
        
        # Se não há cache válido, busca da API
        print(f"🌐 Buscando dados da API...")
        odds_data = self.get_odds(sport_key, **kwargs)
        
        # Salva no cache
        self.save_odds_to_cache(sport_key, odds_data)
        
        return odds_data
    
    @staticmethod
    def _normalize_team_name(name: str) -> str:
        """Normaliza nome do time para comparação"""
        return name.lower().strip()
    
    def compare_with_predictions(
        self,
        match_odds: Dict,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        min_value: float = 1.05
    ) -> Dict:
        """
        Compara odds do mercado com probabilidades do modelo
        
        Args:
            match_odds: Dados da partida da API
            home_prob: Probabilidade de vitória da casa (modelo)
            draw_prob: Probabilidade de empate (modelo)
            away_prob: Probabilidade de vitória fora (modelo)
            min_value: Valor mínimo para considerar value bet
            
        Returns:
            Análise de value betting
        """
        best = self.get_best_odds(match_odds)
        
        # Calcula odds implícitas do modelo
        model_odds = {
            'home': 1 / home_prob if home_prob > 0 else 0,
            'draw': 1 / draw_prob if draw_prob > 0 else 0,
            'away': 1 / away_prob if away_prob > 0 else 0
        }
        
        # Calcula value
        value_bets = []
        
        for outcome in ['home', 'draw', 'away']:
            market_odd = best[outcome]['value']
            model_odd = model_odds[outcome]
            
            if market_odd > 0 and model_odd > 0:
                value = market_odd / model_odd
                
                if value >= min_value:
                    value_bets.append({
                        'outcome': outcome,
                        'market_odd': market_odd,
                        'model_odd': model_odd,
                        'value': value,
                        'bookmaker': best[outcome]['bookmaker']
                    })
        
        return {
            'match': f"{match_odds['home_team']} vs {match_odds['away_team']}",
            'commence_time': match_odds['commence_time'],
            'best_odds': best,
            'model_odds': model_odds,
            'value_bets': sorted(value_bets, key=lambda x: x['value'], reverse=True)
        }


def main():
    """Exemplo de uso"""
    try:
        client = OddsAPIClient()
        
        print("\n🏆 LIGAS DE FUTEBOL DISPONÍVEIS:")
        print("=" * 80)
        
        leagues = client.get_soccer_leagues()
        
        for league in leagues[:10]:  # Mostra primeiras 10
            status = '🟢' if league.get('active') else '🔴'
            print(f"{status} {league['title']} ({league['key']})")
        
        print(f"\nTotal: {len(leagues)} ligas")
        
        print("\n\n📊 BUSCANDO ODDS DO BRASILEIRÃO:")
        print("=" * 80)
        
        odds = client.get_odds_with_cache('soccer_brazil_campeonato')
        
        if odds:
            print(f"\n✅ {len(odds)} partidas encontradas")
            
            # Mostra primeira partida
            if len(odds) > 0:
                match = odds[0]
                print(f"\nExemplo: {match['home_team']} vs {match['away_team']}")
                
                best = client.get_best_odds(match)
                print(f"\nMelhores Odds:")
                print(f"  Casa:   {best['home']['value']:.2f} ({best['home']['bookmaker']})")
                print(f"  Empate: {best['draw']['value']:.2f} ({best['draw']['bookmaker']})")
                print(f"  Fora:   {best['away']['value']:.2f} ({best['away']['bookmaker']})")
        else:
            print("⚠️ Nenhuma partida disponível no momento")
        
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()

