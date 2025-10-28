"""
Testes para o Sistema de Ranqueamento de Apostas
"""

import pytest
from betting_ranking import (
    BettingRankingSystem,
    ApostaInput,
    PerfilApostador,
    RecomendacaoNivel,
    criar_sistema_ranking
)


def test_criar_aposta_input():
    """Testa criação de aposta input válida"""
    aposta = ApostaInput(
        id="1",
        partida="Time A vs Time B",
        mercado="Resultado",
        selecao="Time A",
        odds=2.0,
        p_model=0.55,
        ev_percent=10.0,
        edge=5.0
    )
    
    assert aposta.id == "1"
    assert aposta.odds == 2.0
    assert aposta.p_model == 0.55


def test_aposta_input_odds_invalida():
    """Testa validação de odds inválida"""
    with pytest.raises(ValueError):
        ApostaInput(
            id="1",
            partida="Time A vs Time B",
            mercado="Resultado",
            selecao="Time A",
            odds=0.5,  # Odds inválida
            p_model=0.55,
            ev_percent=10.0,
            edge=5.0
        )


def test_aposta_input_p_model_invalida():
    """Testa validação de p_model inválida"""
    with pytest.raises(ValueError):
        ApostaInput(
            id="1",
            partida="Time A vs Time B",
            mercado="Resultado",
            selecao="Time A",
            odds=2.0,
            p_model=1.5,  # Probabilidade inválida
            ev_percent=10.0,
            edge=5.0
        )


def test_criar_sistema_ranking():
    """Testa criação do sistema de ranking"""
    sistema = criar_sistema_ranking(
        perfil="moderado",
        stake_min=0.5,
        stake_max=10.0,
        bankroll=1000.0
    )
    
    assert sistema.perfil == PerfilApostador.MODERADO
    assert sistema.stake_min_percent == 0.5
    assert sistema.stake_max_percent == 10.0
    assert sistema.bankroll == 1000.0
    assert sistema.fracao_kelly == 0.50


def test_calcular_stake_kelly():
    """Testa cálculo de stake usando Kelly"""
    sistema = criar_sistema_ranking(perfil="moderado", bankroll=1000.0)
    
    # Aposta com edge positivo
    stake = sistema.calcular_stake_kelly(p_model=0.55, odds=2.0)
    assert stake > 0
    assert stake <= sistema.stake_max_percent
    
    # Aposta sem edge
    stake_zero = sistema.calcular_stake_kelly(p_model=0.50, odds=2.0)
    assert stake_zero >= 0


def test_normalizar_valores():
    """Testa normalização de valores"""
    sistema = criar_sistema_ranking()
    
    valores = [10, 20, 30, 40, 50]
    normalizados = sistema.normalizar_valores(valores)
    
    assert len(normalizados) == len(valores)
    assert min(normalizados) == 0.0
    assert max(normalizados) == 100.0
    
    # Valores iguais
    valores_iguais = [5, 5, 5]
    norm_iguais = sistema.normalizar_valores(valores_iguais)
    assert all(v == 50.0 for v in norm_iguais)


def test_calcular_score():
    """Testa cálculo de score"""
    sistema = criar_sistema_ranking(perfil="moderado")
    
    score = sistema.calcular_score(
        ev_norm=80.0,
        edge_norm=70.0,
        p_model_norm=60.0,
        stake_norm=50.0
    )
    
    assert 0 <= score <= 100
    assert isinstance(score, float)


def test_determinar_recomendacao():
    """Testa determinação de nível de recomendação"""
    sistema = criar_sistema_ranking()
    
    # Score alto
    rec_alto = sistema.determinar_recomendacao(score=80, stake_percent=5.0)
    assert rec_alto == RecomendacaoNivel.APOSTAR_ALTO
    
    # Score médio
    rec_medio = sistema.determinar_recomendacao(score=60, stake_percent=3.0)
    assert rec_medio == RecomendacaoNivel.APOSTAR_MEDIO
    
    # Score baixo
    rec_baixo = sistema.determinar_recomendacao(score=30, stake_percent=2.0)
    assert rec_baixo == RecomendacaoNivel.APOSTAR_BAIXO
    
    # Stake muito pequeno
    rec_nao = sistema.determinar_recomendacao(score=80, stake_percent=0.1)
    assert rec_nao == RecomendacaoNivel.NAO_APOSTAR


def test_ranquear_apostas():
    """Testa ranqueamento completo de apostas"""
    sistema = criar_sistema_ranking(perfil="moderado", bankroll=1000.0)
    
    apostas = [
        ApostaInput(
            id="1",
            partida="Jogo 1",
            mercado="Resultado",
            selecao="Casa",
            odds=2.0,
            p_model=0.55,
            ev_percent=10.0,
            edge=5.0
        ),
        ApostaInput(
            id="2",
            partida="Jogo 2",
            mercado="Gols",
            selecao="Mais 2.5",
            odds=1.8,
            p_model=0.60,
            ev_percent=8.0,
            edge=4.0
        ),
        ApostaInput(
            id="3",
            partida="Jogo 3",
            mercado="Ambas Marcam",
            selecao="Sim",
            odds=1.7,
            p_model=0.52,
            ev_percent=3.0,
            edge=1.5
        ),
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    
    # Verificações básicas
    assert len(ranqueadas) == len(apostas)
    assert all(hasattr(a, 'score') for a in ranqueadas)
    assert all(hasattr(a, 'stake_final') for a in ranqueadas)
    assert all(hasattr(a, 'recomendacao') for a in ranqueadas)
    
    # Verificar ordenação por score (decrescente)
    scores = [a.score for a in ranqueadas]
    assert scores == sorted(scores, reverse=True)
    
    # Verificar que existe uma aposta destacada
    destacadas = [a for a in ranqueadas if a.destacar]
    assert len(destacadas) <= 1
    
    # Se há aposta destacada, deve ser a primeira
    if destacadas:
        assert ranqueadas[0].destacar


def test_perfis_diferentes():
    """Testa que diferentes perfis produzem resultados diferentes"""
    apostas = [
        ApostaInput(
            id="1",
            partida="Jogo Test",
            mercado="Resultado",
            selecao="Casa",
            odds=2.0,
            p_model=0.55,
            ev_percent=10.0,
            edge=5.0
        )
    ]
    
    # Ranquear com diferentes perfis
    conservador = criar_sistema_ranking(perfil="conservador", bankroll=1000.0)
    moderado = criar_sistema_ranking(perfil="moderado", bankroll=1000.0)
    agressivo = criar_sistema_ranking(perfil="agressivo", bankroll=1000.0)
    
    rank_conservador = conservador.ranquear_apostas(apostas)
    rank_moderado = moderado.ranquear_apostas(apostas)
    rank_agressivo = agressivo.ranquear_apostas(apostas)
    
    # Stakes devem ser diferentes
    stake_conservador = rank_conservador[0].stake_percent
    stake_moderado = rank_moderado[0].stake_percent
    stake_agressivo = rank_agressivo[0].stake_percent
    
    # Conservador deve ter menor stake
    assert stake_conservador <= stake_moderado <= stake_agressivo


def test_lista_vazia():
    """Testa ranqueamento com lista vazia"""
    sistema = criar_sistema_ranking()
    ranqueadas = sistema.ranquear_apostas([])
    
    assert ranqueadas == []


def test_gerar_relatorio():
    """Testa geração de relatório"""
    sistema = criar_sistema_ranking(perfil="moderado", bankroll=1000.0)
    
    apostas = [
        ApostaInput(
            id="1",
            partida="Jogo 1",
            mercado="Resultado",
            selecao="Casa",
            odds=2.0,
            p_model=0.55,
            ev_percent=10.0,
            edge=5.0
        )
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    relatorio = sistema.gerar_relatorio(ranqueadas, top_n=5)
    
    assert isinstance(relatorio, str)
    assert len(relatorio) > 0
    assert "RANKING DE APOSTAS" in relatorio
    assert "MODERADO" in relatorio


def test_stake_limits():
    """Testa que os limites de stake são respeitados"""
    sistema = criar_sistema_ranking(
        perfil="agressivo",
        stake_min=1.0,
        stake_max=10.0,
        bankroll=1000.0
    )
    
    apostas = [
        ApostaInput(
            id="1",
            partida="Jogo 1",
            mercado="Resultado",
            selecao="Casa",
            odds=1.5,
            p_model=0.70,  # Probabilidade alta
            ev_percent=5.0,
            edge=2.5
        )
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    
    # Stake não deve exceder o máximo
    assert ranqueadas[0].stake_percent <= sistema.stake_max_percent
    
    # Se stake foi calculado, deve respeitar o mínimo ou ser zero
    if ranqueadas[0].stake_percent > 0:
        assert ranqueadas[0].stake_percent >= sistema.stake_min_percent


def test_componentes_normalizados():
    """Testa que os componentes normalizados são salvos corretamente"""
    sistema = criar_sistema_ranking(perfil="moderado")
    
    apostas = [
        ApostaInput(
            id="1",
            partida="Jogo 1",
            mercado="Resultado",
            selecao="Casa",
            odds=2.0,
            p_model=0.55,
            ev_percent=10.0,
            edge=5.0
        )
    ]
    
    ranqueadas = sistema.ranquear_apostas(apostas)
    aposta = ranqueadas[0]
    
    # Verificar que componentes normalizados existem
    assert hasattr(aposta, 'ev_norm')
    assert hasattr(aposta, 'edge_norm')
    assert hasattr(aposta, 'p_model_norm')
    assert hasattr(aposta, 'stake_norm')
    
    # Verificar que estão no range 0-100
    assert 0 <= aposta.ev_norm <= 100
    assert 0 <= aposta.edge_norm <= 100
    assert 0 <= aposta.p_model_norm <= 100
    assert 0 <= aposta.stake_norm <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

