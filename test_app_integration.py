"""
Teste de integração com o app Streamlit
Verifica se as correções funcionam no contexto do app
"""

print("="*80)
print("TESTE DE INTEGRACAO COM APP")
print("="*80)

try:
    # Simula o fluxo do app_betting.py
    from ensemble import EnsembleModel
    from betting_tools import analyze_bet
    
    print("\n[1] Carregando Ensemble (Brasileirao)...")
    ensemble = EnsembleModel()
    ensemble.fit(league_code='BSA')
    
    print("\n[2] Testando predicao...")
    home_team = 'Botafogo FR'
    away_team = 'Santos FC'
    
    prediction = ensemble.predict_match(home_team, away_team)
    ens = prediction['ensemble']
    
    print(f"\nProbabilidades do Ensemble:")
    print(f"  Casa:    {ens['prob_casa']*100:.2f}%")
    print(f"  Empate:  {ens['prob_empate']*100:.2f}%")
    print(f"  Fora:    {ens['prob_fora']*100:.2f}%")
    
    print("\n[3] Testando analise de apostas...")
    # Odds exemplo
    odds = {
        'casa': 2.00,
        'empate': 3.50,
        'fora': 3.80
    }
    
    bankroll = 1000.0
    kelly_fraction = 0.25
    
    # Analisa cada mercado
    markets = [
        ('Casa', ens['prob_casa'], odds['casa']),
        ('Empate', ens['prob_empate'], odds['empate']),
        ('Fora', ens['prob_fora'], odds['fora'])
    ]
    
    value_bets = []
    for market_name, prob, odd in markets:
        analysis = analyze_bet(prob, odd, bankroll, kelly_fraction)
        print(f"\n  {market_name}:")
        print(f"    Prob. Real: {analysis['prob_real']*100:.1f}%")
        print(f"    Prob. Casa: {analysis['prob_implied']*100:.1f}%")
        print(f"    Edge: {analysis['edge_percent']:+.1f}%")
        print(f"    EV%: {analysis['ev']['ev_percent']:+.2f}%")
        print(f"    Value Bet: {'SIM' if analysis['is_value_bet'] else 'NAO'}")
        
        if analysis['is_value_bet']:
            value_bets.append(market_name)
    
    print("\n" + "="*80)
    print("RESUMO:")
    print("="*80)
    print(f"\nValue Bets encontrados: {len(value_bets)}")
    if value_bets:
        print(f"Mercados: {', '.join(value_bets)}")
    else:
        print("Nenhum value bet identificado com estas odds")
    
    print("\n" + "="*80)
    print("TESTE DE INTEGRACAO: SUCESSO!")
    print("="*80)
    print("\nO app Streamlit deveria funcionar corretamente.")
    print("Para testar o app completo, execute:")
    print("  streamlit run app_betting.py")
    
except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()

