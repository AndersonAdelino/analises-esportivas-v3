"""
Gera predições em lote para múltiplas partidas e salva em CSV
"""
from dixon_coles import DixonColesModel, load_match_data
import pandas as pd
from datetime import datetime


def gerar_todas_combinacoes(model, max_por_time=5):
    """
    Gera predições para as combinações mais interessantes
    
    Args:
        model: Modelo Dixon-Coles treinado
        max_por_time: Máximo de partidas por time
    """
    times = model.teams
    predicoes = []
    
    print(f"Gerando predicoes para {len(times)} times...")
    print("Isso pode levar alguns minutos...\n")
    
    # Pega top times por força
    strengths = model.get_team_strengths()
    top_times = strengths.head(10)['Time'].tolist()
    
    total = len(top_times) * (len(top_times) - 1)
    contador = 0
    
    # Gera predições para todos contra todos (top times)
    for i, time_casa in enumerate(top_times):
        for time_visitante in top_times:
            if time_casa == time_visitante:
                continue
            
            contador += 1
            print(f"[{contador}/{total}] {time_casa} vs {time_visitante}", end='\r')
            
            try:
                pred = model.predict_match(time_casa, time_visitante)
                
                predicoes.append({
                    'Time_Casa': time_casa,
                    'Time_Visitante': time_visitante,
                    'Gols_Esp_Casa': round(pred['expected_goals_home'], 2),
                    'Gols_Esp_Fora': round(pred['expected_goals_away'], 2),
                    'Prob_Vit_Casa_%': round(pred['prob_home_win'] * 100, 1),
                    'Prob_Empate_%': round(pred['prob_draw'] * 100, 1),
                    'Prob_Vit_Fora_%': round(pred['prob_away_win'] * 100, 1),
                    'Prob_Over_2.5_%': round(pred['prob_over_2_5'] * 100, 1),
                    'Prob_Under_2.5_%': round(pred['prob_under_2_5'] * 100, 1),
                    'Prob_BTTS_Sim_%': round(pred['prob_btts_yes'] * 100, 1),
                    'Prob_BTTS_Nao_%': round(pred['prob_btts_no'] * 100, 1),
                    'Placar_Mais_Provavel': f"{pred['top_scores'][0][0][0]}-{pred['top_scores'][0][0][1]}",
                    'Prob_Placar_Top_%': round(pred['top_scores'][0][1] * 100, 2),
                })
            except Exception as e:
                print(f"\nErro em {time_casa} vs {time_visitante}: {e}")
                continue
    
    print(f"\n\nTotal de predicoes geradas: {len(predicoes)}")
    
    return pd.DataFrame(predicoes)


def gerar_partidas_especificas(model, partidas):
    """
    Gera predições para lista específica de partidas
    
    Args:
        model: Modelo treinado
        partidas: Lista de tuplas (time_casa, time_visitante)
    """
    predicoes = []
    
    for i, (time_casa, time_visitante) in enumerate(partidas, 1):
        print(f"[{i}/{len(partidas)}] {time_casa} vs {time_visitante}")
        
        try:
            pred = model.predict_match(time_casa, time_visitante)
            
            predicoes.append({
                'Time_Casa': time_casa,
                'Time_Visitante': time_visitante,
                'Gols_Esp_Casa': round(pred['expected_goals_home'], 2),
                'Gols_Esp_Fora': round(pred['expected_goals_away'], 2),
                'Prob_Vit_Casa_%': round(pred['prob_home_win'] * 100, 1),
                'Prob_Empate_%': round(pred['prob_draw'] * 100, 1),
                'Prob_Vit_Fora_%': round(pred['prob_away_win'] * 100, 1),
                'Prob_Over_2.5_%': round(pred['prob_over_2_5'] * 100, 1),
                'Prob_Under_2.5_%': round(pred['prob_under_2_5'] * 100, 1),
                'Prob_BTTS_Sim_%': round(pred['prob_btts_yes'] * 100, 1),
                'Prob_BTTS_Nao_%': round(pred['prob_btts_no'] * 100, 1),
                'Placar_Mais_Provavel': f"{pred['top_scores'][0][0][0]}-{pred['top_scores'][0][0][1]}",
                'Prob_Placar_Top_%': round(pred['top_scores'][0][1] * 100, 2),
                'Top_3_Placares': ', '.join([f"{s[0][0]}-{s[0][1]} ({s[1]*100:.1f}%)" for s in pred['top_scores'][:3]])
            })
        except Exception as e:
            print(f"  ERRO: {e}")
            continue
    
    return pd.DataFrame(predicoes)


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GERADOR DE PREDICOES EM LOTE - MODELO DIXON-COLES")
    print("="*80)
    print("\n")
    
    # Carrega e treina modelo
    print("Carregando dados e treinando modelo...")
    df = load_match_data()
    model = DixonColesModel(xi=0.003)
    model.fit(df, time_decay=True)
    
    print("\n" + "="*80)
    print("OPCOES")
    print("="*80)
    print("1. Gerar predicoes para top 10 times (todos contra todos)")
    print("2. Gerar predicoes para partidas especificas")
    
    opcao = input("\nEscolha (1 ou 2): ").strip()
    
    if opcao == '1':
        # Gera todas as combinações dos top times
        df_pred = gerar_todas_combinacoes(model)
        
        # Salva em CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/predicoes_dixon_coles_{timestamp}.csv'
        df_pred.to_csv(filename, index=False, encoding='utf-8')
        
        print("\n" + "="*80)
        print("PREDICOES SALVAS COM SUCESSO!")
        print("="*80)
        print(f"Arquivo: {filename}")
        print(f"Total de predicoes: {len(df_pred)}")
        
        # Mostra algumas estatísticas
        print("\nExemplo de predicoes (primeiras 5):")
        print(df_pred[['Time_Casa', 'Time_Visitante', 'Prob_Vit_Casa_%', 'Prob_Empate_%', 
                       'Prob_Vit_Fora_%', 'Placar_Mais_Provavel']].head().to_string(index=False))
    
    elif opcao == '2':
        # Partidas específicas
        print("\n" + "="*80)
        print("PARTIDAS DA PROXIMA RODADA DA PREMIER LEAGUE")
        print("="*80)
        
        # Exemplo de partidas (você pode modificar esta lista)
        partidas_exemplo = [
            ('Arsenal FC', 'Liverpool FC'),
            ('Manchester City FC', 'Chelsea FC'),
            ('Manchester United FC', 'Tottenham Hotspur FC'),
            ('Newcastle United FC', 'Brighton & Hove Albion FC'),
            ('Aston Villa FC', 'Crystal Palace FC'),
        ]
        
        df_pred = gerar_partidas_especificas(model, partidas_exemplo)
        
        # Salva em CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/predicoes_proxima_rodada_{timestamp}.csv'
        df_pred.to_csv(filename, index=False, encoding='utf-8')
        
        print("\n" + "="*80)
        print("PREDICOES SALVAS COM SUCESSO!")
        print("="*80)
        print(f"Arquivo: {filename}")
        print(f"Total de predicoes: {len(df_pred)}")
        
        print("\nResumo das predicoes:")
        print(df_pred[['Time_Casa', 'Time_Visitante', 'Prob_Vit_Casa_%', 'Prob_Empate_%', 
                       'Prob_Vit_Fora_%', 'Prob_Over_2.5_%']].to_string(index=False))
    
    else:
        print("Opcao invalida!")

