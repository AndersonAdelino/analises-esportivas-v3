"""
Configurações do projeto
"""
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# API Configuration
# Tenta ler do Streamlit Secrets primeiro, depois do .env
try:
    import streamlit as st
    FOOTBALL_DATA_API_KEY = st.secrets.get('FOOTBALL_DATA_API_KEY', os.getenv('FOOTBALL_DATA_API_KEY', ''))
    ODDS_API_KEY = st.secrets.get('ODDS_API_KEY', os.getenv('ODDS_API_KEY', ''))
except:
    FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', '')
    ODDS_API_KEY = os.getenv('ODDS_API_KEY', '')

BASE_URL = 'https://api.football-data.org/v4'
ODDS_API_URL = 'https://api.the-odds-api.com/v4'

# Exporta ODDS_API_KEY para uso em odds_api_client.py

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

