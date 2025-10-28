"""
Interface Web para Análise de Apostas com Value Betting

Streamlit app que combina:
- Ensemble de modelos (Dixon-Coles 55%, Offensive-Defensive 30%, Heurísticas 15%)
- Cálculo de Expected Value (EV)
- Kelly Criterion para gestão de banca
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone
from api_client import FootballDataClient
from ensemble import EnsembleModel
from betting_tools import analyze_bet, print_bet_analysis
from bingo_analyzer import BingoAnalyzer
import config
import numpy as np
import os
from glob import glob

# Fuso horário de Brasília (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))


def convert_to_brasilia_time(utc_date_str):
    """
    Converte data UTC para horário de Brasília (UTC-3)
    
    Args:
        utc_date_str: String de data em formato ISO (ex: "2025-10-26T15:00:00Z")
    
    Returns:
        String formatada no horário de Brasília (ex: "26/10/2025 12:00")
    """
    try:
        # Parse da data UTC
        utc_date = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        # Converter para Brasília
        brasilia_date = utc_date.astimezone(BRASILIA_TZ)
        # Formatar
        return brasilia_date.strftime("%d/%m/%Y %H:%M")
    except:
        return utc_date_str


def check_data_freshness(league_code, max_age_hours=24):
    """
    Verifica se os dados estão atualizados
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
        max_age_hours: Idade máxima dos dados em horas
        
    Returns:
        tuple: (needs_update, last_update_time, info)
    """
    # NOVO: Verifica do banco de dados primeiro
    try:
        from database import get_database
        db = get_database()
        
        last_update = db.get_last_update(league_code)
        
        if last_update:
            update_time = datetime.fromisoformat(last_update['timestamp'])
            age = datetime.now() - update_time
            needs_update = age.total_seconds() > (max_age_hours * 3600)
            
            return needs_update, update_time, last_update
    except Exception as e:
        # Fallback para CSV se banco não disponível
        pass
    
    # Fallback: Verifica CSV (método antigo)
    league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a').replace('é', 'e')
                      for name, info in config.LEAGUES.items()}
    league_prefix = league_name_map.get(league_code, 'league')
    
    csv_files = glob(f'data/{league_prefix}_matches_*.csv')
    
    if not csv_files:
        return True, None, None  # Sem arquivos, precisa atualizar
    
    latest_file = max(csv_files, key=os.path.getctime)
    file_time = datetime.fromtimestamp(os.path.getctime(latest_file))
    age = datetime.now() - file_time
    
    needs_update = age.total_seconds() > (max_age_hours * 3600)
    
    return needs_update, file_time, {'source': 'csv', 'file': latest_file}


def update_league_data(league_code, league_name):
    """
    Atualiza dados de uma liga específica
    
    Args:
        league_code: Código da liga
        league_name: Nome da liga para exibição
        
    Returns:
        tuple: (success, message, matches_count)
    """
    try:
        from get_team_matches import get_all_teams_matches
        
        # Coleta dados da liga selecionada
        df, data = get_all_teams_matches(
            limit_per_team=20, 
            league_code=league_code
        )
        
        if df is not None and len(df) > 0:
            return True, f"✅ Dados atualizados! {len(df)} partidas coletadas.", len(df)
        else:
            return False, "❌ Erro: Nenhuma partida foi coletada.", 0
            
    except Exception as e:
        return False, f"❌ Erro ao atualizar: {str(e)}", 0


# Configuração da página
st.set_page_config(
    page_title="⚽ Value Betting Analyzer",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .stAlert > div {
        padding: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .value-bet {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .no-value-bet {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_ensemble(league_code=None):
    """
    Carrega e treina o ensemble (cache para não retreinar)
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
    """
    if league_code is None:
        league_code = config.PREMIER_LEAGUE_CODE
    
    league_display = [name for name, info in config.LEAGUES.items() if info['code'] == league_code][0]
    
    with st.spinner(f"Treinando modelos para {league_display}... Aguarde..."):
        ensemble = EnsembleModel()
        ensemble.fit(league_code=league_code)
    return ensemble


@st.cache_data(ttl=86400)  # Cache por 24 horas
def get_upcoming_matches(league_code=None):
    """
    Busca próximas partidas de uma liga
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
    """
    if league_code is None:
        league_code = config.PREMIER_LEAGUE_CODE
    
    try:
        client = FootballDataClient()
        matches_data = client.get_competition_matches(
            league_code,
            status='SCHEDULED',
            limit=20
        )
        
        matches = []
        for match in matches_data.get('matches', []):
            matches.append({
                'id': match['id'],
                'date': match['utcDate'],
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'matchday': match.get('matchday', '?')
            })
        
        return matches
    except Exception as e:
        st.error(f"Erro ao buscar partidas: {e}")
        return []


@st.cache_data(ttl=86400)  # Cache por 24 horas
def get_all_teams(league_code=None):
    """
    Busca todos os times de uma liga
    
    Args:
        league_code: Código da liga (ex: 'PL', 'BSA')
    """
    if league_code is None:
        league_code = config.PREMIER_LEAGUE_CODE
    
    try:
        client = FootballDataClient()
        teams_data = client.get_competition_teams(league_code)
        
        teams = []
        for team in teams_data.get('teams', []):
            teams.append({
                'id': team['id'],
                'name': team['name'],
                'short_name': team.get('shortName', team['name']),
                'crest': team.get('crest', '')
            })
        
        return sorted(teams, key=lambda x: x['name'])
    except Exception as e:
        st.error(f"Erro ao buscar times: {e}")
        return []


@st.cache_data(ttl=86400)  # Cache por 24 horas
def get_team_history(team_id: int, limit: int = 50):
    """Busca histórico de partidas de um time"""
    try:
        client = FootballDataClient()
        matches_data = client.get_team_matches(team_id, status='FINISHED', limit=limit)
        
        matches = []
        for match in matches_data.get('matches', []):
            home_team = match['homeTeam']['name']
            away_team = match['awayTeam']['name']
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            
            # Determina se o time jogou em casa ou fora
            is_home = match['homeTeam']['id'] == team_id
            team_name = home_team if is_home else away_team
            opponent = away_team if is_home else home_team
            
            # Gols marcados e sofridos
            goals_for = home_score if is_home else away_score
            goals_against = away_score if is_home else home_score
            
            # Resultado
            if goals_for > goals_against:
                result = 'V'
                points = 3
            elif goals_for < goals_against:
                result = 'D'
                points = 0
            else:
                result = 'E'
                points = 1
            
            matches.append({
                'date': match['utcDate'],
                'opponent': opponent,
                'venue': 'Casa' if is_home else 'Fora',
                'goals_for': goals_for,
                'goals_against': goals_against,
                'result': result,
                'points': points,
                'competition': match.get('competition', {}).get('name', 'N/A')
            })
        
        return matches
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")
        return []


def calculate_team_stats(matches):
    """Calcula estatísticas de um time"""
    if not matches:
        return None
    
    df = pd.DataFrame(matches)
    
    total_matches = len(df)
    wins = len(df[df['result'] == 'V'])
    draws = len(df[df['result'] == 'E'])
    losses = len(df[df['result'] == 'D'])
    
    goals_for = df['goals_for'].sum()
    goals_against = df['goals_against'].sum()
    goal_difference = goals_for - goals_against
    
    points = df['points'].sum()
    avg_points = points / total_matches if total_matches > 0 else 0
    
    # Estatísticas por local
    home_matches = df[df['venue'] == 'Casa']
    away_matches = df[df['venue'] == 'Fora']
    
    # Últimos 5 jogos (forma)
    last_5 = df.head(5)
    form = ''.join(last_5['result'].tolist())
    
    # Over 2.5 e BTTS
    df['total_goals'] = df['goals_for'] + df['goals_against']
    over_2_5 = len(df[df['total_goals'] > 2.5]) / total_matches * 100
    btts = len(df[(df['goals_for'] > 0) & (df['goals_against'] > 0)]) / total_matches * 100
    
    return {
        'total_matches': total_matches,
        'wins': wins,
        'draws': draws,
        'losses': losses,
        'win_rate': wins / total_matches * 100,
        'goals_for': goals_for,
        'goals_against': goals_against,
        'goal_difference': goal_difference,
        'avg_goals_for': goals_for / total_matches,
        'avg_goals_against': goals_against / total_matches,
        'points': points,
        'avg_points': avg_points,
        'form': form,
        'over_2_5_pct': over_2_5,
        'btts_pct': btts,
        'home_stats': {
            'matches': len(home_matches),
            'wins': len(home_matches[home_matches['result'] == 'V']),
            'goals_for': home_matches['goals_for'].sum() if len(home_matches) > 0 else 0,
            'goals_against': home_matches['goals_against'].sum() if len(home_matches) > 0 else 0,
        },
        'away_stats': {
            'matches': len(away_matches),
            'wins': len(away_matches[away_matches['result'] == 'V']),
            'goals_for': away_matches['goals_for'].sum() if len(away_matches) > 0 else 0,
            'goals_against': away_matches['goals_against'].sum() if len(away_matches) > 0 else 0,
        }
    }


def create_results_chart(matches):
    """Cria gráfico de resultados ao longo do tempo"""
    df = pd.DataFrame(matches)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Cores para resultados
    colors = {'V': 'green', 'E': 'gray', 'D': 'red'}
    df['color'] = df['result'].map(colors)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['points'],
        mode='markers+lines',
        marker=dict(
            size=12,
            color=df['color'],
            line=dict(width=2, color='white')
        ),
        line=dict(color='lightblue', width=1),
        text=df.apply(lambda x: f"{x['opponent']}<br>{x['goals_for']}-{x['goals_against']}", axis=1),
        hovertemplate='<b>%{text}</b><br>Data: %{x}<br>Pontos: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Resultados ao Longo do Tempo',
        xaxis_title='Data',
        yaxis_title='Pontos por Partida',
        hovermode='closest',
        height=400
    )
    
    return fig


def create_goals_chart(matches):
    """Cria gráfico de gols marcados vs sofridos"""
    df = pd.DataFrame(matches)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Médias móveis de 5 jogos
    df['avg_goals_for'] = df['goals_for'].rolling(window=5, min_periods=1).mean()
    df['avg_goals_against'] = df['goals_against'].rolling(window=5, min_periods=1).mean()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['avg_goals_for'],
        mode='lines',
        name='Gols Marcados (Média 5 jogos)',
        line=dict(color='green', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['avg_goals_against'],
        mode='lines',
        name='Gols Sofridos (Média 5 jogos)',
        line=dict(color='red', width=3)
    ))
    
    fig.update_layout(
        title='Tendência de Gols (Média Móvel 5 Jogos)',
        xaxis_title='Data',
        yaxis_title='Média de Gols',
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_form_chart(matches):
    """Cria gráfico de forma (pontos acumulados)"""
    df = pd.DataFrame(matches)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Pontos acumulados
    df['cumulative_points'] = df['points'].cumsum()
    df['match_number'] = range(1, len(df) + 1)
    
    # Pontos esperados (média de 1.5 pontos por jogo - metade da tabela)
    df['expected_points'] = df['match_number'] * 1.5
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['match_number'],
        y=df['cumulative_points'],
        mode='lines+markers',
        name='Pontos Reais',
        line=dict(color='blue', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['match_number'],
        y=df['expected_points'],
        mode='lines',
        name='Pontos Esperados (Média)',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title='Acúmulo de Pontos vs Esperado',
        xaxis_title='Número de Jogos',
        yaxis_title='Pontos Acumulados',
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_venue_comparison(stats):
    """Cria gráfico de comparação casa vs fora"""
    categories = ['Vitórias', 'Gols Marcados', 'Gols Sofridos']
    
    home_data = [
        stats['home_stats']['wins'],
        stats['home_stats']['goals_for'],
        stats['home_stats']['goals_against']
    ]
    
    away_data = [
        stats['away_stats']['wins'],
        stats['away_stats']['goals_for'],
        stats['away_stats']['goals_against']
    ]
    
    fig = go.Figure(data=[
        go.Bar(name='Casa', x=categories, y=home_data, marker_color='lightblue'),
        go.Bar(name='Fora', x=categories, y=away_data, marker_color='lightcoral')
    ])
    
    fig.update_layout(
        title='Desempenho Casa vs Fora',
        barmode='group',
        height=400
    )
    
    return fig


def create_results_pie(stats):
    """Cria gráfico de pizza com distribuição de resultados"""
    labels = ['Vitórias', 'Empates', 'Derrotas']
    values = [stats['wins'], stats['draws'], stats['losses']]
    colors = ['green', 'gray', 'red']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hole=0.3
    )])
    
    fig.update_layout(
        title='Distribuição de Resultados',
        height=400
    )
    
    return fig


# ============================================================================
# MODEL COMPARISON VISUALIZATION FUNCTIONS
# ============================================================================

def create_probability_comparison_chart(predictions, market='1x2'):
    """
    Cria gráfico de barras comparando probabilidades dos 3 modelos
    
    Args:
        predictions: Dict com predições de todos os modelos
        market: '1x2', 'over_under' ou 'btts'
    """
    model_names = ['Dixon-Coles', 'Off-Defensive', 'Heurísticas', 'Ensemble']
    model_keys = ['dixon_coles', 'offensive_defensive', 'heuristicas', 'ensemble']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    fig = go.Figure()
    
    if market == '1x2':
        categories = ['Vitória Casa', 'Empate', 'Vitória Fora']
        prob_keys = ['prob_casa', 'prob_empate', 'prob_fora']
        
        for i, (model_name, model_key) in enumerate(zip(model_names, model_keys)):
            if model_key == 'ensemble':
                model_pred = predictions.get('ensemble', {})
            else:
                model_pred = predictions.get('individual', {}).get(model_key)
            
            if model_pred:
                values = [model_pred.get(key, 0) * 100 for key in prob_keys]
                fig.add_trace(go.Bar(
                    name=model_name,
                    x=categories,
                    y=values,
                    marker_color=colors[i],
                    text=[f'{v:.1f}%' for v in values],
                    textposition='outside'
                ))
        
        title = 'Comparação de Probabilidades - Resultado (1X2)'
        
    elif market == 'over_under':
        categories = ['Over 2.5', 'Under 2.5']
        
        for i, (model_name, model_key) in enumerate(zip(model_names, model_keys)):
            if model_key == 'ensemble':
                model_pred = predictions.get('ensemble', {})
            else:
                model_pred = predictions.get('individual', {}).get(model_key)
            
            if model_pred:
                prob_over = model_pred.get('prob_over_2_5', 0.5) * 100
                prob_under = (1 - model_pred.get('prob_over_2_5', 0.5)) * 100
                values = [prob_over, prob_under]
                fig.add_trace(go.Bar(
                    name=model_name,
                    x=categories,
                    y=values,
                    marker_color=colors[i],
                    text=[f'{v:.1f}%' for v in values],
                    textposition='outside'
                ))
        
        title = 'Comparação de Probabilidades - Over/Under 2.5 Gols'
        
    else:  # btts
        categories = ['BTTS Sim', 'BTTS Não']
        
        for i, (model_name, model_key) in enumerate(zip(model_names, model_keys)):
            if model_key == 'ensemble':
                model_pred = predictions.get('ensemble', {})
            else:
                model_pred = predictions.get('individual', {}).get(model_key)
            
            if model_pred:
                prob_yes = model_pred.get('prob_btts', 0.5) * 100
                prob_no = (1 - model_pred.get('prob_btts', 0.5)) * 100
                values = [prob_yes, prob_no]
                fig.add_trace(go.Bar(
                    name=model_name,
                    x=categories,
                    y=values,
                    marker_color=colors[i],
                    text=[f'{v:.1f}%' for v in values],
                    textposition='outside'
                ))
        
        title = 'Comparação de Probabilidades - BTTS (Ambos Marcam)'
    
    fig.update_layout(
        title=title,
        xaxis_title='Resultado',
        yaxis_title='Probabilidade (%)',
        barmode='group',
        height=450,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_score_heatmap(score_matrix, model_name, max_goals=5):
    """
    Cria heatmap de placares prováveis
    
    Args:
        score_matrix: Matriz numpy (11x11) com probabilidades
        model_name: Nome do modelo
        max_goals: Máximo de gols a exibir (default 5)
    """
    if score_matrix is None:
        return None
    
    # Reduzir matriz para (max_goals+1) x (max_goals+1)
    matrix_display = score_matrix[:max_goals+1, :max_goals+1]
    
    # Converter para porcentagem
    matrix_pct = matrix_display * 100
    
    # Criar texto para células
    text = np.round(matrix_pct, 1).astype(str)
    for i in range(text.shape[0]):
        for j in range(text.shape[1]):
            text[i, j] = f'{text[i, j]}%'
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix_pct,
        x=[str(i) for i in range(max_goals+1)],
        y=[str(i) for i in range(max_goals+1)],
        colorscale='RdYlGn',
        text=text,
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title=dict(text="Prob. (%)", side="right")),
        hovertemplate='Casa: %{y} gols<br>Fora: %{x} gols<br>Probabilidade: %{z:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Placares Prováveis - {model_name}',
        xaxis_title='Gols Fora',
        yaxis_title='Gols Casa',
        height=400,
        xaxis=dict(side='bottom'),
        yaxis=dict(autorange='reversed')  # Casa em ordem crescente de cima para baixo
    )
    
    return fig


def create_top_scores_table(predictions):
    """
    Cria tabela comparativa dos top 10 placares mais prováveis
    
    Args:
        predictions: Dict com predições de todos os modelos
    """
    # Coletar top scores de cada modelo
    models_data = {}
    
    # Dixon-Coles
    dc_pred = predictions.get('individual', {}).get('dixon_coles')
    if dc_pred and dc_pred.get('top_scores'):
        models_data['Dixon-Coles'] = {
            score: prob * 100 
            for (score, prob) in dc_pred['top_scores'][:10]
        }
    
    # Offensive-Defensive
    od_pred = predictions.get('individual', {}).get('offensive_defensive')
    if od_pred and od_pred.get('top_scores'):
        models_data['Off-Defensive'] = {
            score: prob * 100 
            for (score, prob) in od_pred['top_scores'][:10]
        }
    
    # Ensemble
    ens_pred = predictions.get('ensemble', {})
    if ens_pred and ens_pred.get('top_scores'):
        models_data['Ensemble'] = {
            score: prob * 100 
            for (score, prob) in ens_pred['top_scores'][:10]
        }
    
    if not models_data:
        return None
    
    # Obter todos os placares únicos do top 10 de cada modelo
    all_scores = set()
    for model_scores in models_data.values():
        all_scores.update(model_scores.keys())
    
    # Ordenar por soma de probabilidades
    score_sums = {
        score: sum(models_data[model].get(score, 0) for model in models_data)
        for score in all_scores
    }
    top_scores = sorted(score_sums.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Criar DataFrame
    table_data = []
    for score, _ in top_scores:
        row = {'Placar': f'{score[0]}-{score[1]}'}
        for model_name in ['Dixon-Coles', 'Off-Defensive', 'Ensemble']:
            if model_name in models_data:
                prob = models_data[model_name].get(score, 0)
                row[model_name] = f'{prob:.1f}%' if prob > 0 else '-'
            else:
                row[model_name] = '-'
        table_data.append(row)
    
    return pd.DataFrame(table_data)


def create_radar_chart(predictions):
    """
    Cria gráfico radar comparando 6 dimensões dos modelos
    
    Args:
        predictions: Dict com predições de todos os modelos
    """
    categories = [
        'Vitória Casa',
        'Empate',
        'Vitória Fora',
        'Over 2.5',
        'Under 2.5',
        'BTTS'
    ]
    
    fig = go.Figure()
    
    model_names = ['Dixon-Coles', 'Off-Defensive', 'Heurísticas', 'Ensemble']
    model_keys = ['dixon_coles', 'offensive_defensive', 'heuristicas', 'ensemble']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for model_name, model_key, color in zip(model_names, model_keys, colors):
        if model_key == 'ensemble':
            model_pred = predictions.get('ensemble', {})
        else:
            model_pred = predictions.get('individual', {}).get(model_key)
        
        if model_pred:
            values = [
                model_pred.get('prob_casa', 0) * 100,
                model_pred.get('prob_empate', 0) * 100,
                model_pred.get('prob_fora', 0) * 100,
                model_pred.get('prob_over_2_5', 0) * 100,
                (1 - model_pred.get('prob_over_2_5', 0.5)) * 100,
                model_pred.get('prob_btts', 0) * 100
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=model_name,
                line=dict(color=color, width=2),
                opacity=0.6
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title='Comparação Multidimensional dos Modelos',
        height=500
    )
    
    return fig


def calculate_model_divergence(predictions):
    """
    Calcula divergência KL entre modelos
    
    Args:
        predictions: Dict com predições de todos os modelos
        
    Returns:
        Dict com métricas de divergência
    """
    from scipy.special import kl_div
    
    # Obter probabilidades 1X2 de cada modelo
    models_probs = {}
    
    for model_key in ['dixon_coles', 'offensive_defensive', 'heuristicas']:
        model_pred = predictions.get('individual', {}).get(model_key)
        if model_pred:
            models_probs[model_key] = np.array([
                model_pred.get('prob_casa', 0.33),
                model_pred.get('prob_empate', 0.33),
                model_pred.get('prob_fora', 0.33)
            ])
    
    if len(models_probs) < 2:
        return {
            'kl_divergence_avg': 0,
            'max_divergence': 0,
            'interpretation': 'Dados insuficientes'
        }
    
    # Calcular KL divergence entre pares
    divergences = []
    model_list = list(models_probs.keys())
    
    for i in range(len(model_list)):
        for j in range(i + 1, len(model_list)):
            p = models_probs[model_list[i]]
            q = models_probs[model_list[j]]
            
            # KL divergence (evita log(0))
            p = np.clip(p, 1e-10, 1)
            q = np.clip(q, 1e-10, 1)
            
            kl = np.sum(kl_div(p, q))
            divergences.append(kl)
    
    avg_kl = np.mean(divergences) if divergences else 0
    max_kl = np.max(divergences) if divergences else 0
    
    # Interpretação
    if avg_kl < 0.1:
        interpretation = 'Baixa (Modelos muito concordantes)'
    elif avg_kl < 0.3:
        interpretation = 'Moderada (Alguma divergência)'
    else:
        interpretation = 'Alta (Modelos discordam significativamente)'
    
    return {
        'kl_divergence_avg': avg_kl,
        'max_divergence': max_kl,
        'interpretation': interpretation
    }


def calculate_consensus(predictions):
    """
    Calcula nível de consenso entre modelos (%)
    
    Args:
        predictions: Dict com predições de todos os modelos
        
    Returns:
        Dict com métricas de consenso
    """
    # Obter probabilidades 1X2 de cada modelo
    casa_probs = []
    empate_probs = []
    fora_probs = []
    
    for model_key in ['dixon_coles', 'offensive_defensive', 'heuristicas']:
        model_pred = predictions.get('individual', {}).get(model_key)
        if model_pred:
            casa_probs.append(model_pred.get('prob_casa', 0.33))
            empate_probs.append(model_pred.get('prob_empate', 0.33))
            fora_probs.append(model_pred.get('prob_fora', 0.33))
    
    if len(casa_probs) < 2:
        return {
            'consensus_level': 0,
            'std_dev_casa': 0,
            'std_dev_empate': 0,
            'std_dev_fora': 0,
            'interpretation': 'Dados insuficientes'
        }
    
    # Calcular desvio padrão
    std_casa = np.std(casa_probs)
    std_empate = np.std(empate_probs)
    std_fora = np.std(fora_probs)
    
    # Consenso = 1 - (média dos desvios / média das probabilidades)
    avg_std = (std_casa + std_empate + std_fora) / 3
    avg_prob = (np.mean(casa_probs) + np.mean(empate_probs) + np.mean(fora_probs)) / 3
    
    if avg_prob > 0:
        consensus = (1 - (avg_std / avg_prob)) * 100
        consensus = max(0, min(100, consensus))  # Limitar entre 0 e 100
    else:
        consensus = 0
    
    # Interpretação
    if consensus >= 85:
        interpretation = 'Muito Alto (Forte concordância)'
    elif consensus >= 70:
        interpretation = 'Alto (Boa concordância)'
    elif consensus >= 50:
        interpretation = 'Moderado (Concordância parcial)'
    else:
        interpretation = 'Baixo (Modelos divergem)'
    
    return {
        'consensus_level': consensus,
        'std_dev_casa': std_casa,
        'std_dev_empate': std_empate,
        'std_dev_fora': std_fora,
        'interpretation': interpretation
    }


# ============================================================================
# TEAM ANALYSIS FUNCTIONS
# ============================================================================

def display_team_analysis():
    """Exibe análise completa de um time"""
    st.header("📊 Análise Detalhada de Time")
    
    # Busca times (usa league_code do estado global se disponível)
    # Como estamos dentro de display_team_analysis, precisamos do league_code
    # Vamos usar session_state para passar
    league_code = st.session_state.get('selected_league_code', config.PREMIER_LEAGUE_CODE)
    
    with st.spinner("Carregando times..."):
        teams = get_all_teams(league_code)
    
    if not teams:
        st.error("Não foi possível carregar os times.")
        return
    
    # Seletor de time
    team_names = [t['name'] for t in teams]
    selected_team_name = st.selectbox("🔍 Selecione um time para análise:", team_names)
    
    selected_team = next((t for t in teams if t['name'] == selected_team_name), None)
    
    if not selected_team:
        return
    
    # Número de jogos para análise
    num_matches = st.slider(
        "Número de jogos para análise",
        min_value=10,
        max_value=50,
        value=30,
        step=5
    )
    
    # Busca histórico
    with st.spinner(f"Carregando histórico de {selected_team_name}..."):
        matches = get_team_history(selected_team['id'], limit=num_matches)
    
    if not matches:
        st.warning("Nenhum histórico encontrado para este time.")
        return
    
    # Calcula estatísticas
    stats = calculate_team_stats(matches)
    
    if not stats:
        st.error("Erro ao calcular estatísticas.")
        return
    
    # Exibe estatísticas principais
    st.subheader(f"📈 Estatísticas Gerais - {selected_team_name}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Jogos", stats['total_matches'])
    with col2:
        st.metric("Vitórias", stats['wins'], f"{stats['win_rate']:.1f}%")
    with col3:
        st.metric("Empates", stats['draws'])
    with col4:
        st.metric("Derrotas", stats['losses'])
    with col5:
        st.metric("Forma", stats['form'])
    
    st.markdown("---")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Gols Marcados", stats['goals_for'])
    with col2:
        st.metric("Gols Sofridos", stats['goals_against'])
    with col3:
        st.metric("Saldo de Gols", stats['goal_difference'])
    with col4:
        st.metric("Média Gols/Jogo", f"{stats['avg_goals_for']:.2f}")
    with col5:
        st.metric("Pontos", stats['points'], f"{stats['avg_points']:.2f}/jogo")
    
    st.markdown("---")
    
    # Estatísticas de apostas
    st.subheader("🎯 Estatísticas para Apostas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Over 2.5 Gols", f"{stats['over_2_5_pct']:.1f}%")
    with col2:
        st.metric("BTTS (Ambos Marcam)", f"{stats['btts_pct']:.1f}%")
    with col3:
        st.metric("Média Gols Marcados", f"{stats['avg_goals_for']:.2f}")
    with col4:
        st.metric("Média Gols Sofridos", f"{stats['avg_goals_against']:.2f}")
    
    st.markdown("---")
    
    # Gráficos
    st.subheader("📊 Análise Visual")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Resultados", 
        "⚽ Gols", 
        "📈 Forma", 
        "🏠 Casa vs Fora",
        "📋 Distribuição"
    ])
    
    with tab1:
        st.plotly_chart(create_results_chart(matches), use_container_width=True)
        st.info("💡 Verde = Vitória, Cinza = Empate, Vermelho = Derrota")
    
    with tab2:
        st.plotly_chart(create_goals_chart(matches), use_container_width=True)
        st.info("💡 Média móvel de 5 jogos mostra a tendência ofensiva e defensiva")
    
    with tab3:
        st.plotly_chart(create_form_chart(matches), use_container_width=True)
        st.info("💡 Compare o desempenho real com a linha esperada (média da liga)")
    
    with tab4:
        st.plotly_chart(create_venue_comparison(stats), use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🏠 Estatísticas em Casa:**")
            st.write(f"- Jogos: {stats['home_stats']['matches']}")
            st.write(f"- Vitórias: {stats['home_stats']['wins']}")
            st.write(f"- Gols Marcados: {stats['home_stats']['goals_for']}")
            st.write(f"- Gols Sofridos: {stats['home_stats']['goals_against']}")
        
        with col2:
            st.markdown("**✈️ Estatísticas Fora:**")
            st.write(f"- Jogos: {stats['away_stats']['matches']}")
            st.write(f"- Vitórias: {stats['away_stats']['wins']}")
            st.write(f"- Gols Marcados: {stats['away_stats']['goals_for']}")
            st.write(f"- Gols Sofridos: {stats['away_stats']['goals_against']}")
    
    with tab5:
        st.plotly_chart(create_results_pie(stats), use_container_width=True)
    
    st.markdown("---")
    
    # Tabela de partidas recentes
    st.subheader("🗓️ Histórico de Partidas Recentes")
    
    df_matches = pd.DataFrame(matches)
    # Converter datas UTC para horário de Brasília
    df_matches['date'] = df_matches['date'].apply(
        lambda x: convert_to_brasilia_time(x) if 'T' in str(x) else pd.to_datetime(x).strftime('%d/%m/%Y')
    )
    df_matches['placar'] = df_matches.apply(
        lambda x: f"{x['goals_for']}-{x['goals_against']}", axis=1
    )
    
    # Formata tabela para exibição
    display_df = df_matches[[
        'date', 'opponent', 'venue', 'placar', 'result', 'competition'
    ]].copy()
    
    display_df.columns = ['Data', 'Adversário', 'Local', 'Placar', 'Resultado', 'Competição']
    
    # Aplica cores aos resultados
    def highlight_result(row):
        if row['Resultado'] == 'V':
            return ['background-color: #d4edda; color: #155724'] * len(row)
        elif row['Resultado'] == 'D':
            return ['background-color: #f8d7da; color: #721c24'] * len(row)
        else:
            return ['background-color: #f0f0f0; color: #383d41'] * len(row)
    
    st.dataframe(
        display_df.style.apply(highlight_result, axis=1),
        use_container_width=True,
        hide_index=True,
        height=400
    )


def display_bingo_analysis():
    """Exibe a cartela otimizada de apostas múltiplas"""
    st.header("🎰 Bingo do Dia - Apostas Múltiplas")
    st.markdown("Sistema que analisa seus palpites do dia e monta **A MELHOR cartela múltipla possível**")
    
    analyzer = st.session_state.bingo_analyzer
    cached = analyzer.get_cached_analyses()
    unique_matches = analyzer.get_unique_matches()
    
    # Info do cache
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Palpites Analisados", len(cached))
    with col2:
        st.metric("⚽ Partidas Diferentes", len(unique_matches))
    
    # Validação mínima
    if len(unique_matches) < 3:
        st.warning(f"⚠️ Você analisou apenas {len(unique_matches)} partida(s) diferentes hoje.")
        st.info("💡 **Como usar:** Vá na aba 'Análise de Apostas', analise pelo menos 3 partidas diferentes, e volte aqui!")
        
        if len(cached) > 0:
            st.markdown("---")
            st.markdown("### 📋 Palpites em cache:")
            for bet in cached:
                st.write(f"✅ {bet['match_info']['home_team']} vs {bet['match_info']['away_team']} - **{bet['bet_type']}** (EV: {bet['analysis']['ev']['ev_percent']:+.1f}%)")
        
        return
    
    # Interface de configuração
    st.success(f"✅ Pronto para gerar o BINGO! ({len(unique_matches)} partidas disponíveis)")
    
    st.markdown("---")
    st.subheader("⚙️ Configurações da Cartela")
    
    col1, col2 = st.columns(2)
    with col1:
        min_bets = st.slider("Mínimo de jogos", 3, 5, 3, 
                            help="Mínimo de palpites na cartela")
        max_bets = st.slider("Máximo de jogos", 3, 5, 5,
                            help="Máximo de palpites na cartela")
    
    with col2:
        min_ev = st.slider("EV% mínimo por palpite", 0.0, 20.0, 3.0, 0.5,
                          help="Valor esperado mínimo de cada palpite")
        min_prob = st.slider("Probabilidade mínima", 30.0, 80.0, 35.0, 5.0,
                            help="Probabilidade mínima de cada palpite")
    
    stake_cartela = st.number_input("💰 Quanto quer apostar na cartela? (R$)", 
                                    min_value=10.0, max_value=10000.0, 
                                    value=100.0, step=10.0)
    
    # Botão gerar
    st.markdown("---")
    if st.button("🎲 GERAR O MELHOR BINGO DO DIA", type="primary", use_container_width=True):
        with st.spinner("🔍 Analisando todas as combinações possíveis e escolhendo a melhor..."):
            cartela = analyzer.generate_best_cartela(
                min_bets=min_bets,
                max_bets=max_bets,
                min_ev_percent=min_ev,
                min_prob_percent=min_prob,
                stake=stake_cartela
            )
        
        if not cartela:
            st.error("❌ Não foi possível gerar uma cartela com os filtros selecionados.")
            st.info("💡 **Dica:** Tente reduzir os requisitos mínimos (EV% e Probabilidade) ou analise mais partidas.")
            return
        
        # EXIBIR A CARTELA OTIMIZADA
        st.success("✅ **BINGO DO DIA GERADO!**")
        st.balloons()
        
        # Métricas principais
        st.markdown("---")
        st.subheader("📊 Resumo da Cartela")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎲 Odd Total", f"{cartela['odd_total']:.2f}")
        with col2:
            st.metric("🎯 Probabilidade", f"{cartela['prob_combined']*100:.1f}%")
        with col3:
            st.metric("📈 EV%", f"{cartela['ev_percent']:+.2f}%")
        with col4:
            st.metric("⭐ Score", f"{cartela['quality_score']:.1f}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💰 Financeiro")
            st.write(f"**Investimento:** R$ {cartela['stake']:.2f}")
            st.write(f"**Retorno se acertar:** R$ {cartela['potential_return']:.2f}")
            st.write(f"**Lucro potencial:** R$ {cartela['potential_profit']:.2f}")
            st.write(f"**Lucro esperado (EV):** R$ {cartela['expected_profit']:+.2f}")
        
        with col2:
            st.markdown("### 📊 Probabilidades")
            st.write(f"**Chance de acerto:** {cartela['prob_combined']*100:.2f}%")
            st.write(f"**Chance de erro:** {(1-cartela['prob_combined'])*100:.2f}%")
            st.write(f"**ROI esperado:** {cartela['roi_percent']:+.2f}%")
        
        # Detalhes dos palpites
        st.markdown("---")
        st.subheader(f"🎯 {len(cartela['bets'])} Palpites da Cartela")
        
        for idx, bet in enumerate(cartela['bets'], 1):
            with st.expander(f"**{idx}. {bet['match_info']['home_team']} vs {bet['match_info']['away_team']}**", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"### {bet['bet_type']}")
                    st.write(f"📅 Data: {bet['match_info'].get('date', 'N/A')}")
                
                with col2:
                    st.metric("Odd", f"{bet['analysis']['odds']:.2f}")
                    st.metric("Probabilidade", f"{bet['analysis']['prob_real']*100:.1f}%")
                
                with col3:
                    st.metric("EV%", f"{bet['analysis']['ev']['ev_percent']:+.1f}%")
                    st.metric("Score", f"{bet.get('score', 0):.1f}")
        
        # Informação adicional
        st.markdown("---")
        st.info(f"🔍 **Análise:** {cartela['total_combinations_analyzed']} combinações foram analisadas para encontrar esta cartela otimizada.")
        
        # Dica final
        st.success("💡 **Dica:** Copie esses palpites e monte sua múltipla na casa de apostas!")
        
        # Botão para limpar e refazer
        st.markdown("---")
        if st.button("🔄 Limpar Cache e Começar Novo Bingo", type="secondary"):
            analyzer.clear_cache()
            st.rerun()


def display_match_selector(matches):
    """Exibe seletor de partidas"""
    if not matches:
        st.warning("Nenhuma partida futura encontrada.")
        return None
    
    # Formata para exibição
    match_options = []
    for match in matches:
        date_str = convert_to_brasilia_time(match['date'])
        match_str = f"{match['home_team']} vs {match['away_team']} - {date_str} (Brasília)"
        match_options.append(match_str)
    
    # Seletor
    selected_idx = st.selectbox(
        "📅 Selecione a partida:",
        range(len(match_options)),
        format_func=lambda i: match_options[i]
    )
    
    return matches[selected_idx]


def display_odds_input():
    """Exibe campos para entrada de odds"""
    st.subheader("📊 Insira as Odds da Casa de Apostas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Resultado (1X2)**")
        odds_casa = st.number_input("🏠 Vitória Casa", min_value=1.01, max_value=50.0, value=2.00, step=0.05)
        odds_empate = st.number_input("🤝 Empate", min_value=1.01, max_value=50.0, value=3.50, step=0.05)
        odds_fora = st.number_input("✈️ Vitória Fora", min_value=1.01, max_value=50.0, value=3.80, step=0.05)
    
    with col2:
        st.markdown("**Over/Under 2.5 Gols**")
        odds_over = st.number_input("📈 Over 2.5", min_value=1.01, max_value=50.0, value=1.85, step=0.05)
        odds_under = st.number_input("📉 Under 2.5", min_value=1.01, max_value=50.0, value=2.00, step=0.05)
    
    with col3:
        st.markdown("**Both Teams to Score**")
        odds_btts_yes = st.number_input("✅ BTTS Sim", min_value=1.01, max_value=50.0, value=1.70, step=0.05)
        odds_btts_no = st.number_input("❌ BTTS Não", min_value=1.01, max_value=50.0, value=2.10, step=0.05)
    
    return {
        'casa': odds_casa,
        'empate': odds_empate,
        'fora': odds_fora,
        'over_2_5': odds_over,
        'under_2_5': odds_under,
        'btts_yes': odds_btts_yes,
        'btts_no': odds_btts_no
    }


def display_bankroll_input():
    """Campo para entrada da banca"""
    st.subheader("💰 Configurações de Banca")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bankroll = st.number_input(
            "Banca Total (R$)",
            min_value=10.0,
            max_value=1000000.0,
            value=1000.0,
            step=50.0
        )
    
    with col2:
        kelly_fraction = st.slider(
            "Fração de Kelly (conservadorismo)",
            min_value=0.1,
            max_value=1.0,
            value=0.25,
            step=0.05,
            help="Recomendado: 0.25 (conservador) ou 0.5 (moderado)"
        )
    
    return bankroll, kelly_fraction


def get_data_info(home_team, away_team, league_code):
    """Obtém informações sobre os dados utilizados na análise"""
    from data_loader import load_match_data
    from config import LEAGUES
    
    try:
        # Carrega dados
        df = load_match_data(league_code=league_code)
        
        # Nome da liga
        league_name = [name for name, info in LEAGUES.items() if info['code'] == league_code][0]
        
        # Arquivo usado
        league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a').replace('é', 'e')
                          for name, info in LEAGUES.items()}
        league_prefix = league_name_map.get(league_code, 'league')
        csv_files = glob(f'data/{league_prefix}_matches_*.csv')
        
        if csv_files:
            latest_file = max(csv_files, key=os.path.getctime)
            file_name = os.path.basename(latest_file)
            file_time = datetime.fromtimestamp(os.path.getctime(latest_file))
        else:
            file_name = "API (sem arquivo local)"
            file_time = datetime.now()
        
        # Estatísticas gerais
        total_matches = len(df)
        total_teams = len(set(df['time_casa'].unique()) | set(df['time_visitante'].unique()))
        
        # Data das partidas
        df['data'] = pd.to_datetime(df['data'])
        oldest_match = df['data'].min()
        newest_match = df['data'].max()
        
        # Partidas do time da casa
        home_matches = df[(df['time_casa'] == home_team) | (df['time_visitante'] == home_team)]
        home_count = len(home_matches)
        
        # Partidas do time visitante
        away_matches = df[(df['time_casa'] == away_team) | (df['time_visitante'] == away_team)]
        away_count = len(away_matches)
        
        # Últimos jogos do time da casa
        home_recent = home_matches.sort_values('data', ascending=False).head(5)
        home_recent_list = []
        
        for _, match in home_recent.iterrows():
            date_str = match['data'].strftime('%d/%m/%Y')
            is_home = match['time_casa'] == home_team
            opponent = match['time_visitante'] if is_home else match['time_casa']
            
            if is_home:
                score = f"{match['gols_casa']}-{match['gols_visitante']}"
                result = "V" if match['gols_casa'] > match['gols_visitante'] else ("E" if match['gols_casa'] == match['gols_visitante'] else "D")
            else:
                score = f"{match['gols_visitante']}-{match['gols_casa']}"
                result = "V" if match['gols_visitante'] > match['gols_casa'] else ("E" if match['gols_visitante'] == match['gols_casa'] else "D")
            
            home_recent_list.append({
                'date': date_str,
                'opponent': opponent,
                'score': score,
                'result': result,
                'is_home': is_home
            })
        
        # Últimos jogos do time visitante
        away_recent = away_matches.sort_values('data', ascending=False).head(5)
        away_recent_list = []
        
        for _, match in away_recent.iterrows():
            date_str = match['data'].strftime('%d/%m/%Y')
            is_home = match['time_casa'] == away_team
            opponent = match['time_visitante'] if is_home else match['time_casa']
            
            if is_home:
                score = f"{match['gols_casa']}-{match['gols_visitante']}"
                result = "V" if match['gols_casa'] > match['gols_visitante'] else ("E" if match['gols_casa'] == match['gols_visitante'] else "D")
            else:
                score = f"{match['gols_visitante']}-{match['gols_casa']}"
                result = "V" if match['gols_visitante'] > match['gols_casa'] else ("E" if match['gols_visitante'] == match['gols_casa'] else "D")
            
            away_recent_list.append({
                'date': date_str,
                'opponent': opponent,
                'score': score,
                'result': result,
                'is_home': is_home
            })
        
        # Confrontos diretos
        direct_matches = df[
            ((df['time_casa'] == home_team) & (df['time_visitante'] == away_team)) |
            ((df['time_casa'] == away_team) & (df['time_visitante'] == home_team))
        ].sort_values('data', ascending=False)
        
        direct_count = len(direct_matches)
        direct_list = []
        
        for _, match in direct_matches.head(5).iterrows():
            date_str = match['data'].strftime('%d/%m/%Y')
            if match['time_casa'] == home_team:
                score = f"{match['gols_casa']}-{match['gols_visitante']}"
                result = "V" if match['gols_casa'] > match['gols_visitante'] else ("E" if match['gols_casa'] == match['gols_visitante'] else "D")
            else:
                score = f"{match['gols_visitante']}-{match['gols_casa']}"
                result = "V" if match['gols_visitante'] > match['gols_casa'] else ("E" if match['gols_visitante'] == match['gols_casa'] else "D")
            
            direct_list.append({
                'date': date_str,
                'score': score,
                'result': result,
                'home_was': match['time_casa'],
                'away_was': match['time_visitante']
            })
        
        return {
            'league': league_name,
            'file_name': file_name,
            'file_time': file_time,
            'total_matches': total_matches,
            'total_teams': total_teams,
            'oldest_match': oldest_match,
            'newest_match': newest_match,
            'home_count': home_count,
            'away_count': away_count,
            'home_recent': home_recent_list,
            'away_recent': away_recent_list,
            'direct_count': direct_count,
            'direct_matches': direct_list
        }
    except Exception as e:
        return None


def analyze_and_display(ensemble, match, odds, bankroll, kelly_fraction):
    """Realiza análise e exibe resultados"""
    
    home_team = match['home_team']
    away_team = match['away_team']
    
    # Predição do ensemble
    with st.spinner("Calculando probabilidades..."):
        try:
            prediction = ensemble.predict_match(home_team, away_team)
        except Exception as e:
            st.error(f"Erro ao calcular predição: {e}")
            return
    
    ens = prediction['ensemble']
    
    # Validar se o ensemble retornou resultados válidos
    if not ens or ens.get('prob_casa') is None:
        st.error("❌ Não foi possível gerar predições. Os modelos falharam ao treinar.")
        st.warning("⚠️ **Possíveis causas:**")
        st.markdown("""
        1. **API Key não configurada** - Configure em Settings > Secrets
        2. **Dados insuficientes** - A API pode não ter dados históricos
        3. **Limite de requisições** - Aguarde 1 minuto e tente novamente
        
        **Como resolver:**
        - Configure a API Key nos Secrets (veja documentação)
        - Verifique se a liga selecionada está disponível
        - Aguarde alguns minutos e recarregue a página
        """)
        return
    
    # Exibe probabilidades do modelo
    st.success("✅ Análise concluída!")
    
    # Mostra informações sobre os dados utilizados
    league_code = st.session_state.get('selected_league_code', config.PREMIER_LEAGUE_CODE)
    data_info = get_data_info(home_team, away_team, league_code)
    
    if data_info:
        with st.expander("📊 Dados Utilizados na Análise", expanded=False):
            st.markdown("### 📁 Informações do Dataset")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Partidas", data_info['total_matches'])
                st.metric("Times na Base", data_info['total_teams'])
            with col2:
                st.metric(f"Jogos de {home_team}", data_info['home_count'])
                st.metric(f"Jogos de {away_team}", data_info['away_count'])
            with col3:
                st.metric("Confrontos Diretos", data_info['direct_count'])
                age = datetime.now() - data_info['file_time']
                hours_old = int(age.total_seconds() / 3600)
                st.metric("Idade dos Dados", f"{hours_old}h")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**📅 Período dos Dados:**")
                st.write(f"De: {data_info['oldest_match'].strftime('%d/%m/%Y')}")
                st.write(f"Até: {data_info['newest_match'].strftime('%d/%m/%Y')}")
            with col2:
                st.markdown(f"**📂 Arquivo Usado:**")
                st.code(data_info['file_name'], language=None)
                st.write(f"Atualizado em: {data_info['file_time'].strftime('%d/%m/%Y %H:%M')}")
            
            # Histórico recente de cada time
            st.markdown("---")
            st.markdown("### 📋 Histórico Recente dos Times")
            
            col1, col2 = st.columns(2)
            
            # Histórico do time da casa
            with col1:
                st.markdown(f"**🏠 {home_team}** (últimos 5 jogos)")
                
                if data_info['home_recent']:
                    for jogo in data_info['home_recent']:
                        emoji = "🟢" if jogo['result'] == "V" else ("🟡" if jogo['result'] == "E" else "🔴")
                        resultado_texto = "V" if jogo['result'] == "V" else ("E" if jogo['result'] == "E" else "D")
                        local = "🏠" if jogo['is_home'] else "✈️"
                        
                        st.markdown(
                            f"{emoji} **{jogo['date']}** {local} vs {jogo['opponent']} - "
                            f"**{jogo['score']}** ({resultado_texto})"
                        )
                else:
                    st.info(f"Sem dados de {home_team}")
            
            # Histórico do time visitante
            with col2:
                st.markdown(f"**✈️ {away_team}** (últimos 5 jogos)")
                
                if data_info['away_recent']:
                    for jogo in data_info['away_recent']:
                        emoji = "🟢" if jogo['result'] == "V" else ("🟡" if jogo['result'] == "E" else "🔴")
                        resultado_texto = "V" if jogo['result'] == "V" else ("E" if jogo['result'] == "E" else "D")
                        local = "🏠" if jogo['is_home'] else "✈️"
                        
                        st.markdown(
                            f"{emoji} **{jogo['date']}** {local} vs {jogo['opponent']} - "
                            f"**{jogo['score']}** ({resultado_texto})"
                        )
                else:
                    st.info(f"Sem dados de {away_team}")
            
            # Histórico de confrontos diretos
            if data_info['direct_matches']:
                st.markdown("---")
                st.markdown("### ⚔️ Confrontos Diretos")
                st.caption(f"*Resultado do ponto de vista de {home_team}*")
                
                for idx, confronto in enumerate(data_info['direct_matches'], 1):
                    emoji = "🟢" if confronto['result'] == "V" else ("🟡" if confronto['result'] == "E" else "🔴")
                    resultado_texto = "Vitória" if confronto['result'] == "V" else ("Empate" if confronto['result'] == "E" else "Derrota")
                    
                    local = "🏠 Casa" if confronto['home_was'] == home_team else "✈️ Fora"
                    
                    st.markdown(
                        f"{emoji} **{confronto['date']}** - {local} - "
                        f"**{confronto['score']}** - {resultado_texto}"
                    )
            else:
                st.markdown("---")
                st.info("ℹ️ Não há confrontos diretos recentes entre estes times no dataset.")
    
    st.markdown("---")
    
    # Banner informativo sobre os modelos usados
    st.info("🤖 **Ensemble combinando 3 modelos:** Dixon-Coles (55%) + Offensive-Defensive (30%) + Heurísticas (15%)")
    
    st.subheader("🎯 Probabilidades do Ensemble (Combinação dos 3 Modelos)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏠 Vitória Casa", f"{ens['prob_casa']*100:.1f}%")
        st.metric("🤝 Empate", f"{ens['prob_empate']*100:.1f}%")
        st.metric("✈️ Vitória Fora", f"{ens['prob_fora']*100:.1f}%")
    
    with col2:
        st.metric("📈 Over 2.5", f"{ens['prob_over_2_5']*100:.1f}%")
        st.metric("📉 Under 2.5", f"{(1-ens['prob_over_2_5'])*100:.1f}%")
    
    with col3:
        st.metric("✅ BTTS Sim", f"{ens['prob_btts']*100:.1f}%")
        st.metric("❌ BTTS Não", f"{(1-ens['prob_btts'])*100:.1f}%")
    
    # Análise de cada mercado
    st.subheader("💡 Análise de Value Bets")
    
    markets = [
        ('🏠 Vitória Casa', ens['prob_casa'], odds['casa']),
        ('🤝 Empate', ens['prob_empate'], odds['empate']),
        ('✈️ Vitória Fora', ens['prob_fora'], odds['fora']),
        ('📈 Over 2.5', ens['prob_over_2_5'], odds['over_2_5']),
        ('📉 Under 2.5', 1 - ens['prob_over_2_5'], odds['under_2_5']),
        ('✅ BTTS Sim', ens['prob_btts'], odds['btts_yes']),
        ('❌ BTTS Não', 1 - ens['prob_btts'], odds['btts_no'])
    ]
    
    value_bets = []
    
    for market_name, prob, odd in markets:
        analysis = analyze_bet(prob, odd, bankroll, kelly_fraction)
        
        if analysis['is_value_bet']:
            value_bets.append({
                'market': market_name,
                'analysis': analysis
            })
            
            # Salvar no cache do bingo
            st.session_state.bingo_analyzer.add_analysis(
                match_info={
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match.get('date', ''),
                    'match_id': f"{home_team}_vs_{away_team}"
                },
                bet_type=market_name,
                analysis=analysis
            )
    
    # Exibe value bets encontrados
    if value_bets:
        # Identifica a MELHOR aposta
        from betting_tools import find_best_bet
        analyses_list = [vb['analysis'] for vb in value_bets]
        best_bet_analysis = find_best_bet(analyses_list, min_prob=0.60)
        
        st.success(f"✅ {len(value_bets)} Value Bet(s) identificado(s)!")
        
        for idx, vb in enumerate(value_bets):
            analysis = vb['analysis']
            
            # Verifica se é a MELHOR aposta
            is_best_bet = (best_bet_analysis is not None and 
                          analysis['prob_real'] == best_bet_analysis['prob_real'] and
                          analysis['ev']['ev_percent'] == best_bet_analysis['ev']['ev_percent'])
            
            # Destaque visual elegante para a MELHOR aposta
            if is_best_bet:
                # Badge dourado discreto antes do expander
                st.markdown("""
                <div style='
                    display: inline-block;
                    background: linear-gradient(90deg, #f59e0b, #d97706);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                    margin: 5px 0;
                    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
                '>
                    🏆 MELHOR APOSTA (EV+ Alto + Prob>60%)
                </div>
                """, unsafe_allow_html=True)
                expander_title = f"⭐ {vb['market']} - APOSTE R$ {vb['analysis']['stake_recommended']:.2f} ⭐"
                expanded_state = True
            else:
                expander_title = f"🎯 {vb['market']} - APOSTE R$ {vb['analysis']['stake_recommended']:.2f}"
                expanded_state = True if len(value_bets) <= 3 else False
            
            with st.expander(expander_title, expanded=expanded_state):
                if is_best_bet:
                    st.success("✨ **RECOMENDAÇÃO PREMIUM:** Melhor relação risco/retorno desta partida!")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("**Odds & Probabilidades**")
                    st.write(f"Odds: **{analysis['odds']:.2f}**")
                    st.write(f"Prob. Real: **{analysis['prob_real']*100:.1f}%**")
                    st.write(f"Prob. Casa: **{analysis['prob_implied']*100:.1f}%**")
                    st.write(f"Edge: **{analysis['edge_percent']:+.1f}%**")
                
                with col2:
                    st.markdown("**Expected Value**")
                    st.write(f"EV%: **{analysis['ev']['ev_percent']:+.2f}%**")
                    st.write(f"ROI: **{analysis['ev']['roi_percent']:+.2f}%**")
                    st.write(f"EV/R$: **R$ {analysis['ev']['ev_absolute']:+.2f}**")
                
                with col3:
                    st.markdown("**Kelly Criterion**")
                    st.write(f"Kelly Full: **{analysis['kelly']['kelly_percent']*100:.1f}%**")
                    st.write(f"Kelly Ajustado: **{analysis['kelly']['kelly_adjusted']*100:.1f}%**")
                    st.write(f"Recomendação: **{analysis['kelly']['recommendation']}**")
                
                with col4:
                    st.markdown("**Recomendação de Stake**")
                    st.write(f"Banca: **R$ {analysis['bankroll']:.2f}**")
                    st.write(f"Apostar: **R$ {analysis['stake_recommended']:.2f}**")
                    st.write(f"% Banca: **{analysis['stake_percent']:.2f}%**")
                    if analysis.get('stake_limited', False):
                        st.warning("⚠️ Stake limitado a 12% (proteção)")
                    st.write(f"Lucro Potencial: **R$ {analysis['potential_profit']:.2f}**")
    else:
        st.warning("⚠️ Nenhum Value Bet identificado nesta partida.")
        st.info("💡 Dica: As odds da casa estão justas ou desfavoráveis segundo nossos modelos.")
    
    # Tabela resumo de todos os mercados
    st.subheader("📋 Resumo de Todos os Mercados")
    
    summary_data = []
    for market_name, prob, odd in markets:
        analysis = analyze_bet(prob, odd, bankroll, kelly_fraction)
        summary_data.append({
            'Mercado': market_name,
            'Odds': f"{analysis['odds']:.2f}",
            'Prob. Modelo': f"{analysis['prob_real']*100:.1f}%",
            'Prob. Casa': f"{analysis['prob_implied']*100:.1f}%",
            'Edge': f"{analysis['edge_percent']:+.1f}%",
            'EV%': f"{analysis['ev']['ev_percent']:+.2f}%",
            'Kelly%': f"{analysis['kelly']['kelly_adjusted']*100:.1f}%",
            'Apostar': f"R$ {analysis['stake_recommended']:.2f}",
            'Value?': '✅' if analysis['is_value_bet'] else '❌'
        })
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # Detalhes dos modelos individuais
    with st.expander("🔍 Ver Probabilidades Individuais dos 3 Modelos (CLIQUE AQUI)", expanded=False):
        st.markdown("### 📊 Como funciona o Ensemble:")
        st.markdown("""
        O sistema combina as predições de 3 modelos estatísticos diferentes, 
        ponderando cada um conforme sua eficácia histórica:
        """)
        
        col_w1, col_w2, col_w3 = st.columns(3)
        with col_w1:
            st.metric("Dixon-Coles", f"{prediction['weights']['dixon_coles']*100:.0f}%", "Peso")
        with col_w2:
            st.metric("Offensive-Defensive", f"{prediction['weights']['offensive_defensive']*100:.0f}%", "Peso")
        with col_w3:
            st.metric("Heurísticas", f"{prediction['weights']['heuristicas']*100:.0f}%", "Peso")
        
        st.markdown("---")
        st.markdown("### 📈 Probabilidades de cada modelo:")
        
        col1, col2, col3 = st.columns(3)
        
        for idx, (model_name, model_pred) in enumerate(prediction['individual'].items()):
            if model_pred:
                with [col1, col2, col3][idx]:
                    st.markdown(f"**🎯 {model_name.upper().replace('_', '-')}**")
                    st.write(f"Casa: **{model_pred['prob_casa']*100:.1f}%**")
                    st.write(f"Empate: **{model_pred['prob_empate']*100:.1f}%**")
                    st.write(f"Fora: **{model_pred['prob_fora']*100:.1f}%**")
                    st.write(f"Over 2.5: **{model_pred['prob_over_2_5']*100:.1f}%**")
                    st.write(f"BTTS: **{model_pred['prob_btts']*100:.1f}%**")
            else:
                with [col1, col2, col3][idx]:
                    st.markdown(f"**❌ {model_name.upper().replace('_', '-')}**")
                    st.error("Modelo falhou")
    
    # ============================================================================
    # NOVA SEÇÃO: COMPARAÇÃO DETALHADA DOS MODELOS
    # ============================================================================
    
    st.markdown("---")
    st.header("🔍 Comparação Detalhada dos Modelos")
    st.markdown("""
    Explore como cada modelo chegou às suas conclusões, veja placares mais prováveis 
    e analise o nível de consenso entre os modelos.
    """)
    
    # Tabs para diferentes visualizações
    comp_tab1, comp_tab2, comp_tab3 = st.tabs([
        "📊 Probabilidades", 
        "🎯 Placares", 
        "📈 Convergência"
    ])
    
    with comp_tab1:
        st.subheader("Comparação de Probabilidades entre Modelos")
        st.markdown("Compare as probabilidades previstas por cada modelo para diferentes mercados.")
        
        # Gráficos de barras comparativas
        col1, col2 = st.columns(2)
        
        with col1:
            fig_1x2 = create_probability_comparison_chart(prediction, market='1x2')
            st.plotly_chart(fig_1x2, use_container_width=True)
        
        with col2:
            fig_ou = create_probability_comparison_chart(prediction, market='over_under')
            st.plotly_chart(fig_ou, use_container_width=True)
        
        fig_btts = create_probability_comparison_chart(prediction, market='btts')
        st.plotly_chart(fig_btts, use_container_width=True)
        
        st.markdown("---")
        
        # Gráfico Radar
        st.subheader("Visualização Multidimensional")
        st.markdown("Compare todas as dimensões dos modelos em um único gráfico.")
        fig_radar = create_radar_chart(prediction)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.info("""
        💡 **Como interpretar:** 
        - Quanto mais sobrepostas as formas, maior o consenso
        - Áreas onde os modelos divergem indicam maior incerteza
        - O **Ensemble** (vermelho) combina todos os modelos
        """)
    
    with comp_tab2:
        st.subheader("Placares Mais Prováveis por Modelo")
        st.markdown("Visualize a distribuição de probabilidades para diferentes placares.")
        
        # Heatmaps dos modelos
        st.markdown("### 🗺️ Mapas de Calor (Heatmaps)")
        
        col1, col2, col3 = st.columns(3)
        
        # Dixon-Coles
        dc_pred = prediction.get('individual', {}).get('dixon_coles')
        if dc_pred and dc_pred.get('score_matrix') is not None:
            with col1:
                fig_dc = create_score_heatmap(dc_pred['score_matrix'], 'Dixon-Coles')
                if fig_dc:
                    st.plotly_chart(fig_dc, use_container_width=True)
        else:
            with col1:
                st.warning("Dixon-Coles: Matriz de placares não disponível")
        
        # Offensive-Defensive
        od_pred = prediction.get('individual', {}).get('offensive_defensive')
        if od_pred and od_pred.get('score_matrix') is not None:
            with col2:
                fig_od = create_score_heatmap(od_pred['score_matrix'], 'Off-Defensive')
                if fig_od:
                    st.plotly_chart(fig_od, use_container_width=True)
        else:
            with col2:
                st.warning("Off-Defensive: Matriz de placares não disponível")
        
        # Ensemble
        ens_pred = prediction.get('ensemble', {})
        if ens_pred.get('score_matrix') is not None:
            with col3:
                fig_ens = create_score_heatmap(ens_pred['score_matrix'], 'Ensemble')
                if fig_ens:
                    st.plotly_chart(fig_ens, use_container_width=True)
        else:
            with col3:
                st.warning("Ensemble: Matriz de placares não disponível")
        
        st.info("""
        💡 **Como interpretar os heatmaps:** 
        - Cores mais **verdes** = maior probabilidade
        - Cores mais **vermelhas** = menor probabilidade
        - **Eixo Y** (vertical) = Gols da Casa
        - **Eixo X** (horizontal) = Gols do Visitante
        """)
        
        st.markdown("---")
        
        # Top 10 Placares
        st.markdown("### 🏆 Top 10 Placares Mais Prováveis")
        
        scores_table = create_top_scores_table(prediction)
        if scores_table is not None:
            st.dataframe(
                scores_table, 
                use_container_width=True, 
                hide_index=True
            )
            
            st.success("""
            ✅ **Dica para apostas em placar exato:**  
            Placares com alta probabilidade no **Ensemble** e consenso entre modelos 
            geralmente oferecem melhor valor.
            """)
        else:
            st.warning("Tabela de placares não disponível")
    
    with comp_tab3:
        st.subheader("Análise de Convergência e Consenso")
        st.markdown("""
        Avalie o grau de concordância entre os modelos. Maior consenso geralmente 
        indica predições mais confiáveis.
        """)
        
        # Calcular métricas
        divergence_metrics = calculate_model_divergence(prediction)
        consensus_metrics = calculate_consensus(prediction)
        
        # Exibir métricas em cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📈 Divergência KL Média", 
                f"{divergence_metrics['kl_divergence_avg']:.3f}",
                help="Kullback-Leibler divergence. Quanto menor, mais concordantes os modelos."
            )
            st.caption(f"**Interpretação:** {divergence_metrics['interpretation']}")
        
        with col2:
            st.metric(
                "🎯 Nível de Consenso", 
                f"{consensus_metrics['consensus_level']:.1f}%",
                help="Percentual de concordância entre modelos. Maior = mais confiança."
            )
            st.caption(f"**Interpretação:** {consensus_metrics['interpretation']}")
        
        with col3:
            # Determinar recomendação
            if consensus_metrics['consensus_level'] >= 85:
                confidence_icon = "🟢"
                confidence_text = "Alta"
                confidence_color = "green"
            elif consensus_metrics['consensus_level'] >= 70:
                confidence_icon = "🟡"
                confidence_text = "Boa"
                confidence_color = "orange"
            else:
                confidence_icon = "🔴"
                confidence_text = "Baixa"
                confidence_color = "red"
            
            st.metric(
                f"{confidence_icon} Confiança na Predição", 
                confidence_text,
                help="Baseado no nível de consenso entre os modelos."
            )
        
        st.markdown("---")
        
        # Detalhes das métricas
        with st.expander("📊 Detalhes das Métricas de Convergência"):
            st.markdown("### Desvio Padrão por Mercado")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Vitória Casa", 
                    f"{consensus_metrics['std_dev_casa']:.3f}",
                    help="Desvio padrão das probabilidades de vitória da casa"
                )
            with col2:
                st.metric(
                    "Empate", 
                    f"{consensus_metrics['std_dev_empate']:.3f}",
                    help="Desvio padrão das probabilidades de empate"
                )
            with col3:
                st.metric(
                    "Vitória Fora", 
                    f"{consensus_metrics['std_dev_fora']:.3f}",
                    help="Desvio padrão das probabilidades de vitória do visitante"
                )
            
            st.markdown("---")
            
            st.markdown("### 📖 Sobre as Métricas")
            st.markdown("""
            **Divergência KL (Kullback-Leibler):**
            - Mede a diferença entre as distribuições de probabilidade dos modelos
            - **0** = Modelos idênticos
            - **< 0.1** = Baixa divergência (modelos muito concordantes)
            - **0.1-0.3** = Divergência moderada
            - **> 0.3** = Alta divergência (modelos discordam significativamente)
            
            **Nível de Consenso:**
            - Baseado no desvio padrão das probabilidades
            - **> 85%** = Muito Alto (forte concordância)
            - **70-85%** = Alto (boa concordância)
            - **50-70%** = Moderado (concordância parcial)
            - **< 50%** = Baixo (modelos divergem)
            
            **Recomendação:**
            - **Alto consenso** → Maior confiança na predição
            - **Baixo consenso** → Cautela recomendada, reduzir stake
            """)
        
        st.markdown("---")
        
        # Recomendação final
        if consensus_metrics['consensus_level'] >= 80:
            st.success("""
            ✅ **ALTO CONSENSO:** Os modelos concordam fortemente.  
            As predições têm maior probabilidade de serem precisas.  
            Você pode apostar com mais confiança (respeitando a gestão de banca).
            """)
        elif consensus_metrics['consensus_level'] >= 60:
            st.info("""
            ℹ️ **CONSENSO MODERADO:** Os modelos concordam parcialmente.  
            As predições são razoáveis, mas há alguma incerteza.  
            Considere reduzir o stake em 25-50%.
            """)
        else:
            st.warning("""
            ⚠️ **BAIXO CONSENSO:** Os modelos divergem significativamente.  
            Há alta incerteza nesta predição.  
            Recomenda-se não apostar ou usar stakes mínimos.
            """)


def main():
    """Função principal da aplicação"""
    
    # Inicializar bingo analyzer no session_state
    if 'bingo_analyzer' not in st.session_state:
        st.session_state.bingo_analyzer = BingoAnalyzer()
    
    # Sidebar - Seleção de Liga (no topo)
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seletor de Liga com bandeiras dos países
        league_options_display = [
            f"{info['flag']} {name}"
            for name, info in config.LEAGUES.items()
        ]
        
        selected_display = st.selectbox(
            "🏆 Selecione a Liga",
            options=league_options_display,
            index=0,  # Premier League como padrão
            help="Escolha a liga para análise"
        )
        
        # Obtém nome real da liga (sem bandeira)
        selected_league_name = selected_display.split(' ', 1)[1]  # Remove a bandeira
        
        # Obtém código da liga selecionada
        selected_league_code = config.LEAGUES[selected_league_name]['code']
        selected_league_flag = config.LEAGUES[selected_league_name]['flag']
        
        # Armazena no session_state para uso em outras funções
        st.session_state['selected_league_code'] = selected_league_code
        st.session_state['selected_league_name'] = selected_league_name
        
        st.markdown("---")
        
        # ===== SEÇÃO DE ATUALIZAÇÃO DE DADOS =====
        st.subheader("🔄 Atualização de Dados")
        
        # Verifica idade dos dados
        needs_update, last_update, file_path = check_data_freshness(selected_league_code, max_age_hours=24)
        
        if last_update:
            age = datetime.now() - last_update
            hours_old = int(age.total_seconds() / 3600)
            minutes_old = int((age.total_seconds() % 3600) / 60)
            
            # Mostra informação da última atualização
            st.info(f"📅 **Última atualização:**\n\n{last_update.strftime('%d/%m/%Y às %H:%M')}")
            
            # Mostra idade dos dados com cores
            if hours_old < 12:
                st.success(f"⏰ **Idade:** {hours_old}h {minutes_old}min\n\n✅ Dados recentes!")
            elif hours_old < 24:
                st.warning(f"⏰ **Idade:** {hours_old}h {minutes_old}min\n\n⚠️ Dados OK, mas considere atualizar")
            else:
                days_old = hours_old // 24
                hours_remainder = hours_old % 24
                st.error(f"⏰ **Idade:** {days_old}d {hours_remainder}h\n\n❗ Recomendado atualizar!")
        else:
            st.error("❌ **Nenhum dado encontrado!**\n\nClique no botão abaixo para coletar dados.")
        
        # Botão de atualização
        update_button = st.button(
            "📥 Atualizar Dados Agora",
            help=f"Busca os dados mais recentes da {selected_league_flag} {selected_league_name} via API (leva 2-3 minutos)",
            type="primary" if needs_update else "secondary",
            use_container_width=True
        )
        
        if update_button:
            with st.spinner(f"🔄 Coletando dados de {selected_league_flag} {selected_league_name}...\n\nIsso levará ~2-3 minutos. Aguarde..."):
                success, message, count = update_league_data(selected_league_code, selected_league_name)
                
                if success:
                    st.success(message)
                    st.balloons()
                    st.info("💡 **Próximo passo:** Recarregue a página (F5) ou clique em 'Limpar Cache' abaixo para usar os novos dados.")
                    
                    # Limpa cache automaticamente
                    st.cache_data.clear()
                    st.cache_resource.clear()
                else:
                    st.error(message)
        
        st.markdown("---")
    
    # Título com liga selecionada
    st.title(f"⚽ Value Betting Analyzer")
    st.markdown(f"**Liga: {selected_league_flag} {selected_league_name}**")
    st.markdown("**Sistema de Análise de Apostas com Ensemble de Modelos**")
    st.markdown("---")
    
    # Sidebar - Informações
    with st.sidebar:
        st.header("ℹ️ Sobre")
        st.markdown("""
        Este sistema combina 3 modelos preditivos:
        - **Dixon-Coles** (55%)
        - **Offensive-Defensive** (30%)
        - **Heurísticas** (15%)
        
        Analisa apostas usando:
        - **Expected Value (EV)**
        - **Kelly Criterion**
        """)
        
        st.markdown("---")
        
        # Botão para limpar cache
        if st.button("🔄 Limpar Cache", help="Use se os modelos não estiverem funcionando corretamente"):
            st.cache_resource.clear()
            st.cache_data.clear()
            st.success("✅ Cache limpo! Recarregue a página (F5)")
        
        st.markdown("---")
        st.markdown("**📖 Como usar:**")
        st.markdown("""
        **Análise de Apostas:**
        1. Selecione uma partida
        2. Insira as odds da casa
        3. Configure sua banca
        4. Clique em **Analisar**
        5. Veja as recomendações!
        
        **Análise de Times:**
        1. Selecione a aba "Análise de Times"
        2. Escolha um time
        3. Veja histórico e estatísticas
        """)
        
        st.markdown("---")
        st.info("💡 **Dica:** Use Kelly Fraction de 0.25 para ser conservador.")
    
    # Cria abas principais
    tab1, tab2, tab3 = st.tabs([
        "🎯 Análise de Apostas", 
        "📊 Análise de Times", 
        "🎰 Bingo (Apostas Múltiplas)"
    ])
    
    with tab1:
        # Carrega ensemble
        try:
            ensemble = load_ensemble(selected_league_code)
            
            # Verifica status dos modelos
            models_status = []
            if ensemble.models.get('dixon_coles'):
                models_status.append("✅ Dixon-Coles")
            else:
                models_status.append("❌ Dixon-Coles")
            
            if ensemble.models.get('offensive_defensive'):
                models_status.append("✅ Offensive-Defensive")
            else:
                models_status.append("❌ Offensive-Defensive")
            
            if ensemble.models.get('heuristicas'):
                models_status.append("✅ Heurísticas")
            else:
                models_status.append("❌ Heurísticas")
            
            # Exibe status
            st.success(f"✅ Sistema carregado para {selected_league_flag} {selected_league_name}!")
            with st.expander("📊 Status dos Modelos", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if ensemble.models.get('dixon_coles'):
                        st.success("**Dixon-Coles**\n✅ Ativo (55%)")
                    else:
                        st.error("**Dixon-Coles**\n❌ Falhou")
                with col2:
                    if ensemble.models.get('offensive_defensive'):
                        st.success("**Offensive-Defensive**\n✅ Ativo (30%)")
                    else:
                        st.error("**Offensive-Defensive**\n❌ Falhou")
                with col3:
                    if ensemble.models.get('heuristicas'):
                        st.success("**Heurísticas**\n✅ Ativo (15%)")
                    else:
                        st.error("**Heurísticas**\n❌ Falhou")
        except Exception as e:
            st.error(f"❌ Erro ao carregar modelos: {e}")
            st.stop()
        
        # Busca partidas
        st.subheader(f"📅 Próximas Partidas - {selected_league_flag} {selected_league_name}")
        st.caption("🕐 Horários em UTC-3 (Brasília)")
        
        with st.spinner("Buscando próximas partidas..."):
            matches = get_upcoming_matches(selected_league_code)
        
        if not matches:
            st.warning("Nenhuma partida futura encontrada. Verifique a API.")
            st.stop()
        
        # Seleção da partida
        selected_match = display_match_selector(matches)
        
        if selected_match:
            st.info(f"**Partida selecionada:** {selected_match['home_team']} vs {selected_match['away_team']}")
        
        st.markdown("---")
        
        # Entrada de odds
        odds = display_odds_input()
        
        st.markdown("---")
        
        # Configuração de banca
        bankroll, kelly_fraction = display_bankroll_input()
        
        st.markdown("---")
        
        # Botão de análise
        if st.button("🔍 ANALISAR APOSTAS", type="primary", use_container_width=True):
            with st.container():
                analyze_and_display(ensemble, selected_match, odds, bankroll, kelly_fraction)
    
    with tab2:
        display_team_analysis()
    
    with tab3:
        display_bingo_analysis()


if __name__ == "__main__":
    main()

