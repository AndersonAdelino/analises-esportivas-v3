"""
Configuração OTIMIZADA para economizar requisições
Use este arquivo para configurar a estratégia de economia
"""

# ==========================================
# CONFIGURAÇÃO DE ECONOMIA
# ==========================================

# Casa de apostas preferida (apenas 1 para economizar)
# Opções disponíveis que operam no Brasil:
# - 'bet365' (Bet365 - Casa mais popular no Brasil)
# - 'pinnacle' (Pinnacle - Boas odds, baixa margem)
# - 'betfair_ex_eu' (Betfair Exchange - Europa)
# - 'onexbet' (1xBet)
# - 'unibet_uk' (Unibet)
CASA_PREFERIDA = 'bet365'

# Região única (economiza 2/3 das requisições)
# 'us' = Estados Unidos
# 'uk' = Reino Unido  
# 'eu' = Europa (recomendado para Brasil)
REGIAO_UNICA = 'eu'

# Mercados (1X2 + Over/Under + BTTS)
# 'h2h' = 1X2 apenas (mais econômico)
# 'h2h,totals' = 1X2 + Over/Under
# 'h2h,totals,btts' = 1X2 + Over/Under + BTTS (mais completo)
MERCADOS_COMPLETOS = 'h2h,totals'  # btts não disponível no plano gratuito

# Cache agressivo (em horas)
# Quanto maior, mais economia
CACHE_HORAS = 12  # 12 horas = 2 coletas por dia

# ==========================================
# CÁLCULO DE ECONOMIA
# ==========================================

# Configuração padrão:
# - 3 regiões (us,uk,eu)
# - 2 mercados (h2h,totals)
# - Custo: 3 x 2 = 6 requisições por liga

# Configuração econômica:
# - 1 região (eu)
# - 1 mercado (h2h)
# - Custo: 1 x 1 = 1 requisição por liga

# ECONOMIA: 83% menos requisições!

# Com 2 ligas (BSA + PL):
# - Padrão: 12 req/dia x 30 = 360 req/mês
# - Econômico: 2 req/dia x 30 = 60 req/mês
# - SOBRA: 440 requisições!

# ==========================================
# MAPEAMENTO DE CASAS
# ==========================================

CASAS_DISPONIVEIS = {
    # Casas recomendadas (operam no Brasil)
    'pinnacle': {
        'nome': 'Pinnacle',
        'descricao': 'Baixa margem, boas odds',
        'regiao': 'us',
        'recomendado': True
    },
    'betfair_ex_eu': {
        'nome': 'Betfair Exchange',
        'descricao': 'Exchange, odds variáveis',
        'regiao': 'eu',
        'recomendado': True
    },
    'onexbet': {
        'nome': '1xBet',
        'descricao': 'Muitos mercados',
        'regiao': 'eu',
        'recomendado': True
    },
    'unibet_uk': {
        'nome': 'Unibet',
        'descricao': 'Casa tradicional',
        'regiao': 'uk',
        'recomendado': False
    },
    'williamhill': {
        'nome': 'William Hill',
        'descricao': 'Casa tradicional UK',
        'regiao': 'uk',
        'recomendado': False
    },
    'betway': {
        'nome': 'Betway',
        'descricao': 'Casa popular',
        'regiao': 'eu',
        'recomendado': False
    },
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def calcular_custo_mensal(ligas: int = 2, coletas_por_dia: int = 2):
    """
    Calcula custo mensal de requisições
    
    Args:
        ligas: Número de ligas a coletar
        coletas_por_dia: Quantas vezes coletar por dia
    
    Returns:
        Custo mensal em requisições
    """
    custo_por_coleta = ligas * 1  # 1 req por liga (modo econômico)
    custo_diario = custo_por_coleta * coletas_por_dia
    custo_mensal = custo_diario * 30
    
    return custo_mensal


def verificar_viabilidade(quota_mensal: int = 500):
    """
    Verifica se a configuração é viável com a quota
    
    Args:
        quota_mensal: Quota mensal de requisições
    
    Returns:
        Dicionário com análise
    """
    cenarios = {
        'minimo': calcular_custo_mensal(ligas=1, coletas_por_dia=1),
        'economico': calcular_custo_mensal(ligas=2, coletas_por_dia=2),
        'moderado': calcular_custo_mensal(ligas=3, coletas_por_dia=2),
        'intensivo': calcular_custo_mensal(ligas=5, coletas_por_dia=3),
    }
    
    resultados = {}
    
    for nome, custo in cenarios.items():
        viavel = custo <= quota_mensal
        sobra = quota_mensal - custo if viavel else 0
        
        resultados[nome] = {
            'custo': custo,
            'viavel': viavel,
            'sobra': sobra,
            'percentual': (custo / quota_mensal) * 100
        }
    
    return resultados


if __name__ == '__main__':
    print("=" * 80)
    print("CONFIGURAÇÃO DE ECONOMIA - THE ODDS API")
    print("=" * 80)
    
    print(f"\n📊 CONFIGURAÇÃO ATUAL:")
    print(f"   Casa preferida: {CASA_PREFERIDA}")
    print(f"   Região: {REGIAO_UNICA}")
    print(f"   Mercado: {MERCADO_UNICO}")
    print(f"   Cache: {CACHE_HORAS} horas")
    
    print("\n" + "=" * 80)
    print("ANÁLISE DE CENÁRIOS (Quota: 500 req/mês)")
    print("=" * 80)
    
    cenarios = verificar_viabilidade()
    
    for nome, dados in cenarios.items():
        print(f"\n{nome.upper()}:")
        print(f"   Custo: {dados['custo']} req/mês ({dados['percentual']:.1f}%)")
        print(f"   Viável: {'✅ Sim' if dados['viavel'] else '❌ Não'}")
        print(f"   Sobra: {dados['sobra']} requisições")
    
    print("\n" + "=" * 80)
    print("RECOMENDAÇÃO")
    print("=" * 80)
    print("\n✅ CENÁRIO ECONÔMICO:")
    print("   - 2 ligas (Brasileirão + Premier League)")
    print("   - 2 coletas/dia (manhã e tarde)")
    print("   - Custo: 120 req/mês (24%)")
    print("   - Sobra: 380 requisições")
    print("\n💡 Com cache de 12h, você faz análises ilimitadas!")

