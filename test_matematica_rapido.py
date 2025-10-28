"""Teste matematico rapido e focado"""

import numpy as np
from ensemble import EnsembleModel

print("="*80)
print("TESTE MATEMATICO RAPIDO")
print("="*80)

erros = []
avisos = []
checks = 0

def validar(condicao, mensagem):
    """Valida uma condicao"""
    global checks, erros
    checks += 1
    if not condicao:
        erros.append(mensagem)
        return False
    return True

# Teste 1: Brasileirao
print("\n[1] Testando Brasileirao...")
try:
    ensemble_bsa = EnsembleModel()
    ensemble_bsa.fit(league_code='BSA')
    
    pred = ensemble_bsa.predict_match('Botafogo FR', 'Santos FC')
    ens = pred['ensemble']
    
    print(f"    Casa: {ens['prob_casa']*100:.2f}%")
    print(f"    Empate: {ens['prob_empate']*100:.2f}%")
    print(f"    Fora: {ens['prob_fora']*100:.2f}%")
    
    # VALIDACOES MATEMATICAS
    # 1. Sem NaN
    validar(not np.isnan(ens['prob_casa']), "BSA - Casa e NaN")
    validar(not np.isnan(ens['prob_empate']), "BSA - Empate e NaN")
    validar(not np.isnan(ens['prob_fora']), "BSA - Fora e NaN")
    
    # 2. Sem Inf
    validar(not np.isinf(ens['prob_casa']), "BSA - Casa e Inf")
    validar(not np.isinf(ens['prob_empate']), "BSA - Empate e Inf")
    validar(not np.isinf(ens['prob_fora']), "BSA - Fora e Inf")
    
    # 3. Intervalo [0, 1]
    validar(0 <= ens['prob_casa'] <= 1, f"BSA - Casa fora do intervalo: {ens['prob_casa']}")
    validar(0 <= ens['prob_empate'] <= 1, f"BSA - Empate fora do intervalo: {ens['prob_empate']}")
    validar(0 <= ens['prob_fora'] <= 1, f"BSA - Fora fora do intervalo: {ens['prob_fora']}")
    
    # 4. Soma = 1
    soma = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
    validar(abs(soma - 1.0) < 0.01, f"BSA - Soma 1X2: {soma:.6f} (deveria ser ~1.0)")
    
    # 5. Over/Under
    validar(0 <= ens['prob_over_2_5'] <= 1, f"BSA - Over 2.5 fora do intervalo: {ens['prob_over_2_5']}")
    
    # 6. BTTS
    validar(0 <= ens['prob_btts'] <= 1, f"BSA - BTTS fora do intervalo: {ens['prob_btts']}")
    
    # 7. Valida predicoes individuais
    for model_name, model_pred in pred['individual'].items():
        if model_pred:
            validar(not np.isnan(model_pred['prob_casa']), f"BSA/{model_name} - Casa e NaN")
            validar(not np.isnan(model_pred['prob_empate']), f"BSA/{model_name} - Empate e NaN")
            validar(not np.isnan(model_pred['prob_fora']), f"BSA/{model_name} - Fora e NaN")
            
            validar(0 <= model_pred['prob_casa'] <= 1, f"BSA/{model_name} - Casa: {model_pred['prob_casa']}")
            validar(0 <= model_pred['prob_empate'] <= 1, f"BSA/{model_name} - Empate: {model_pred['prob_empate']}")
            validar(0 <= model_pred['prob_fora'] <= 1, f"BSA/{model_name} - Fora: {model_pred['prob_fora']}")
            
            soma_ind = model_pred['prob_casa'] + model_pred['prob_empate'] + model_pred['prob_fora']
            validar(abs(soma_ind - 1.0) < 0.01, f"BSA/{model_name} - Soma: {soma_ind:.6f}")
    
    print("    OK - Brasileirao validado")
    
except Exception as e:
    print(f"    ERRO: {e}")
    erros.append(f"Brasileirao: {str(e)}")

# Teste 2: Premier League
print("\n[2] Testando Premier League...")
try:
    ensemble_pl = EnsembleModel()
    ensemble_pl.fit(league_code='PL')
    
    pred = ensemble_pl.predict_match('Arsenal FC', 'Liverpool FC')
    ens = pred['ensemble']
    
    print(f"    Casa: {ens['prob_casa']*100:.2f}%")
    print(f"    Empate: {ens['prob_empate']*100:.2f}%")
    print(f"    Fora: {ens['prob_fora']*100:.2f}%")
    
    # VALIDACOES MATEMATICAS
    validar(not np.isnan(ens['prob_casa']), "PL - Casa e NaN")
    validar(not np.isnan(ens['prob_empate']), "PL - Empate e NaN")
    validar(not np.isnan(ens['prob_fora']), "PL - Fora e NaN")
    
    validar(not np.isinf(ens['prob_casa']), "PL - Casa e Inf")
    validar(not np.isinf(ens['prob_empate']), "PL - Empate e Inf")
    validar(not np.isinf(ens['prob_fora']), "PL - Fora e Inf")
    
    validar(0 <= ens['prob_casa'] <= 1, f"PL - Casa: {ens['prob_casa']}")
    validar(0 <= ens['prob_empate'] <= 1, f"PL - Empate: {ens['prob_empate']}")
    validar(0 <= ens['prob_fora'] <= 1, f"PL - Fora: {ens['prob_fora']}")
    
    soma = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
    validar(abs(soma - 1.0) < 0.01, f"PL - Soma 1X2: {soma:.6f}")
    
    validar(0 <= ens['prob_over_2_5'] <= 1, f"PL - Over 2.5: {ens['prob_over_2_5']}")
    validar(0 <= ens['prob_btts'] <= 1, f"PL - BTTS: {ens['prob_btts']}")
    
    # Valida predicoes individuais
    for model_name, model_pred in pred['individual'].items():
        if model_pred:
            validar(not np.isnan(model_pred['prob_casa']), f"PL/{model_name} - Casa e NaN")
            validar(0 <= model_pred['prob_casa'] <= 1, f"PL/{model_name} - Casa: {model_pred['prob_casa']}")
            
            soma_ind = model_pred['prob_casa'] + model_pred['prob_empate'] + model_pred['prob_fora']
            validar(abs(soma_ind - 1.0) < 0.01, f"PL/{model_name} - Soma: {soma_ind:.6f}")
    
    print("    OK - Premier League validado")
    
except Exception as e:
    print(f"    ERRO: {e}")
    erros.append(f"Premier League: {str(e)}")

# Relatorio
print("\n" + "="*80)
print("RELATORIO")
print("="*80)
print(f"\nTotal de verificacoes: {checks}")

if erros:
    print(f"\nERROS ENCONTRADOS: {len(erros)}")
    print("-"*80)
    for erro in erros:
        print(f"  {erro}")
    print("\n" + "="*80)
    print("RESULTADO: FALHOU")
    print("="*80)
else:
    print(f"\nERROS ENCONTRADOS: 0")
    print("\n" + "="*80)
    print("RESULTADO: SUCESSO!")
    print("="*80)
    print("\nVERIFICADO:")
    print("  [OK] Sem NaN (Not a Number)")
    print("  [OK] Sem Inf (Infinito)")
    print("  [OK] Todas probabilidades no intervalo [0, 1]")
    print("  [OK] Soma de probabilidades = 1.0")
    print("  [OK] Over/Under e BTTS validos")
    print("  [OK] Predicoes individuais validas")
    print("\n*** SISTEMA MATEMATICAMENTE CORRETO ***")

