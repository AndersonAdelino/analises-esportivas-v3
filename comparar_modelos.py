"""
Compara os modelos Dixon-Coles e Offensive-Defensive
"""
from dixon_coles import DixonColesModel, load_match_data as load_dc
from offensive_defensive import OffensiveDefensiveModel, load_match_data as load_od
import pandas as pd


def comparar_predicoes(home_team, away_team):
    """Compara predições dos dois modelos para uma partida"""
    
    print("\n" + "=" * 90)
    print(f"COMPARACAO: {home_team} vs {away_team}")
    print("=" * 90)
    
    # Dixon-Coles
    print("\n[1/2] Treinando Dixon-Coles...")
    df_dc = load_dc()
    model_dc = DixonColesModel(xi=0.003)
    model_dc.fit(df_dc, time_decay=True)
    pred_dc = model_dc.predict_match(home_team, away_team)
    
    # Offensive-Defensive
    print("\n[2/2] Treinando Offensive-Defensive...")
    df_od = load_od()
    model_od = OffensiveDefensiveModel(xi=0.003)
    model_od.fit(df_od, time_decay=True)
    pred_od = model_od.predict_match(home_team, away_team)
    
    # Comparação
    print("\n" + "=" * 90)
    print("COMPARACAO DOS MODELOS")
    print("=" * 90)
    
    # Gols esperados
    print(f"\n{'Metrica':<30} {'Dixon-Coles':<25} {'Offensive-Defensive':<25}")
    print("-" * 90)
    
    print(f"\nGOLS ESPERADOS:")
    print(f"  {home_team[:27]:<27}   {pred_dc['expected_goals_home']:>5.2f}                    {pred_od['expected_goals_home']:>5.2f}")
    print(f"  {away_team[:27]:<27}   {pred_dc['expected_goals_away']:>5.2f}                    {pred_od['expected_goals_away']:>5.2f}")
    
    print(f"\nPROBABILIDADES 1X2:")
    print(f"  Vitoria Casa               {pred_dc['prob_home_win']*100:>6.1f}%                  {pred_od['prob_home_win']*100:>6.1f}%")
    print(f"  Empate                     {pred_dc['prob_draw']*100:>6.1f}%                  {pred_od['prob_draw']*100:>6.1f}%")
    print(f"  Vitoria Fora               {pred_dc['prob_away_win']*100:>6.1f}%                  {pred_od['prob_away_win']*100:>6.1f}%")
    
    print(f"\nOVER/UNDER 2.5:")
    print(f"  Over 2.5                   {pred_dc['prob_over_2_5']*100:>6.1f}%                  {pred_od['prob_over_2_5']*100:>6.1f}%")
    print(f"  Under 2.5                  {pred_dc['prob_under_2_5']*100:>6.1f}%                  {pred_od['prob_under_2_5']*100:>6.1f}%")
    
    print(f"\nAMBAS MARCAM (BTTS):")
    print(f"  Sim                        {pred_dc['prob_btts_yes']*100:>6.1f}%                  {pred_od['prob_btts_yes']*100:>6.1f}%")
    print(f"  Nao                        {pred_dc['prob_btts_no']*100:>6.1f}%                  {pred_od['prob_btts_no']*100:>6.1f}%")
    
    print(f"\nPLACAR MAIS PROVAVEL:")
    dc_top = pred_dc['top_scores'][0]
    od_top = pred_od['top_scores'][0]
    print(f"  Placar                     {dc_top[0][0]}-{dc_top[0][1]} ({dc_top[1]*100:.1f}%)         {od_top[0][0]}-{od_top[0][1]} ({od_top[1]*100:.1f}%)")
    
    # Diferenças
    print(f"\nDIFERENCAS (|DC - OD|):")
    diff_home_win = abs(pred_dc['prob_home_win'] - pred_od['prob_home_win']) * 100
    diff_draw = abs(pred_dc['prob_draw'] - pred_od['prob_draw']) * 100
    diff_away_win = abs(pred_dc['prob_away_win'] - pred_od['prob_away_win']) * 100
    diff_over = abs(pred_dc['prob_over_2_5'] - pred_od['prob_over_2_5']) * 100
    
    print(f"  Vitoria Casa:  {diff_home_win:.1f} pontos percentuais")
    print(f"  Empate:        {diff_draw:.1f} pontos percentuais")
    print(f"  Vitoria Fora:  {diff_away_win:.1f} pontos percentuais")
    print(f"  Over 2.5:      {diff_over:.1f} pontos percentuais")
    
    # Análise
    print(f"\nANALISE:")
    if diff_home_win < 3 and diff_draw < 3 and diff_away_win < 3:
        print("  Modelos MUITO CONCORDANTES (diferencas < 3%)")
    elif diff_home_win < 5 and diff_draw < 5 and diff_away_win < 5:
        print("  Modelos CONCORDANTES (diferencas < 5%)")
    else:
        print("  Modelos DISCORDANTES (diferencas significativas)")
    
    print("=" * 90)
    
    return {
        'dixon_coles': pred_dc,
        'offensive_defensive': pred_od,
        'diferencas': {
            'home_win': diff_home_win,
            'draw': diff_draw,
            'away_win': diff_away_win,
            'over_2_5': diff_over
        }
    }


def comparar_forcas_times():
    """Compara as forças dos times nos dois modelos"""
    
    print("\n" + "=" * 90)
    print("COMPARACAO DE FORCAS DOS TIMES")
    print("=" * 90)
    
    # Treina modelos
    print("\nTreinando modelos...")
    
    df_dc = load_dc()
    model_dc = DixonColesModel(xi=0.003)
    model_dc.fit(df_dc, time_decay=True)
    
    df_od = load_od()
    model_od = OffensiveDefensiveModel(xi=0.003)
    model_od.fit(df_od, time_decay=True)
    
    # Obtém forças
    strengths_dc = model_dc.get_team_strengths()
    strengths_od = model_od.get_team_strengths()
    
    # Combina
    comparison = strengths_dc.merge(
        strengths_od, 
        on='Time', 
        suffixes=('_DC', '_OD')
    )
    
    print("\n" + "=" * 90)
    print(f"{'Time':<30} {'Ataque DC':<12} {'Ataque OD':<12} {'Defesa DC':<12} {'Defesa OD':<12}")
    print("-" * 90)
    
    for _, row in comparison.head(10).iterrows():
        print(f"{row['Time'][:28]:<30} {row['Ataque_DC']:>10.3f}  {row['Ataque_OD']:>10.3f}  "
              f"{row['Defesa_DC']:>10.3f}  {row['Defesa_OD']:>10.3f}")
    
    print("=" * 90)
    
    print("\nOBSERVACOES:")
    print("- Dixon-Coles inclui parametro RHO (correlacao de gols baixos)")
    print("- Offensive-Defensive usa Poisson puro (mais simples)")
    print("- Valores proximos indicam modelos consistentes")
    
    return comparison


def resumo_modelos():
    """Exibe resumo comparativo dos modelos"""
    
    print("\n" + "=" * 90)
    print("RESUMO COMPARATIVO DOS MODELOS")
    print("=" * 90)
    
    print("\nDIXON-COLES:")
    print("  Complexidade:    Alta")
    print("  Parametros:      Home Advantage + Rho + Ataque + Defesa")
    print("  Vantagens:       - Correcao para placares baixos (0-0, 1-1, etc)")
    print("                   - Mais preciso teoricamente")
    print("                   - Usado por profissionais")
    print("  Desvantagens:    - Mais lento para treinar")
    print("                   - Mais parametros = pode overfit")
    
    print("\nOFFENSIVE-DEFENSIVE:")
    print("  Complexidade:    Media")
    print("  Parametros:      Home Advantage + Ataque + Defesa")
    print("  Vantagens:       - Mais simples e rapido")
    print("                   - Facil de interpretar")
    print("                   - Menos propenso a overfit")
    print("  Desvantagens:    - Assume independencia (sem correlacao)")
    print("                   - Pode subestimar empates 0-0")
    
    print("\nQUANDO USAR CADA UM:")
    print("  Dixon-Coles:     - Quando precisa maxima precisao")
    print("                   - Tem muitos dados historicos")
    print("                   - Foco em apostas profissionais")
    
    print("  Off-Defensive:   - Para analises rapidas")
    print("                   - Poucos dados disponiveis")
    print("                   - Interpretabilidade importante")
    
    print("\nRECOMENDACAO:")
    print("  Use AMBOS e compare as predicoes!")
    print("  Quando concordam -> maior confianca")
    print("  Quando discordam -> mais cautela")
    
    print("=" * 90)


if __name__ == "__main__":
    print("\n")
    print("*" * 90)
    print("COMPARACAO: DIXON-COLES vs OFFENSIVE-DEFENSIVE")
    print("*" * 90)
    
    # Resumo teórico
    resumo_modelos()
    
    # Compara forças dos times
    print("\n")
    input("Pressione ENTER para comparar forcas dos times...")
    comparar_forcas_times()
    
    # Compara predições
    print("\n")
    input("Pressione ENTER para comparar predicoes...")
    
    partidas = [
        ('Arsenal FC', 'Liverpool FC'),
        ('Manchester City FC', 'Chelsea FC'),
        ('Manchester United FC', 'Tottenham Hotspur FC'),
    ]
    
    for home, away in partidas:
        comparar_predicoes(home, away)
        print("\n")
    
    print("*" * 90)
    print("COMPARACAO CONCLUIDA!")
    print("*" * 90)
    print("\nCONCLUSAO:")
    print("- Ambos os modelos sao validos e complementares")
    print("- Use Dixon-Coles quando precisar de maxima precisao")
    print("- Use Offensive-Defensive para analises rapidas")
    print("- Combine ambos para maior confianca nas predicoes")
    print()

