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


def analyze_bet(prob_win, odds_decimal, bankroll=100, kelly_fraction=0.25):
    """
    Análise completa de uma aposta
    
    Args:
        prob_win: Probabilidade real de ganhar (0-1)
        odds_decimal: Odds da casa
        bankroll: Banca total
        kelly_fraction: Fração de Kelly (recomendado: 0.25)
        
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
    
    # Valor a apostar
    stake = calculate_stake(bankroll, kelly['kelly_adjusted'])
    
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
        'potential_profit': potential_profit,
        'expected_return': expected_return,
        'is_value_bet': ev['is_value_bet'] and kelly['kelly_adjusted'] > 0.01
    }


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
    
    # Exemplo 2: Não é value
    print("\nEXEMPLO 2: Nao eh Value Bet")
    print("-" * 80)
    prob_win = 0.40  # Modelo diz 40%
    odds = 2.00      # Casa paga 2.00 (implica 50%)
    
    analysis = analyze_bet(prob_win, odds, bankroll, kelly_fraction=0.25)
    print_bet_analysis(analysis, "Vitoria Time B @ 2.00")
    
    print("\n" + "=" * 80)
    print("EXEMPLOS CONCLUIDOS")
    print("=" * 80)
    print("\nUso programatico:")
    print("  from betting_tools import analyze_bet")
    print("  analysis = analyze_bet(prob_win=0.65, odds_decimal=2.20, bankroll=1000)")
    print("  print_bet_analysis(analysis)")
    print()

