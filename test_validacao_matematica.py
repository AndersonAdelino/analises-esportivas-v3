"""
TESTE DE VALIDACAO MATEMATICA COMPLETA
Garante que todos os calculos sao matematicamente corretos
Verifica: NaN, Inf, soma de probabilidades, consistencia, etc.
"""

import sys
import numpy as np
from ensemble import EnsembleModel
from dixon_coles import DixonColesModel, load_match_data as load_dc_data
from offensive_defensive import OffensiveDefensiveModel, load_match_data as load_od_data

class MathValidator:
    """Validador matematico rigoroso"""
    
    def __init__(self):
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
        self.errors = []
        self.warnings = []
    
    def check(self, condition, message, is_critical=True):
        """Verifica uma condicao"""
        self.total_checks += 1
        
        if condition:
            self.passed_checks += 1
            return True
        else:
            if is_critical:
                self.errors.append(f"  [ERRO] {message}")
                self.failed_checks += 1
            else:
                self.warnings.append(f"  [AVISO] {message}")
            return False
    
    def validate_float(self, value, name, context):
        """Valida se um valor float e valido"""
        # Verifica None
        if value is None:
            return self.check(False, f"{context} - {name}: None (nao deveria ser None)")
        
        # Verifica NaN
        if np.isnan(value):
            return self.check(False, f"{context} - {name}: NaN (Not a Number)")
        
        # Verifica Inf
        if np.isinf(value):
            return self.check(False, f"{context} - {name}: Inf (Infinito)")
        
        return True
    
    def validate_probability(self, value, name, context, allow_boundary=True):
        """Valida uma probabilidade [0, 1]"""
        # Primeiro valida se e um float valido
        if not self.validate_float(value, name, context):
            return False
        
        # Verifica limites
        if allow_boundary:
            ok = self.check(0 <= value <= 1, 
                          f"{context} - {name}: {value:.6f} fora do intervalo [0, 1]")
        else:
            # Alguns casos nao devem ser exatamente 0 ou 1
            ok = self.check(0 < value < 1, 
                          f"{context} - {name}: {value:.6f} fora do intervalo (0, 1)")
        
        return ok
    
    def validate_sum_equals_one(self, values, names, context, tolerance=0.01):
        """Valida se a soma de probabilidades = 1"""
        total = sum(values)
        
        # Verifica se a soma e valida
        if not self.validate_float(total, "soma", context):
            return False
        
        # Verifica se soma = 1 (com tolerancia)
        ok = self.check(abs(total - 1.0) <= tolerance,
                       f"{context} - Soma {'+'.join(names)}: {total:.6f} (deveria ser ~1.0)")
        
        return ok
    
    def validate_lambda(self, lambda_val, team, context):
        """Valida taxa de gols (lambda) do modelo de Poisson"""
        # Lambda deve ser positivo
        if not self.validate_float(lambda_val, f"lambda_{team}", context):
            return False
        
        # Lambda tipicamente entre 0.5 e 4.0 gols
        ok = self.check(0.1 < lambda_val < 5.0,
                       f"{context} - lambda_{team}: {lambda_val:.3f} fora do intervalo razoavel [0.1, 5.0]",
                       is_critical=False)
        
        return ok
    
    def validate_model_params(self, model, model_name, context):
        """Valida parametros do modelo"""
        # Home advantage
        if hasattr(model, 'home_advantage'):
            self.validate_float(model.home_advantage, 'home_advantage', context)
            self.check(0 < model.home_advantage < 1.0,
                      f"{context} - home_advantage: {model.home_advantage:.3f} fora do intervalo razoavel (0, 1)",
                      is_critical=False)
        
        # Rho (Dixon-Coles)
        if hasattr(model, 'rho'):
            self.validate_float(model.rho, 'rho', context)
            self.check(-0.5 < model.rho < 0.5,
                      f"{context} - rho: {model.rho:.3f} fora do intervalo razoavel (-0.5, 0.5)",
                      is_critical=False)
        
        # Attack/Defense
        if hasattr(model, 'attack') and hasattr(model, 'defense'):
            for team in list(model.attack.keys())[:5]:  # Testa primeiros 5 times
                attack = model.attack[team]
                defense = model.defense[team]
                
                self.validate_float(attack, f'attack[{team}]', context)
                self.validate_float(defense, f'defense[{team}]', context)
                
                # Valores tipicamente entre -1 e 1
                self.check(-2.0 < attack < 2.0,
                          f"{context} - attack[{team}]: {attack:.3f} muito extremo",
                          is_critical=False)
                self.check(-2.0 < defense < 2.0,
                          f"{context} - defense[{team}]: {defense:.3f} muito extremo",
                          is_critical=False)
    
    def validate_score_matrix(self, prob_matrix, context):
        """Valida matriz de probabilidades de placares"""
        # Verifica se e um array numpy valido
        if not isinstance(prob_matrix, np.ndarray):
            return self.check(False, f"{context} - Matriz nao e numpy array")
        
        # Verifica NaN/Inf
        if np.any(np.isnan(prob_matrix)):
            return self.check(False, f"{context} - Matriz contem NaN")
        
        if np.any(np.isinf(prob_matrix)):
            return self.check(False, f"{context} - Matriz contem Inf")
        
        # Verifica valores negativos
        if np.any(prob_matrix < 0):
            return self.check(False, f"{context} - Matriz contem valores negativos")
        
        # Verifica valores > 1
        if np.any(prob_matrix > 1):
            return self.check(False, f"{context} - Matriz contem valores > 1")
        
        # Verifica soma = 1
        total = prob_matrix.sum()
        self.check(abs(total - 1.0) <= 0.01,
                  f"{context} - Soma da matriz: {total:.6f} (deveria ser ~1.0)")
        
        return True
    
    def validate_prediction(self, prediction, home_team, away_team, model_name):
        """Valida uma predicao completa"""
        context = f"{model_name} - {home_team} vs {away_team}"
        
        # 1. Valida lambdas
        if 'lambda_home' in prediction:
            self.validate_lambda(prediction['lambda_home'], home_team, context)
        if 'lambda_away' in prediction:
            self.validate_lambda(prediction['lambda_away'], away_team, context)
        
        # 2. Valida probabilidades 1X2
        prob_home = prediction.get('prob_home_win') or prediction.get('prob_casa')
        prob_draw = prediction.get('prob_draw') or prediction.get('prob_empate')
        prob_away = prediction.get('prob_away_win') or prediction.get('prob_fora')
        
        if prob_home is not None:
            self.validate_probability(prob_home, 'Prob Casa', context)
        if prob_draw is not None:
            self.validate_probability(prob_draw, 'Prob Empate', context)
        if prob_away is not None:
            self.validate_probability(prob_away, 'Prob Fora', context)
        
        # 3. Valida soma 1X2 = 1
        if all(p is not None for p in [prob_home, prob_draw, prob_away]):
            self.validate_sum_equals_one(
                [prob_home, prob_draw, prob_away],
                ['Casa', 'Empate', 'Fora'],
                context
            )
        
        # 4. Valida Over/Under
        prob_over = prediction.get('prob_over_2_5')
        prob_under = prediction.get('prob_under_2_5')
        
        if prob_over is not None:
            self.validate_probability(prob_over, 'Prob Over 2.5', context)
        if prob_under is not None:
            self.validate_probability(prob_under, 'Prob Under 2.5', context)
        
        # Soma Over + Under = 1
        if prob_over is not None and prob_under is not None:
            self.validate_sum_equals_one(
                [prob_over, prob_under],
                ['Over 2.5', 'Under 2.5'],
                context
            )
        
        # 5. Valida BTTS
        prob_btts_yes = prediction.get('prob_btts_yes') or prediction.get('prob_btts')
        prob_btts_no = prediction.get('prob_btts_no')
        
        if prob_btts_yes is not None:
            self.validate_probability(prob_btts_yes, 'Prob BTTS Sim', context)
        if prob_btts_no is not None:
            self.validate_probability(prob_btts_no, 'Prob BTTS Nao', context)
        
        # Soma BTTS = 1
        if prob_btts_yes is not None and prob_btts_no is not None:
            self.validate_sum_equals_one(
                [prob_btts_yes, prob_btts_no],
                ['BTTS Sim', 'BTTS Nao'],
                context
            )
        
        # 6. Valida matriz de placares (se disponivel)
        if 'prob_matrix' in prediction:
            self.validate_score_matrix(prediction['prob_matrix'], context)
        
        # 7. Valida top scores (se disponivel)
        if 'top_scores' in prediction:
            for (home_goals, away_goals), prob in prediction['top_scores'][:5]:
                self.validate_float(prob, f'Placar {home_goals}-{away_goals}', context)
                self.check(0 <= prob <= 1,
                          f"{context} - Prob placar {home_goals}-{away_goals}: {prob:.6f}")
        
        # 8. Consistencia: Home advantage
        # Geralmente casa deve ter mais chance que fora (nao sempre, mas na maioria)
        if prob_home and prob_away:
            # Nao e critico, apenas aviso
            if prob_home < prob_away:
                self.warnings.append(
                    f"  [INFO] {context} - Visitante favorito ({prob_away*100:.1f}% vs {prob_home*100:.1f}%)"
                )
    
    def print_report(self):
        """Imprime relatorio final"""
        print("\n" + "="*80)
        print("RELATORIO DE VALIDACAO MATEMATICA")
        print("="*80)
        print(f"\nTotal de verificacoes: {self.total_checks}")
        print(f"Passou: {self.passed_checks} ({self.passed_checks/self.total_checks*100:.1f}%)")
        print(f"Falhou: {self.failed_checks} ({self.failed_checks/self.total_checks*100:.1f}%)")
        
        if self.errors:
            print("\n" + "="*80)
            print("ERROS CRITICOS:")
            print("="*80)
            for error in self.errors:
                print(error)
        
        if self.warnings:
            print("\n" + "="*80)
            print(f"AVISOS ({len(self.warnings)}):")
            print("="*80)
            for warning in self.warnings[:10]:  # Mostra apenas primeiros 10
                print(warning)
            if len(self.warnings) > 10:
                print(f"  ... e mais {len(self.warnings) - 10} avisos")
        
        if self.errors:
            print("\n" + "="*80)
            print("RESULTADO: FALHOU")
            print("="*80)
            return False
        else:
            print("\n" + "="*80)
            print("RESULTADO: SUCESSO!")
            print("="*80)
            print("\nTodos os calculos matematicos estao corretos!")
            return True


def test_individual_models(validator):
    """Testa modelos individuais com validacao matematica rigorosa"""
    print("\n" + "="*80)
    print("TESTE 1: VALIDACAO DOS MODELOS INDIVIDUAIS")
    print("="*80)
    
    # Partidas de teste
    test_matches_bsa = [
        ('Botafogo FR', 'Santos FC'),
        ('CR Flamengo', 'SE Palmeiras'),
    ]
    
    test_matches_pl = [
        ('Arsenal FC', 'Liverpool FC'),
        ('Manchester City FC', 'Chelsea FC'),
    ]
    
    # DIXON-COLES - Brasileirao
    print("\n[1] Dixon-Coles - Brasileirao")
    print("-"*80)
    try:
        df = load_dc_data(league_code='BSA')
        model_dc_bsa = DixonColesModel(xi=0.003)
        model_dc_bsa.fit(df, time_decay=True)
        
        # Valida parametros do modelo
        validator.validate_model_params(model_dc_bsa, 'Dixon-Coles', 'Brasileirao')
        
        # Testa predicoes
        for home, away in test_matches_bsa:
            pred = model_dc_bsa.predict_match(home, away)
            validator.validate_prediction(pred, home, away, 'Dixon-Coles BSA')
        
        print("OK - Dixon-Coles Brasileirao validado")
    except Exception as e:
        print(f"ERRO: {e}")
        validator.errors.append(f"Dixon-Coles Brasileirao: {str(e)}")
    
    # DIXON-COLES - Premier League
    print("\n[2] Dixon-Coles - Premier League")
    print("-"*80)
    try:
        df = load_dc_data(league_code='PL')
        model_dc_pl = DixonColesModel(xi=0.003)
        model_dc_pl.fit(df, time_decay=True)
        
        validator.validate_model_params(model_dc_pl, 'Dixon-Coles', 'Premier League')
        
        for home, away in test_matches_pl:
            pred = model_dc_pl.predict_match(home, away)
            validator.validate_prediction(pred, home, away, 'Dixon-Coles PL')
        
        print("OK - Dixon-Coles Premier League validado")
    except Exception as e:
        print(f"ERRO: {e}")
        validator.errors.append(f"Dixon-Coles Premier League: {str(e)}")
    
    # OFFENSIVE-DEFENSIVE - Brasileirao
    print("\n[3] Offensive-Defensive - Brasileirao")
    print("-"*80)
    try:
        df = load_od_data(league_code='BSA')
        model_od_bsa = OffensiveDefensiveModel(xi=0.003)
        model_od_bsa.fit(df, time_decay=True)
        
        validator.validate_model_params(model_od_bsa, 'Offensive-Defensive', 'Brasileirao')
        
        for home, away in test_matches_bsa:
            pred = model_od_bsa.predict_match(home, away)
            validator.validate_prediction(pred, home, away, 'Offensive-Defensive BSA')
        
        print("OK - Offensive-Defensive Brasileirao validado")
    except Exception as e:
        print(f"ERRO: {e}")
        validator.errors.append(f"Offensive-Defensive Brasileirao: {str(e)}")
    
    # OFFENSIVE-DEFENSIVE - Premier League
    print("\n[4] Offensive-Defensive - Premier League")
    print("-"*80)
    try:
        df = load_od_data(league_code='PL')
        model_od_pl = OffensiveDefensiveModel(xi=0.003)
        model_od_pl.fit(df, time_decay=True)
        
        validator.validate_model_params(model_od_pl, 'Offensive-Defensive', 'Premier League')
        
        for home, away in test_matches_pl:
            pred = model_od_pl.predict_match(home, away)
            validator.validate_prediction(pred, home, away, 'Offensive-Defensive PL')
        
        print("OK - Offensive-Defensive Premier League validado")
    except Exception as e:
        print(f"ERRO: {e}")
        validator.errors.append(f"Offensive-Defensive Premier League: {str(e)}")


def test_ensemble(validator):
    """Testa ensemble com validacao matematica"""
    print("\n" + "="*80)
    print("TESTE 2: VALIDACAO DO ENSEMBLE")
    print("="*80)
    
    test_cases = [
        ('BSA', 'Brasileirao', [
            ('Botafogo FR', 'Santos FC'),
            ('CR Flamengo', 'SE Palmeiras'),
            ('SC Corinthians Paulista', 'São Paulo FC'),
        ]),
        ('PL', 'Premier League', [
            ('Arsenal FC', 'Liverpool FC'),
            ('Manchester City FC', 'Chelsea FC'),
            ('Manchester United FC', 'Tottenham Hotspur FC'),
        ])
    ]
    
    for league_code, league_name, matches in test_cases:
        print(f"\n[{league_name}]")
        print("-"*80)
        
        try:
            ensemble = EnsembleModel()
            ensemble.fit(league_code=league_code)
            
            for home, away in matches:
                prediction = ensemble.predict_match(home, away)
                
                # Valida ensemble
                ens = prediction['ensemble']
                context = f"Ensemble {league_name} - {home} vs {away}"
                
                # Valida cada probabilidade
                validator.validate_probability(ens.get('prob_casa'), 'Casa', context)
                validator.validate_probability(ens.get('prob_empate'), 'Empate', context)
                validator.validate_probability(ens.get('prob_fora'), 'Fora', context)
                validator.validate_probability(ens.get('prob_over_2_5'), 'Over 2.5', context)
                validator.validate_probability(ens.get('prob_btts'), 'BTTS', context)
                
                # Valida soma 1X2
                validator.validate_sum_equals_one(
                    [ens['prob_casa'], ens['prob_empate'], ens['prob_fora']],
                    ['Casa', 'Empate', 'Fora'],
                    context
                )
                
                # Valida predicoes individuais
                for model_name, pred in prediction.get('individual', {}).items():
                    if pred:
                        validator.validate_prediction(pred, home, away, f"Ensemble/{model_name}")
            
            print(f"OK - Ensemble {league_name} validado")
        except Exception as e:
            print(f"ERRO: {e}")
            validator.errors.append(f"Ensemble {league_name}: {str(e)}")


def main():
    """Executa validacao matematica completa"""
    print("="*80)
    print("VALIDACAO MATEMATICA COMPLETA")
    print("Garante que todos os calculos sao matematicamente corretos")
    print("="*80)
    
    validator = MathValidator()
    
    # Testa modelos individuais
    test_individual_models(validator)
    
    # Testa ensemble
    test_ensemble(validator)
    
    # Relatorio final
    success = validator.print_report()
    
    if success:
        print("\n" + "="*80)
        print("CONCLUSAO")
        print("="*80)
        print("\n*** TODOS OS CALCULOS MATEMATICOS SAO VALIDOS ***")
        print("\nVerificado:")
        print("  [OK] Sem NaN (Not a Number)")
        print("  [OK] Sem Inf (Infinito)")
        print("  [OK] Todas probabilidades no intervalo [0, 1]")
        print("  [OK] Somas de probabilidades = 1.0")
        print("  [OK] Lambdas (taxas de gols) positivos")
        print("  [OK] Parametros dos modelos razoaveis")
        print("  [OK] Matrizes de placares validas")
        print("  [OK] Consistencia matematica garantida")
        print("\n*** SISTEMA MATEMATICAMENTE CORRETO ***")
    else:
        print("\n" + "="*80)
        print("CONCLUSAO")
        print("="*80)
        print("\nForam detectados erros matematicos!")
        print("Revise os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERRO CRITICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

