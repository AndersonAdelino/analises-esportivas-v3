"""
TESTE COMPLETO DE VALIDAÇÃO
Garante que não há probabilidades negativas em nenhum cenário
Testa: Brasileirão + Premier League + Casos extremos
"""

import sys
from ensemble import EnsembleModel
import traceback

class TestValidator:
    """Validador de probabilidades"""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
    
    def validate_probability(self, value, name, context):
        """Valida se uma probabilidade está no intervalo [0, 1]"""
        self.total_tests += 1
        
        if value is None:
            self.errors.append(f"  {context} - {name}: None (não deveria ser None)")
            self.failed_tests += 1
            return False
        
        if value < 0:
            self.errors.append(f"  {context} - {name}: {value*100:.2f}% (NEGATIVO!)")
            self.failed_tests += 1
            return False
        
        if value > 1:
            self.errors.append(f"  {context} - {name}: {value*100:.2f}% (MAIOR QUE 100%!)")
            self.failed_tests += 1
            return False
        
        self.passed_tests += 1
        return True
    
    def validate_prediction(self, prediction, context):
        """Valida uma predição completa"""
        ens = prediction.get('ensemble', {})
        
        # Valida probabilidades 1X2
        ok = True
        ok &= self.validate_probability(ens.get('prob_casa'), 'Casa', context)
        ok &= self.validate_probability(ens.get('prob_empate'), 'Empate', context)
        ok &= self.validate_probability(ens.get('prob_fora'), 'Fora', context)
        
        # Valida outras probabilidades
        ok &= self.validate_probability(ens.get('prob_over_2_5'), 'Over 2.5', context)
        ok &= self.validate_probability(ens.get('prob_btts'), 'BTTS', context)
        
        # Valida soma 1X2 = 1
        if all(ens.get(k) is not None for k in ['prob_casa', 'prob_empate', 'prob_fora']):
            total = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
            if abs(total - 1.0) > 0.01:
                self.errors.append(f"  {context} - Soma 1X2: {total:.4f} (deveria ser 1.0)")
                self.failed_tests += 1
                ok = False
            else:
                self.passed_tests += 1
        
        # Valida predições individuais
        for model_name, pred in prediction.get('individual', {}).items():
            if pred:
                ctx = f"{context} [{model_name}]"
                ok &= self.validate_probability(pred.get('prob_casa'), 'Casa', ctx)
                ok &= self.validate_probability(pred.get('prob_empate'), 'Empate', ctx)
                ok &= self.validate_probability(pred.get('prob_fora'), 'Fora', ctx)
        
        return ok
    
    def print_report(self):
        """Imprime relatório final"""
        print("\n" + "="*80)
        print("RELATORIO FINAL DE VALIDACAO")
        print("="*80)
        print(f"\nTotal de validações: {self.total_tests}")
        print(f"Passou: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"Falhou: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        
        if self.errors:
            print("\n" + "="*80)
            print("ERROS DETECTADOS:")
            print("="*80)
            for error in self.errors:
                print(error)
            print("\n❌ TESTE FALHOU - Foram encontrados problemas!")
            return False
        else:
            print("\n✅ TODOS OS TESTES PASSARAM!")
            print("Sistema está funcionando corretamente.")
            return True


def test_league(league_code, league_name, test_matches, validator):
    """Testa uma liga específica"""
    print("\n" + "="*80)
    print(f"TESTANDO: {league_name}")
    print("="*80)
    
    try:
        # Treina ensemble
        print(f"\n[1] Treinando ensemble para {league_name}...")
        ensemble = EnsembleModel()
        ensemble.fit(league_code=league_code)
        print(f"✓ Ensemble treinado")
        
        # Testa cada partida
        print(f"\n[2] Testando {len(test_matches)} partidas...")
        
        for i, (home, away) in enumerate(test_matches, 1):
            try:
                print(f"\n  [{i}/{len(test_matches)}] {home} vs {away}")
                
                prediction = ensemble.predict_match(home, away)
                ens = prediction['ensemble']
                
                # Mostra resultado
                print(f"    Casa: {ens['prob_casa']*100:6.2f}% | Empate: {ens['prob_empate']*100:6.2f}% | Fora: {ens['prob_fora']*100:6.2f}%")
                
                # Valida
                context = f"{league_name} - {home} vs {away}"
                validator.validate_prediction(prediction, context)
                
            except Exception as e:
                print(f"    ❌ ERRO: {e}")
                validator.errors.append(f"  {league_name} - {home} vs {away}: {str(e)}")
                validator.failed_tests += 1
        
        print(f"\n✓ Testes do {league_name} concluídos")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO ao testar {league_name}: {e}")
        traceback.print_exc()
        validator.errors.append(f"  {league_name}: {str(e)}")
        validator.failed_tests += 1
        return False


def main():
    """Executa todos os testes"""
    print("="*80)
    print("TESTE COMPLETO DE VALIDACAO")
    print("Verifica probabilidades em Brasileirão e Premier League")
    print("="*80)
    
    validator = TestValidator()
    
    # =========================================================================
    # BRASILEIRÃO
    # =========================================================================
    brasileirao_matches = [
        # Times fortes vs fortes
        ('Botafogo FR', 'Palmeiras'),
        ('Flamengo', 'São Paulo FC'),
        ('Atlético Mineiro', 'Grêmio'),
        
        # Times fortes vs médios
        ('Botafogo FR', 'Santos FC'),
        ('Flamengo', 'Internacional'),
        
        # Times médios vs fracos
        ('Bahia', 'Cuiabá'),
        ('Vasco da Gama', 'Cruzeiro'),
        
        # Times fracos vs fortes (caso extremo)
        ('Athletico Paranaense', 'Palmeiras'),
        ('Cuiabá', 'Flamengo'),
        
        # Clássicos
        ('Flamengo', 'Fluminense'),
        ('Corinthians', 'Palmeiras'),
    ]
    
    test_league('BSA', 'Brasileirão Série A', brasileirao_matches, validator)
    
    # =========================================================================
    # PREMIER LEAGUE
    # =========================================================================
    premier_league_matches = [
        # Times fortes vs fortes
        ('Manchester City FC', 'Arsenal FC'),
        ('Liverpool FC', 'Chelsea FC'),
        ('Tottenham Hotspur FC', 'Manchester United FC'),
        
        # Times fortes vs médios
        ('Arsenal FC', 'Newcastle United FC'),
        ('Liverpool FC', 'Aston Villa FC'),
        
        # Times médios vs fracos
        ('West Ham United FC', 'Everton FC'),
        ('Brighton & Hove Albion FC', 'Fulham FC'),
        
        # Times fracos vs fortes (caso extremo)
        ('Sheffield United FC', 'Manchester City FC'),
        ('Luton Town FC', 'Liverpool FC'),
        
        # Clássicos
        ('Manchester United FC', 'Liverpool FC'),
        ('Arsenal FC', 'Tottenham Hotspur FC'),
    ]
    
    test_league('PL', 'Premier League', premier_league_matches, validator)
    
    # =========================================================================
    # RELATÓRIO FINAL
    # =========================================================================
    success = validator.print_report()
    
    if success:
        print("\n" + "="*80)
        print("CONCLUSÃO")
        print("="*80)
        print("\n✅ SISTEMA VALIDADO COM SUCESSO!")
        print("\nO sistema foi testado com:")
        print(f"  • {len(brasileirao_matches)} partidas do Brasileirão")
        print(f"  • {len(premier_league_matches)} partidas da Premier League")
        print(f"  • Total: {len(brasileirao_matches) + len(premier_league_matches)} partidas")
        print(f"  • Total: {validator.total_tests} validações de probabilidades")
        print("\nTodas as probabilidades estão corretas!")
        print("Não há risco de valores negativos ou inválidos.")
        print("\n🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
    else:
        print("\n" + "="*80)
        print("CONCLUSÃO")
        print("="*80)
        print("\n❌ SISTEMA FALHOU NA VALIDAÇÃO")
        print("\nForam detectados problemas que precisam ser corrigidos.")
        print("Revise os erros acima e faça as correções necessárias.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {e}")
        traceback.print_exc()
        sys.exit(1)

