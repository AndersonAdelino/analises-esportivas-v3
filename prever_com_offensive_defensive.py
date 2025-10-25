"""
Versão do script de predição usando modelo Offensive-Defensive
"""
from api_client import FootballDataClient
from offensive_defensive import OffensiveDefensiveModel, load_match_data
from config import PREMIER_LEAGUE_CODE
import pandas as pd
from datetime import datetime


def buscar_proximas_partidas(limit=10):
    """Busca próximas partidas da API"""
    print("Buscando proximas partidas da Premier League...")
    
    client = FootballDataClient()
    matches_data = client.get_competition_matches(
        competition_code=PREMIER_LEAGUE_CODE,
        status='SCHEDULED',
        limit=limit
    )
    
    matches = matches_data.get('matches', [])
    
    partidas = []
    for match in matches:
        partidas.append({
            'data': match['utcDate'][:10],
            'hora': match['utcDate'][11:16],
            'time_casa': match['homeTeam']['name'],
            'time_visitante': match['awayTeam']['name'],
            'rodada': match.get('matchday', 'N/A'),
        })
    
    return partidas


def gerar_predicoes(partidas, model):
    """Gera predições usando Offensive-Defensive"""
    
    predicoes = []
    
    for i, partida in enumerate(partidas, 1):
        time_casa = partida['time_casa']
        time_visitante = partida['time_visitante']
        
        print(f"[{i}/{len(partidas)}] {time_casa} vs {time_visitante}")
        
        try:
            pred = model.predict_match(time_casa, time_visitante)
            
            probs = {
                'Casa': pred['prob_home_win'],
                'Empate': pred['prob_draw'],
                'Fora': pred['prob_away_win']
            }
            resultado_provavel = max(probs, key=probs.get)
            
            predicoes.append({
                'Data': partida['data'],
                'Hora': partida['hora'],
                'Rodada': partida['rodada'],
                'Time_Casa': time_casa,
                'Time_Visitante': time_visitante,
                'Gols_Esp_Casa': round(pred['expected_goals_home'], 2),
                'Gols_Esp_Fora': round(pred['expected_goals_away'], 2),
                'Prob_Vit_Casa_%': round(pred['prob_home_win'] * 100, 1),
                'Prob_Empate_%': round(pred['prob_draw'] * 100, 1),
                'Prob_Vit_Fora_%': round(pred['prob_away_win'] * 100, 1),
                'Resultado_Provavel': resultado_provavel,
                'Confianca_%': round(probs[resultado_provavel] * 100, 1),
                'Prob_Over_2.5_%': round(pred['prob_over_2_5'] * 100, 1),
                'Prob_Under_2.5_%': round(pred['prob_under_2_5'] * 100, 1),
                'Prob_BTTS_Sim_%': round(pred['prob_btts_yes'] * 100, 1),
                'Prob_BTTS_Nao_%': round(pred['prob_btts_no'] * 100, 1),
                'Placar_Mais_Provavel': f"{pred['top_scores'][0][0][0]}-{pred['top_scores'][0][0][1]}",
            })
            
            print(f"  -> {resultado_provavel} ({probs[resultado_provavel]*100:.1f}%)")
            
        except ValueError as e:
            print(f"  -> AVISO: {e}")
            continue
    
    return pd.DataFrame(predicoes)


def main():
    print("\n" + "*" * 80)
    print("PREDICOES - MODELO OFFENSIVE-DEFENSIVE")
    print("*" * 80)
    print()
    
    # Busca partidas
    print("[1/3] Buscando proximas partidas...")
    partidas = buscar_proximas_partidas(limit=10)
    
    if not partidas:
        print("Nenhuma partida encontrada.")
        return
    
    print(f"OK - {len(partidas)} partidas encontradas\n")
    
    # Treina modelo
    print("[2/3] Treinando modelo Offensive-Defensive...")
    df = load_match_data()
    model = OffensiveDefensiveModel(xi=0.003)
    model.fit(df, time_decay=True)
    
    print()
    
    # Gera predições
    print("[3/3] Gerando predicoes...")
    df_pred = gerar_predicoes(partidas, model)
    
    # Salva
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/predicoes_offensive_defensive_{timestamp}.csv'
    df_pred.to_csv(filename, index=False, encoding='utf-8')
    
    print("\n" + "=" * 80)
    print("PREDICOES SALVAS!")
    print("=" * 80)
    print(f"Arquivo: {filename}")
    print(f"Total: {len(df_pred)} predicoes")
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    
    for _, jogo in df_pred.iterrows():
        print(f"\n{jogo['Data']} {jogo['Hora']} - Rodada {jogo['Rodada']}")
        print(f"{jogo['Time_Casa']} vs {jogo['Time_Visitante']}")
        print(f"  Resultado: {jogo['Resultado_Provavel']} ({jogo['Confianca_%']:.1f}%)")
        print(f"  Over 2.5: {jogo['Prob_Over_2.5_%']:.1f}% | BTTS: {jogo['Prob_BTTS_Sim_%']:.1f}%")
        print(f"  Placar: {jogo['Placar_Mais_Provavel']}")
    
    print("\n" + "*" * 80)
    print("CONCLUIDO!")
    print("*" * 80)
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

