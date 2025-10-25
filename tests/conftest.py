"""
Configurações e fixtures compartilhadas para os testes
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def sample_match_data():
    """Gera dados de exemplo para testes"""
    dates = pd.date_range(start='2024-01-01', periods=50, freq='W')
    
    teams = [
        'Arsenal FC', 'Liverpool FC', 'Manchester City FC', 'Chelsea FC',
        'Manchester United FC', 'Tottenham Hotspur FC', 'Newcastle United FC',
        'Aston Villa FC', 'Brighton & Hove Albion FC', 'West Ham United FC'
    ]
    
    matches = []
    for i, date in enumerate(dates):
        # Cria partidas balanceadas
        home_team = teams[i % len(teams)]
        away_team = teams[(i + 1) % len(teams)]
        
        # Gera gols com alguma lógica (time melhor marca mais)
        home_strength = 1.0 + (i % 3) * 0.3
        away_strength = 1.0 + ((i + 1) % 3) * 0.3
        
        gols_casa = np.random.poisson(home_strength * 1.5)
        gols_visitante = np.random.poisson(away_strength * 1.0)
        
        matches.append({
            'data': date,
            'time_casa': home_team,
            'time_visitante': away_team,
            'gols_casa': gols_casa,
            'gols_visitante': gols_visitante,
            'competicao': 'Premier League'
        })
    
    return pd.DataFrame(matches)


@pytest.fixture
def trained_dixon_coles(sample_match_data):
    """Modelo Dixon-Coles treinado com dados de exemplo"""
    from dixon_coles import DixonColesModel
    
    model = DixonColesModel(xi=0.003)
    model.fit(sample_match_data, time_decay=False)
    
    return model


@pytest.fixture
def trained_offensive_defensive(sample_match_data):
    """Modelo Offensive-Defensive treinado com dados de exemplo"""
    from offensive_defensive import OffensiveDefensiveModel
    
    model = OffensiveDefensiveModel(xi=0.003)
    model.fit(sample_match_data, time_decay=False)
    
    return model


@pytest.fixture
def trained_heuristicas(sample_match_data):
    """Modelo de Heurísticas com dados de exemplo"""
    from heuristicas import HeuristicasModel
    import os
    import json
    
    # Salva temporariamente os dados para o modelo carregar
    temp_file = 'data/temp_test_matches.csv'
    os.makedirs('data', exist_ok=True)
    sample_match_data.to_csv(temp_file, index=False)
    
    model = HeuristicasModel()
    # Normaliza os dados antes de atribuir
    model.df = model._normalize_data(sample_match_data)
    model.teams = sorted(set(model.df['time'].unique()))
    
    # Limpa arquivo temporário
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    return model

