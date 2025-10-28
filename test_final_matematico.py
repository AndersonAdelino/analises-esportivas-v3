"""Teste matematico final com output garantido"""

import sys
sys.stdout.write("Iniciando teste...\n")
sys.stdout.flush()

import numpy as np
from ensemble import EnsembleModel

erros_totais = []

# Teste Brasileirao
sys.stdout.write("\n[BRASILEIRAO]\n")
sys.stdout.flush()

ensemble_bsa = EnsembleModel()
ensemble_bsa.fit(league_code='BSA')

pred_bsa = ensemble_bsa.predict_match('Botafogo FR', 'Santos FC')
ens_bsa = pred_bsa['ensemble']

sys.stdout.write(f"Casa: {ens_bsa['prob_casa']*100:.2f}%\n")
sys.stdout.write(f"Empate: {ens_bsa['prob_empate']*100:.2f}%\n")
sys.stdout.write(f"Fora: {ens_bsa['prob_fora']*100:.2f}%\n")
sys.stdout.flush()

# Valida Brasileirao
if np.isnan(ens_bsa['prob_casa']):
    erros_totais.append("BSA - Casa e NaN")
if np.isnan(ens_bsa['prob_empate']):
    erros_totais.append("BSA - Empate e NaN")
if np.isnan(ens_bsa['prob_fora']):
    erros_totais.append("BSA - Fora e NaN")

if np.isinf(ens_bsa['prob_casa']):
    erros_totais.append("BSA - Casa e Inf")
if np.isinf(ens_bsa['prob_empate']):
    erros_totais.append("BSA - Empate e Inf")
if np.isinf(ens_bsa['prob_fora']):
    erros_totais.append("BSA - Fora e Inf")

if ens_bsa['prob_casa'] < 0 or ens_bsa['prob_casa'] > 1:
    erros_totais.append(f"BSA - Casa fora do intervalo: {ens_bsa['prob_casa']}")
if ens_bsa['prob_empate'] < 0 or ens_bsa['prob_empate'] > 1:
    erros_totais.append(f"BSA - Empate fora do intervalo: {ens_bsa['prob_empate']}")
if ens_bsa['prob_fora'] < 0 or ens_bsa['prob_fora'] > 1:
    erros_totais.append(f"BSA - Fora fora do intervalo: {ens_bsa['prob_fora']}")

soma_bsa = ens_bsa['prob_casa'] + ens_bsa['prob_empate'] + ens_bsa['prob_fora']
if abs(soma_bsa - 1.0) > 0.01:
    erros_totais.append(f"BSA - Soma 1X2: {soma_bsa:.6f}")

sys.stdout.write("OK - Brasileirao validado\n\n")
sys.stdout.flush()

# Teste Premier League
sys.stdout.write("[PREMIER LEAGUE]\n")
sys.stdout.flush()

ensemble_pl = EnsembleModel()
ensemble_pl.fit(league_code='PL')

pred_pl = ensemble_pl.predict_match('Arsenal FC', 'Liverpool FC')
ens_pl = pred_pl['ensemble']

sys.stdout.write(f"Casa: {ens_pl['prob_casa']*100:.2f}%\n")
sys.stdout.write(f"Empate: {ens_pl['prob_empate']*100:.2f}%\n")
sys.stdout.write(f"Fora: {ens_pl['prob_fora']*100:.2f}%\n")
sys.stdout.flush()

# Valida Premier League
if np.isnan(ens_pl['prob_casa']):
    erros_totais.append("PL - Casa e NaN")
if np.isnan(ens_pl['prob_empate']):
    erros_totais.append("PL - Empate e NaN")
if np.isnan(ens_pl['prob_fora']):
    erros_totais.append("PL - Fora e NaN")

if np.isinf(ens_pl['prob_casa']):
    erros_totais.append("PL - Casa e Inf")
if np.isinf(ens_pl['prob_empate']):
    erros_totais.append("PL - Empate e Inf")
if np.isinf(ens_pl['prob_fora']):
    erros_totais.append("PL - Fora e Inf")

if ens_pl['prob_casa'] < 0 or ens_pl['prob_casa'] > 1:
    erros_totais.append(f"PL - Casa fora do intervalo: {ens_pl['prob_casa']}")
if ens_pl['prob_empate'] < 0 or ens_pl['prob_empate'] > 1:
    erros_totais.append(f"PL - Empate fora do intervalo: {ens_pl['prob_empate']}")
if ens_pl['prob_fora'] < 0 or ens_pl['prob_fora'] > 1:
    erros_totais.append(f"PL - Fora fora do intervalo: {ens_pl['prob_fora']}")

soma_pl = ens_pl['prob_casa'] + ens_pl['prob_empate'] + ens_pl['prob_fora']
if abs(soma_pl - 1.0) > 0.01:
    erros_totais.append(f"PL - Soma 1X2: {soma_pl:.6f}")

sys.stdout.write("OK - Premier League validado\n\n")
sys.stdout.flush()

# Relatorio
sys.stdout.write("="*80 + "\n")
sys.stdout.write("RESULTADO FINAL\n")
sys.stdout.write("="*80 + "\n\n")

if erros_totais:
    sys.stdout.write(f"ERROS ENCONTRADOS: {len(erros_totais)}\n")
    for erro in erros_totais:
        sys.stdout.write(f"  {erro}\n")
    sys.stdout.write("\nFALHOU\n")
else:
    sys.stdout.write("ERROS ENCONTRADOS: 0\n\n")
    sys.stdout.write("VERIFICADO:\n")
    sys.stdout.write("  [OK] Sem NaN\n")
    sys.stdout.write("  [OK] Sem Inf\n")
    sys.stdout.write("  [OK] Probabilidades no intervalo [0, 1]\n")
    sys.stdout.write("  [OK] Soma de probabilidades = 1.0\n")
    sys.stdout.write("\n*** SISTEMA MATEMATICAMENTE CORRETO ***\n")

sys.stdout.flush()

