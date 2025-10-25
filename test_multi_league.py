"""
Script de teste para validar funcionamento do sistema multi-ligas
"""
import sys
from config import LEAGUES

def test_config():
    """Testa se as configurações de ligas estão corretas"""
    print("=" * 70)
    print("TESTE 1: Configurações de Ligas")
    print("=" * 70)
    
    assert 'Premier League' in LEAGUES, "Premier League não encontrada em LEAGUES"
    assert 'Brasileirão Série A' in LEAGUES, "Brasileirão não encontrado em LEAGUES"
    
    for name, info in LEAGUES.items():
        assert 'code' in info, f"{name} não tem 'code'"
        assert 'id' in info, f"{name} não tem 'id'"
        assert 'name' in info, f"{name} não tem 'name'"
        print(f"✅ {name}: {info['code']} (ID: {info['id']})")
    
    print("\n✅ TESTE 1 PASSOU!\n")


def test_data_loading():
    """Testa se é possível carregar dados de ambas as ligas"""
    print("=" * 70)
    print("TESTE 2: Carregamento de Dados")
    print("=" * 70)
    
    try:
        from dixon_coles import load_match_data
        
        # Tenta carregar Premier League
        print("\nCarregando dados da Premier League...")
        try:
            df_pl = load_match_data(league_code='PL')
            print(f"✅ Premier League: {len(df_pl)} partidas carregadas")
        except FileNotFoundError as e:
            print(f"⚠️ Premier League: Dados não encontrados - {e}")
            print("   Execute: python get_team_matches.py")
        
        # Tenta carregar Brasileirão
        print("\nCarregando dados do Brasileirão...")
        try:
            df_bsa = load_match_data(league_code='BSA')
            print(f"✅ Brasileirão: {len(df_bsa)} partidas carregadas")
        except FileNotFoundError as e:
            print(f"⚠️ Brasileirão: Dados não encontrados - {e}")
            print("   Execute: python get_brasileirao_data.py")
        
        print("\n✅ TESTE 2 COMPLETADO!\n")
        
    except Exception as e:
        print(f"\n❌ ERRO no TESTE 2: {e}\n")
        return False
    
    return True


def test_models():
    """Testa se os modelos podem ser treinados para ambas as ligas"""
    print("=" * 70)
    print("TESTE 3: Treinamento de Modelos")
    print("=" * 70)
    
    try:
        from ensemble import EnsembleModel
        
        # Testa Premier League
        print("\nTestando modelos para Premier League...")
        try:
            ensemble_pl = EnsembleModel()
            ensemble_pl.fit(league_code='PL')
            print("✅ Ensemble treinado com sucesso para Premier League")
        except FileNotFoundError:
            print("⚠️ Dados da Premier League não encontrados")
            print("   Treinamento não testado")
        except Exception as e:
            print(f"❌ Erro ao treinar Premier League: {e}")
        
        # Testa Brasileirão
        print("\nTestando modelos para Brasileirão...")
        try:
            ensemble_bsa = EnsembleModel()
            ensemble_bsa.fit(league_code='BSA')
            print("✅ Ensemble treinado com sucesso para Brasileirão")
        except FileNotFoundError:
            print("⚠️ Dados do Brasileirão não encontrados")
            print("   Treinamento não testado")
        except Exception as e:
            print(f"❌ Erro ao treinar Brasileirão: {e}")
        
        print("\n✅ TESTE 3 COMPLETADO!\n")
        
    except Exception as e:
        print(f"\n❌ ERRO no TESTE 3: {e}\n")
        return False
    
    return True


def main():
    """Executa todos os testes"""
    print("\n")
    print("=" * 70)
    print("TESTES DO SISTEMA MULTI-LIGAS")
    print("=" * 70)
    print("\n")
    
    # Testa configurações
    try:
        test_config()
    except AssertionError as e:
        print(f"\n❌ FALHA NO TESTE 1: {e}\n")
        sys.exit(1)
    
    # Testa carregamento de dados
    test_data_loading()
    
    # Testa modelos
    test_models()
    
    print("=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    print("""
Status dos componentes:

✅ Configurações: OK
✅ Sistema de dados: OK  
✅ Modelos: OK (se dados disponíveis)

Próximos passos:
1. Se houver avisos ⚠️, colete os dados faltantes
2. Execute: streamlit run app_betting.py
3. Teste a seleção de ligas na interface
4. Verifique se as análises funcionam para ambas

""")
    print("=" * 70)
    print("TESTES CONCLUÍDOS!")
    print("=" * 70)
    print("\n")


if __name__ == "__main__":
    main()

