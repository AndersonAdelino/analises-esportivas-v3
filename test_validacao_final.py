"""
TESTE DE VALIDACAO FINAL
SEM EMOJIS - Compativel com Windows
Testa Brasileirao + Premier League com nomes corretos
"""

import sys
from ensemble import EnsembleModel

def validar_probabilidades(pred, contexto):
    """Valida todas as probabilidades de uma predicao"""
    erros = []
    ens = pred['ensemble']
    
    for key, val in ens.items():
        if val is not None:
            if val < 0:
                erros.append(f"{contexto} - {key}: {val*100:.2f}% (NEGATIVO!)")
            if val > 1.0:
                erros.append(f"{contexto} - {key}: {val*100:.2f}% (>100%!)")
    
    # Verifica soma 1X2
    if all(ens.get(k) is not None for k in ['prob_casa', 'prob_empate', 'prob_fora']):
        total = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
        if abs(total - 1.0) > 0.01:
            erros.append(f"{contexto} - Soma 1X2: {total:.4f} (deveria ser ~1.0)")
    
    return erros

print("="*80)
print("TESTE DE VALIDACAO FINAL")
print("="*80)

total_testes = 0
total_erros = []

# ============================================================================
# BRASILEIRAO
# ============================================================================
print("\n[1] BRASILEIRAO SERIE A")
print("-"*80)

try:
    ensemble_bsa = EnsembleModel()
    ensemble_bsa.fit(league_code='BSA')
    print("OK - Ensemble treinado")
    
    jogos_bsa = [
        # Nomes corretos conforme CSV
        ('Botafogo FR', 'Santos FC'),
        ('CR Flamengo', 'SE Palmeiras'),
        ('SC Corinthians Paulista', 'São Paulo FC'),
        ('Grêmio FBPA', 'SC Internacional'),
        ('Fluminense FC', 'CR Vasco da Gama'),
        ('EC Bahia', 'Fortaleza EC'),
    ]
    
    print(f"\nTestando {len(jogos_bsa)} partidas:\n")
    
    for i, (home, away) in enumerate(jogos_bsa, 1):
        try:
            pred = ensemble_bsa.predict_match(home, away)
            ens = pred['ensemble']
            
            print(f"[{i}] {home} vs {away}")
            print(f"    Casa: {ens['prob_casa']*100:6.2f}% | Empate: {ens['prob_empate']*100:6.2f}% | Fora: {ens['prob_fora']*100:6.2f}%")
            
            erros = validar_probabilidades(pred, f"Brasileirao - {home} vs {away}")
            total_erros.extend(erros)
            total_testes += 1
            
        except Exception as e:
            print(f"    ERRO: {e}")
            total_erros.append(f"Brasileirao - {home} vs {away}: {str(e)}")
    
    print(f"\nOK - {total_testes} partidas testadas no Brasileirao")
        
except Exception as e:
    print(f"ERRO ao testar Brasileirao: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# PREMIER LEAGUE
# ============================================================================
print("\n[2] PREMIER LEAGUE")
print("-"*80)

try:
    ensemble_pl = EnsembleModel()
    ensemble_pl.fit(league_code='PL')
    print("OK - Ensemble treinado")
    
    jogos_pl = [
        ('Arsenal FC', 'Liverpool FC'),
        ('Manchester City FC', 'Chelsea FC'),
        ('Manchester United FC', 'Tottenham Hotspur FC'),
        ('Newcastle United FC', 'Aston Villa FC'),
        ('West Ham United FC', 'Everton FC'),
        ('Brighton & Hove Albion FC', 'Fulham FC'),
    ]
    
    print(f"\nTestando {len(jogos_pl)} partidas:\n")
    
    for i, (home, away) in enumerate(jogos_pl, 1):
        try:
            pred = ensemble_pl.predict_match(home, away)
            ens = pred['ensemble']
            
            print(f"[{i}] {home} vs {away}")
            print(f"    Casa: {ens['prob_casa']*100:6.2f}% | Empate: {ens['prob_empate']*100:6.2f}% | Fora: {ens['prob_fora']*100:6.2f}%")
            
            erros = validar_probabilidades(pred, f"Premier League - {home} vs {away}")
            total_erros.extend(erros)
            total_testes += 1
            
        except Exception as e:
            print(f"    ERRO: {e}")
            total_erros.append(f"Premier League - {home} vs {away}: {str(e)}")
    
    print(f"\nOK - {total_testes - len(jogos_bsa)} partidas testadas na Premier League")
        
except Exception as e:
    print(f"ERRO ao testar Premier League: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# RELATORIO FINAL
# ============================================================================
print("\n" + "="*80)
print("RELATORIO FINAL")
print("="*80)

print(f"\nTotal de partidas testadas: {total_testes}")
print(f"  - Brasileirao: {len(jogos_bsa)}")
print(f"  - Premier League: {len(jogos_pl)}")

if total_erros:
    print(f"\nERROS ENCONTRADOS: {len(total_erros)}")
    print("-"*80)
    for erro in total_erros:
        print(f"  {erro}")
    print("\n" + "="*80)
    print("RESULTADO: FALHOU")
    print("="*80)
    print("\nForam detectados problemas que precisam ser corrigidos.")
    sys.exit(1)
else:
    print(f"\nERROS ENCONTRADOS: 0")
    print("\n" + "="*80)
    print("RESULTADO: SUCESSO!")
    print("="*80)
    print("\nTodas as {0} partidas foram testadas com sucesso!".format(total_testes))
    print("\nVERIFICADO:")
    print("  [OK] Nenhuma probabilidade negativa")
    print("  [OK] Nenhuma probabilidade > 100%")
    print("  [OK] Probabilidades 1X2 somam ~1.0")
    print("  [OK] Brasileirao funciona corretamente")
    print("  [OK] Premier League funciona corretamente")
    print("\n*** SISTEMA VALIDADO E PRONTO PARA PRODUCAO ***")

