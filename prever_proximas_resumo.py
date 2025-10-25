"""
Versão simplificada: Busca próximas partidas e gera predições (apenas primeiras 10)
"""
from prever_proximas_partidas import buscar_proximas_partidas, gerar_predicoes_proximas_partidas, salvar_predicoes
from dixon_coles import DixonColesModel, load_match_data
import pandas as pd

print("\n" + "*" * 80)
print("PREDICOES - PROXIMAS PARTIDAS DA PREMIER LEAGUE (RESUMO)")
print("*" * 80)
print()

# Busca próximas partidas (limita a 10 para ser rápido)
print("[1/3] Buscando proximas partidas da API...")
partidas = buscar_proximas_partidas(limit=10)

if not partidas:
    print("Nenhuma partida agendada encontrada.")
    exit()

print(f"\nEncontradas {len(partidas)} partidas para prever\n")

# Treina modelo
print("[2/3] Treinando modelo Dixon-Coles...")
df = load_match_data()
model = DixonColesModel(xi=0.003)
model.fit(df, time_decay=True)

print()

# Gera predições
print("[3/3] Gerando predicoes...")
df_pred = gerar_predicoes_proximas_partidas(partidas, model)

# Salva
filename = salvar_predicoes(df_pred)

print("\n" + "=" * 80)
print("RESUMO DAS PREDICOES")
print("=" * 80)

for _, jogo in df_pred.iterrows():
    print(f"\n{jogo['Data']} {jogo['Hora']} - Rodada {jogo['Rodada']}")
    print(f"{jogo['Time_Casa']} vs {jogo['Time_Visitante']}")
    print(f"  Resultado Provavel: {jogo['Resultado_Provavel']} ({jogo['Confianca_%']:.1f}%)")
    print(f"  Over 2.5: {jogo['Prob_Over_2.5_%']:.1f}% | BTTS: {jogo['Prob_BTTS_Sim_%']:.1f}%")
    print(f"  Placar Mais Provavel: {jogo['Placar_Mais_Provavel']}")

print("\n" + "*" * 80)
print(f"PREDICOES SALVAS EM: {filename}")
print("*" * 80)

