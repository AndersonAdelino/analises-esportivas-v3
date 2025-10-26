"""
Página de Value Bets Automáticos
Mostra palpites de valor baseados nas odds da Bet365
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Adiciona o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from value_betting_auto import ValueBettingAuto
from config import LEAGUES
from config_economia import CASA_PREFERIDA


def formatar_data(data_str):
    """Formata data ISO para formato legível"""
    try:
        dt = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return data_str


def main():
    st.title("💰 Value Bets Automáticos")
    st.markdown(f"**Casa de referência:** {CASA_PREFERIDA.upper()}")
    
    # Sidebar - Configurações
    st.sidebar.header("⚙️ Configurações")
    
    # Seleção de ligas
    ligas_disponiveis = list(LEAGUES.keys())
    ligas_selecionadas = st.sidebar.multiselect(
        "📊 Ligas para Analisar",
        ligas_disponiveis,
        default=ligas_disponiveis[:2]  # Primeiras 2 por padrão
    )
    
    # Filtros
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtros")
    
    mercados_filtro = st.sidebar.multiselect(
        "Mercados",
        ['1X2', 'Over/Under', 'BTTS'],
        default=['1X2', 'Over/Under']
    )
    
    min_value_percent = st.sidebar.slider(
        "Value Mínimo (%)",
        min_value=0,
        max_value=50,
        value=5,
        step=1,
        help="Porcentagem mínima de value para mostrar"
    )
    
    min_ev_percent = st.sidebar.slider(
        "EV Mínimo (%)",
        min_value=-10,
        max_value=50,
        value=0,
        step=1,
        help="Expected Value mínimo para mostrar"
    )
    
    # Ordenação
    ordenar_por = st.sidebar.selectbox(
        "📈 Ordenar por",
        ['EV (Maior)', 'EV (Menor)', 'Probabilidade (Maior)', 'Probabilidade (Menor)', 'Value (Maior)', 'Value (Menor)']
    )
    
    # Botão de atualizar
    if st.sidebar.button("🔄 Atualizar Dados", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Info
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **💡 Como funciona:**
    
    1. Busca odds da Bet365
    2. Calcula probabilidades com os modelos
    3. Identifica value bets automaticamente
    4. Mostra oportunidades ordenadas
    
    **Mercados:**
    - 1X2: Casa/Empate/Fora
    - Over/Under: Mais/Menos 2.5 gols
    - BTTS: Ambos marcam
    """)
    
    # Conteúdo principal
    if not ligas_selecionadas:
        st.warning("⚠️ Selecione pelo menos uma liga para analisar")
        return
    
    # Busca value bets
    with st.spinner(f"🔍 Buscando value bets em {len(ligas_selecionadas)} liga(s)..."):
        try:
            vb = ValueBettingAuto(casa=CASA_PREFERIDA)
            df = vb.analisar_todas_ligas(ligas_selecionadas)
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados: {e}")
            st.info("💡 Certifique-se de que ODDS_API_KEY está configurada no .env")
            return
    
    if len(df) == 0:
        st.warning("⚠️ Nenhum value bet encontrado no momento")
        st.info("""
        **Possíveis motivos:**
        - Não há jogos agendados
        - As odds estão muito ajustadas (mercado eficiente)
        - Os modelos não identificaram value significativo
        
        Tente:
        - Reduzir o value mínimo
        - Selecionar outras ligas
        - Aguardar novos jogos
        """)
        return
    
    # Aplica filtros
    df_filtrado = df.copy()
    
    # Filtro de mercados
    if mercados_filtro:
        df_filtrado = df_filtrado[df_filtrado['mercado'].isin(mercados_filtro)]
    
    # Filtro de value
    df_filtrado = df_filtrado[df_filtrado['value_percent'] >= min_value_percent]
    
    # Filtro de EV
    df_filtrado = df_filtrado[df_filtrado['ev'] >= min_ev_percent]
    
    if len(df_filtrado) == 0:
        st.warning("⚠️ Nenhum value bet encontrado com os filtros atuais")
        st.info("Tente reduzir os filtros mínimos na barra lateral")
        return
    
    # Ordenação
    if 'EV' in ordenar_por:
        ascending = 'Menor' in ordenar_por
        df_filtrado = df_filtrado.sort_values('ev', ascending=ascending)
    elif 'Probabilidade' in ordenar_por:
        ascending = 'Menor' in ordenar_por
        df_filtrado = df_filtrado.sort_values('prob_modelo', ascending=ascending)
    elif 'Value' in ordenar_por:
        ascending = 'Menor' in ordenar_por
        df_filtrado = df_filtrado.sort_values('value_percent', ascending=ascending)
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Value Bets", len(df_filtrado))
    
    with col2:
        ev_medio = df_filtrado['ev'].mean()
        st.metric("📊 EV Médio", f"{ev_medio:.2f}%")
    
    with col3:
        value_medio = df_filtrado['value_percent'].mean()
        st.metric("💎 Value Médio", f"{value_medio:.2f}%")
    
    with col4:
        partidas_unicas = df_filtrado['partida'].nunique()
        st.metric("⚽ Partidas", partidas_unicas)
    
    st.markdown("---")
    
    # Tabs para visualização
    tab1, tab2, tab3 = st.tabs(["📊 Lista Completa", "🏆 Top 10", "📈 Estatísticas"])
    
    with tab1:
        st.subheader("📋 Todos os Value Bets")
        
        # Formata DataFrame para exibição
        df_display = df_filtrado.copy()
        df_display['data'] = df_display['data'].apply(formatar_data)
        df_display['prob_modelo'] = df_display['prob_modelo'].apply(lambda x: f"{x:.1f}%")
        df_display['value_percent'] = df_display['value_percent'].apply(lambda x: f"+{x:.1f}%")
        df_display['ev'] = df_display['ev'].apply(lambda x: f"{x:+.2f}%")
        df_display['odd_mercado'] = df_display['odd_mercado'].apply(lambda x: f"{x:.2f}")
        df_display['kelly'] = df_display['kelly'].apply(lambda x: f"{x*100:.1f}%")
        
        # Seleciona colunas para exibir
        colunas_exibir = ['partida', 'liga', 'data', 'mercado', 'tipo', 'odd_mercado', 'prob_modelo', 'value_percent', 'ev', 'kelly']
        
        # Renomeia colunas
        nomes_colunas = {
            'partida': 'Partida',
            'liga': 'Liga',
            'data': 'Data/Hora',
            'mercado': 'Mercado',
            'tipo': 'Aposta',
            'odd_mercado': 'Odd',
            'prob_modelo': 'Prob.',
            'value_percent': 'Value',
            'ev': 'EV',
            'kelly': 'Kelly'
        }
        
        df_final = df_display[colunas_exibir].rename(columns=nomes_colunas)
        
        # Estilo condicional (verde para EV positivo alto)
        st.dataframe(
            df_final,
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Botão de download
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"value_bets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("🏆 Top 10 Value Bets")
        
        top10 = df_filtrado.head(10)
        
        for idx, row in top10.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {row['partida']}")
                    st.markdown(f"**{row['mercado']}** - {row['tipo']}")
                    st.caption(f"📅 {formatar_data(row['data'])} | 🏆 {row['liga']}")
                
                with col2:
                    st.metric("Odd", f"{row['odd_mercado']:.2f}")
                    st.metric("Prob.", f"{row['prob_modelo']:.1f}%")
                
                with col3:
                    st.metric("Value", f"+{row['value_percent']:.1f}%", delta=None)
                    st.metric("EV", f"{row['ev']:+.2f}%", delta=None)
                
                # Barra de progresso do Kelly
                st.progress(min(row['kelly'], 1.0), text=f"Kelly Criterion: {row['kelly']*100:.1f}%")
                
                st.markdown("---")
    
    with tab3:
        st.subheader("📊 Estatísticas Detalhadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Por Mercado")
            mercados_count = df_filtrado['mercado'].value_counts()
            st.bar_chart(mercados_count)
            
            st.markdown("### 🏆 Por Liga")
            ligas_count = df_filtrado['liga'].value_counts()
            st.bar_chart(ligas_count)
        
        with col2:
            st.markdown("### 💰 Distribuição de EV")
            st.line_chart(df_filtrado['ev'].sort_values(ascending=False).reset_index(drop=True))
            
            st.markdown("### 💎 Distribuição de Value")
            st.line_chart(df_filtrado['value_percent'].sort_values(ascending=False).reset_index(drop=True))
        
        # Tabela de resumo
        st.markdown("### 📊 Resumo por Mercado")
        
        resumo = df_filtrado.groupby('mercado').agg({
            'ev': ['mean', 'min', 'max'],
            'value_percent': ['mean', 'min', 'max'],
            'partida': 'count'
        }).round(2)
        
        resumo.columns = ['EV Médio', 'EV Mín', 'EV Máx', 'Value Médio', 'Value Mín', 'Value Máx', 'Quantidade']
        st.dataframe(resumo, use_container_width=True)
    
    # Rodapé
    st.markdown("---")
    st.caption(f"""
    **⚠️ Aviso:** Este sistema usa modelos preditivos para identificar value bets. 
    Os resultados são baseados em probabilidades estatísticas e não garantem lucro.
    Aposte com responsabilidade.
    
    **Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    """)


if __name__ == "__main__":
    main()

