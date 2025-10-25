"""
Configurações do projeto
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# API Configuration
FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
BASE_URL = 'https://api.football-data.org/v4'

# Ligas disponíveis
LEAGUES = {
    'Premier League': {
        'code': 'PL',
        'id': 2021,
        'name': 'Premier League',
        'country': 'England',
        'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿'
    },
    'Brasileirão Série A': {
        'code': 'BSA',
        'id': 2013,
        'name': 'Campeonato Brasileiro Série A',
        'country': 'Brazil',
        'flag': '🇧🇷'
    }
}

# Liga padrão
DEFAULT_LEAGUE = 'Premier League'

# Backward compatibility (mantém variáveis antigas)
PREMIER_LEAGUE_CODE = 'PL'
PREMIER_LEAGUE_ID = 2021

# Configurações de busca
DEFAULT_LIMIT = 20  # Número de partidas a buscar por padrão

