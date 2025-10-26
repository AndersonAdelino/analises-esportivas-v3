"""
Script para verificar quais casas de apostas estão disponíveis
"""
import json

# Carrega dados do último teste
try:
    with open('odds_api_test_20251025_220024.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print("CASAS DE APOSTAS DISPONÍVEIS NO BRASILEIRÃO")
    print("=" * 80)
    
    # Pega todas as casas únicas
    casas = set()
    
    for match in data:
        for bookmaker in match.get('bookmakers', []):
            casas.add(bookmaker['key'] + ' - ' + bookmaker['title'])
    
    # Ordena e mostra
    casas_lista = sorted(list(casas))
    
    print(f"\nTotal: {len(casas_lista)} casas diferentes\n")
    
    for idx, casa in enumerate(casas_lista, 1):
        print(f"{idx:2d}. {casa}")
    
    print("\n" + "=" * 80)
    print("CASAS BRASILEIRAS DISPONÍVEIS:")
    print("=" * 80)
    
    brasileiras = [c for c in casas_lista if any(termo in c.lower() for termo in ['betano', 'bet365', 'betfair', 'sportingbet'])]
    
    if brasileiras:
        for casa in brasileiras:
            print(f"  ✅ {casa}")
    else:
        print("  ⚠️ Nenhuma casa explicitamente brasileira")
        print("  💡 Mas Bet365 e Betano operam no Brasil!")
    
    print("\n" + "=" * 80)
    print("PROCURANDO ESTRELA BET...")
    print("=" * 80)
    
    estrela = [c for c in casas_lista if 'estrela' in c.lower()]
    
    if estrela:
        print("  ✅ ENCONTRADA!")
        for casa in estrela:
            print(f"     {casa}")
    else:
        print("  ❌ Estrela Bet não está disponível na API")
        print("\n  💡 ALTERNATIVAS QUE OPERAM NO BRASIL:")
        print("     - Bet365 (disponível)")
        print("     - Betano (disponível)")
        print("     - Betfair (disponível)")
        print("     - Pinnacle (disponível)")
    
except FileNotFoundError:
    print("❌ Arquivo de teste não encontrado")
    print("Execute primeiro: TESTAR_ODDS_API.bat")

