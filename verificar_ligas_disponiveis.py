"""
Script para verificar ligas disponíveis na API Football-Data.org
e identificar códigos corretos para La Liga e Serie A
"""

from api_client import FootballDataClient

def test_league_codes():
    """Testa códigos de ligas conhecidos"""
    client = FootballDataClient()
    
    # Códigos conhecidos da API Football-Data.org
    test_codes = {
        'La Liga (Espanha)': ['PD', 'LL', 'LALIGA'],  # PD = Primera Division
        'Serie A (Itália)': ['SA', 'SERIA', 'IT1'],
        'Bundesliga (Alemanha)': ['BL1', 'BL', 'BUNDESLIGA'],
        'Ligue 1 (França)': ['FL1', 'L1', 'LIGUE1'],
    }
    
    print("=" * 70)
    print("VERIFICANDO LIGAS DISPONÍVEIS NA API")
    print("=" * 70)
    print()
    
    results = {}
    
    for league_name, codes in test_codes.items():
        print(f"\nTestando {league_name}:")
        print("-" * 70)
        
        for code in codes:
            try:
                print(f"   Tentando codigo '{code}'...", end=' ')
                
                # Tenta buscar times da liga
                response = client.get_competition_teams(code)
                
                if 'teams' in response:
                    num_teams = len(response['teams'])
                    print(f"[OK] SUCESSO! ({num_teams} times)")
                    
                    # Tenta buscar info da competição
                    try:
                        matches_response = client.get_competition_matches(code, limit=1)
                        if 'competition' in matches_response:
                            comp_info = matches_response['competition']
                            comp_id = comp_info.get('id', 'N/A')
                            comp_name = comp_info.get('name', 'N/A')
                            print(f"      ID: {comp_id}")
                            print(f"      Nome: {comp_name}")
                            
                            results[league_name] = {
                                'code': code,
                                'id': comp_id,
                                'name': comp_name,
                                'teams': num_teams
                            }
                    except Exception as e:
                        print(f"      (Nao foi possivel obter ID: {e})")
                        results[league_name] = {
                            'code': code,
                            'id': 'N/A',
                            'name': league_name,
                            'teams': num_teams
                        }
                    
                    break  # Codigo encontrado, passa para proxima liga
                else:
                    print("[X] Sem dados de times")
                    
            except Exception as e:
                error_msg = str(e)
                if '404' in error_msg:
                    print("[X] Liga nao encontrada (404)")
                elif '403' in error_msg:
                    print("[!] Sem permissao (403)")
                else:
                    print(f"[X] Erro: {error_msg}")
    
    # Resumo final
    print("\n")
    print("=" * 70)
    print("RESUMO - LIGAS DISPONÍVEIS")
    print("=" * 70)
    
    if results:
        print("\n[OK] Ligas encontradas e prontas para uso:\n")
        for league_name, info in results.items():
            print(f"{league_name}:")
            print(f"   Código: {info['code']}")
            print(f"   ID: {info['id']}")
            print(f"   Nome oficial: {info['name']}")
            print(f"   Times: {info['teams']}")
            print()
        
        # Gera configuração para config.py
        print("=" * 70)
        print("CONFIGURAÇÃO PARA config.py")
        print("=" * 70)
        print("\nAdicione ao dicionário LEAGUES:\n")
        
        for league_name, info in results.items():
            # Define flag baseado no nome
            flags = {
                'La Liga (Espanha)': '🇪🇸',
                'Serie A (Itália)': '🇮🇹',
                'Bundesliga (Alemanha)': '🇩🇪',
                'Ligue 1 (França)': '🇫🇷'
            }
            flag = flags.get(league_name, '⚽')
            
            # Define country
            country = league_name.split('(')[1].rstrip(')') if '(' in league_name else 'Unknown'
            
            # Nome simplificado
            simple_name = league_name.split('(')[0].strip()
            
            print(f"    '{simple_name}': {{")
            print(f"        'code': '{info['code']}',")
            print(f"        'id': {info['id']},")
            print(f"        'name': '{info['name']}',")
            print(f"        'country': '{country}',")
            print(f"        'flag': '{flag}'")
            print(f"    }},")
    else:
        print("\n[X] Nenhuma liga foi encontrada com os codigos testados.")
        print("   Verifique sua API Key e tente novamente.")
    
    print("\n" + "=" * 70)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    try:
        results = test_league_codes()
        
        if results:
            print("\n[OK] Sucesso! Use as informacoes acima para atualizar config.py")
        else:
            print("\n[!] Nenhuma liga adicional foi encontrada.")
            print("   Possiveis motivos:")
            print("   - API Key sem permissao para essas ligas")
            print("   - Codigos das ligas mudaram")
            print("   - Problema de conexao")
            
    except ValueError as e:
        print(f"\n[X] ERRO: {e}")
        print("   Verifique se sua API Key esta configurada corretamente no arquivo .env")
    except Exception as e:
        print(f"\n[X] ERRO inesperado: {e}")
        import traceback
        traceback.print_exc()

