"""
Interface Streamlit para o Sistema de Ranqueamento de Apostas
==============================================================

Interface interativa para ranquear apostas usando múltiplos critérios.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from betting_ranking import (
    BettingRankingSystem,
    ApostaInput,
    PerfilApostador,
    criar_sistema_ranking
)


# Configuração da página
st.set_page_config(
    page_title="Sistema de Ranqueamento de Apostas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS customizado
st.markdown("""
<style>
    .stAlert {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .best-bet {
        background-color: #ffd700;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #ff6347;
    }
    .high-rec {
        color: #00cc00;
        font-weight: bold;
    }
    .medium-rec {
        color: #ff9900;
        font-weight: bold;
    }
    .low-rec {
        color: #ffcc00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def formatar_recomendacao(recomendacao):
    """Formata a recomendação com cor"""
    cores = {
        "APOSTAR_ALTO": "high-rec",
        "APOSTAR_MEDIO": "medium-rec",
        "APOSTAR_BAIXO": "low-rec"
    }
    classe = cores.get(recomendacao, "")
    return f'<span class="{classe}">{recomendacao}</span>'


def criar_apostas_exemplo():
    """Cria apostas de exemplo para demonstração"""
    return [
        {
            "partida": "Flamengo vs Palmeiras",
            "mercado": "Resultado Final",
            "selecao": "Flamengo",
            "odds": 2.10,
            "p_model": 0.52,
            "ev_percent": 9.2,
            "edge": 4.5
        },
        {
            "partida": "São Paulo vs Santos",
            "mercado": "Mais de 2.5 Gols",
            "selecao": "Sim",
            "odds": 1.85,
            "p_model": 0.58,
            "ev_percent": 7.3,
            "edge": 3.8
        },
        {
            "partida": "Corinthians vs Internacional",
            "mercado": "Ambas Marcam",
            "selecao": "Sim",
            "odds": 1.75,
            "p_model": 0.62,
            "ev_percent": 8.5,
            "edge": 5.1
        },
        {
            "partida": "Atlético-MG vs Grêmio",
            "mercado": "Resultado Final",
            "selecao": "Atlético-MG",
            "odds": 1.65,
            "p_model": 0.55,
            "ev_percent": 2.3,
            "edge": 1.2
        },
        {
            "partida": "Botafogo vs Fluminense",
            "mercado": "Menos de 3.5 Gols",
            "selecao": "Sim",
            "odds": 1.55,
            "p_model": 0.68,
            "ev_percent": 5.4,
            "edge": 3.5
        },
    ]


def main():
    st.title("🎯 Sistema de Ranqueamento de Apostas")
    st.markdown("### Ranqueie suas apostas usando critérios avançados")
    
    # Sidebar - Configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Perfil do apostador
        perfil = st.selectbox(
            "Perfil do Apostador",
            options=["conservador", "moderado", "agressivo"],
            index=1,
            help="Define a agressividade do sistema de Kelly"
        )
        
        # Informação sobre o perfil
        perfil_info = {
            "conservador": {
                "kelly": "25%",
                "desc": "Menor risco, prioriza EV% e Edge",
                "color": "🟢"
            },
            "moderado": {
                "kelly": "50%",
                "desc": "Equilíbrio entre risco e retorno",
                "color": "🟡"
            },
            "agressivo": {
                "kelly": "100%",
                "desc": "Maior risco, prioriza probabilidade",
                "color": "🔴"
            }
        }
        
        info = perfil_info[perfil]
        st.info(f"{info['color']} **{perfil.upper()}**\n\n"
                f"Kelly: {info['kelly']}\n\n"
                f"{info['desc']}")
        
        st.divider()
        
        # Configurações de bankroll
        st.subheader("💰 Bankroll")
        bankroll = st.number_input(
            "Valor Total (R$)",
            min_value=100.0,
            max_value=1000000.0,
            value=1000.0,
            step=100.0
        )
        
        st.divider()
        
        # Limites de stake
        st.subheader("📊 Limites de Stake")
        stake_min = st.slider(
            "Stake Mínima (%)",
            min_value=0.1,
            max_value=5.0,
            value=0.5,
            step=0.1
        )
        
        stake_max = st.slider(
            "Stake Máxima (%)",
            min_value=1.0,
            max_value=25.0,
            value=12.0,
            step=0.5
        )
        
        st.divider()
        
        # Pesos do perfil (informativo)
        with st.expander("📋 Pesos do Perfil"):
            pesos = {
                "conservador": {"EV": 40, "Edge": 30, "P(model)": 20, "Stake": 10},
                "moderado": {"EV": 35, "Edge": 25, "P(model)": 25, "Stake": 15},
                "agressivo": {"EV": 25, "Edge": 20, "P(model)": 30, "Stake": 25}
            }
            
            p = pesos[perfil]
            st.write(f"**EV%:** {p['EV']}%")
            st.write(f"**Edge:** {p['Edge']}%")
            st.write(f"**P(model):** {p['P(model)]}%")
            st.write(f"**Stake:** {p['Stake']}%")
    
    # Área principal
    tab1, tab2, tab3 = st.tabs(["📊 Ranqueamento", "➕ Adicionar Apostas", "📚 Como Usar"])
    
    with tab1:
        st.header("Ranking de Apostas")
        
        # Inicializar estado da sessão
        if 'apostas' not in st.session_state:
            st.session_state.apostas = criar_apostas_exemplo()
        
        if not st.session_state.apostas:
            st.warning("Nenhuma aposta adicionada. Use a aba 'Adicionar Apostas' para começar.")
            return
        
        # Criar sistema de ranking
        sistema = criar_sistema_ranking(
            perfil=perfil,
            stake_min=stake_min,
            stake_max=stake_max,
            bankroll=bankroll
        )
        
        # Converter apostas para objetos ApostaInput
        apostas_input = []
        for i, aposta in enumerate(st.session_state.apostas):
            try:
                apostas_input.append(ApostaInput(
                    id=str(i),
                    partida=aposta['partida'],
                    mercado=aposta['mercado'],
                    selecao=aposta['selecao'],
                    odds=aposta['odds'],
                    p_model=aposta['p_model'],
                    ev_percent=aposta['ev_percent'],
                    edge=aposta['edge']
                ))
            except Exception as e:
                st.error(f"Erro ao processar aposta {i+1}: {e}")
        
        # Ranquear apostas
        apostas_ranqueadas = sistema.ranquear_apostas(apostas_input)
        
        # Filtrar apenas apostas recomendadas
        apostas_recomendadas = [
            a for a in apostas_ranqueadas 
            if a.recomendacao.value != "NÃO_APOSTAR"
        ]
        
        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Apostas", len(apostas_ranqueadas))
        
        with col2:
            st.metric("Recomendadas", len(apostas_recomendadas))
        
        with col3:
            exposicao = sum(a.stake_final for a in apostas_recomendadas)
            st.metric("Exposição Total", f"R$ {exposicao:.2f}")
        
        with col4:
            pct_exposicao = (exposicao / bankroll) * 100
            st.metric("% do Bankroll", f"{pct_exposicao:.1f}%")
        
        st.divider()
        
        # Exibir apostas ranqueadas
        if apostas_recomendadas:
            for i, aposta in enumerate(apostas_recomendadas, 1):
                # Destacar a melhor aposta
                if aposta.destacar:
                    st.markdown("### ⭐ MELHOR APOSTA DO DIA")
                
                with st.container():
                    # Criar colunas para layout
                    col_info, col_metricas, col_stake = st.columns([3, 2, 2])
                    
                    with col_info:
                        st.markdown(f"**#{i} - {aposta.partida}**")
                        st.write(f"**Mercado:** {aposta.mercado}")
                        st.write(f"**Seleção:** {aposta.selecao}")
                        st.write(f"**Odds:** {aposta.odds:.2f}")
                    
                    with col_metricas:
                        st.metric("Score", f"{aposta.score:.1f}/100")
                        st.write(f"**EV:** {aposta.ev_percent:+.2f}%")
                        st.write(f"**Edge:** {aposta.edge:+.2f}%")
                        st.write(f"**P(modelo):** {aposta.p_model:.1%}")
                    
                    with col_stake:
                        st.metric("Stake Sugerida", f"R$ {aposta.stake_final:.2f}")
                        st.write(f"**% Bankroll:** {aposta.stake_percent:.2f}%")
                        
                        # Cor da recomendação
                        rec_color = {
                            "APOSTAR_ALTO": "🟢",
                            "APOSTAR_MEDIO": "🟡",
                            "APOSTAR_BAIXO": "🟠"
                        }.get(aposta.recomendacao.value, "⚪")
                        
                        st.write(f"{rec_color} **{aposta.recomendacao.value}**")
                    
                    # Barra de progresso do score
                    st.progress(aposta.score / 100)
                    
                    # Detalhes expandíveis
                    with st.expander("📊 Detalhes do Score"):
                        detail_col1, detail_col2 = st.columns(2)
                        
                        with detail_col1:
                            st.write(f"**EV normalizado:** {aposta.ev_norm:.1f}/100")
                            st.write(f"**Edge normalizado:** {aposta.edge_norm:.1f}/100")
                        
                        with detail_col2:
                            st.write(f"**P(model) normalizado:** {aposta.p_model_norm:.1f}/100")
                            st.write(f"**Stake normalizado:** {aposta.stake_norm:.1f}/100")
                
                st.divider()
        else:
            st.info("Nenhuma aposta recomendada com os parâmetros atuais.")
        
        # Tabela resumo
        st.subheader("📋 Tabela Resumo")
        
        df_data = []
        for aposta in apostas_ranqueadas:
            df_data.append({
                "Rank": apostas_ranqueadas.index(aposta) + 1,
                "Partida": aposta.partida,
                "Mercado": aposta.mercado,
                "Seleção": aposta.selecao,
                "Odds": aposta.odds,
                "Score": round(aposta.score, 1),
                "EV%": round(aposta.ev_percent, 2),
                "Edge%": round(aposta.edge, 2),
                "Stake R$": round(aposta.stake_final, 2),
                "Stake %": round(aposta.stake_percent, 2),
                "Recomendação": aposta.recomendacao.value,
                "Destaque": "⭐" if aposta.destacar else ""
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"ranking_apostas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.header("Adicionar Novas Apostas")
        
        with st.form("adicionar_aposta"):
            col1, col2 = st.columns(2)
            
            with col1:
                partida = st.text_input("Partida", placeholder="Ex: Flamengo vs Palmeiras")
                mercado = st.text_input("Mercado", placeholder="Ex: Resultado Final")
                selecao = st.text_input("Seleção", placeholder="Ex: Flamengo")
            
            with col2:
                odds = st.number_input("Odds", min_value=1.01, max_value=100.0, value=2.0, step=0.01)
                p_model = st.number_input("P(modelo)", min_value=0.01, max_value=0.99, value=0.50, step=0.01)
                ev_percent = st.number_input("EV%", min_value=-100.0, max_value=100.0, value=5.0, step=0.1)
                edge = st.number_input("Edge%", min_value=-100.0, max_value=100.0, value=2.0, step=0.1)
            
            submitted = st.form_submit_button("➕ Adicionar Aposta")
            
            if submitted:
                if not partida or not mercado or not selecao:
                    st.error("Preencha todos os campos obrigatórios!")
                else:
                    nova_aposta = {
                        "partida": partida,
                        "mercado": mercado,
                        "selecao": selecao,
                        "odds": odds,
                        "p_model": p_model,
                        "ev_percent": ev_percent,
                        "edge": edge
                    }
                    st.session_state.apostas.append(nova_aposta)
                    st.success(f"✅ Aposta '{partida}' adicionada com sucesso!")
        
        st.divider()
        
        # Gerenciar apostas existentes
        st.subheader("Apostas Cadastradas")
        
        if st.session_state.apostas:
            for i, aposta in enumerate(st.session_state.apostas):
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.write(f"**{i+1}.** {aposta['partida']} - {aposta['mercado']} ({aposta['selecao']}) @ {aposta['odds']}")
                
                with col2:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.apostas.pop(i)
                        st.rerun()
            
            if st.button("🗑️ Limpar Todas"):
                st.session_state.apostas = []
                st.rerun()
            
            if st.button("🔄 Carregar Exemplos"):
                st.session_state.apostas = criar_apostas_exemplo()
                st.rerun()
        else:
            st.info("Nenhuma aposta cadastrada.")
    
    with tab3:
        st.header("Como Usar o Sistema")
        
        st.markdown("""
        ## 📖 Guia de Uso
        
        ### 1️⃣ Conceitos Básicos
        
        O sistema ranqueia apostas usando 4 critérios principais:
        
        - **EV% (Expected Value)**: Valor esperado da aposta em percentual
        - **Edge**: Diferença entre a probabilidade do modelo e a implícita nas odds
        - **P(modelo)**: Probabilidade estimada pelo seu modelo preditivo
        - **Stake**: Fração de Kelly ajustada conforme o perfil
        
        ### 2️⃣ Perfis de Apostador
        
        #### 🟢 Conservador
        - Fração de Kelly: 25%
        - Prioriza EV% (40%) e Edge (30%)
        - Menor exposição ao risco
        
        #### 🟡 Moderado
        - Fração de Kelly: 50%
        - Balanceado entre critérios
        - Recomendado para maioria dos apostadores
        
        #### 🔴 Agressivo
        - Fração de Kelly: 100%
        - Prioriza P(modelo) (30%) e Stake (25%)
        - Maior exposição ao risco
        
        ### 3️⃣ Sistema de Score
        
        Cada aposta recebe um score de 0 a 100 calculado como:
        
        ```
        Score = (EV_norm × w_ev + Edge_norm × w_edge + 
                 P_norm × w_p + Stake_norm × w_stake) / soma_pesos
        ```
        
        Onde cada variável é normalizada entre 0-100 baseada nos valores do dia.
        
        ### 4️⃣ Recomendações
        
        - **🟢 APOSTAR_ALTO**: Score ≥ 75
        - **🟡 APOSTAR_MEDIO**: Score entre 50-74
        - **🟠 APOSTAR_BAIXO**: Score entre 25-49
        - **⚪ NÃO_APOSTAR**: Score < 25 ou stake < mínimo
        
        ### 5️⃣ Como Adicionar Apostas
        
        1. Vá para a aba "Adicionar Apostas"
        2. Preencha os campos com dados da sua análise
        3. Clique em "Adicionar Aposta"
        4. Volte para a aba "Ranqueamento" para ver o resultado
        
        ### 6️⃣ Interpretação dos Resultados
        
        - A aposta com **⭐** é a melhor do dia
        - Verifique a **Exposição Total** para não exceder seu bankroll
        - Use os **Detalhes do Score** para entender por que uma aposta foi ranqueada
        
        ### ⚠️ Avisos Importantes
        
        - Este sistema é uma **ferramenta de auxílio**, não uma garantia de lucro
        - Sempre faça sua própria análise antes de apostar
        - Respeite seu bankroll e limites pessoais
        - Apostas esportivas envolvem risco
        """)


if __name__ == "__main__":
    main()

