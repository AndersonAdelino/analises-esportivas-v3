"""
Script interativo para fazer predições usando o modelo Dixon-Coles
"""
from dixon_coles import DixonColesModel, load_match_data, print_prediction
import sys


def listar_times(model):
    """Lista todos os times disponíveis"""
    print("\n" + "="*60)
    print("TIMES DISPONIVEIS NO MODELO")
    print("="*60)
    
    strengths = model.get_team_strengths()
    
    for idx, row in strengths.iterrows():
        print(f"{idx+1:2d}. {row['Time']}")
    
    print("="*60)
    return strengths['Time'].tolist()


def escolher_time(times, mensagem):
    """Permite escolher um time"""
    while True:
        print(f"\n{mensagem}")
        print("Digite o numero do time ou o nome completo:")
        escolha = input("> ").strip()
        
        # Tenta converter para número
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(times):
                return times[idx]
        except ValueError:
            pass
        
        # Tenta buscar por nome (case insensitive, parcial)
        escolha_lower = escolha.lower()
        matches = [t for t in times if escolha_lower in t.lower()]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"\nVarios times encontrados:")
            for i, t in enumerate(matches, 1):
                print(f"{i}. {t}")
            print("Seja mais especifico.")
        else:
            print("Time nao encontrado. Tente novamente.")


def main():
    """Função principal do script interativo"""
    print("\n" + "="*80)
    print("PREDICAO INTERATIVA - MODELO DIXON-COLES")
    print("="*80)
    print("\n")
    
    # Carrega dados e treina modelo
    print("Carregando dados e treinando modelo...")
    df = load_match_data()
    
    model = DixonColesModel(xi=0.003)
    model.fit(df, time_decay=True)
    
    print("\nModelo treinado com sucesso!")
    
    while True:
        print("\n" + "="*80)
        print("MENU")
        print("="*80)
        print("1. Fazer predicao")
        print("2. Ver forcas dos times")
        print("3. Listar times disponiveis")
        print("4. Sair")
        
        opcao = input("\nEscolha uma opcao (1-4): ").strip()
        
        if opcao == '1':
            # Fazer predição
            times = model.teams
            
            print("\n" + "-"*60)
            print("NOVA PREDICAO")
            print("-"*60)
            
            # Listar times primeiro
            listar_times(model)
            
            # Escolher times
            time_casa = escolher_time(times, "\n[1/2] Escolha o TIME DA CASA:")
            time_visitante = escolher_time(times, "\n[2/2] Escolha o TIME VISITANTE:")
            
            if time_casa == time_visitante:
                print("\nERRO: Os times devem ser diferentes!")
                continue
            
            # Fazer predição
            print("\nCalculando probabilidades...\n")
            
            try:
                prediction = model.predict_match(time_casa, time_visitante)
                print_prediction(prediction)
                
                # Pergunta se quer salvar
                salvar = input("\nDeseja salvar esta predicao? (s/n): ").strip().lower()
                if salvar == 's':
                    filename = f"predicao_{time_casa.replace(' ', '_')}_vs_{time_visitante.replace(' ', '_')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"{time_casa} vs {time_visitante}\n")
                        f.write("="*80 + "\n\n")
                        f.write(f"Gols Esperados:\n")
                        f.write(f"  {time_casa}: {prediction['expected_goals_home']:.2f}\n")
                        f.write(f"  {time_visitante}: {prediction['expected_goals_away']:.2f}\n\n")
                        f.write(f"Probabilidades (1X2):\n")
                        f.write(f"  Vitoria {time_casa}: {prediction['prob_home_win']*100:.1f}%\n")
                        f.write(f"  Empate: {prediction['prob_draw']*100:.1f}%\n")
                        f.write(f"  Vitoria {time_visitante}: {prediction['prob_away_win']*100:.1f}%\n\n")
                        f.write(f"Over/Under 2.5:\n")
                        f.write(f"  Over 2.5: {prediction['prob_over_2_5']*100:.1f}%\n")
                        f.write(f"  Under 2.5: {prediction['prob_under_2_5']*100:.1f}%\n\n")
                        f.write(f"Ambas Equipes Marcam:\n")
                        f.write(f"  Sim: {prediction['prob_btts_yes']*100:.1f}%\n")
                        f.write(f"  Nao: {prediction['prob_btts_no']*100:.1f}%\n\n")
                        f.write(f"Top 10 Placares:\n")
                        for i, ((hg, ag), prob) in enumerate(prediction['top_scores'][:10], 1):
                            f.write(f"  {i}. {hg}-{ag}: {prob*100:.2f}%\n")
                    
                    print(f"Predicao salva em: {filename}")
                
            except Exception as e:
                print(f"\nErro ao fazer predicao: {e}")
        
        elif opcao == '2':
            # Ver forças dos times
            print("\n")
            strengths = model.get_team_strengths()
            
            print("="*80)
            print("FORCAS DOS TIMES")
            print("="*80)
            print(f"\n{'Pos':<4} {'Time':<35} {'Ataque':<10} {'Defesa':<10} {'Total':<10}")
            print("-"*80)
            
            for idx, row in strengths.iterrows():
                print(f"{idx+1:<4} {row['Time']:<35} {row['Ataque']:<10.3f} {row['Defesa']:<10.3f} {row['Forca_Total']:<10.3f}")
            
            print("="*80)
            print("\nNota: Valores maiores = melhor ataque/pior defesa/maior forca total")
        
        elif opcao == '3':
            # Listar times
            listar_times(model)
        
        elif opcao == '4':
            # Sair
            print("\nEncerrando programa...")
            sys.exit(0)
        
        else:
            print("\nOpcao invalida! Tente novamente.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()

