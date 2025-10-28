"""
Exemplo Completo de Uso do Sistema de Ranqueamento
===================================================

Este script demonstra como usar o sistema de ranqueamento
em conjunto com suas análises esportivas.
"""

from betting_ranking import criar_sistema_ranking, ApostaInput
from datetime import datetime
import pandas as pd


def exemplo_basico():
    """Exemplo básico de uso do sistema"""
    print("=" * 80)
    print("EXEMPLO 1: Uso Básico")
    print("=" * 80)
    
    # Criar sistema com perfil moderado
    sistema = criar_sistema_ranking(
        perfil="moderado",
        stake_min=0.5,
        stake_max=12.0,
        bankroll=1000.0
    )
    
    # Criar apostas
    apostas = [
        ApostaInput(
            id="1",
            partida="Flamengo vs Palmeiras",
            mercado="Resultado Final",
            selecao="Flamengo",
            odds=2.10,
            p_model=0.52,
            ev_percent=9.2,
            edge=4.5
        ),
        ApostaInput(
            id="2",
            partida="São Paulo vs Santos",
            mercado="Mais de 2.5 Gols",
            selecao="Sim",
            odds=1.85,
            p_model=0.58,
            ev_percent=7.3,
            edge=3.8
        ),
    ]
    
    # Ranquear
    ranqueadas = sistema.ranquear_apostas(apostas)
    
    # Exibir resultados
    for aposta in ranqueadas:
        destaque = "[MELHOR]" if aposta.destacar else ""
        print(f"\n{destaque} {aposta.partida}")
        print(f"  Score: {aposta.score:.1f}/100")
        print(f"  Stake: R$ {aposta.stake_final:.2f} ({aposta.stake_percent:.2f}%)")
        print(f"  Recomendação: {aposta.recomendacao.value}")


def exemplo_multiplos_perfis():
    """Exemplo comparando diferentes perfis"""
    print("\n" + "=" * 80)
    print("EXEMPLO 2: Comparação de Perfis")
    print("=" * 80)
    
    # Aposta de exemplo
    aposta = ApostaInput(
        id="1",
        partida="Corinthians vs Internacional",
        mercado="Ambas Marcam",
        selecao="Sim",
        odds=1.75,
        p_model=0.62,
        ev_percent=8.5,
        edge=5.1
    )
    
    print(f"\nAposta: {aposta.partida} - {aposta.mercado}")
    print(f"Odds: {aposta.odds} | P(modelo): {aposta.p_model:.0%}")
    print(f"EV: {aposta.ev_percent:+.2f}% | Edge: {aposta.edge:+.2f}%")
    print("\nAnálise por perfil:")
    print("-" * 80)
    
    # Testar cada perfil
    for perfil in ["conservador", "moderado", "agressivo"]:
        sistema = criar_sistema_ranking(
            perfil=perfil,
            bankroll=1000.0
        )
        
        ranqueadas = sistema.ranquear_apostas([aposta])
        resultado = ranqueadas[0]
        
        print(f"\n{perfil.upper()}")
        print(f"  Score: {resultado.score:.1f}/100")
        print(f"  Stake: R$ {resultado.stake_final:.2f} ({resultado.stake_percent:.2f}%)")
        print(f"  Kelly: {sistema.fracao_kelly:.0%}")


def exemplo_portfolio_apostas():
    """Exemplo de portfolio completo de apostas"""
    print("\n" + "=" * 80)
    print("EXEMPLO 3: Portfolio de Apostas")
    print("=" * 80)
    
    # Criar sistema
    sistema = criar_sistema_ranking(
        perfil="moderado",
        bankroll=2000.0,
        stake_min=0.5,
        stake_max=10.0
    )
    
    # Portfolio de apostas do dia
    apostas = [
        ApostaInput(
            id="1",
            partida="Flamengo vs Palmeiras",
            mercado="Resultado Final",
            selecao="Flamengo",
            odds=2.10,
            p_model=0.52,
            ev_percent=9.2,
            edge=4.5
        ),
        ApostaInput(
            id="2",
            partida="São Paulo vs Santos",
            mercado="Mais de 2.5 Gols",
            selecao="Sim",
            odds=1.85,
            p_model=0.58,
            ev_percent=7.3,
            edge=3.8
        ),
        ApostaInput(
            id="3",
            partida="Corinthians vs Internacional",
            mercado="Ambas Marcam",
            selecao="Sim",
            odds=1.75,
            p_model=0.62,
            ev_percent=8.5,
            edge=5.1
        ),
        ApostaInput(
            id="4",
            partida="Atlético-MG vs Grêmio",
            mercado="Resultado Final",
            selecao="Atlético-MG",
            odds=1.65,
            p_model=0.55,
            ev_percent=2.3,
            edge=1.2
        ),
        ApostaInput(
            id="5",
            partida="Botafogo vs Fluminense",
            mercado="Menos de 3.5 Gols",
            selecao="Sim",
            odds=1.55,
            p_model=0.68,
            ev_percent=5.4,
            edge=3.5
        ),
    ]
    
    # Ranquear
    ranqueadas = sistema.ranquear_apostas(apostas)
    
    # Filtrar recomendadas
    recomendadas = [
        a for a in ranqueadas 
        if a.recomendacao.value != "NÃO_APOSTAR"
    ]
    
    print(f"\nPortfolio: {len(apostas)} apostas analisadas")
    print(f"Recomendadas: {len(recomendadas)}")
    print(f"Bankroll: R$ {sistema.bankroll:,.2f}")
    print("\n" + "-" * 80)
    
    # Estatísticas do portfolio
    total_stake = sum(a.stake_final for a in recomendadas)
    exposicao_pct = (total_stake / sistema.bankroll) * 100
    
    print(f"\nEstatísticas do Portfolio:")
    print(f"  Exposição Total: R$ {total_stake:,.2f} ({exposicao_pct:.1f}% do bankroll)")
    
    ev_medio = sum(a.ev_percent for a in recomendadas) / len(recomendadas) if recomendadas else 0
    print(f"  EV% Médio: {ev_medio:+.2f}%")
    
    score_medio = sum(a.score for a in recomendadas) / len(recomendadas) if recomendadas else 0
    print(f"  Score Médio: {score_medio:.1f}/100")
    
    # Top 3 apostas
    print("\n" + "-" * 80)
    print("TOP 3 APOSTAS:")
    print("-" * 80)
    
    for i, aposta in enumerate(recomendadas[:3], 1):
        destaque = "[MELHOR] " if aposta.destacar else ""
        print(f"\n{destaque}#{i} - {aposta.partida}")
        print(f"  Mercado: {aposta.mercado} ({aposta.selecao})")
        print(f"  Score: {aposta.score:.1f}/100")
        print(f"  Odds: {aposta.odds:.2f}")
        print(f"  Stake: R$ {aposta.stake_final:.2f} ({aposta.stake_percent:.2f}%)")
        print(f"  EV: {aposta.ev_percent:+.2f}% | Edge: {aposta.edge:+.2f}%")
        print(f"  Recomendação: {aposta.recomendacao.value}")


def exemplo_geracao_relatorio():
    """Exemplo de geração de relatório completo"""
    print("\n" + "=" * 80)
    print("EXEMPLO 4: Relatório Completo")
    print("=" * 80)
    
    sistema = criar_sistema_ranking(
        perfil="conservador",
        bankroll=5000.0
    )
    
    apostas = [
        ApostaInput(
            id="1",
            partida="Real Madrid vs Barcelona",
            mercado="Resultado Final",
            selecao="Real Madrid",
            odds=2.20,
            p_model=0.50,
            ev_percent=10.0,
            edge=4.5
        ),
        ApostaInput(
            id="2",
            partida="Liverpool vs Manchester City",
            mercado="Mais de 2.5 Gols",
            selecao="Sim",
            odds=1.90,
            p_model=0.60,
            ev_percent=14.0,
            edge=7.4
        ),
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    relatorio = sistema.gerar_relatorio(ranqueadas, top_n=5)
    
    print("\n" + relatorio)


def exemplo_exportar_csv():
    """Exemplo de exportação para CSV"""
    print("\n" + "=" * 80)
    print("EXEMPLO 5: Exportar para CSV")
    print("=" * 80)
    
    sistema = criar_sistema_ranking(perfil="moderado", bankroll=1000.0)
    
    apostas = [
        ApostaInput(
            id=str(i),
            partida=f"Jogo {i}",
            mercado="Resultado",
            selecao="Casa",
            odds=2.0 + (i * 0.1),
            p_model=0.50 + (i * 0.02),
            ev_percent=5.0 + i,
            edge=2.0 + (i * 0.5)
        )
        for i in range(1, 6)
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    
    # Criar DataFrame
    data = []
    for rank, aposta in enumerate(ranqueadas, 1):
        data.append({
            'Rank': rank,
            'Partida': aposta.partida,
            'Mercado': aposta.mercado,
            'Selecao': aposta.selecao,
            'Odds': aposta.odds,
            'P_Modelo': aposta.p_model,
            'EV_Percent': aposta.ev_percent,
            'Edge': aposta.edge,
            'Score': round(aposta.score, 2),
            'Stake_R$': round(aposta.stake_final, 2),
            'Stake_%': round(aposta.stake_percent, 2),
            'Recomendacao': aposta.recomendacao.value,
            'Destaque': 'Sim' if aposta.destacar else 'Não'
        })
    
    df = pd.DataFrame(data)
    
    # Salvar CSV
    filename = f"ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\nDataFrame criado com {len(df)} apostas")
    print(f"Arquivo salvo: {filename}")
    print("\nPrimeiras linhas:")
    print(df.head())


def exemplo_analise_detalhada():
    """Exemplo de análise detalhada de uma aposta"""
    print("\n" + "=" * 80)
    print("EXEMPLO 6: Análise Detalhada")
    print("=" * 80)
    
    sistema = criar_sistema_ranking(
        perfil="moderado",
        bankroll=1000.0
    )
    
    aposta = ApostaInput(
        id="1",
        partida="Bayern Munich vs Borussia Dortmund",
        mercado="Ambas Marcam",
        selecao="Sim",
        odds=1.80,
        p_model=0.65,
        ev_percent=17.0,
        edge=9.4
    )
    
    ranqueadas = sistema.ranquear_apostas([aposta])
    resultado = ranqueadas[0]
    
    print(f"\nAposta: {resultado.partida}")
    print(f"Mercado: {resultado.mercado} - {resultado.selecao}")
    print("-" * 80)
    
    print("\nDados de Entrada:")
    print(f"  Odds: {resultado.odds:.2f}")
    print(f"  P(modelo): {resultado.p_model:.2%}")
    print(f"  EV%: {resultado.ev_percent:+.2f}%")
    print(f"  Edge: {resultado.edge:+.2f}%")
    
    print("\nComponentes Normalizados (0-100):")
    print(f"  EV normalizado: {resultado.ev_norm:.1f}")
    print(f"  Edge normalizado: {resultado.edge_norm:.1f}")
    print(f"  P(modelo) normalizado: {resultado.p_model_norm:.1f}")
    print(f"  Stake normalizado: {resultado.stake_norm:.1f}")
    
    print("\nResultado do Ranqueamento:")
    print(f"  Score Final: {resultado.score:.1f}/100")
    print(f"  Stake Sugerida: R$ {resultado.stake_final:.2f} ({resultado.stake_percent:.2f}%)")
    print(f"  Recomendação: {resultado.recomendacao.value}")
    print(f"  Destaque: {'SIM [MELHOR]' if resultado.destacar else 'Não'}")
    
    # Cálculo manual do retorno esperado
    retorno_esperado = resultado.stake_final * (resultado.ev_percent / 100)
    print(f"\nRetorno Esperado (a longo prazo): R$ {retorno_esperado:+.2f}")


def exemplo_gestao_bankroll():
    """Exemplo de gestão de bankroll com múltiplas sessões"""
    print("\n" + "=" * 80)
    print("EXEMPLO 7: Gestão de Bankroll")
    print("=" * 80)
    
    bankroll_inicial = 1000.0
    bankroll_atual = bankroll_inicial
    
    print(f"\nBankroll Inicial: R$ {bankroll_inicial:,.2f}")
    print("\nSimulando 3 sessões de apostas...")
    
    sessoes = [
        {
            "nome": "Sessão 1 - Rodada Brasileirão",
            "apostas": [
                {"odds": 2.1, "p_model": 0.52, "ev": 9.2, "edge": 4.5},
                {"odds": 1.85, "p_model": 0.58, "ev": 7.3, "edge": 3.8},
            ]
        },
        {
            "nome": "Sessão 2 - Champions League",
            "apostas": [
                {"odds": 1.75, "p_model": 0.62, "ev": 8.5, "edge": 5.1},
            ]
        },
        {
            "nome": "Sessão 3 - Premier League",
            "apostas": [
                {"odds": 2.2, "p_model": 0.50, "ev": 10.0, "edge": 4.5},
                {"odds": 1.9, "p_model": 0.60, "ev": 14.0, "edge": 7.4},
            ]
        }
    ]
    
    for i, sessao in enumerate(sessoes, 1):
        print(f"\n{'-' * 80}")
        print(f"{sessao['nome']}")
        print(f"{'-' * 80}")
        
        # Criar sistema com bankroll atual
        sistema = criar_sistema_ranking(
            perfil="moderado",
            bankroll=bankroll_atual
        )
        
        # Criar apostas
        apostas_input = []
        for j, dados in enumerate(sessao['apostas']):
            apostas_input.append(ApostaInput(
                id=f"s{i}_a{j}",
                partida=f"Jogo {j+1}",
                mercado="Mercado Exemplo",
                selecao="Seleção",
                odds=dados['odds'],
                p_model=dados['p_model'],
                ev_percent=dados['ev'],
                edge=dados['edge']
            ))
        
        ranqueadas = sistema.ranquear_apostas(apostas_input)
        recomendadas = [a for a in ranqueadas if a.recomendacao.value != "NÃO_APOSTAR"]
        
        total_apostado = sum(a.stake_final for a in recomendadas)
        
        print(f"Bankroll disponível: R$ {bankroll_atual:,.2f}")
        print(f"Total a apostar: R$ {total_apostado:,.2f}")
        print(f"Exposição: {(total_apostado/bankroll_atual)*100:.1f}%")
        
        # Simular resultado (apenas exemplo - na prática seria o resultado real)
        # Aqui assumimos um ROI baseado no EV médio
        ev_medio = sum(a.ev_percent for a in recomendadas) / len(recomendadas) if recomendadas else 0
        lucro_sessao = total_apostado * (ev_medio / 100) * 0.7  # 70% do EV realizado
        
        bankroll_atual += lucro_sessao
        
        print(f"Resultado da sessão: R$ {lucro_sessao:+,.2f}")
        print(f"Novo bankroll: R$ {bankroll_atual:,.2f}")
    
    print(f"\n{'=' * 80}")
    print("RESUMO GERAL")
    print(f"{'=' * 80}")
    print(f"Bankroll Inicial: R$ {bankroll_inicial:,.2f}")
    print(f"Bankroll Final: R$ {bankroll_atual:,.2f}")
    lucro_total = bankroll_atual - bankroll_inicial
    roi = (lucro_total / bankroll_inicial) * 100
    print(f"Lucro/Prejuízo: R$ {lucro_total:+,.2f} ({roi:+.1f}%)")


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("EXEMPLOS DE USO DO SISTEMA DE RANQUEAMENTO DE APOSTAS")
    print("=" * 80)
    
    exemplo_basico()
    exemplo_multiplos_perfis()
    exemplo_portfolio_apostas()
    exemplo_geracao_relatorio()
    exemplo_exportar_csv()
    exemplo_analise_detalhada()
    exemplo_gestao_bankroll()
    
    print("\n" + "=" * 80)
    print("EXEMPLOS CONCLUÍDOS")
    print("=" * 80)
    print("\nPara mais informações, consulte: GUIA_SISTEMA_RANQUEAMENTO.md")
    print()

