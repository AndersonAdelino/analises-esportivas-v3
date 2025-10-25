"""
Busca próximas partidas da Premier League pela API e gera predições usando Dixon-Coles
"""
from api_client import FootballDataClient
from dixon_coles import DixonColesModel, load_match_data
from config import PREMIER_LEAGUE_CODE
import pandas as pd
from datetime import datetime
import os


def buscar_proximas_partidas(limit=20):
    """
    Busca próximas partidas agendadas da Premier League
    
    Args:
        limit: Número máximo de partidas a buscar
        
    Returns:
        Lista de partidas agendadas
    """
    print("=" * 80)
    print("BUSCANDO PROXIMAS PARTIDAS DA PREMIER LEAGUE")
    print("=" * 80)
    
    client = FootballDataClient()
    
    try:
        # Busca partidas agendadas (SCHEDULED)
        print("\nBuscando partidas agendadas da API...")
        matches_data = client.get_competition_matches(
            competition_code=PREMIER_LEAGUE_CODE,
            status='SCHEDULED',
            limit=limit
        )
        
        matches = matches_data.get('matches', [])
        
        if not matches:
            print("Nenhuma partida agendada encontrada!")
            return []
        
        print(f"OK - {len(matches)} partidas encontradas\n")
        
        partidas = []
        for match in matches:
            partidas.append({
                'match_id': match['id'],
                'data': match['utcDate'],
                'data_formatada': match['utcDate'][:10],
                'hora': match['utcDate'][11:16],
                'time_casa': match['homeTeam']['name'],
                'time_casa_id': match['homeTeam']['id'],
                'time_visitante': match['awayTeam']['name'],
                'time_visitante_id': match['awayTeam']['id'],
                'rodada': match.get('matchday', 'N/A'),
                'estadio': match.get('venue', 'N/A'),
            })
        
        return partidas
        
    except Exception as e:
        print(f"ERRO ao buscar partidas: {e}")
        return []


def gerar_predicoes_proximas_partidas(partidas, model):
    """
    Gera predições para lista de partidas
    
    Args:
        partidas: Lista de dicionários com informações das partidas
        model: Modelo Dixon-Coles treinado
        
    Returns:
        DataFrame com predições
    """
    print("=" * 80)
    print("GERANDO PREDICOES COM MODELO DIXON-COLES")
    print("=" * 80)
    print()
    
    predicoes = []
    
    for i, partida in enumerate(partidas, 1):
        time_casa = partida['time_casa']
        time_visitante = partida['time_visitante']
        
        print(f"[{i}/{len(partidas)}] {time_casa} vs {time_visitante}")
        
        try:
            # Gera predição
            pred = model.predict_match(time_casa, time_visitante)
            
            # Determina resultado mais provável
            probs = {
                'Casa': pred['prob_home_win'],
                'Empate': pred['prob_draw'],
                'Fora': pred['prob_away_win']
            }
            resultado_provavel = max(probs, key=probs.get)
            
            predicoes.append({
                'Data': partida['data_formatada'],
                'Hora': partida['hora'],
                'Rodada': partida['rodada'],
                'Time_Casa': time_casa,
                'Time_Visitante': time_visitante,
                'Estadio': partida['estadio'],
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
                'Prob_Placar_%': round(pred['top_scores'][0][1] * 100, 2),
                'Top_3_Placares': ', '.join([
                    f"{s[0][0]}-{s[0][1]} ({s[1]*100:.1f}%)" 
                    for s in pred['top_scores'][:3]
                ])
            })
            
            print(f"  -> {resultado_provavel} ({probs[resultado_provavel]*100:.1f}%)")
            
        except ValueError as e:
            print(f"  -> AVISO: {e}")
            # Time não está no modelo, pula
            continue
        except Exception as e:
            print(f"  -> ERRO: {e}")
            continue
    
    print()
    return pd.DataFrame(predicoes)


def exibir_resumo_predicoes(df_pred):
    """Exibe resumo formatado das predições"""
    print("=" * 80)
    print("RESUMO DAS PREDICOES")
    print("=" * 80)
    print()
    
    if df_pred.empty:
        print("Nenhuma predição foi gerada.")
        return
    
    # Agrupar por data
    for data in df_pred['Data'].unique():
        jogos_data = df_pred[df_pred['Data'] == data]
        
        print(f"\n[DATA: {data}]")
        print("-" * 80)
        
        for _, jogo in jogos_data.iterrows():
            print(f"\n{jogo['Hora']} - Rodada {jogo['Rodada']}")
            print(f"{jogo['Time_Casa']} vs {jogo['Time_Visitante']}")
            print(f"  Estadio: {jogo['Estadio']}")
            print(f"\n  Gols Esperados: {jogo['Time_Casa']}: {jogo['Gols_Esp_Casa']:.2f} | "
                  f"{jogo['Time_Visitante']}: {jogo['Gols_Esp_Fora']:.2f}")
            
            print(f"\n  Probabilidades:")
            print(f"    Vitoria {jogo['Time_Casa']}: {jogo['Prob_Vit_Casa_%']:.1f}%")
            print(f"    Empate: {jogo['Prob_Empate_%']:.1f}%")
            print(f"    Vitoria {jogo['Time_Visitante']}: {jogo['Prob_Vit_Fora_%']:.1f}%")
            
            print(f"\n  Resultado Mais Provavel: {jogo['Resultado_Provavel']} "
                  f"(confianca: {jogo['Confianca_%']:.1f}%)")
            
            print(f"\n  Over/Under 2.5: Over {jogo['Prob_Over_2.5_%']:.1f}% | "
                  f"Under {jogo['Prob_Under_2.5_%']:.1f}%")
            
            print(f"  Ambos Marcam: Sim {jogo['Prob_BTTS_Sim_%']:.1f}% | "
                  f"Nao {jogo['Prob_BTTS_Nao_%']:.1f}%")
            
            print(f"\n  Placar Mais Provavel: {jogo['Placar_Mais_Provavel']} "
                  f"({jogo['Prob_Placar_%']:.2f}%)")
            
            print(f"  Top 3 Placares: {jogo['Top_3_Placares']}")
            print()
        
        print("-" * 80)
        print()


def salvar_predicoes(df_pred):
    """Salva predições em CSV"""
    if df_pred.empty:
        print("Nenhuma predição para salvar.")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'data/predicoes_proximas_partidas_{timestamp}.csv'
    
    df_pred.to_csv(filename, index=False, encoding='utf-8')
    
    print("=" * 80)
    print("PREDICOES SALVAS COM SUCESSO!")
    print("=" * 80)
    print(f"Arquivo: {filename}")
    print(f"Total de predicoes: {len(df_pred)}")
    
    return filename


def main():
    """Função principal"""
    print("\n")
    print("*" * 80)
    print("PREDICOES AUTOMATICAS - PROXIMAS PARTIDAS DA PREMIER LEAGUE")
    print("*" * 80)
    print("\n")
    
    # Passo 1: Buscar próximas partidas da API
    partidas = buscar_proximas_partidas(limit=20)
    
    if not partidas:
        print("\nNao ha partidas agendadas para prever.")
        print("\nDica: Isso pode acontecer entre temporadas ou em pausas internacionais.")
        print("Voce pode usar 'gerar_predicoes_lote.py' para simular partidas.")
        return
    
    print(f"\nPartidas encontradas para previsao:")
    for i, p in enumerate(partidas, 1):
        print(f"{i:2d}. {p['data_formatada']} {p['hora']} - "
              f"{p['time_casa']} vs {p['time_visitante']} (Rodada {p['rodada']})")
    
    print("\n" + "=" * 80)
    
    # Passo 2: Treinar modelo Dixon-Coles
    print("\nTREINANDO MODELO DIXON-COLES COM DADOS HISTORICOS")
    print("=" * 80)
    
    try:
        df = load_match_data()
        print(f"Partidas historicas carregadas: {len(df)}")
        
        model = DixonColesModel(xi=0.003)
        model.fit(df, time_decay=True)
        
        print("Modelo treinado com sucesso!")
        print(f"- Home advantage: {model.home_advantage:.3f}")
        print(f"- Rho: {model.rho:.3f}")
        print()
        
    except FileNotFoundError as e:
        print(f"\nERRO: {e}")
        print("\nExecute primeiro: python get_team_matches.py")
        return
    except Exception as e:
        print(f"\nERRO ao treinar modelo: {e}")
        return
    
    # Passo 3: Gerar predições
    df_pred = gerar_predicoes_proximas_partidas(partidas, model)
    
    if df_pred.empty:
        print("\nNenhuma predicao foi gerada.")
        print("Possivel causa: Times nao estao na base de dados de treino.")
        return
    
    # Passo 4: Exibir resumo
    exibir_resumo_predicoes(df_pred)
    
    # Passo 5: Salvar em CSV
    filename = salvar_predicoes(df_pred)
    
    # Estatísticas finais
    print("\n" + "=" * 80)
    print("ESTATISTICAS DAS PREDICOES")
    print("=" * 80)
    
    print(f"\nResultados mais provaveis:")
    resultados = df_pred['Resultado_Provavel'].value_counts()
    for resultado, count in resultados.items():
        print(f"  {resultado}: {count} jogos ({count/len(df_pred)*100:.1f}%)")
    
    print(f"\nJogos com Over 2.5 provavel (>60%):")
    over_provaveis = df_pred[df_pred['Prob_Over_2.5_%'] > 60]
    if len(over_provaveis) > 0:
        for _, jogo in over_provaveis.iterrows():
            print(f"  {jogo['Time_Casa']} vs {jogo['Time_Visitante']}: "
                  f"{jogo['Prob_Over_2.5_%']:.1f}%")
    else:
        print("  Nenhum jogo")
    
    print(f"\nJogos com BTTS provavel (>65%):")
    btts_provaveis = df_pred[df_pred['Prob_BTTS_Sim_%'] > 65]
    if len(btts_provaveis) > 0:
        for _, jogo in btts_provaveis.iterrows():
            print(f"  {jogo['Time_Casa']} vs {jogo['Time_Visitante']}: "
                  f"{jogo['Prob_BTTS_Sim_%']:.1f}%")
    else:
        print("  Nenhum jogo")
    
    print(f"\nJogos com resultado muito provavel (>70%):")
    alta_confianca = df_pred[df_pred['Confianca_%'] > 70]
    if len(alta_confianca) > 0:
        for _, jogo in alta_confianca.iterrows():
            print(f"  {jogo['Time_Casa']} vs {jogo['Time_Visitante']}: "
                  f"{jogo['Resultado_Provavel']} ({jogo['Confianca_%']:.1f}%)")
    else:
        print("  Nenhum jogo")
    
    print("\n" + "*" * 80)
    print("PREDICOES CONCLUIDAS COM SUCESSO!")
    print("*" * 80)
    print(f"\nArquivo salvo em: {filename}")
    print("Use estas predicoes com responsabilidade!")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuario.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()

