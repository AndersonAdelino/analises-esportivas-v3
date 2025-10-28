"""
Sistema de Ranqueamento de Apostas
====================================

Sistema avançado de scoring e ranking de apostas baseado em múltiplos critérios:
- Expected Value (EV%)
- Edge (diferença entre p_model e p_implícita)
- Probabilidade do modelo
- Stake sugerida (Kelly ajustada)

Perfis de apostador:
- Conservador: Prioriza EV% e Edge
- Moderado: Balanceado entre critérios
- Agressivo: Prioriza probabilidade do modelo e stake
"""

import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class PerfilApostador(Enum):
    """Perfis de apostador disponíveis"""
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    AGRESSIVO = "agressivo"


class RecomendacaoNivel(Enum):
    """Níveis de recomendação de aposta"""
    APOSTAR_ALTO = "APOSTAR_ALTO"
    APOSTAR_MEDIO = "APOSTAR_MEDIO"
    APOSTAR_BAIXO = "APOSTAR_BAIXO"
    NAO_APOSTAR = "NÃO_APOSTAR"


@dataclass
class PesosRanking:
    """Pesos para cálculo do score de ranking"""
    w_ev: float
    w_edge: float
    w_p: float
    w_stake: float
    
    def soma_pesos(self) -> float:
        """Retorna a soma dos pesos"""
        return self.w_ev + self.w_edge + self.w_p + self.w_stake


# Configuração dos pesos por perfil
PESOS_POR_PERFIL = {
    PerfilApostador.CONSERVADOR: PesosRanking(
        w_ev=0.40,
        w_edge=0.30,
        w_p=0.20,
        w_stake=0.10
    ),
    PerfilApostador.MODERADO: PesosRanking(
        w_ev=0.35,
        w_edge=0.25,
        w_p=0.25,
        w_stake=0.15
    ),
    PerfilApostador.AGRESSIVO: PesosRanking(
        w_ev=0.25,
        w_edge=0.20,
        w_p=0.30,
        w_stake=0.25
    )
}


# Configuração da fração de Kelly por perfil
FRACAO_KELLY_POR_PERFIL = {
    PerfilApostador.CONSERVADOR: 0.25,
    PerfilApostador.MODERADO: 0.50,
    PerfilApostador.AGRESSIVO: 1.00
}


@dataclass
class ApostaInput:
    """Dados de entrada para uma aposta"""
    id: str
    partida: str
    mercado: str
    selecao: str
    odds: float
    p_model: float
    ev_percent: float
    edge: float
    
    def __post_init__(self):
        """Validação dos dados de entrada"""
        if self.odds <= 1.0:
            raise ValueError(f"Odds inválida: {self.odds}")
        if not 0 <= self.p_model <= 1:
            raise ValueError(f"p_model deve estar entre 0 e 1: {self.p_model}")


@dataclass
class ApostaRanqueada:
    """Resultado do ranqueamento de uma aposta"""
    # Dados originais
    id: str
    partida: str
    mercado: str
    selecao: str
    odds: float
    p_model: float
    ev_percent: float
    edge: float
    
    # Resultados do ranqueamento
    score: float
    stake_percent: float
    stake_final: float
    recomendacao: RecomendacaoNivel
    destacar: bool
    
    # Componentes normalizados do score (para debug/explicação)
    ev_norm: float
    edge_norm: float
    p_model_norm: float
    stake_norm: float
    
    def __repr__(self):
        return (
            f"ApostaRanqueada(partida='{self.partida}', mercado='{self.mercado}', "
            f"score={self.score:.1f}, stake={self.stake_percent:.2f}%, "
            f"recomendacao={self.recomendacao.value})"
        )


class BettingRankingSystem:
    """Sistema de ranqueamento de apostas"""
    
    def __init__(
        self,
        perfil: PerfilApostador = PerfilApostador.MODERADO,
        stake_min_percent: float = 0.50,
        stake_max_percent: float = 12.0,
        bankroll: float = 1000.0
    ):
        """
        Inicializa o sistema de ranqueamento
        
        Args:
            perfil: Perfil do apostador (conservador/moderado/agressivo)
            stake_min_percent: Stake mínima em % do bankroll
            stake_max_percent: Stake máxima em % do bankroll
            bankroll: Valor total do bankroll
        """
        self.perfil = perfil
        self.stake_min_percent = stake_min_percent
        self.stake_max_percent = stake_max_percent
        self.bankroll = bankroll
        self.pesos = PESOS_POR_PERFIL[perfil]
        self.fracao_kelly = FRACAO_KELLY_POR_PERFIL[perfil]
    
    def calcular_stake_kelly(self, p_model: float, odds: float) -> float:
        """
        Calcula o stake usando a fração de Kelly ajustada
        
        Fórmula de Kelly: f = (bp - q) / b
        Onde:
        - b = odds - 1 (retorno líquido)
        - p = probabilidade de ganhar
        - q = probabilidade de perder (1 - p)
        - f = fração do bankroll a apostar
        
        Args:
            p_model: Probabilidade estimada pelo modelo
            odds: Odds da casa de apostas
            
        Returns:
            Stake em % do bankroll (ajustado pela fração de Kelly e limitado)
        """
        if p_model <= 0 or odds <= 1.0:
            return 0.0
        
        b = odds - 1  # retorno líquido
        p = p_model
        q = 1 - p
        
        # Fórmula de Kelly
        kelly_full = (b * p - q) / b
        
        # Aplicar fração de Kelly baseada no perfil
        kelly_ajustado = kelly_full * self.fracao_kelly
        
        # Converter para percentual
        stake_percent = kelly_ajustado * 100
        
        # Aplicar limites
        if stake_percent < self.stake_min_percent:
            return 0.0  # Aposta muito pequena, não vale a pena
        
        stake_percent = min(stake_percent, self.stake_max_percent)
        
        return max(0.0, stake_percent)
    
    def normalizar_valores(
        self,
        valores: List[float],
        min_val: float = None,
        max_val: float = None
    ) -> List[float]:
        """
        Normaliza uma lista de valores para escala 0-100
        
        Args:
            valores: Lista de valores a normalizar
            min_val: Valor mínimo (se None, usa o mínimo da lista)
            max_val: Valor máximo (se None, usa o máximo da lista)
            
        Returns:
            Lista de valores normalizados entre 0 e 100
        """
        if not valores:
            return []
        
        valores_arr = np.array(valores)
        
        v_min = min_val if min_val is not None else valores_arr.min()
        v_max = max_val if max_val is not None else valores_arr.max()
        
        # Evitar divisão por zero
        if v_max - v_min == 0:
            return [50.0] * len(valores)  # Todos os valores iguais
        
        # Normalizar para 0-100
        normalizados = ((valores_arr - v_min) / (v_max - v_min)) * 100
        
        return normalizados.tolist()
    
    def calcular_score(
        self,
        ev_norm: float,
        edge_norm: float,
        p_model_norm: float,
        stake_norm: float
    ) -> float:
        """
        Calcula o score final da aposta como média ponderada
        
        Args:
            ev_norm: Expected Value normalizado (0-100)
            edge_norm: Edge normalizado (0-100)
            p_model_norm: Probabilidade do modelo normalizada (0-100)
            stake_norm: Stake normalizado (0-100)
            
        Returns:
            Score final (0-100)
        """
        score = (
            ev_norm * self.pesos.w_ev +
            edge_norm * self.pesos.w_edge +
            p_model_norm * self.pesos.w_p +
            stake_norm * self.pesos.w_stake
        ) / self.pesos.soma_pesos()
        
        return score
    
    def determinar_recomendacao(
        self,
        score: float,
        stake_percent: float
    ) -> RecomendacaoNivel:
        """
        Determina o nível de recomendação baseado no score e stake
        
        Args:
            score: Score da aposta (0-100)
            stake_percent: Stake em % do bankroll
            
        Returns:
            Nível de recomendação
        """
        if stake_percent < self.stake_min_percent:
            return RecomendacaoNivel.NAO_APOSTAR
        
        if score >= 75:
            return RecomendacaoNivel.APOSTAR_ALTO
        elif score >= 50:
            return RecomendacaoNivel.APOSTAR_MEDIO
        elif score >= 25:
            return RecomendacaoNivel.APOSTAR_BAIXO
        else:
            return RecomendacaoNivel.NAO_APOSTAR
    
    def ranquear_apostas(
        self,
        apostas: List[ApostaInput]
    ) -> List[ApostaRanqueada]:
        """
        Ranqueia uma lista de apostas
        
        Args:
            apostas: Lista de apostas a ranquear
            
        Returns:
            Lista de apostas ranqueadas, ordenadas por score (maior para menor)
        """
        if not apostas:
            return []
        
        # Calcular stakes para todas as apostas
        stakes = []
        for aposta in apostas:
            stake = self.calcular_stake_kelly(aposta.p_model, aposta.odds)
            stakes.append(stake)
        
        # Extrair valores para normalização
        evs = [a.ev_percent for a in apostas]
        edges = [a.edge for a in apostas]
        p_models = [a.p_model * 100 for a in apostas]  # Converter para percentual
        
        # Normalizar todos os valores
        evs_norm = self.normalizar_valores(evs)
        edges_norm = self.normalizar_valores(edges)
        p_models_norm = self.normalizar_valores(p_models)
        stakes_norm = self.normalizar_valores(stakes)
        
        # Calcular scores e criar objetos ApostaRanqueada
        apostas_ranqueadas = []
        for i, aposta in enumerate(apostas):
            score = self.calcular_score(
                evs_norm[i],
                edges_norm[i],
                p_models_norm[i],
                stakes_norm[i]
            )
            
            stake_percent = stakes[i]
            stake_final = (stake_percent / 100) * self.bankroll
            
            recomendacao = self.determinar_recomendacao(score, stake_percent)
            
            aposta_ranqueada = ApostaRanqueada(
                id=aposta.id,
                partida=aposta.partida,
                mercado=aposta.mercado,
                selecao=aposta.selecao,
                odds=aposta.odds,
                p_model=aposta.p_model,
                ev_percent=aposta.ev_percent,
                edge=aposta.edge,
                score=score,
                stake_percent=stake_percent,
                stake_final=stake_final,
                recomendacao=recomendacao,
                destacar=False,  # Será definido depois
                ev_norm=evs_norm[i],
                edge_norm=edges_norm[i],
                p_model_norm=p_models_norm[i],
                stake_norm=stakes_norm[i]
            )
            apostas_ranqueadas.append(aposta_ranqueada)
        
        # Ordenar por score (maior para menor)
        apostas_ranqueadas.sort(key=lambda x: x.score, reverse=True)
        
        # Destacar a melhor aposta
        if apostas_ranqueadas and apostas_ranqueadas[0].recomendacao != RecomendacaoNivel.NAO_APOSTAR:
            apostas_ranqueadas[0].destacar = True
        
        return apostas_ranqueadas
    
    def gerar_relatorio(
        self,
        apostas_ranqueadas: List[ApostaRanqueada],
        top_n: int = 10
    ) -> str:
        """
        Gera um relatório textual do ranqueamento
        
        Args:
            apostas_ranqueadas: Lista de apostas ranqueadas
            top_n: Número de apostas top para exibir
            
        Returns:
            String com o relatório formatado
        """
        if not apostas_ranqueadas:
            return "Nenhuma aposta disponível para ranquear."
        
        linhas = []
        linhas.append("=" * 80)
        linhas.append(f"RANKING DE APOSTAS - PERFIL {self.perfil.value.upper()}")
        linhas.append("=" * 80)
        linhas.append(f"Bankroll: R$ {self.bankroll:,.2f}")
        linhas.append(f"Fração de Kelly: {self.fracao_kelly:.2%}")
        linhas.append(f"Stake Min: {self.stake_min_percent:.2f}% | Stake Max: {self.stake_max_percent:.2f}%")
        linhas.append("=" * 80)
        linhas.append("")
        
        # Filtrar apostas recomendadas
        apostas_recomendadas = [
            a for a in apostas_ranqueadas 
            if a.recomendacao != RecomendacaoNivel.NAO_APOSTAR
        ]
        
        if not apostas_recomendadas:
            linhas.append("AVISO: Nenhuma aposta recomendada no momento.")
            return "\n".join(linhas)
        
        # Exibir top apostas
        linhas.append(f">>> TOP {min(top_n, len(apostas_recomendadas))} APOSTAS RECOMENDADAS <<<")
        linhas.append("")
        
        for i, aposta in enumerate(apostas_recomendadas[:top_n], 1):
            destaque = "***" if aposta.destacar else "   "
            
            linhas.append(f"{destaque}#{i} | Score: {aposta.score:.1f}/100")
            linhas.append(f"    Partida: {aposta.partida}")
            linhas.append(f"    Mercado: {aposta.mercado} -> {aposta.selecao}")
            linhas.append(f"    Odds: {aposta.odds:.2f} | P(modelo): {aposta.p_model:.1%}")
            linhas.append(f"    EV: {aposta.ev_percent:+.2f}% | Edge: {aposta.edge:+.2f}%")
            linhas.append(f"    $$ Stake: {aposta.stake_percent:.2f}% (R$ {aposta.stake_final:.2f})")
            linhas.append(f"    >> Recomendacao: {aposta.recomendacao.value}")
            linhas.append("")
        
        # Estatísticas gerais
        linhas.append("=" * 80)
        linhas.append("ESTATÍSTICAS")
        linhas.append("=" * 80)
        linhas.append(f"Total de apostas analisadas: {len(apostas_ranqueadas)}")
        linhas.append(f"Apostas recomendadas: {len(apostas_recomendadas)}")
        
        total_stake = sum(a.stake_final for a in apostas_recomendadas[:top_n])
        linhas.append(f"Exposição total (top {min(top_n, len(apostas_recomendadas))}): R$ {total_stake:,.2f} ({total_stake/self.bankroll:.1%} do bankroll)")
        
        return "\n".join(linhas)


def criar_sistema_ranking(
    perfil: str = "moderado",
    stake_min: float = 0.50,
    stake_max: float = 12.0,
    bankroll: float = 1000.0
) -> BettingRankingSystem:
    """
    Factory function para criar um sistema de ranking
    
    Args:
        perfil: 'conservador', 'moderado' ou 'agressivo'
        stake_min: Stake mínima em %
        stake_max: Stake máxima em %
        bankroll: Valor do bankroll
        
    Returns:
        Instância configurada do BettingRankingSystem
    """
    perfil_enum = PerfilApostador(perfil.lower())
    
    return BettingRankingSystem(
        perfil=perfil_enum,
        stake_min_percent=stake_min,
        stake_max_percent=stake_max,
        bankroll=bankroll
    )


if __name__ == "__main__":
    # Exemplo de uso
    print("Sistema de Ranqueamento de Apostas")
    print("=" * 80)
    
    # Criar apostas de exemplo
    apostas_exemplo = [
        ApostaInput(
            id="1",
            partida="Flamengo vs Palmeiras",
            mercado="Resultado Final",
            selecao="Flamengo",
            odds=2.10,
            p_model=0.52,
            ev_percent=9.2,
            edge=4.5
        ),
        ApostaInput(
            id="2",
            partida="São Paulo vs Santos",
            mercado="Mais de 2.5 Gols",
            selecao="Sim",
            odds=1.85,
            p_model=0.58,
            ev_percent=7.3,
            edge=3.8
        ),
        ApostaInput(
            id="3",
            partida="Corinthians vs Internacional",
            mercado="Ambas Marcam",
            selecao="Sim",
            odds=1.75,
            p_model=0.62,
            ev_percent=8.5,
            edge=5.1
        ),
        ApostaInput(
            id="4",
            partida="Atlético-MG vs Grêmio",
            mercado="Resultado Final",
            selecao="Atlético-MG",
            odds=1.65,
            p_model=0.55,
            ev_percent=2.3,
            edge=1.2
        ),
    ]
    
    # Testar com diferentes perfis
    for perfil_nome in ["conservador", "moderado", "agressivo"]:
        print(f"\n{'='*80}")
        print(f"TESTANDO PERFIL: {perfil_nome.upper()}")
        print(f"{'='*80}\n")
        
        sistema = criar_sistema_ranking(
            perfil=perfil_nome,
            bankroll=1000.0
        )
        
        apostas_ranqueadas = sistema.ranquear_apostas(apostas_exemplo)
        
        relatorio = sistema.gerar_relatorio(apostas_ranqueadas, top_n=5)
        print(relatorio)

