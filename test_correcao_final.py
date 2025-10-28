"""Teste final apos correcoes - SEM EMOJIS"""

print("="*80)
print("TESTE FINAL: BOTAFOGO X SANTOS")
print("="*80)

try:
    from ensemble import EnsembleModel
    
    print("\n[1] Treinando Ensemble para Brasileirao...")
    ensemble = EnsembleModel()
    ensemble.fit(league_code='BSA')
    
    print("\n[2] Fazendo predicao Botafogo FR vs Santos FC...")
    home_team = 'Botafogo FR'
    away_team = 'Santos FC'
    
    prediction = ensemble.predict_match(home_team, away_team)
    ens = prediction['ensemble']
    
    print("\n" + "="*80)
    print("RESULTADO:")
    print("="*80)
    print(f"\nENSEMBLE (Combinado):")
    print(f"  Casa:      {ens['prob_casa']*100:7.2f}%")
    print(f"  Empate:    {ens['prob_empate']*100:7.2f}%")
    print(f"  Fora:      {ens['prob_fora']*100:7.2f}%")
    print(f"  Over 2.5:  {ens['prob_over_2_5']*100:7.2f}%")
    print(f"  BTTS:      {ens['prob_btts']*100:7.2f}%")
    
    # Verificar problemas
    print("\n" + "="*80)
    print("DIAGNOSTICO:")
    print("="*80)
    
    problemas = []
    for key, value in ens.items():
        if value is not None:
            if value < 0:
                problemas.append(f"  ERRO: {key} = {value*100:.2f}% (NEGATIVO!)")
            elif value > 1:
                problemas.append(f"  AVISO: {key} = {value*100:.2f}% (>100%!)")
    
    if problemas:
        print("\nPROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(p)
    else:
        print("\nOK - Nenhum problema detectado!")
        print("Todas as probabilidades estao no intervalo [0, 100%]")
    
    # Mostrar predicoes individuais
    print("\n" + "="*80)
    print("PREDICOES INDIVIDUAIS:")
    print("="*80)
    
    for model_name, pred in prediction['individual'].items():
        print(f"\n{model_name.upper()}:")
        if pred:
            print(f"  Casa:    {pred.get('prob_casa', 0)*100:7.2f}%")
            print(f"  Empate:  {pred.get('prob_empate', 0)*100:7.2f}%")
            print(f"  Fora:    {pred.get('prob_fora', 0)*100:7.2f}%")
        else:
            print("  FALHOU")
    
    print("\n" + "="*80)
    print("TESTE CONCLUIDO COM SUCESSO!")
    print("="*80)
    
except Exception as e:
    print(f"\nERRO: {e}")
    import traceback
    traceback.print_exc()

