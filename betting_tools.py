"""
Ferramentas para Análise de Apostas

- Expected Value (EV)
- Kelly Criterion
- Análise de Value Bets
"""

import numpy as np


def decimal_to_probability(odds):
    """
    Converte odds decimais para probabilidade implícita
    
    Args:
        odds: Odds decimal (ex: 2.50)
        
    Returns:
        Probabilidade implícita (0-1)
    """
    if odds <= 1.0:
        return 1.0
    return 1.0 / odds


def probability_to_decimal(prob):
    """
    Converte probabilidade para odds decimal
    
    Args:
        prob: Probabilidade (0-1)
        
    Returns:
        Odds decimal
    """
    if prob <= 0:
        return 999.99
    if prob >= 1:
        return 1.01
    return 1.0 / prob


def calculate_ev(prob_win, odds_decimal, stake=1.0):
    """
    Calcula Expected Value (Valor Esperado)
    
    EV = (Probabilidade de Ganhar × Retorno) - (Probabilidade de Perder × Stake)
    
    Args:
        prob_win: Probabilidade real de ganhar (0-1)
        odds_decimal: Odds da casa de apostas (decimal)
        stake: Valor apostado (padrão: 1)
        
    Returns:
        Dict com EV absoluto, EV%, ROI%
    """
    prob_lose = 1 - prob_win
    profit_if_win = (odds_decimal - 1) * stake
    loss_if_lose = stake
    
    ev_absolute = (prob_win * profit_if_win) - (prob_lose * loss_if_lose)
    ev_percent = (ev_absolute / stake) * 100
    roi_percent = ev_percent  # ROI = EV%
    
    return {
        'ev_absolute': ev_absolute,
        'ev_percent': ev_percent,
        'roi_percent': roi_percent,
        'is_value_bet': ev_absolute > 0
    }


def kelly_criterion(prob_win, odds_decimal, kelly_fraction=1.0):
    """
    Calcula a fração da banca a apostar usando Kelly Criterion
    
    Kelly% = (prob_win × odds - 1) / (odds - 1)
    
    Args:
        prob_win: Probabilidade real de ganhar (0-1)
        odds_decimal: Odds da casa de apostas
        kelly_fraction: Fração de Kelly (0-1, recomendado: 0.25 a 0.5)
        
    Returns:
        Dict com kelly_percent, kelly_adjusted, recomendação
    """
    if odds_decimal <= 1.0:
        return {
            'kelly_percent': 0.0,
            'kelly_adjusted': 0.0,
            'recommendation': 'NAO_APOSTAR',
            'reason': 'Odds inválidas'
        }
    
    # Fórmula de Kelly
    kelly_percent = ((prob_win * odds_decimal) - 1) / (odds_decimal - 1)
    
    # Limita entre 0 e 100%
    kelly_percent = max(0.0, min(kelly_percent, 1.0))
    
    # Aplica fração (conservative Kelly)
    kelly_adjusted = kelly_percent * kelly_fraction
    
    # Recomendação
    if kelly_adjusted <= 0:
        recommendation = 'NAO_APOSTAR'
        reason = 'EV negativo'
    elif kelly_adjusted < 0.01:
        recommendation = 'NAO_APOSTAR'
        reason = 'Value muito baixo (< 1%)'
    elif kelly_adjusted < 0.02:
        recommendation = 'APOSTAR_MINIMO'
        reason = f'Value baixo ({kelly_adjusted*100:.1f}%)'
    elif kelly_adjusted < 0.05:
        recommendation = 'APOSTAR_MODERADO'
        reason = f'Value moderado ({kelly_adjusted*100:.1f}%)'
    else:
        recommendation = 'APOSTAR_ALTO'
        reason = f'Value alto ({kelly_adjusted*100:.1f}%)'
    
    return {
        'kelly_percent': kelly_percent,
        'kelly_adjusted': kelly_adjusted,
        'kelly_fraction_used': kelly_fraction,
        'recommendation': recommendation,
        'reason': reason
    }


def calculate_stake(bankroll, kelly_percent):
    """
    Calcula quanto apostar baseado na banca e Kelly%
    
    Args:
        bankroll: Valor total da banca
        kelly_percent: Percentual de Kelly (0-1)
        
    Returns:
        Valor a apostar
    """
    return bankroll * kelly_percent


def analyze_bet(prob_win, odds_decimal, bankroll=100, kelly_fraction=0.25, max_stake_percent=0.05):
    """
    Análise completa de uma aposta
    
    Args:
        prob_win: Probabilidade real de ganhar (0-1)
        odds_decimal: Odds da casa
        bankroll: Banca total
        kelly_fraction: Fração de Kelly (recomendado: 0.25)
        max_stake_percent: Percentual máximo da banca por aposta (padrão: 5% - REDUZIDO!)
        
    Returns:
        Dict com análise completa
    """
    # Probabilidade implícita da casa
    prob_implied = decimal_to_probability(odds_decimal)
    
    # Margem da casa
    edge = prob_win - prob_implied
    edge_percent = edge * 100
    
    # EV
    ev = calculate_ev(prob_win, odds_decimal, stake=1.0)
    
    # Kelly
    kelly = kelly_criterion(prob_win, odds_decimal, kelly_fraction)
    
    # Valor a apostar (Kelly)
    stake_kelly = calculate_stake(bankroll, kelly['kelly_adjusted'])
    
    # Aplica limite máximo de 5% (REDUZIDO de 12% para maior segurança)
    stake_max = bankroll * max_stake_percent
    stake = min(stake_kelly, stake_max)
    
    # Flag se foi limitado
    stake_limited = stake < stake_kelly
    
    # Retorno esperado
    potential_profit = stake * (odds_decimal - 1)
    expected_return = stake * (1 + ev['ev_percent'] / 100)
    
    return {
        'odds': odds_decimal,
        'prob_real': prob_win,
        'prob_implied': prob_implied,
        'edge': edge,
        'edge_percent': edge_percent,
        'ev': ev,
        'kelly': kelly,
        'bankroll': bankroll,
        'stake_recommended': stake,
        'stake_percent': (stake / bankroll) * 100,
        'stake_limited': stake_limited,
        'potential_profit': potential_profit,
        'expected_return': expected_return,
        'is_value_bet': ev['is_value_bet'] and kelly['kelly_adjusted'] > 0.01
    }


def find_best_bet(bets_analysis, min_prob=0.60):
    """
    Identifica a MELHOR aposta de uma lista
    
    Requisitos:
    - Probabilidade > min_prob (padrão: 60%)
    - Maior EV possível
    
    Args:
        bets_analysis: Lista de dicts com análises de apostas
        min_prob: Probabilidade mínima (0-1)
        
    Returns:
        Dict da melhor aposta ou None se nenhuma qualificar
    """
    # Filtra apostas que atendem critério mínimo
    qualified_bets = [
        bet for bet in bets_analysis
        if bet.get('prob_real', 0) > min_prob and bet.get('is_value_bet', False)
    ]
    
    if not qualified_bets:
        return None
    
    # Encontra a com maior EV
    best_bet = max(qualified_bets, key=lambda x: x['ev']['ev_percent'])
    
    return best_bet


def compare_odds(prob_win, odds_list):
    """
    Compara múltiplas odds para encontrar melhor value
    
    Args:
        prob_win: Probabilidade real de ganhar
        odds_list: Lista de tuples (casa, odds_decimal)
        
    Returns:
        Lista ordenada por EV
    """
    results = []
    
    for casa, odds in odds_list:
        ev = calculate_ev(prob_win, odds)
        kelly = kelly_criterion(prob_win, odds, kelly_fraction=0.25)
        
        results.append({
            'casa': casa,
            'odds': odds,
            'ev_percent': ev['ev_percent'],
            'kelly_percent': kelly['kelly_adjusted'] * 100,
            'is_value': ev['is_value_bet']
        })
    
    # Ordena por EV (maior primeiro)
    results.sort(key=lambda x: x['ev_percent'], reverse=True)
    
    return results


def print_bet_analysis(analysis, bet_name="Aposta"):
    """
    Imprime análise de aposta de forma formatada
    
    Args:
        analysis: Dict retornado por analyze_bet()
        bet_name: Nome da aposta (ex: "Vitória Casa")
    """
    print(f"\n{'='*80}")
    print(f"ANALISE: {bet_name}")
    print(f"{'='*80}")
    
    print(f"\nODDS E PROBABILIDADES:")
    print(f"  Odds da casa:           {analysis['odds']:.2f}")
    print(f"  Prob. real (modelo):    {analysis['prob_real']*100:.2f}%")
    print(f"  Prob. implicita (casa): {analysis['prob_implied']*100:.2f}%")
    print(f"  Edge (vantagem):        {analysis['edge_percent']:+.2f}%")
    
    ev = analysis['ev']
    print(f"\nEXPECTED VALUE (EV):")
    print(f"  EV absoluto:            R$ {ev['ev_absolute']:+.2f} (por R$ 1)")
    print(f"  EV%:                    {ev['ev_percent']:+.2f}%")
    print(f"  ROI esperado:           {ev['roi_percent']:+.2f}%")
    print(f"  É value bet?            {'SIM' if ev['is_value_bet'] else 'NAO'}")
    
    kelly = analysis['kelly']
    print(f"\nKELLY CRITERION:")
    print(f"  Kelly full:             {kelly['kelly_percent']*100:.2f}%")
    print(f"  Kelly ajustado:         {kelly['kelly_adjusted']*100:.2f}% (fração: {kelly['kelly_fraction_used']})")
    print(f"  Recomendacao:           {kelly['recommendation']}")
    print(f"  Razao:                  {kelly['reason']}")
    
    print(f"\nRECOMENDACAO DE STAKE:")
    print(f"  Banca total:            R$ {analysis['bankroll']:.2f}")
    print(f"  Valor a apostar:        R$ {analysis['stake_recommended']:.2f} ({analysis['stake_percent']:.2f}%)")
    print(f"  Lucro potencial:        R$ {analysis['potential_profit']:.2f}")
    print(f"  Retorno esperado:       R$ {analysis['expected_return']:.2f}")
    
    print(f"\nVEREDICTO FINAL:")
    if analysis['is_value_bet']:
        print(f"  >> APOSTAR - Value bet identificado!")
        print(f"  Aposte R$ {analysis['stake_recommended']:.2f} ({analysis['stake_percent']:.1f}% da banca)")
    else:
        print(f"  >> NAO APOSTAR - Sem value")
    
    print(f"{'='*80}\n")


def is_high_quality_bet(analysis, min_ev=5.0, min_prob=0.40, min_kelly=0.02, min_edge=3.0):
    """
    Verifica se uma aposta atende critérios de QUALIDADE RIGOROSOS
    
    Esta função implementa filtros mais rigorosos para reduzir perdas.
    Apenas apostas que atendem TODOS os critérios são aprovadas.
    
    Args:
        analysis: Resultado de analyze_bet()
        min_ev: EV% mínimo (padrão: 5%)
        min_prob: Probabilidade mínima (padrão: 40%)
        min_kelly: Kelly ajustado mínimo (padrão: 2%)
        min_edge: Edge% mínimo (padrão: 3%)
    
    Returns:
        bool: True se atende todos os critérios
    """
    return (
        analysis['ev']['ev_percent'] >= min_ev and
        analysis['prob_real'] >= min_prob and
        analysis['kelly']['kelly_adjusted'] >= min_kelly and
        analysis['edge_percent'] >= min_edge and
        analysis['is_value_bet']
    )


def calculate_bet_quality_score(analysis, consensus_level=None):
    """
    Calcula score de qualidade (0-100) baseado em múltiplos fatores
    
    Score considera:
    - EV% (peso: 30%)
    - Edge% (peso: 25%)
    - Probabilidade (peso: 20%)
    - Kelly% (peso: 15%)
    - Consenso entre modelos (peso: 10%) - se disponível
    
    Classificação:
    - 85-100: Excelente (aposte com confiança)
    - 70-84:  Boa (aposte)
    - 55-69:  Aceitável (considere)
    - < 55:   Fraca (evite)
    
    Args:
        analysis: Dict retornado por analyze_bet()
        consensus_level: Nível de consenso entre modelos (0-100)
    
    Returns:
        float: Score 0-100
    """
    score = 0.0
    
    # 1. EV% (0-30 pontos)
    ev_pct = analysis['ev']['ev_percent']
    if ev_pct >= 15:
        score += 30
    elif ev_pct >= 12:
        score += 27
    elif ev_pct >= 10:
        score += 25
    elif ev_pct >= 8:
        score += 22
    elif ev_pct >= 7:
        score += 20
    elif ev_pct >= 5:
        score += 15
    elif ev_pct >= 3:
        score += 10
    elif ev_pct > 0:
        score += 5
    
    # 2. Edge% (0-25 pontos)
    edge_pct = analysis['edge_percent']
    if edge_pct >= 10:
        score += 25
    elif edge_pct >= 8:
        score += 22
    elif edge_pct >= 7:
        score += 20
    elif edge_pct >= 5:
        score += 15
    elif edge_pct >= 3:
        score += 10
    elif edge_pct > 0:
        score += 5
    
    # 3. Probabilidade (0-20 pontos)
    prob = analysis['prob_real']
    if prob >= 0.70:
        score += 20
    elif prob >= 0.65:
        score += 19
    elif prob >= 0.60:
        score += 18
    elif prob >= 0.55:
        score += 16
    elif prob >= 0.50:
        score += 15
    elif prob >= 0.45:
        score += 12
    elif prob >= 0.40:
        score += 8
    elif prob >= 0.35:
        score += 4
    
    # 4. Kelly% (0-15 pontos)
    kelly_adj = analysis['kelly']['kelly_adjusted']
    if kelly_adj >= 0.08:
        score += 15
    elif kelly_adj >= 0.06:
        score += 13
    elif kelly_adj >= 0.05:
        score += 12
    elif kelly_adj >= 0.04:
        score += 10
    elif kelly_adj >= 0.03:
        score += 9
    elif kelly_adj >= 0.02:
        score += 6
    elif kelly_adj > 0:
        score += 3
    
    # 5. Consenso entre modelos (0-10 pontos) - NOVO CRITÉRIO
    if consensus_level is not None:
        if consensus_level >= 85:
            score += 10
        elif consensus_level >= 80:
            score += 9
        elif consensus_level >= 75:
            score += 8
        elif consensus_level >= 70:
            score += 7
        elif consensus_level >= 65:
            score += 6
        elif consensus_level >= 60:
            score += 4
        elif consensus_level >= 50:
            score += 2
        else:
            score += 0  # Penaliza baixo consenso
    
    return round(score, 1)


def get_bet_warnings(analysis, consensus_level=None, divergence_kl=None):
    """
    Gera lista de avisos baseados em métricas de risco
    
    Args:
        analysis: Dict retornado por analyze_bet()
        consensus_level: Nível de consenso entre modelos (0-100)
        divergence_kl: Divergência KL entre modelos
    
    Returns:
        list: Lista de avisos (strings)
    """
    warnings = []
    
    # Aviso 1: Probabilidade baixa
    if analysis['prob_real'] < 0.40:
        warnings.append('⚠️ Probabilidade < 40% - RISCO MUITO ALTO!')
    elif analysis['prob_real'] < 0.45:
        warnings.append('⚠️ Probabilidade < 45% - Risco alto')
    
    # Aviso 2: EV muito baixo
    if 0 < analysis['ev']['ev_percent'] < 3:
        warnings.append('⚠️ EV% < 3% - Value MUITO marginal')
    elif 0 < analysis['ev']['ev_percent'] < 5:
        warnings.append('⚠️ EV% < 5% - Value marginal')
    
    # Aviso 3: Edge pequeno
    if 0 < analysis['edge_percent'] < 2:
        warnings.append('⚠️ Edge < 2% - Vantagem MÍNIMA')
    elif 0 < analysis['edge_percent'] < 3:
        warnings.append('⚠️ Edge < 3% - Vantagem pequena')
    
    # Aviso 4: Baixo consenso entre modelos
    if consensus_level is not None:
        if consensus_level < 60:
            warnings.append('⚠️ BAIXO CONSENSO (<60%) - Modelos DIVERGEM!')
        elif consensus_level < 70:
            warnings.append('⚠️ Consenso moderado (<70%) - Alguma incerteza')
    
    # Aviso 5: Alta divergência KL
    if divergence_kl is not None:
        if divergence_kl > 0.30:
            warnings.append('⚠️ ALTA DIVERGÊNCIA - Modelos discordam significativamente!')
        elif divergence_kl > 0.20:
            warnings.append('⚠️ Divergência moderada entre modelos')
    
    # Aviso 6: Stake alto
    if analysis['stake_percent'] > 4:
        warnings.append('⚠️ Stake > 4% da banca - Considere REDUZIR!')
    elif analysis['stake_percent'] > 3:
        warnings.append('⚠️ Stake > 3% da banca - Risco elevado')
    
    # Aviso 7: Kelly muito baixo
    if 0 < analysis['kelly']['kelly_adjusted'] < 0.015:
        warnings.append('⚠️ Kelly < 1.5% - Value questionável')
    
    return warnings


def get_quality_level(score):
    """
    Retorna nível de qualidade baseado no score
    
    Args:
        score: Score 0-100
    
    Returns:
        tuple: (nivel, emoji, cor, recomendacao)
    """
    if score >= 85:
        return ('Excelente', '🟢', 'green', 'APOSTE COM CONFIANÇA!')
    elif score >= 70:
        return ('Boa', '🟡', 'yellow', 'APOSTE')
    elif score >= 55:
        return ('Aceitável', '🟠', 'orange', 'CONSIDERE (com cautela)')
    else:
        return ('Fraca', '🔴', 'red', 'EVITE')


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("FERRAMENTAS DE ANALISE DE APOSTAS")
    print("=" * 80)
    print("\n")
    
    # Exemplo 1: Value bet
    print("EXEMPLO 1: Value Bet Claro")
    print("-" * 80)
    prob_win = 0.60  # Modelo diz 60% de chance
    odds = 2.00      # Casa paga 2.00 (implica 50%)
    bankroll = 1000
    
    analysis = analyze_bet(prob_win, odds, bankroll, kelly_fraction=0.25)
    print_bet_analysis(analysis, "Vitoria Time A @ 2.00")
    
    # Testa novo sistema de qualidade
    score = calculate_bet_quality_score(analysis, consensus_level=80)
    quality, emoji, _, recom = get_quality_level(score)
    warnings = get_bet_warnings(analysis, consensus_level=80)
    
    print(f"\nSCORE DE QUALIDADE: {score}/100 ({quality})")
    print(f"RECOMENDACAO: {recom}")
    if warnings:
        print("\nAVISOS:")
        for w in warnings:
            # Remove emojis para compatibilidade com Windows console
            print(f"  {w}".encode('ascii', errors='ignore').decode('ascii'))
    
    # Exemplo 2: Não é value
    print("\n\nEXEMPLO 2: Nao eh Value Bet")
    print("-" * 80)
    prob_win = 0.40  # Modelo diz 40%
    odds = 2.00      # Casa paga 2.00 (implica 50%)
    
    analysis = analyze_bet(prob_win, odds, bankroll, kelly_fraction=0.25)
    print_bet_analysis(analysis, "Vitoria Time B @ 2.00")
    
    # Exemplo 3: Value bet marginal (baixa qualidade)
    print("\n\nEXEMPLO 3: Value Bet Marginal (Baixa Qualidade)")
    print("-" * 80)
    prob_win = 0.36  # Modelo diz 36%
    odds = 2.90      # Casa paga 2.90 (implica 34.5%)
    
    analysis = analyze_bet(prob_win, odds, bankroll, kelly_fraction=0.25)
    print_bet_analysis(analysis, "Vitoria Time C @ 2.90")
    
    score = calculate_bet_quality_score(analysis, consensus_level=55)
    quality, emoji, _, recom = get_quality_level(score)
    warnings = get_bet_warnings(analysis, consensus_level=55, divergence_kl=0.28)
    is_quality = is_high_quality_bet(analysis)
    
    print(f"\nSCORE DE QUALIDADE: {score}/100 ({quality})")
    print(f"RECOMENDACAO: {recom}")
    print(f"ATENDE CRITERIOS DE QUALIDADE: {'SIM' if is_quality else 'NAO'}")
    if warnings:
        print("\nAVISOS:")
        for w in warnings:
            # Remove emojis para compatibilidade com Windows console
            print(f"  {w}".encode('ascii', errors='ignore').decode('ascii'))
    
    print("\n" + "=" * 80)
    print("EXEMPLOS CONCLUIDOS")
    print("=" * 80)
    print("\nUso programatico:")
    print("  from betting_tools import analyze_bet, calculate_bet_quality_score")
    print("  analysis = analyze_bet(prob_win=0.65, odds_decimal=2.20, bankroll=1000)")
    print("  score = calculate_bet_quality_score(analysis, consensus_level=75)")
    print("  print(f'Score: {score}/100')")
    print()

