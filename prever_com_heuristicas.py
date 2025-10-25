"""
Script Interativo para Análise com Heurísticas

Permite fazer análises heurísticas de partidas de forma interativa
"""

from heuristicas import HeuristicasModel, print_prediction


def listar_times(model):
    """Lista times disponíveis"""
    print("\nTimes disponíveis:")
    print("-" * 60)
    for idx, time in enumerate(model.teams, 1):
        print(f"{idx:2d}. {time}")
    print("-" * 60)


def main():
    print("\n")
    print("=" * 80)
    print("ANALISE HEURISTICA INTERATIVA")
    print("=" * 80)
    print("\n")
    
    # Carrega dados
    model = HeuristicasModel()
    model.load_data()
    
    while True:
        print("\n")
        print("=" * 80)
        print("NOVA ANALISE")
        print("=" * 80)
        
        listar_times(model)
        
        print("\nEscolha os times (ou 'sair' para encerrar):")
        
        # Time da casa
        home_input = input("\nTime da CASA (numero ou nome): ").strip()
        if home_input.lower() == 'sair':
            break
        
        try:
            home_idx = int(home_input) - 1
            if 0 <= home_idx < len(model.teams):
                home_team = model.teams[home_idx]
            else:
                print("Numero invalido!")
                continue
        except ValueError:
            # Busca por nome
            matches = [t for t in model.teams if home_input.lower() in t.lower()]
            if len(matches) == 1:
                home_team = matches[0]
            elif len(matches) > 1:
                print(f"\nVarios times encontrados: {matches}")
                print("Seja mais especifico!")
                continue
            else:
                print("Time nao encontrado!")
                continue
        
        # Time visitante
        away_input = input("Time VISITANTE (numero ou nome): ").strip()
        if away_input.lower() == 'sair':
            break
        
        try:
            away_idx = int(away_input) - 1
            if 0 <= away_idx < len(model.teams):
                away_team = model.teams[away_idx]
            else:
                print("Numero invalido!")
                continue
        except ValueError:
            # Busca por nome
            matches = [t for t in model.teams if away_input.lower() in t.lower()]
            if len(matches) == 1:
                away_team = matches[0]
            elif len(matches) > 1:
                print(f"\nVarios times encontrados: {matches}")
                print("Seja mais especifico!")
                continue
            else:
                print("Time nao encontrado!")
                continue
        
        # Validação
        if home_team == away_team:
            print("\nErro: Times devem ser diferentes!")
            continue
        
        # Faz análise
        try:
            pred = model.predict_match(home_team, away_team)
            print_prediction(pred)
            
            # Análise detalhada adicional
            print("\n" + "=" * 80)
            print("DETALHES ADICIONAIS")
            print("=" * 80)
            
            if pred['forma_casa']:
                print(f"\n{home_team} - Estatisticas Recentes:")
                fc = pred['forma_casa']
                print(f"  Gols marcados: {fc['gols_marcados']} ({fc['media_gols_marcados']:.2f}/jogo)")
                print(f"  Gols sofridos: {fc['gols_sofridos']} ({fc['media_gols_sofridos']:.2f}/jogo)")
                print(f"  Saldo: {fc['saldo']:+d}")
                print(f"  Invicto: {'Sim' if fc['invicto'] else 'Nao'}")
            
            if pred['forma_fora']:
                print(f"\n{away_team} - Estatisticas Recentes:")
                ff = pred['forma_fora']
                print(f"  Gols marcados: {ff['gols_marcados']} ({ff['media_gols_marcados']:.2f}/jogo)")
                print(f"  Gols sofridos: {ff['gols_sofridos']} ({ff['media_gols_sofridos']:.2f}/jogo)")
                print(f"  Saldo: {ff['saldo']:+d}")
                print(f"  Invicto: {'Sim' if ff['invicto'] else 'Nao'}")
            
            if pred['sequencias_casa']:
                sc = pred['sequencias_casa']
                print(f"\n{home_team} - Sequencias:")
                print(f"  Atual: {sc['sequencia_desc']}")
                print(f"  Max vitorias consecutivas: {sc['max_vitorias_consecutivas']}")
                print(f"  Jogos sem vencer: {sc['jogos_sem_vencer']}")
            
            if pred['sequencias_fora']:
                sf = pred['sequencias_fora']
                print(f"\n{away_team} - Sequencias:")
                print(f"  Atual: {sf['sequencia_desc']}")
                print(f"  Max vitorias consecutivas: {sf['max_vitorias_consecutivas']}")
                print(f"  Jogos sem vencer: {sf['jogos_sem_vencer']}")
            
            print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"\nErro ao fazer analise: {e}")
            import traceback
            traceback.print_exc()
        
        # Continuar?
        continuar = input("\n\nFazer outra analise? (s/n): ").strip().lower()
        if continuar != 's':
            break
    
    print("\n")
    print("=" * 80)
    print("ANALISES ENCERRADAS")
    print("=" * 80)
    print("\n")


if __name__ == "__main__":
    main()

