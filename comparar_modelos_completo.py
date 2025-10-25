"""
Script para Comparação entre Dixon-Coles, Offensive-Defensive e Heurísticas

Compara as predições dos 3 métodos lado a lado
"""

from dixon_coles import DixonColesModel, load_match_data as load_dc_data
from offensive_defensive import OffensiveDefensiveModel, load_match_data as load_od_data
from heuristicas import HeuristicasModel
import pandas as pd


def comparar_predicoes(home_team, away_team):
    """
    Compara predições de todos os modelos
    
    Args:
        home_team: Time da casa
        away_team: Time visitante
    """
    print("\n")
    print("=" * 90)
    print(f"COMPARACAO DE MODELOS: {home_team} vs {away_team}")
    print("=" * 90)
    
    resultados = {}
    
    # Dixon-Coles
    print("\n[1/3] Calculando Dixon-Coles...")
    try:
        df = load_dc_data()
        dc = DixonColesModel(xi=0.003)
        dc.fit(df, time_decay=True)
        pred_dc = dc.predict_match(home_team, away_team)
        resultados['dixon_coles'] = pred_dc
        print("OK - Dixon-Coles calculado")
    except Exception as e:
        print(f"ERRO - Dixon-Coles: {e}")
        resultados['dixon_coles'] = None
    
    # Offensive-Defensive
    print("\n[2/3] Calculando Offensive-Defensive...")
    try:
        df = load_od_data()
        od = OffensiveDefensiveModel(xi=0.003)
        od.fit(df, time_decay=True)
        pred_od = od.predict_match(home_team, away_team)
        resultados['offensive_defensive'] = pred_od
        print("OK - Offensive-Defensive calculado")
    except Exception as e:
        print(f"ERRO - Offensive-Defensive: {e}")
        resultados['offensive_defensive'] = None
    
    # Heurísticas
    print("\n[3/3] Calculando Heuristicas...")
    try:
        heur = HeuristicasModel()
        heur.load_data()
        pred_heur = heur.predict_match(home_team, away_team)
        resultados['heuristicas'] = pred_heur
        print("OK - Heuristicas calculadas")
    except Exception as e:
        print(f"ERRO - Heuristicas: {e}")
        resultados['heuristicas'] = None
    
    # Exibe comparação
    print("\n")
    print("=" * 90)
    print("COMPARACAO DE RESULTADOS")
    print("=" * 90)
    
    # Tabela de probabilidades 1X2
    print("\n1. PROBABILIDADES DE RESULTADO (1X2)")
    print("-" * 90)
    print(f"{'Modelo':<25} {'Casa':>12} {'Empate':>12} {'Fora':>12} {'Mais Provavel':>25}")
    print("-" * 90)
    
    if resultados['dixon_coles']:
        dc = resultados['dixon_coles']
        prob_casa = dc['prob_home_win'] * 100
        prob_empate = dc['prob_draw'] * 100
        prob_fora = dc['prob_away_win'] * 100
        mais_provavel = max([('Casa', prob_casa), ('Empate', prob_empate), ('Fora', prob_fora)], key=lambda x: x[1])
        print(f"{'Dixon-Coles':<25} {prob_casa:>11.1f}% {prob_empate:>11.1f}% {prob_fora:>11.1f}% {mais_provavel[0]:>20} ({mais_provavel[1]:.1f}%)")
    
    if resultados['offensive_defensive']:
        od = resultados['offensive_defensive']
        prob_casa = od['prob_home_win'] * 100
        prob_empate = od['prob_draw'] * 100
        prob_fora = od['prob_away_win'] * 100
        mais_provavel = max([('Casa', prob_casa), ('Empate', prob_empate), ('Fora', prob_fora)], key=lambda x: x[1])
        print(f"{'Offensive-Defensive':<25} {prob_casa:>11.1f}% {prob_empate:>11.1f}% {prob_fora:>11.1f}% {mais_provavel[0]:>20} ({mais_provavel[1]:.1f}%)")
    
    if resultados['heuristicas']:
        heur = resultados['heuristicas']
        # Heurísticas retornam resultado categórico, então adaptamos
        resultado = heur['resultado_previsto']
        confianca = heur['confianca']
        print(f"{'Heuristicas':<25} {'-':>12} {'-':>12} {'-':>12} {resultado:>25}")
        print(f"{'':25} {'':>12} {'':>12} {'':>12} {'(Confianca: ' + str(confianca) + '%)':>25}")
    
    # Over/Under 2.5
    print("\n2. OVER/UNDER 2.5 GOLS")
    print("-" * 90)
    print(f"{'Modelo':<25} {'Over 2.5':>15} {'Under 2.5':>15} {'Predicao':>25}")
    print("-" * 90)
    
    if resultados['dixon_coles']:
        dc = resultados['dixon_coles']
        over = dc['prob_over_2_5'] * 100
        under = (1 - dc['prob_over_2_5']) * 100
        pred = 'Over 2.5' if over > 50 else 'Under 2.5'
        print(f"{'Dixon-Coles':<25} {over:>14.1f}% {under:>14.1f}% {pred:>25}")
    
    if resultados['offensive_defensive']:
        od = resultados['offensive_defensive']
        over = od['prob_over_2_5'] * 100
        under = (1 - od['prob_over_2_5']) * 100
        pred = 'Over 2.5' if over > 50 else 'Under 2.5'
        print(f"{'Offensive-Defensive':<25} {over:>14.1f}% {under:>14.1f}% {pred:>25}")
    
    if resultados['heuristicas']:
        heur = resultados['heuristicas']
        pred_ou = heur['over_under']
        conf_ou = heur['confianca_ou']
        print(f"{'Heuristicas':<25} {'-':>15} {'-':>15} {pred_ou + ' (' + str(conf_ou) + '%)':>25}")
    
    # Both Teams to Score
    print("\n3. AMBOS MARCAM (BTTS)")
    print("-" * 90)
    print(f"{'Modelo':<25} {'Sim':>15} {'Nao':>15} {'Predicao':>25}")
    print("-" * 90)
    
    if resultados['dixon_coles']:
        dc = resultados['dixon_coles']
        btts_sim = dc['prob_btts_yes'] * 100
        btts_nao = dc['prob_btts_no'] * 100
        pred = 'Sim' if btts_sim > 50 else 'Nao'
        print(f"{'Dixon-Coles':<25} {btts_sim:>14.1f}% {btts_nao:>14.1f}% {pred:>25}")
    
    if resultados['offensive_defensive']:
        od = resultados['offensive_defensive']
        btts_sim = od['prob_btts_yes'] * 100
        btts_nao = od['prob_btts_no'] * 100
        pred = 'Sim' if btts_sim > 50 else 'Nao'
        print(f"{'Offensive-Defensive':<25} {btts_sim:>14.1f}% {btts_nao:>14.1f}% {pred:>25}")
    
    if resultados['heuristicas']:
        heur = resultados['heuristicas']
        pred_btts = heur['btts']
        conf_btts = heur['confianca_btts']
        print(f"{'Heuristicas':<25} {'-':>15} {'-':>15} {pred_btts + ' (' + str(conf_btts) + '%)':>25}")
    
    # Placar mais provável
    print("\n4. PLACAR MAIS PROVAVEL")
    print("-" * 90)
    print(f"{'Modelo':<25} {'Placar':>15} {'Probabilidade':>20}")
    print("-" * 90)
    
    if resultados['dixon_coles']:
        dc = resultados['dixon_coles']
        top_score = dc['top_scores'][0]
        placar = f"{top_score[0][0]}-{top_score[0][1]}"
        prob = top_score[1] * 100
        print(f"{'Dixon-Coles':<25} {placar:>15} {prob:>19.1f}%")
    
    if resultados['offensive_defensive']:
        od = resultados['offensive_defensive']
        top_score = od['top_scores'][0]
        placar = f"{top_score[0][0]}-{top_score[0][1]}"
        prob = top_score[1] * 100
        print(f"{'Offensive-Defensive':<25} {placar:>15} {prob:>19.1f}%")
    
    if resultados['heuristicas']:
        heur = resultados['heuristicas']
        gols = heur['gols_esperados']
        print(f"{'Heuristicas':<25} {'-':>15} {f'~{gols:.1f} gols esperados':>20}")
    
    # Análise de consenso
    print("\n5. CONSENSO DOS MODELOS")
    print("-" * 90)
    
    # Consenso 1X2
    votos_casa = 0
    votos_empate = 0
    votos_fora = 0
    
    if resultados['dixon_coles']:
        dc = resultados['dixon_coles']
        max_prob = max(dc['prob_home_win'], dc['prob_draw'], dc['prob_away_win'])
        if dc['prob_home_win'] == max_prob:
            votos_casa += 1
        elif dc['prob_draw'] == max_prob:
            votos_empate += 1
        else:
            votos_fora += 1
    
    if resultados['offensive_defensive']:
        od = resultados['offensive_defensive']
        max_prob = max(od['prob_home_win'], od['prob_draw'], od['prob_away_win'])
        if od['prob_home_win'] == max_prob:
            votos_casa += 1
        elif od['prob_draw'] == max_prob:
            votos_empate += 1
        else:
            votos_fora += 1
    
    if resultados['heuristicas']:
        heur = resultados['heuristicas']
        if 'Casa' in heur['resultado_previsto'] or home_team in heur['resultado_previsto']:
            votos_casa += 1
        elif 'Empate' in heur['resultado_previsto']:
            votos_empate += 1
        else:
            votos_fora += 1
    
    total_votos = votos_casa + votos_empate + votos_fora
    
    print(f"\nResultado:")
    print(f"  Vitoria Casa:      {votos_casa}/{total_votos} modelos")
    print(f"  Empate:            {votos_empate}/{total_votos} modelos")
    print(f"  Vitoria Visitante: {votos_fora}/{total_votos} modelos")
    
    if votos_casa > votos_empate and votos_casa > votos_fora:
        print(f"\nCONSENSO: Vitoria {home_team}")
    elif votos_fora > votos_casa and votos_fora > votos_empate:
        print(f"\nCONSENSO: Vitoria {away_team}")
    elif votos_empate > votos_casa and votos_empate > votos_fora:
        print(f"\nCONSENSO: Empate")
    else:
        print(f"\nSEM CONSENSO CLARO - Modelos divergem")
    
    # Consenso Over/Under
    votos_over = 0
    votos_under = 0
    
    if resultados['dixon_coles'] and resultados['dixon_coles']['prob_over_2_5'] > 0.5:
        votos_over += 1
    elif resultados['dixon_coles']:
        votos_under += 1
    
    if resultados['offensive_defensive'] and resultados['offensive_defensive']['prob_over_2_5'] > 0.5:
        votos_over += 1
    elif resultados['offensive_defensive']:
        votos_under += 1
    
    if resultados['heuristicas']:
        if resultados['heuristicas']['over_under'] == 'Over 2.5':
            votos_over += 1
        elif resultados['heuristicas']['over_under'] == 'Under 2.5':
            votos_under += 1
    
    print(f"\nOver/Under 2.5:")
    print(f"  Over:  {votos_over}/{total_votos} modelos")
    print(f"  Under: {votos_under}/{total_votos} modelos")
    
    print("\n" + "=" * 90)
    
    return resultados


if __name__ == "__main__":
    import sys
    
    print("\n")
    print("=" * 90)
    print("COMPARACAO COMPLETA DE MODELOS")
    print("Dixon-Coles vs Offensive-Defensive vs Heuristicas")
    print("=" * 90)
    print("\n")
    
    if len(sys.argv) == 3:
        home = sys.argv[1]
        away = sys.argv[2]
        comparar_predicoes(home, away)
    else:
        print("Exemplos de uso:")
        print("\n1. Comparacao rapida:")
        partidas = [
            ('Arsenal FC', 'Liverpool FC'),
            ('Manchester City FC', 'Chelsea FC'),
        ]
        
        for home, away in partidas:
            try:
                comparar_predicoes(home, away)
                print("\n")
            except Exception as e:
                print(f"\nErro ao comparar {home} vs {away}: {e}\n")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 90)
        print("COMPARACOES CONCLUIDAS!")
        print("=" * 90)
        print("\nUso:")
        print("  python comparar_modelos_completo.py 'Arsenal FC' 'Liverpool FC'")
        print()

