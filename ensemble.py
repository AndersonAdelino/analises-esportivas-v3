"""
Sistema de Ensemble - Combina predições dos 3 modelos

Pesos:
- Dixon-Coles: 55%
- Offensive-Defensive: 30%
- Heurísticas: 15%
"""

import numpy as np
from dixon_coles import DixonColesModel, load_match_data as load_dc_data
from offensive_defensive import OffensiveDefensiveModel, load_match_data as load_od_data
from heuristicas import HeuristicasModel


class EnsembleModel:
    """Ensemble que combina Dixon-Coles, Offensive-Defensive e Heurísticas"""
    
    def __init__(self, weights=None):
        """
        Inicializa o ensemble
        
        Args:
            weights: Dict com pesos {'dixon_coles': float, 'offensive_defensive': float, 'heuristicas': float}
                     Se None, usa pesos padrão: DC=55%, OD=30%, H=15%
        """
        if weights is None:
            self.weights = {
                'dixon_coles': 0.55,
                'offensive_defensive': 0.30,
                'heuristicas': 0.15
            }
        else:
            # Normaliza pesos para somarem 1
            total = sum(weights.values())
            self.weights = {k: v/total for k, v in weights.items()}
        
        self.models = {}
        self._fitted = False
        
    def fit(self, league_code=None):
        """
        Treina todos os modelos
        
        Args:
            league_code: Código da liga (ex: 'PL', 'BSA'). Se None, usa Premier League
        
        Returns:
            self
        """
        from config import LEAGUES, PREMIER_LEAGUE_CODE
        
        if league_code is None:
            league_code = PREMIER_LEAGUE_CODE
        
        # Obtém nome da liga para exibição
        league_display = [name for name, info in LEAGUES.items() if info['code'] == league_code][0]
        
        print(f"Treinando ensemble para {league_display}...")
        
        # Dixon-Coles
        print("\n[1/3] Treinando Dixon-Coles...")
        try:
            df = load_dc_data(league_code=league_code)
            self.models['dixon_coles'] = DixonColesModel(xi=0.003)
            self.models['dixon_coles'].fit(df, time_decay=True)
            print("OK - Dixon-Coles treinado")
        except Exception as e:
            print(f"ERRO - Dixon-Coles: {e}")
            self.models['dixon_coles'] = None
        
        # Offensive-Defensive
        print("\n[2/3] Treinando Offensive-Defensive...")
        try:
            df = load_od_data(league_code=league_code)
            self.models['offensive_defensive'] = OffensiveDefensiveModel(xi=0.003)
            self.models['offensive_defensive'].fit(df, time_decay=True)
            print("OK - Offensive-Defensive treinado")
        except Exception as e:
            print(f"ERRO - Offensive-Defensive: {e}")
            self.models['offensive_defensive'] = None
        
        # Heurísticas
        print("\n[3/3] Carregando Heuristicas...")
        try:
            self.models['heuristicas'] = HeuristicasModel()
            self.models['heuristicas'].load_data(league_code=league_code)
            print("OK - Heuristicas carregadas")
        except Exception as e:
            print(f"ERRO - Heuristicas: {e}")
            self.models['heuristicas'] = None
        
        self._fitted = True
        print(f"\nEnsemble treinado com sucesso para {league_display}!")
        
        return self
    
    def predict_match(self, home_team, away_team):
        """
        Predição combinada dos 3 modelos
        
        Args:
            home_team: Time da casa
            away_team: Time visitante
            
        Returns:
            Dict com probabilidades combinadas e predições individuais
        """
        if not self._fitted:
            raise RuntimeError("Ensemble não foi treinado. Execute fit() primeiro.")
        
        predictions = {}
        
        # Dixon-Coles
        if self.models['dixon_coles']:
            try:
                pred_dc = self.models['dixon_coles'].predict_match(home_team, away_team)
                predictions['dixon_coles'] = {
                    'prob_casa': pred_dc['prob_home_win'],
                    'prob_empate': pred_dc['prob_draw'],
                    'prob_fora': pred_dc['prob_away_win'],
                    'prob_over_2_5': pred_dc['prob_over_2_5'],
                    'prob_btts': pred_dc['prob_btts_yes'],
                    'top_scores': pred_dc.get('top_scores', []),
                    'score_matrix': pred_dc.get('prob_matrix', None)
                }
            except Exception as e:
                print(f"Erro em Dixon-Coles: {e}")
                predictions['dixon_coles'] = None
        
        # Offensive-Defensive
        if self.models['offensive_defensive']:
            try:
                pred_od = self.models['offensive_defensive'].predict_match(home_team, away_team)
                predictions['offensive_defensive'] = {
                    'prob_casa': pred_od['prob_home_win'],
                    'prob_empate': pred_od['prob_draw'],
                    'prob_fora': pred_od['prob_away_win'],
                    'prob_over_2_5': pred_od['prob_over_2_5'],
                    'prob_btts': pred_od['prob_btts_yes'],
                    'top_scores': pred_od.get('top_scores', []),
                    'score_matrix': pred_od.get('prob_matrix', None)
                }
            except Exception as e:
                print(f"Erro em Offensive-Defensive: {e}")
                predictions['offensive_defensive'] = None
        
        # Heurísticas
        if self.models['heuristicas']:
            try:
                pred_heur = self.models['heuristicas'].predict_match(home_team, away_team)
                
                # Converte heurísticas para probabilidades
                # Baseado na confiança e resultado previsto
                confianca = pred_heur['confianca'] / 100.0
                
                if 'Casa' in pred_heur['resultado_previsto'] or home_team in pred_heur['resultado_previsto']:
                    prob_casa = 0.5 + (confianca - 0.5) * 0.8  # Ajusta para range razoável
                    prob_fora = (1 - prob_casa) * 0.4
                    prob_empate = 1 - prob_casa - prob_fora
                elif 'Fora' in pred_heur['resultado_previsto'] or away_team in pred_heur['resultado_previsto']:
                    prob_fora = 0.5 + (confianca - 0.5) * 0.8
                    prob_casa = (1 - prob_fora) * 0.4
                    prob_empate = 1 - prob_casa - prob_fora
                else:  # Empate
                    prob_empate = 0.3 + (confianca - 0.3) * 0.5
                    prob_casa = (1 - prob_empate) * 0.55
                    prob_fora = 1 - prob_casa - prob_empate
                
                # Over/Under
                if pred_heur['over_under'] == 'Over 2.5':
                    prob_over = 0.5 + (pred_heur['confianca_ou'] / 100 - 0.5) * 0.6
                elif pred_heur['over_under'] == 'Under 2.5':
                    prob_over = 0.5 - (pred_heur['confianca_ou'] / 100 - 0.5) * 0.6
                else:
                    prob_over = 0.5
                
                # BTTS
                if pred_heur['btts'] == 'Sim':
                    prob_btts = 0.5 + (pred_heur['confianca_btts'] / 100 - 0.5) * 0.6
                elif pred_heur['btts'] == 'Nao':
                    prob_btts = 0.5 - (pred_heur['confianca_btts'] / 100 - 0.5) * 0.6
                else:
                    prob_btts = 0.5
                
                predictions['heuristicas'] = {
                    'prob_casa': prob_casa,
                    'prob_empate': prob_empate,
                    'prob_fora': prob_fora,
                    'prob_over_2_5': prob_over,
                    'prob_btts': prob_btts,
                    'top_scores': [],  # Heurísticas não gera placares específicos
                    'score_matrix': None  # Heurísticas não gera matriz de placares
                }
            except Exception as e:
                print(f"Erro em Heuristicas: {e}")
                predictions['heuristicas'] = None
        
        # Combina probabilidades com pesos
        ensemble_probs = self._combine_predictions(predictions)
        
        # Combina score matrices (se disponíveis)
        ensemble_matrix, ensemble_top_scores = self._combine_score_matrices(predictions)
        ensemble_probs['score_matrix'] = ensemble_matrix
        ensemble_probs['top_scores'] = ensemble_top_scores
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'ensemble': ensemble_probs,
            'individual': predictions,
            'weights': self.weights
        }
    
    def _combine_predictions(self, predictions):
        """
        Combina predições individuais usando pesos
        
        Args:
            predictions: Dict com predições de cada modelo
            
        Returns:
            Dict com probabilidades combinadas
        """
        # Coleta probabilidades válidas
        valid_probs = {
            'prob_casa': [],
            'prob_empate': [],
            'prob_fora': [],
            'prob_over_2_5': [],
            'prob_btts': []
        }
        
        valid_weights = {key: [] for key in valid_probs.keys()}
        
        for model_name, pred in predictions.items():
            if pred is not None:
                weight = self.weights[model_name]
                for key in valid_probs.keys():
                    if key in pred and pred[key] is not None:
                        # VALIDAÇÃO: Garante que probabilidades estão no intervalo [0, 1]
                        prob_value = pred[key]
                        if prob_value < 0:
                            print(f"AVISO: {model_name} retornou {key}={prob_value:.4f} (negativo). Corrigindo para 0.")
                            prob_value = 0.0
                        elif prob_value > 1:
                            print(f"AVISO: {model_name} retornou {key}={prob_value:.4f} (>1). Corrigindo para 1.")
                            prob_value = 1.0
                        
                        valid_probs[key].append(prob_value)
                        valid_weights[key].append(weight)
        
        # Calcula média ponderada
        combined = {}
        for key in valid_probs.keys():
            if valid_probs[key]:
                # Normaliza pesos
                total_weight = sum(valid_weights[key])
                normalized_weights = [w / total_weight for w in valid_weights[key]]
                
                # Média ponderada
                combined[key] = sum(p * w for p, w in zip(valid_probs[key], normalized_weights))
                
                # VALIDAÇÃO FINAL: Garante que o resultado está no intervalo [0, 1]
                combined[key] = max(0.0, min(1.0, combined[key]))
            else:
                combined[key] = None
        
        # Normaliza probabilidades 1X2 para somarem 1
        if all(combined[k] is not None for k in ['prob_casa', 'prob_empate', 'prob_fora']):
            total = combined['prob_casa'] + combined['prob_empate'] + combined['prob_fora']
            if total > 0:  # Evita divisão por zero
                combined['prob_casa'] /= total
                combined['prob_empate'] /= total
                combined['prob_fora'] /= total
            else:
                # Fallback: distribuição uniforme
                print("AVISO: Soma de probabilidades 1X2 é zero. Usando distribuição uniforme.")
                combined['prob_casa'] = 1.0 / 3.0
                combined['prob_empate'] = 1.0 / 3.0
                combined['prob_fora'] = 1.0 / 3.0
        
        return combined
    
    def _combine_score_matrices(self, predictions):
        """
        Combina matrizes de placares dos modelos usando pesos
        
        Args:
            predictions: Dict com predições de cada modelo
            
        Returns:
            Tuple (ensemble_matrix, ensemble_top_scores)
        """
        import numpy as np
        
        # Coleta matrizes válidas
        matrices = []
        weights = []
        
        for model_name in ['dixon_coles', 'offensive_defensive']:
            if model_name in predictions and predictions[model_name] is not None:
                score_matrix = predictions[model_name].get('score_matrix')
                if score_matrix is not None:
                    matrices.append(score_matrix)
                    weights.append(self.weights[model_name])
        
        if not matrices:
            return None, []
        
        # Normaliza pesos
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Combina matrizes usando média ponderada
        ensemble_matrix = np.zeros_like(matrices[0])
        for matrix, weight in zip(matrices, normalized_weights):
            ensemble_matrix += matrix * weight
        
        # Gera top scores da matriz ensemble
        max_goals = ensemble_matrix.shape[0] - 1
        top_scores = []
        for i in range(ensemble_matrix.shape[0]):
            for j in range(ensemble_matrix.shape[1]):
                top_scores.append(((i, j), ensemble_matrix[i, j]))
        top_scores.sort(key=lambda x: x[1], reverse=True)
        
        return ensemble_matrix, top_scores[:10]


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("SISTEMA DE ENSEMBLE - COMBINACAO DE MODELOS")
    print("=" * 80)
    print("\nPesos:")
    print("  Dixon-Coles: 55%")
    print("  Offensive-Defensive: 30%")
    print("  Heuristicas: 15%")
    print("\n")
    
    # Treina ensemble
    ensemble = EnsembleModel()
    ensemble.fit()
    
    print("\n")
    print("=" * 80)
    print("EXEMPLO DE PREDICAO COM ENSEMBLE")
    print("=" * 80)
    
    # Exemplo
    home = 'Arsenal FC'
    away = 'Liverpool FC'
    
    pred = ensemble.predict_match(home, away)
    
    print(f"\n{home} vs {away}")
    print("-" * 80)
    
    ens = pred['ensemble']
    print("\nPROBABILIDADES COMBINADAS (ENSEMBLE):")
    print(f"  Vitoria Casa:      {ens['prob_casa']*100:>6.2f}%")
    print(f"  Empate:            {ens['prob_empate']*100:>6.2f}%")
    print(f"  Vitoria Visitante: {ens['prob_fora']*100:>6.2f}%")
    print(f"  Over 2.5:          {ens['prob_over_2_5']*100:>6.2f}%")
    print(f"  BTTS:              {ens['prob_btts']*100:>6.2f}%")
    
    print("\nPROBABILIDADES INDIVIDUAIS:")
    for model_name, model_pred in pred['individual'].items():
        if model_pred:
            print(f"\n  {model_name.upper()} (peso: {pred['weights'][model_name]*100:.0f}%):")
            print(f"    Casa:    {model_pred['prob_casa']*100:>6.2f}%")
            print(f"    Empate:  {model_pred['prob_empate']*100:>6.2f}%")
            print(f"    Fora:    {model_pred['prob_fora']*100:>6.2f}%")
    
    print("\n" + "=" * 80)
    print("ENSEMBLE PRONTO PARA USO!")
    print("=" * 80)
    print()

