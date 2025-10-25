"""
Testes para ferramentas de apostas:
- Expected Value (EV)
- Kelly Criterion
- Análise de apostas
"""
import pytest
from betting_tools import (
    calculate_ev,
    kelly_criterion,
    analyze_bet,
    decimal_to_probability,
    probability_to_decimal
)


class TestEVCalculation:
    """Testes para cálculo de Expected Value"""
    
    def test_positive_ev(self):
        """Testa EV positivo (value bet)"""
        result = calculate_ev(prob_win=0.6, odds_decimal=2.0, stake=100)
        
        assert result['ev_absolute'] > 0
        assert result['ev_percent'] > 0
        assert result['is_value_bet'] is True
    
    def test_negative_ev(self):
        """Testa EV negativo (sem value)"""
        result = calculate_ev(prob_win=0.4, odds_decimal=2.0, stake=100)
        
        assert result['ev_absolute'] < 0
        assert result['ev_percent'] < 0
        assert result['is_value_bet'] is False
    
    def test_zero_ev(self):
        """Testa EV zero (break-even)"""
        result = calculate_ev(prob_win=0.5, odds_decimal=2.0, stake=100)
        
        assert abs(result['ev_absolute']) < 0.01
        assert abs(result['ev_percent']) < 0.01
    
    def test_ev_scales_with_stake(self):
        """Testa se EV escala proporcionalmente com stake"""
        ev1 = calculate_ev(prob_win=0.6, odds_decimal=2.0, stake=100)
        ev2 = calculate_ev(prob_win=0.6, odds_decimal=2.0, stake=200)
        
        # EV absoluto deve dobrar
        assert abs(ev2['ev_absolute'] - 2 * ev1['ev_absolute']) < 0.01
        
        # EV percentual deve ser o mesmo
        assert abs(ev2['ev_percent'] - ev1['ev_percent']) < 0.01


class TestKellyCriterion:
    """Testes para Kelly Criterion"""
    
    def test_kelly_positive(self):
        """Testa Kelly com value bet"""
        result = kelly_criterion(prob_win=0.6, odds_decimal=2.0, kelly_fraction=1.0)
        
        assert result['kelly_percent'] > 0
        assert result['recommendation'] == 'APOSTAR'
    
    def test_kelly_negative(self):
        """Testa Kelly sem value"""
        result = kelly_criterion(prob_win=0.4, odds_decimal=2.0, kelly_fraction=1.0)
        
        assert result['kelly_percent'] == 0
        assert result['recommendation'] == 'NAO_APOSTAR'
    
    def test_kelly_fraction_adjustment(self):
        """Testa se fração de Kelly reduz corretamente"""
        full_kelly = kelly_criterion(prob_win=0.6, odds_decimal=2.0, kelly_fraction=1.0)
        half_kelly = kelly_criterion(prob_win=0.6, odds_decimal=2.0, kelly_fraction=0.5)
        quarter_kelly = kelly_criterion(prob_win=0.6, odds_decimal=2.0, kelly_fraction=0.25)
        
        assert half_kelly['kelly_adjusted'] == full_kelly['kelly_adjusted'] * 0.5
        assert quarter_kelly['kelly_adjusted'] == full_kelly['kelly_adjusted'] * 0.25
    
    def test_kelly_bounded(self):
        """Testa se Kelly está entre 0 e 1"""
        # Mesmo com prob muito alta
        result = kelly_criterion(prob_win=0.99, odds_decimal=1.5, kelly_fraction=1.0)
        
        assert 0 <= result['kelly_percent'] <= 1
        assert 0 <= result['kelly_adjusted'] <= 1
    
    def test_kelly_invalid_odds(self):
        """Testa Kelly com odds inválidas"""
        result = kelly_criterion(prob_win=0.6, odds_decimal=0.5, kelly_fraction=1.0)
        
        assert result['recommendation'] == 'NAO_APOSTAR'
        assert result['kelly_percent'] == 0


class TestOddsConversion:
    """Testes para conversão de odds"""
    
    def test_decimal_to_probability(self):
        """Testa conversão de odds para probabilidade"""
        assert decimal_to_probability(2.0) == 0.5
        assert abs(decimal_to_probability(3.0) - 0.333333) < 0.001
        assert decimal_to_probability(1.5) == pytest.approx(0.666667, rel=0.001)
    
    def test_probability_to_decimal(self):
        """Testa conversão de probabilidade para odds"""
        assert probability_to_decimal(0.5) == 2.0
        assert probability_to_decimal(0.333333) == pytest.approx(3.0, rel=0.01)
        assert probability_to_decimal(0.666667) == pytest.approx(1.5, rel=0.01)
    
    def test_roundtrip_conversion(self):
        """Testa conversão ida e volta"""
        original_prob = 0.6
        odds = probability_to_decimal(original_prob)
        back_to_prob = decimal_to_probability(odds)
        
        assert abs(back_to_prob - original_prob) < 0.0001
    
    def test_edge_cases(self):
        """Testa casos extremos"""
        # Probabilidade 0
        assert probability_to_decimal(0) == 999.99
        
        # Probabilidade 1
        assert probability_to_decimal(1) == 1.01
        
        # Odds muito baixas
        assert decimal_to_probability(1.0) == 1.0


class TestBetAnalysis:
    """Testes para análise completa de apostas"""
    
    def test_analyze_value_bet(self):
        """Testa análise de value bet"""
        analysis = analyze_bet(
            prob_win=0.6,
            odds_decimal=2.0,
            bankroll=1000,
            kelly_fraction=0.25
        )
        
        assert 'ev' in analysis
        assert 'kelly' in analysis
        assert 'stake_recommended' in analysis
        assert 'recommendation' in analysis
        
        assert analysis['recommendation'] == 'APOSTAR'
        assert analysis['stake_recommended'] > 0
    
    def test_analyze_no_value_bet(self):
        """Testa análise sem value"""
        analysis = analyze_bet(
            prob_win=0.4,
            odds_decimal=2.0,
            bankroll=1000,
            kelly_fraction=0.25
        )
        
        assert analysis['recommendation'] == 'NAO_APOSTAR'
        assert analysis['stake_recommended'] == 0
    
    def test_stake_respects_bankroll(self):
        """Testa se stake nunca excede banca"""
        analysis = analyze_bet(
            prob_win=0.8,
            odds_decimal=3.0,
            bankroll=100,
            kelly_fraction=1.0
        )
        
        assert analysis['stake_recommended'] <= 100
    
    def test_analysis_structure(self):
        """Testa estrutura completa da análise"""
        analysis = analyze_bet(
            prob_win=0.55,
            odds_decimal=2.2,
            bankroll=1000,
            kelly_fraction=0.25
        )
        
        # Verifica estrutura de EV
        assert 'ev_absolute' in analysis['ev']
        assert 'ev_percent' in analysis['ev']
        assert 'is_value_bet' in analysis['ev']
        
        # Verifica estrutura de Kelly
        assert 'kelly_percent' in analysis['kelly']
        assert 'kelly_adjusted' in analysis['kelly']
        assert 'recommendation' in analysis['kelly']
        
        # Verifica outras chaves
        assert 'edge' in analysis
        assert 'prob_implied' in analysis


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

