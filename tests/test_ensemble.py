"""
Testes para o sistema de Ensemble
"""
import pytest
from ensemble import EnsembleModel


class TestEnsemble:
    """Testes para o modelo Ensemble"""
    
    def test_default_weights(self):
        """Testa pesos padrão do ensemble"""
        ensemble = EnsembleModel()
        
        assert ensemble.weights['dixon_coles'] == 0.55
        assert ensemble.weights['offensive_defensive'] == 0.30
        assert ensemble.weights['heuristicas'] == 0.15
        
        # Soma deve ser 1
        assert abs(sum(ensemble.weights.values()) - 1.0) < 0.0001
    
    def test_custom_weights_normalization(self):
        """Testa normalização de pesos customizados"""
        weights = {
            'dixon_coles': 2.0,
            'offensive_defensive': 1.0,
            'heuristicas': 1.0
        }
        
        ensemble = EnsembleModel(weights=weights)
        
        # Devem ser normalizados para somar 1
        assert abs(sum(ensemble.weights.values()) - 1.0) < 0.0001
        
        # Proporções devem ser mantidas
        assert ensemble.weights['dixon_coles'] == 0.5  # 2/4
        assert ensemble.weights['offensive_defensive'] == 0.25  # 1/4
        assert ensemble.weights['heuristicas'] == 0.25  # 1/4
    
    def test_ensemble_fit(self, sample_match_data):
        """Testa se ensemble treina todos os modelos"""
        ensemble = EnsembleModel()
        ensemble.fit()  # Usa dados reais
        
        assert ensemble._fitted is True
        assert 'dixon_coles' in ensemble.models
        assert 'offensive_defensive' in ensemble.models
        assert 'heuristicas' in ensemble.models
    
    def test_ensemble_prediction_structure(self, sample_match_data):
        """Testa estrutura da predição do ensemble"""
        ensemble = EnsembleModel()
        ensemble.fit()
        
        pred = ensemble.predict_match('Arsenal FC', 'Liverpool FC')
        
        # Deve conter predições individuais
        assert 'dixon_coles' in pred
        assert 'offensive_defensive' in pred
        assert 'heuristicas' in pred
        
        # Deve conter predição combinada
        assert 'ensemble' in pred
        
        # Estrutura do ensemble
        assert 'prob_casa' in pred['ensemble']
        assert 'prob_empate' in pred['ensemble']
        assert 'prob_fora' in pred['ensemble']
        assert 'prob_over_2_5' in pred['ensemble']
        assert 'prob_btts_sim' in pred['ensemble']
    
    def test_ensemble_probabilities_valid(self, sample_match_data):
        """Testa se probabilidades do ensemble são válidas"""
        ensemble = EnsembleModel()
        ensemble.fit()
        
        pred = ensemble.predict_match('Chelsea FC', 'Manchester United FC')
        ens = pred['ensemble']
        
        # Todas devem estar entre 0 e 1
        assert 0 <= ens['prob_casa'] <= 1
        assert 0 <= ens['prob_empate'] <= 1
        assert 0 <= ens['prob_fora'] <= 1
        assert 0 <= ens['prob_over_2_5'] <= 1
        assert 0 <= ens['prob_btts_sim'] <= 1
        
        # 1X2 deve somar ~1
        total = ens['prob_casa'] + ens['prob_empate'] + ens['prob_fora']
        assert abs(total - 1.0) < 0.01
    
    def test_ensemble_weighted_average(self, sample_match_data):
        """Testa se ensemble realmente faz média ponderada"""
        ensemble = EnsembleModel()
        ensemble.fit()
        
        pred = ensemble.predict_match('Arsenal FC', 'Liverpool FC')
        
        # Calcula média manual
        expected_prob_casa = (
            pred['dixon_coles']['prob_home_win'] * 0.55 +
            pred['offensive_defensive']['prob_home_win'] * 0.30 +
            pred['heuristicas'].get('prob_home_win', pred['dixon_coles']['prob_home_win']) * 0.15
        )
        
        # Deve ser próximo (com alguma tolerância para conversão de heurísticas)
        assert abs(pred['ensemble']['prob_casa'] - expected_prob_casa) < 0.05


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

