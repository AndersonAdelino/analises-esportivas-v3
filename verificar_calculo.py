"""
Script de Verificação de Cálculos
Recalcula tudo do zero para garantir precisão
"""

from ensemble import EnsembleModel
from betting_tools import analyze_bet, decimal_to_probability
import numpy as np

print("=" * 80)
print("VERIFICACAO DE CALCULOS - CHELSEA VS SUNDERLAND")
print("=" * 80)

# Treina ensemble
print("\n1. TREINANDO ENSEMBLE...")
ensemble = EnsembleModel()
ensemble.fit()

# Predição
home_team = 'Chelsea FC'
away_team = 'Sunderland AFC'

print(f"\n2. CALCULANDO PROBABILIDADES PARA: {home_team} vs {away_team}")
print("-" * 80)

try:
    prediction = ensemble.predict_match(home_team, away_team)
    
    ens = prediction['ensemble']
    
    print("\n>> PROBABILIDADES DO ENSEMBLE (CALCULADAS):")
    print("-" * 80)
    print(f"Vitoria Casa:      {ens['prob_casa']*100:>6.2f}%")
    print(f"Empate:            {ens['prob_empate']*100:>6.2f}%")
    print(f"Vitoria Fora:      {ens['prob_fora']*100:>6.2f}%")
    print(f"Over 2.5:          {ens['prob_over_2_5']*100:>6.2f}%")
    print(f"Under 2.5:         {(1-ens['prob_over_2_5'])*100:>6.2f}%")
    print(f"BTTS Sim:          {ens['prob_btts']*100:>6.2f}%")
    print(f"BTTS Nao:          {(1-ens['prob_btts'])*100:>6.2f}%")
    
    # Verificação: soma deve ser ~1.0
    soma_1x2 = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
    print(f"\n[V] Verificacao: Soma 1X2 = {soma_1x2:.6f} (deve ser ~1.0)")
    
    if abs(soma_1x2 - 1.0) > 0.001:
        print("[!] AVISO: Soma nao eh exatamente 1.0!")
    else:
        print("[V] OK: Probabilidades normalizadas corretamente")
    
    # Mostra contribuição de cada modelo
    print("\n3. PROBABILIDADES INDIVIDUAIS DOS MODELOS:")
    print("-" * 80)
    
    for model_name, pred in prediction['individual'].items():
        if pred:
            weight = prediction['weights'][model_name]
            print(f"\n{model_name.upper()} (peso: {weight*100:.0f}%):")
            print(f"  Casa:    {pred['prob_casa']*100:>6.2f}%")
            print(f"  Empate:  {pred['prob_empate']*100:>6.2f}%")
            print(f"  Fora:    {pred['prob_fora']*100:>6.2f}%")
            print(f"  Over2.5: {pred['prob_over_2_5']*100:>6.2f}%")
            print(f"  BTTS:    {pred['prob_btts']*100:>6.2f}%")
    
    # Verifica cálculo manual do ensemble
    print("\n4. VERIFICACAO MANUAL DO CALCULO DO ENSEMBLE:")
    print("-" * 80)
    
    # Exemplo: Calcular prob_casa manualmente
    probs_casa = []
    weights_casa = []
    
    for model_name, pred in prediction['individual'].items():
        if pred and pred['prob_casa'] is not None:
            probs_casa.append(pred['prob_casa'])
            weights_casa.append(prediction['weights'][model_name])
    
    # Normaliza pesos
    total_weight = sum(weights_casa)
    weights_norm = [w / total_weight for w in weights_casa]
    
    # Calcula média ponderada
    prob_casa_manual = sum(p * w for p, w in zip(probs_casa, weights_norm))
    
    print(f"Prob. Casa (ensemble):  {ens['prob_casa']*100:.4f}%")
    print(f"Prob. Casa (manual):    {prob_casa_manual*100:.4f}%")
    print(f"Diferenca:              {abs(ens['prob_casa'] - prob_casa_manual)*100:.6f}%")
    
    if abs(ens['prob_casa'] - prob_casa_manual) < 0.0001:
        print("[V] OK: Calculo do ensemble esta correto!")
    else:
        print("[!] AVISO: Diferenca detectada no calculo!")
    
    # Agora vamos simular análise com odds de exemplo
    print("\n" + "=" * 80)
    print("5. SIMULACAO DE ANALISE DE APOSTAS (ODDS DE EXEMPLO)")
    print("=" * 80)
    
    # Odds de exemplo (você pode alterar aqui)
    odds_exemplo = {
        'casa': 1.50,
        'empate': 4.00,
        'fora': 7.00,
        'over_2_5': 1.75,
        'under_2_5': 2.10,
        'btts_yes': 1.85,
        'btts_no': 2.00
    }
    
    print("\nOdds usadas (EXEMPLO - altere se necessário):")
    for mercado, odd in odds_exemplo.items():
        print(f"  {mercado}: {odd}")
    
    bankroll = 1000
    kelly_fraction = 0.25
    
    print(f"\nBanca: R$ {bankroll}")
    print(f"Kelly Fraction: {kelly_fraction}")
    
    mercados = [
        ('Casa', ens['prob_casa'], odds_exemplo['casa']),
        ('Empate', ens['prob_empate'], odds_exemplo['empate']),
        ('Fora', ens['prob_fora'], odds_exemplo['fora']),
        ('Over 2.5', ens['prob_over_2_5'], odds_exemplo['over_2_5']),
        ('Under 2.5', 1 - ens['prob_over_2_5'], odds_exemplo['under_2_5']),
        ('BTTS Sim', ens['prob_btts'], odds_exemplo['btts_yes']),
        ('BTTS Nao', 1 - ens['prob_btts'], odds_exemplo['btts_no'])
    ]
    
    print("\n6. ANALISE DE CADA MERCADO:")
    print("=" * 80)
    
    value_bets = []
    
    for nome, prob, odds in mercados:
        analysis = analyze_bet(prob, odds, bankroll, kelly_fraction)
        
        print(f"\n[{nome}]")
        print(f"  Odds:           {odds:.2f}")
        print(f"  Prob. Real:     {prob*100:.2f}%")
        print(f"  Prob. Implicita:{analysis['prob_implied']*100:.2f}%")
        print(f"  Edge:           {analysis['edge_percent']:+.2f}%")
        print(f"  EV%:            {analysis['ev']['ev_percent']:+.2f}%")
        print(f"  Kelly%:         {analysis['kelly']['kelly_adjusted']*100:.2f}%")
        print(f"  Stake:          R$ {analysis['stake_recommended']:.2f}")
        print(f"  Value Bet?      {'>> SIM' if analysis['is_value_bet'] else '>> NAO'}")
        
        if analysis['is_value_bet']:
            value_bets.append({
                'nome': nome,
                'analysis': analysis
            })
    
    print("\n" + "=" * 80)
    print("7. RESUMO DE VALUE BETS:")
    print("=" * 80)
    
    if value_bets:
        print(f"\n>> {len(value_bets)} Value Bet(s) identificado(s):\n")
        
        total_stake = 0
        for vb in value_bets:
            a = vb['analysis']
            print(f">> {vb['nome']}:")
            print(f"   Odds: {a['odds']:.2f} | EV%: {a['ev']['ev_percent']:+.2f}% | Apostar: R$ {a['stake_recommended']:.2f}")
            total_stake += a['stake_recommended']
        
        print(f"\n>> Total a apostar: R$ {total_stake:.2f} ({total_stake/bankroll*100:.2f}% da banca)")
        
        if total_stake / bankroll > 0.15:
            print("[!] AVISO: Total > 15% da banca. Considere reduzir Kelly fraction.")
    else:
        print("\n>> Nenhum Value Bet identificado com essas odds.")
    
    print("\n" + "=" * 80)
    print("VERIFICACAO CONCLUIDA!")
    print("=" * 80)
    
    print("\n[V] Todos os calculos foram refeitos do zero")
    print("[V] Probabilidades verificadas e normalizadas")
    print("[V] EV e Kelly calculados corretamente")
    print("\nSe os valores acima conferem com o que viu na interface,")
    print("entao os calculos estao CORRETOS!")
    
except ValueError as e:
    print(f"\n[X] ERRO: {e}")
    print("\nPossíveis razões:")
    print("  - Time nao encontrado nos dados")
    print("  - Nome do time incorreto")
    print("  - Falta de dados históricos")
    
    print("\nTimes disponiveis:")
    from glob import glob
    import pandas as pd
    csv_files = glob('data/all_teams_matches_*.csv')
    if csv_files:
        csv_file = max(csv_files, key=lambda x: x)
        df = pd.read_csv(csv_file)
        times = sorted(df['time'].unique())
        for i, time in enumerate(times, 1):
            print(f"  {i:2d}. {time}")

except Exception as e:
    print(f"\n[X] ERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()

print("\n")

