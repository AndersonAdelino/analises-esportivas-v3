"""
Sistema de Validação e Backtesting dos Modelos

Funcionalidades:
- Cross-validation temporal
- Cálculo de métricas (Brier Score, Log Loss, ROI)
- Simulação de apostas
- Comparação entre modelos
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
import os

from logger_config import setup_logger, log_model_training

logger = setup_logger(__name__)


class ModelValidator:
    """Validador de modelos preditivos com métricas estatísticas"""
    
    def __init__(self, model, df: pd.DataFrame, model_name: str = "Unknown"):
        """
        Inicializa validador
        
        Args:
            model: Modelo a ser validado (deve ter métodos fit() e predict_match())
            df: DataFrame com dados históricos
            model_name: Nome do modelo para logs
        """
        self.model = model
        self.df = df.sort_values('data').reset_index(drop=True)
        self.model_name = model_name
        
        logger.info(f"Validador criado para modelo {model_name} com {len(df)} partidas")
    
    def time_series_split(self, n_splits: int = 5) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Divide dados em treino/teste respeitando ordem temporal
        
        Args:
            n_splits: Número de splits
            
        Returns:
            Lista de tuplas (treino, teste)
        """
        split_size = len(self.df) // (n_splits + 1)
        splits = []
        
        for i in range(n_splits):
            train_end = (i + 1) * split_size
            test_end = min((i + 2) * split_size, len(self.df))
            
            train = self.df.iloc[:train_end]
            test = self.df.iloc[train_end:test_end]
            
            splits.append((train, test))
            
            logger.debug(f"Split {i+1}: {len(train)} treino, {len(test)} teste")
        
        return splits
    
    def calculate_brier_score(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Calcula Brier Score (0-1, menor é melhor)
        
        Args:
            y_true: Resultados reais (0 ou 1)
            y_pred: Probabilidades preditas (0-1)
            
        Returns:
            Brier Score
        """
        return np.mean((y_pred - y_true) ** 2)
    
    def calculate_log_loss(self, y_true: List[List[int]], y_pred: List[List[float]]) -> float:
        """
        Calcula Log Loss para classificação multiclasse
        
        Args:
            y_true: Labels verdadeiros (one-hot encoded)
            y_pred: Probabilidades preditas
            
        Returns:
            Log Loss
        """
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        
        log_loss = -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
        return log_loss
    
    def simulate_betting(
        self, 
        test_df: pd.DataFrame, 
        predictions: Dict,
        initial_bankroll: float = 1000.0,
        kelly_fraction: float = 0.25,
        bookmaker_margin: float = 0.05
    ) -> Dict:
        """
        Simula estratégia de apostas usando Kelly Criterion
        
        Args:
            test_df: Dados de teste
            predictions: Dicionário com predições {index: prediction}
            initial_bankroll: Banca inicial
            kelly_fraction: Fração de Kelly (0.25 = conservador)
            bookmaker_margin: Margem da casa de apostas
            
        Returns:
            Dict com estatísticas da simulação
        """
        bankroll = initial_bankroll
        total_staked = 0
        total_profit = 0
        bets_made = 0
        bets_won = 0
        
        bet_history = []
        
        for idx, row in test_df.iterrows():
            if idx not in predictions:
                continue
            
            pred = predictions[idx]
            
            # Simula odds da casa (fair odds + margem)
            prob_home = pred.get('prob_home_win', pred.get('prob_casa', 0.33))
            fair_odds = 1 / prob_home if prob_home > 0 else 3.0
            bookmaker_odds = fair_odds * (1 - bookmaker_margin)
            
            # Calcula Kelly
            kelly_pct = ((prob_home * bookmaker_odds) - 1) / (bookmaker_odds - 1)
            kelly_pct = max(0, min(kelly_pct, 1)) * kelly_fraction
            
            # Aposta se Kelly > 1% da banca
            if kelly_pct > 0.01 and bankroll > 0:
                stake = bankroll * kelly_pct
                total_staked += stake
                bets_made += 1
                
                # Resultado real
                if row['gols_casa'] > row['gols_visitante']:
                    profit = stake * (bookmaker_odds - 1)
                    total_profit += profit
                    bankroll += profit
                    bets_won += 1
                    result = 'WON'
                else:
                    bankroll -= stake
                    total_profit -= stake
                    result = 'LOST'
                
                bet_history.append({
                    'match': f"{row['time_casa']} vs {row['time_visitante']}",
                    'prob_model': prob_home,
                    'odds': bookmaker_odds,
                    'kelly_pct': kelly_pct,
                    'stake': stake,
                    'result': result,
                    'bankroll_after': bankroll
                })
        
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        win_rate = (bets_won / bets_made * 100) if bets_made > 0 else 0
        
        return {
            'initial_bankroll': initial_bankroll,
            'final_bankroll': bankroll,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi_percent': roi,
            'bets_made': bets_made,
            'bets_won': bets_won,
            'win_rate': win_rate,
            'bet_history': bet_history
        }
    
    def calculate_metrics(self, test_df: pd.DataFrame, predictions: Dict) -> Dict:
        """
        Calcula todas as métricas de validação
        
        Args:
            test_df: DataFrame de teste
            predictions: Dicionário {index: prediction}
            
        Returns:
            Dict com métricas calculadas
        """
        # Prepara dados para Brier Score
        y_true_home = []
        y_pred_home = []
        
        # Prepara dados para Log Loss
        y_true_categorical = []
        y_pred_categorical = []
        
        for idx, row in test_df.iterrows():
            if idx not in predictions:
                continue
            
            pred = predictions[idx]
            
            # Brier Score (apenas vitória casa)
            y_true_home.append(1 if row['gols_casa'] > row['gols_visitante'] else 0)
            y_pred_home.append(pred.get('prob_home_win', pred.get('prob_casa', 0.33)))
            
            # Log Loss (1X2)
            if row['gols_casa'] > row['gols_visitante']:
                y_true_categorical.append([1, 0, 0])  # Casa
            elif row['gols_casa'] < row['gols_visitante']:
                y_true_categorical.append([0, 0, 1])  # Fora
            else:
                y_true_categorical.append([0, 1, 0])  # Empate
            
            y_pred_categorical.append([
                pred.get('prob_home_win', pred.get('prob_casa', 0.33)),
                pred.get('prob_draw', pred.get('prob_empate', 0.33)),
                pred.get('prob_away_win', pred.get('prob_fora', 0.33))
            ])
        
        # Calcula métricas
        brier = self.calculate_brier_score(np.array(y_true_home), np.array(y_pred_home))
        logloss = self.calculate_log_loss(y_true_categorical, y_pred_categorical)
        
        # Simula apostas
        betting_results = self.simulate_betting(test_df, predictions)
        
        return {
            'brier_score': brier,
            'log_loss': logloss,
            'roi_percent': betting_results['roi_percent'],
            'win_rate': betting_results['win_rate'],
            'n_matches': len(test_df),
            'n_predictions': len(predictions),
            'betting_simulation': betting_results
        }
    
    def cross_validate(self, n_splits: int = 5, save_results: bool = True) -> Dict:
        """
        Executa cross-validation completa
        
        Args:
            n_splits: Número de splits temporais
            save_results: Se True, salva resultados em arquivo JSON
            
        Returns:
            Dict com resultados agregados
        """
        logger.info(f"Iniciando cross-validation de {self.model_name} com {n_splits} splits")
        
        results = []
        
        for i, (train, test) in enumerate(self.time_series_split(n_splits)):
            logger.info(f"Fold {i+1}/{n_splits}: Treino={len(train)}, Teste={len(test)}")
            
            # Treina modelo
            with log_model_training(logger, f"{self.model_name} (Fold {i+1})"):
                self.model.fit(train, time_decay=False)
            
            # Gera predições
            predictions = {}
            for idx, row in test.iterrows():
                try:
                    pred = self.model.predict_match(row['time_casa'], row['time_visitante'])
                    predictions[idx] = pred
                except Exception as e:
                    logger.warning(f"Erro ao predizer {row['time_casa']} vs {row['time_visitante']}: {e}")
                    continue
            
            # Calcula métricas
            metrics = self.calculate_metrics(test, predictions)
            results.append(metrics)
            
            logger.info(f"Fold {i+1} - Brier: {metrics['brier_score']:.4f}, "
                       f"Log Loss: {metrics['log_loss']:.4f}, ROI: {metrics['roi_percent']:.2f}%")
        
        # Agrega resultados
        avg_results = {
            'model_name': self.model_name,
            'n_splits': n_splits,
            'brier_score': {
                'mean': np.mean([r['brier_score'] for r in results]),
                'std': np.std([r['brier_score'] for r in results]),
                'min': np.min([r['brier_score'] for r in results]),
                'max': np.max([r['brier_score'] for r in results])
            },
            'log_loss': {
                'mean': np.mean([r['log_loss'] for r in results]),
                'std': np.std([r['log_loss'] for r in results]),
                'min': np.min([r['log_loss'] for r in results]),
                'max': np.max([r['log_loss'] for r in results])
            },
            'roi_percent': {
                'mean': np.mean([r['roi_percent'] for r in results]),
                'std': np.std([r['roi_percent'] for r in results]),
                'min': np.min([r['roi_percent'] for r in results]),
                'max': np.max([r['roi_percent'] for r in results])
            },
            'win_rate': {
                'mean': np.mean([r['win_rate'] for r in results]),
                'std': np.std([r['win_rate'] for r in results])
            },
            'fold_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Salva resultados
        if save_results:
            output_dir = 'data/validation'
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"{output_dir}/{self.model_name.lower().replace(' ', '_')}_validation.json"
            with open(filename, 'w') as f:
                json.dump(avg_results, f, indent=2, default=str)
            
            logger.info(f"Resultados salvos em: {filename}")
        
        return avg_results
    
    def print_results(self, results: Dict):
        """Exibe resultados formatados"""
        print(f"\n{'='*60}")
        print(f"📊 RESULTADOS DA VALIDAÇÃO - {results['model_name']}")
        print(f"{'='*60}\n")
        
        print(f"🎯 Brier Score: {results['brier_score']['mean']:.4f} ± {results['brier_score']['std']:.4f}")
        print(f"   (Menor é melhor. Ideal: < 0.20)")
        
        print(f"\n📉 Log Loss: {results['log_loss']['mean']:.4f} ± {results['log_loss']['std']:.4f}")
        print(f"   (Menor é melhor. Ideal: < 1.0)")
        
        print(f"\n💰 ROI Simulado: {results['roi_percent']['mean']:.2f}% ± {results['roi_percent']['std']:.2f}%")
        print(f"   Min: {results['roi_percent']['min']:.2f}% | Max: {results['roi_percent']['max']:.2f}%")
        print(f"   (Positivo indica lucro)")
        
        print(f"\n🎲 Win Rate: {results['win_rate']['mean']:.1f}% ± {results['win_rate']['std']:.1f}%")
        print(f"   (% de apostas ganhas)")
        
        print(f"\n{'='*60}\n")


def compare_models(models: Dict[str, Tuple], df: pd.DataFrame, n_splits: int = 5):
    """
    Compara múltiplos modelos
    
    Args:
        models: Dict {nome: (model, model_class)} 
        df: DataFrame com dados
        n_splits: Número de splits para validação
        
    Example:
        >>> from dixon_coles import DixonColesModel, load_match_data
        >>> from offensive_defensive import OffensiveDefensiveModel
        >>> 
        >>> df = load_match_data()
        >>> models = {
        >>>     'Dixon-Coles': (DixonColesModel(xi=0.003), DixonColesModel),
        >>>     'Offensive-Defensive': (OffensiveDefensiveModel(xi=0.003), OffensiveDefensiveModel)
        >>> }
        >>> 
        >>> comparison = compare_models(models, df)
    """
    logger.info(f"Comparando {len(models)} modelos")
    
    all_results = {}
    
    for model_name, (model, _) in models.items():
        logger.info(f"\nValidando modelo: {model_name}")
        
        validator = ModelValidator(model, df, model_name)
        results = validator.cross_validate(n_splits, save_results=True)
        validator.print_results(results)
        
        all_results[model_name] = results
    
    # Salva comparação
    output_file = 'data/validation/model_comparison.json'
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    logger.info(f"Comparação salva em: {output_file}")
    
    # Exibe ranking
    print(f"\n{'='*60}")
    print("🏆 RANKING DOS MODELOS")
    print(f"{'='*60}\n")
    
    # Ordena por ROI
    sorted_by_roi = sorted(all_results.items(), key=lambda x: x[1]['roi_percent']['mean'], reverse=True)
    
    print("📈 Por ROI:")
    for i, (name, results) in enumerate(sorted_by_roi, 1):
        print(f"  {i}. {name}: {results['roi_percent']['mean']:+.2f}%")
    
    # Ordena por Brier Score
    sorted_by_brier = sorted(all_results.items(), key=lambda x: x[1]['brier_score']['mean'])
    
    print("\n🎯 Por Brier Score (menor é melhor):")
    for i, (name, results) in enumerate(sorted_by_brier, 1):
        print(f"  {i}. {name}: {results['brier_score']['mean']:.4f}")
    
    print(f"\n{'='*60}\n")
    
    return all_results


if __name__ == "__main__":
    """Exemplo de uso"""
    print("🔬 Sistema de Validação e Backtesting\n")
    
    # Importa modelos
    from dixon_coles import DixonColesModel, load_match_data
    from offensive_defensive import OffensiveDefensiveModel
    
    # Carrega dados
    print("Carregando dados...")
    df = load_match_data()
    print(f"✅ {len(df)} partidas carregadas\n")
    
    # Valida Dixon-Coles
    print("Validando Dixon-Coles...")
    dc_model = DixonColesModel(xi=0.003)
    dc_validator = ModelValidator(dc_model, df, "Dixon-Coles")
    dc_results = dc_validator.cross_validate(n_splits=3)
    dc_validator.print_results(dc_results)
    
    # Valida Offensive-Defensive
    print("\nValidando Offensive-Defensive...")
    od_model = OffensiveDefensiveModel(xi=0.003)
    od_validator = ModelValidator(od_model, df, "Offensive-Defensive")
    od_results = od_validator.cross_validate(n_splits=3)
    od_validator.print_results(od_results)
    
    print("✅ Validação concluída!")
    print("📁 Resultados salvos em data/validation/")

