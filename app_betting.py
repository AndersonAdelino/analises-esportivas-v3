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


@st.cache_data(ttl=3600)  # Cache por 1 hora
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


@st.cache_data(ttl=3600)  # Cache por 1 hora
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


@st.cache_data(ttl=3600)  # Cache por 1 hora
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
        st.success(f"✅ {len(value_bets)} Value Bet(s) identificado(s)!")
        
        for idx, vb in enumerate(value_bets):
            with st.expander(f"🎯 {vb['market']} - APOSTE R$ {vb['analysis']['stake_recommended']:.2f}", expanded=True):
                analysis = vb['analysis']
                
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


def main():
    """Função principal da aplicação"""
    
    # Inicializar bingo analyzer no session_state
    if 'bingo_analyzer' not in st.session_state:
        st.session_state.bingo_analyzer = BingoAnalyzer()
    
    # Sidebar - Seleção de Liga (no topo)
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Seletor de Liga
        league_options = list(config.LEAGUES.keys())
        selected_league_name = st.selectbox(
            "🏆 Selecione a Liga",
            options=league_options,
            index=0,  # Premier League como padrão
            help="Escolha a liga para análise"
        )
        
        # Obtém código da liga selecionada
        selected_league_code = config.LEAGUES[selected_league_name]['code']
        selected_league_flag = config.LEAGUES[selected_league_name]['flag']
        
        # Armazena no session_state para uso em outras funções
        st.session_state['selected_league_code'] = selected_league_code
        st.session_state['selected_league_name'] = selected_league_name
        
        st.markdown("---")
    
    # Título com liga selecionada
    st.title(f"{selected_league_flag} Value Betting Analyzer")
    st.markdown(f"**Liga: {selected_league_name}**")
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
    tab1, tab2, tab3 = st.tabs(["🎯 Análise de Apostas", "📊 Análise de Times", "🎰 Bingo (Apostas Múltiplas)"])
    
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
            st.success(f"✅ Sistema carregado para {selected_league_name}!")
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
        st.subheader(f"📅 Próximas Partidas - {selected_league_name}")
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

