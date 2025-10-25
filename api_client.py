"""
Cliente para a API do Football-Data.org
"""
import requests
from typing import Dict, List, Optional
import time
from config import FOOTBALL_DATA_API_KEY, BASE_URL


class FootballDataClient:
    """Cliente para interagir com a API do Football-Data.org"""
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o cliente da API
        
        Args:
            api_key: Chave da API (se não fornecida, usa a configuração)
        """
        self.api_key = api_key or FOOTBALL_DATA_API_KEY
        self.base_url = BASE_URL
        self.headers = {
            'X-Auth-Token': self.api_key
        }
        
        if not self.api_key:
            raise ValueError(
                "API Key não configurada. "
                "Crie um arquivo .env com FOOTBALL_DATA_API_KEY=sua_chave"
            )
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Faz uma requisição à API
        
        Args:
            endpoint: Endpoint da API (ex: '/competitions/PL/matches')
            params: Parâmetros da query string
            
        Returns:
            Resposta da API em formato JSON
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("AVISO: Limite de requisicoes atingido. Aguardando 60 segundos...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            elif response.status_code == 403:
                raise ValueError(
                    "API Key inválida ou sem permissão. "
                    "Verifique sua chave em https://www.football-data.org/"
                )
            else:
                raise Exception(f"Erro na requisição: {e}\nResposta: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na conexão: {e}")
    
    def get_competition_matches(
        self, 
        competition_code: str, 
        status: str = 'FINISHED',
        limit: int = 20,
        season: Optional[str] = None,
        matchday: Optional[int] = None
    ) -> Dict:
        """
        Busca partidas de uma competição
        
        Args:
            competition_code: Código da competição (ex: 'PL' para Premier League)
            status: Status das partidas (FINISHED, SCHEDULED, LIVE, etc.)
            limit: Número máximo de partidas
            season: Temporada (ex: '2023')
            matchday: Rodada específica
            
        Returns:
            Dados das partidas
        """
        endpoint = f"/competitions/{competition_code}/matches"
        params = {
            'status': status,
            'limit': limit
        }
        
        if season:
            params['season'] = season
        if matchday:
            params['matchday'] = matchday
            
        return self._make_request(endpoint, params)
    
    def get_team_matches(
        self, 
        team_id: int, 
        status: str = 'FINISHED',
        limit: int = 20,
        venue: Optional[str] = None
    ) -> Dict:
        """
        Busca partidas de um time específico
        
        Args:
            team_id: ID do time
            status: Status das partidas (FINISHED, SCHEDULED, etc.)
            limit: Número máximo de partidas
            venue: Local (HOME ou AWAY)
            
        Returns:
            Dados das partidas do time
        """
        endpoint = f"/teams/{team_id}/matches"
        params = {
            'status': status,
            'limit': limit
        }
        
        if venue:
            params['venue'] = venue
            
        return self._make_request(endpoint, params)
    
    def get_competition_standings(self, competition_code: str) -> Dict:
        """
        Busca a classificação de uma competição
        
        Args:
            competition_code: Código da competição (ex: 'PL')
            
        Returns:
            Tabela de classificação
        """
        endpoint = f"/competitions/{competition_code}/standings"
        return self._make_request(endpoint)
    
    def get_competition_teams(self, competition_code: str, season: Optional[str] = None) -> Dict:
        """
        Busca os times de uma competição
        
        Args:
            competition_code: Código da competição (ex: 'PL')
            season: Temporada específica (opcional)
            
        Returns:
            Lista de times da competição
        """
        endpoint = f"/competitions/{competition_code}/teams"
        params = {}
        if season:
            params['season'] = season
            
        return self._make_request(endpoint, params)
    
    def get_team_info(self, team_id: int) -> Dict:
        """
        Busca informações detalhadas de um time
        
        Args:
            team_id: ID do time
            
        Returns:
            Informações do time
        """
        endpoint = f"/teams/{team_id}"
        return self._make_request(endpoint)

