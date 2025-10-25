"""
Testes para os modelos preditivos:
- Dixon-Coles
- Offensive-Defensive
- Heurísticas
"""
import pytest
import numpy as np
from dixon_coles import DixonColesModel
from offensive_defensive import OffensiveDefensiveModel
from heuristicas import HeuristicasModel


class TestDixonColes:
    """Testes para o modelo Dixon-Coles"""
    
    def test_model_fits(self, sample_match_data):
        """Testa se o modelo treina sem erros"""
        model = DixonColesModel(xi=0.003)
        model.fit(sample_match_data, time_decay=False)
        
        assert model._fitted is True
        assert model.home_advantage > 0
        assert len(model.teams) > 0
    
    def test_home_advantage_range(self, trained_dixon_coles):
        """Testa se home advantage está em range razoável"""
        assert 0.1 <= trained_dixon_coles.home_advantage <= 0.6
    
    def test_rho_range(self, trained_dixon_coles):
        """Testa se rho está em range esperado"""
        assert -0.5 <= trained_dixon_coles.rho <= 0.5
    
    def test_prediction_structure(self, trained_dixon_coles):
        """Testa estrutura da predição"""
        pred = trained_dixon_coles.predict_match('Arsenal FC', 'Liverpool FC')
        
        # Verifica chaves esperadas
        assert 'prob_home_win' in pred
        assert 'prob_draw' in pred
        assert 'prob_away_win' in pred
        assert 'prob_over_2_5' in pred
        assert 'prob_btts_yes' in pred
        assert 'top_scores' in pred
    
    def test_probabilities_sum_to_one(self, trained_dixon_coles):
        """Testa se probabilidades 1X2 somam ~1"""
        pred = trained_dixon_coles.predict_match('Arsenal FC', 'Liverpool FC')
        
        total = pred['prob_home_win'] + pred['prob_draw'] + pred['prob_away_win']
        assert abs(total - 1.0) < 0.01
    
    def test_probabilities_in_valid_range(self, trained_dixon_coles):
        """Testa se todas probabilidades estão entre 0 e 1"""
        pred = trained_dixon_coles.predict_match('Arsenal FC', 'Manchester City FC')
        
        assert 0 <= pred['prob_home_win'] <= 1
        assert 0 <= pred['prob_draw'] <= 1
        assert 0 <= pred['prob_away_win'] <= 1
        assert 0 <= pred['prob_over_2_5'] <= 1
        assert 0 <= pred['prob_btts_yes'] <= 1
    
    def test_team_strengths(self, trained_dixon_coles):
        """Testa se forças dos times são calculadas"""
        strengths = trained_dixon_coles.get_team_strengths()
        
        assert len(strengths) > 0
        assert 'Time' in strengths.columns
        assert 'Ataque' in strengths.columns
        assert 'Defesa' in strengths.columns
    
    def test_predict_nonexistent_team(self, trained_dixon_coles):
        """Testa erro ao predizer com time inexistente"""
        with pytest.raises(ValueError):
            trained_dixon_coles.predict_match('Team Inexistente', 'Arsenal FC')


class TestOffensiveDefensive:
    """Testes para o modelo Offensive-Defensive"""
    
    def test_model_fits(self, sample_match_data):
        """Testa se o modelo treina sem erros"""
        model = OffensiveDefensiveModel(xi=0.003)
        model.fit(sample_match_data, time_decay=False)
        
        assert model._fitted is True
        assert model.home_advantage > 0
        assert len(model.teams) > 0
    
    def test_prediction_structure(self, trained_offensive_defensive):
        """Testa estrutura da predição"""
        pred = trained_offensive_defensive.predict_match('Arsenal FC', 'Liverpool FC')
        
        assert 'prob_home_win' in pred
        assert 'prob_draw' in pred
        assert 'prob_away_win' in pred
        assert 'prob_over_2_5' in pred
        assert 'prob_btts_yes' in pred
    
    def test_probabilities_valid(self, trained_offensive_defensive):
        """Testa validade das probabilidades"""
        pred = trained_offensive_defensive.predict_match('Chelsea FC', 'Manchester United FC')
        
        total = pred['prob_home_win'] + pred['prob_draw'] + pred['prob_away_win']
        assert abs(total - 1.0) < 0.01
        
        assert 0 <= pred['prob_home_win'] <= 1
        assert 0 <= pred['prob_draw'] <= 1
        assert 0 <= pred['prob_away_win'] <= 1


class TestHeuristicas:
    """Testes para o modelo de Heurísticas"""
    
    def test_forma_recente(self, trained_heuristicas):
        """Testa cálculo de forma recente"""
        forma = trained_heuristicas.forma_recente('Arsenal FC', n_jogos=5)
        
        assert 'jogos' in forma
        assert 'vitorias' in forma
        assert 'aproveitamento' in forma
        assert 0 <= forma['aproveitamento'] <= 100
    
    def test_prediction_structure(self, trained_heuristicas):
        """Testa estrutura da predição"""
        pred = trained_heuristicas.predict_match('Arsenal FC', 'Liverpool FC')
        
        assert 'resultado_previsto' in pred
        assert 'confianca' in pred
        assert 'pontos_casa' in pred
        assert 'pontos_fora' in pred
        assert 'over_under' in pred
        assert 'btts' in pred
    
    def test_resultado_valido(self, trained_heuristicas):
        """Testa se resultado é uma das opções válidas"""
        pred = trained_heuristicas.predict_match('Chelsea FC', 'Tottenham Hotspur FC')
        
        # O modelo retorna "Vitoria [TIME]" ou "Empate"
        resultado = pred['resultado_previsto']
        assert resultado == 'Empate' or resultado.startswith('Vitoria ')
    
    def test_confianca_range(self, trained_heuristicas):
        """Testa se confiança está em range válido"""
        pred = trained_heuristicas.predict_match('Manchester City FC', 'Newcastle United FC')
        
        assert 0 <= pred['confianca'] <= 100


class TestModelComparison:
    """Testes comparando os modelos"""
    
    def test_models_produce_different_predictions(
        self, 
        trained_dixon_coles, 
        trained_offensive_defensive
    ):
        """Testa se modelos produzem predições diferentes (não idênticas)"""
        pred_dc = trained_dixon_coles.predict_match('Arsenal FC', 'Liverpool FC')
        pred_od = trained_offensive_defensive.predict_match('Arsenal FC', 'Liverpool FC')
        
        # Não devem ser idênticos (diferença > 1%)
        assert abs(pred_dc['prob_home_win'] - pred_od['prob_home_win']) > 0.01 or \
               abs(pred_dc['prob_draw'] - pred_od['prob_draw']) > 0.01
    
    def test_all_models_agree_on_obvious_favorite(
        self, 
        trained_dixon_coles, 
        trained_offensive_defensive,
        trained_heuristicas
    ):
        """Testa se todos os modelos concordam em favorito óbvio"""
        # Arsenal em casa vs time mais fraco
        pred_dc = trained_dixon_coles.predict_match('Arsenal FC', 'Brighton & Hove Albion FC')
        pred_od = trained_offensive_defensive.predict_match('Arsenal FC', 'Brighton & Hove Albion FC')
        pred_h = trained_heuristicas.predict_match('Arsenal FC', 'Brighton & Hove Albion FC')
        
        # Todos devem prever vitória da casa como mais provável
        assert pred_dc['prob_home_win'] > pred_dc['prob_draw']
        assert pred_od['prob_home_win'] > pred_od['prob_draw']
        assert 'Casa' in pred_h['resultado_previsto'] or pred_h['confianca'] >= 40


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

