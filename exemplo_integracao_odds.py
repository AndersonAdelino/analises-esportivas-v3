"""
Exemplo de Integração: Odds API + Modelos Preditivos
Demonstra como buscar odds automaticamente e comparar com suas predições
"""
from odds_api_client import OddsAPIClient
from ensemble import EnsembleModel
import pandas as pd


def exemplo_buscar_odds_partida():
    """Exemplo 1: Buscar odds de uma partida específica"""
    print("=" * 80)
    print("EXEMPLO 1: BUSCAR ODDS DE UMA PARTIDA")
    print("=" * 80)
    
    client = OddsAPIClient()
    
    # Busca odds de todas as partidas do Brasileirão
    odds = client.get_odds_with_cache('soccer_brazil_campeonato')
    
    if not odds:
        print("⚠️ Nenhuma partida disponível no momento")
        return
    
    # Pega primeira partida como exemplo
    match = odds[0]
    
    print(f"\nPartida: {match['home_team']} vs {match['away_team']}")
    print(f"Data: {match['commence_time']}")
    print(f"Casas disponíveis: {len(match['bookmakers'])}")
    
    # Extrai melhores odds
    best = client.get_best_odds(match)
    
    print("\n📊 MELHORES ODDS:")
    print(f"  Casa:   {best['home']['value']:.2f} ({best['home']['bookmaker']})")
    print(f"  Empate: {best['draw']['value']:.2f} ({best['draw']['bookmaker']})")
    print(f"  Fora:   {best['away']['value']:.2f} ({best['away']['bookmaker']})")
    
    if best['over_2_5']['value'] > 0:
        print(f"\n⚽ OVER/UNDER 2.5:")
        print(f"  Over:  {best['over_2_5']['value']:.2f} ({best['over_2_5']['bookmaker']})")
        print(f"  Under: {best['under_2_5']['value']:.2f} ({best['under_2_5']['bookmaker']})")
    
    if best['btts_yes']['value'] > 0:
        print(f"\n🎯 AMBOS MARCAM:")
        print(f"  Sim: {best['btts_yes']['value']:.2f} ({best['btts_yes']['bookmaker']})")
        print(f"  Não: {best['btts_no']['value']:.2f} ({best['btts_no']['bookmaker']})")
    
    return match, best


def exemplo_comparar_com_modelo():
    """Exemplo 2: Comparar odds do mercado com predições do modelo"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 2: COMPARAR ODDS COM MODELO")
    print("=" * 80)
    
    client = OddsAPIClient()
    
    # Busca odds
    odds = client.get_odds_with_cache('soccer_brazil_campeonato')
    
    if not odds:
        print("⚠️ Nenhuma partida disponível")
        return
    
    match = odds[0]
    
    print(f"\nPartida: {match['home_team']} vs {match['away_team']}")
    
    # SIMULAÇÃO: Em produção, você usaria dados reais
    # Aqui vamos simular probabilidades do modelo
    
    print("\n🤖 PROBABILIDADES DO MODELO (simuladas):")
    home_prob = 0.45  # 45% de chance de vitória da casa
    draw_prob = 0.28  # 28% de chance de empate
    away_prob = 0.27  # 27% de chance de vitória fora
    
    print(f"  Casa:   {home_prob*100:.1f}%")
    print(f"  Empate: {draw_prob*100:.1f}%")
    print(f"  Fora:   {away_prob*100:.1f}%")
    
    # Compara com mercado
    analysis = client.compare_with_predictions(
        match,
        home_prob,
        draw_prob,
        away_prob,
        min_value=1.05  # Mínimo 5% de value
    )
    
    # Mostra odds do mercado
    best = analysis['best_odds']
    print("\n📊 MELHORES ODDS DO MERCADO:")
    print(f"  Casa:   {best['home']['value']:.2f}")
    print(f"  Empate: {best['draw']['value']:.2f}")
    print(f"  Fora:   {best['away']['value']:.2f}")
    
    # Mostra odds implícitas do modelo
    model_odds = analysis['model_odds']
    print("\n🎯 ODDS IMPLÍCITAS DO MODELO:")
    print(f"  Casa:   {model_odds['home']:.2f}")
    print(f"  Empate: {model_odds['draw']:.2f}")
    print(f"  Fora:   {model_odds['away']:.2f}")
    
    # Mostra value bets
    print("\n💰 VALUE BETS ENCONTRADOS:")
    
    if analysis['value_bets']:
        for vb in analysis['value_bets']:
            outcome_label = {
                'home': 'Casa',
                'draw': 'Empate',
                'away': 'Fora'
            }[vb['outcome']]
            
            value_percent = (vb['value'] - 1) * 100
            
            print(f"\n  ✅ {outcome_label}")
            print(f"     Odd Mercado: {vb['market_odd']:.2f} ({vb['bookmaker']})")
            print(f"     Odd Modelo:  {vb['model_odd']:.2f}")
            print(f"     Value:       +{value_percent:.1f}%")
            print(f"     Recomendação: APOSTAR")
    else:
        print("  ⚠️ Nenhum value bet encontrado (odds do mercado estão ajustadas)")
    
    return analysis


def exemplo_analise_multiplas_partidas():
    """Exemplo 3: Analisar todas as partidas de uma liga"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 3: ANÁLISE DE MÚLTIPLAS PARTIDAS")
    print("=" * 80)
    
    client = OddsAPIClient()
    
    # Busca todas as partidas
    odds = client.get_odds_with_cache('soccer_brazil_campeonato')
    
    if not odds:
        print("⚠️ Nenhuma partida disponível")
        return
    
    print(f"\n📊 Analisando {len(odds)} partidas...\n")
    
    value_bets_encontrados = []
    
    for match in odds:
        # SIMULAÇÃO: Probabilidades fictícias
        # Em produção, você calcularia com seus modelos reais
        import random
        home_prob = random.uniform(0.3, 0.5)
        draw_prob = random.uniform(0.2, 0.3)
        away_prob = 1 - home_prob - draw_prob
        
        # Analisa
        analysis = client.compare_with_predictions(
            match,
            home_prob,
            draw_prob,
            away_prob,
            min_value=1.10  # Procura value > 10%
        )
        
        # Se encontrou value bets
        if analysis['value_bets']:
            value_bets_encontrados.append({
                'match': analysis['match'],
                'value_bets': analysis['value_bets']
            })
    
    # Mostra resultados
    print("=" * 80)
    print(f"🎯 RESUMO DA ANÁLISE")
    print("=" * 80)
    print(f"\nPartidas analisadas: {len(odds)}")
    print(f"Value bets encontrados: {len(value_bets_encontrados)}")
    
    if value_bets_encontrados:
        print("\n💰 OPORTUNIDADES ENCONTRADAS:\n")
        
        for idx, item in enumerate(value_bets_encontrados, 1):
            print(f"[{idx}] {item['match']}")
            
            for vb in item['value_bets']:
                outcome_label = {
                    'home': 'Casa',
                    'draw': 'Empate',
                    'away': 'Fora'
                }[vb['outcome']]
                
                value_percent = (vb['value'] - 1) * 100
                
                print(f"    • {outcome_label}: {vb['market_odd']:.2f} "
                      f"(+{value_percent:.1f}% value) - {vb['bookmaker']}")
            print()
    else:
        print("\n⚠️ Nenhuma oportunidade de value betting encontrada nesta rodada")


def exemplo_economizar_requisicoes():
    """Exemplo 4: Como usar cache para economizar requisições"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 4: ECONOMIZAR REQUISIÇÕES COM CACHE")
    print("=" * 80)
    
    client = OddsAPIClient()
    
    print("\n1️⃣ Primeira busca (vai usar API):")
    odds1 = client.get_odds_with_cache(
        'soccer_brazil_campeonato',
        max_cache_age_hours=6
    )
    
    print(f"\n✅ {len(odds1)} partidas carregadas")
    
    print("\n2️⃣ Segunda busca (vai usar CACHE):")
    odds2 = client.get_odds_with_cache(
        'soccer_brazil_campeonato',
        max_cache_age_hours=6
    )
    
    print(f"\n✅ {len(odds2)} partidas carregadas")
    
    print("\n💡 DICA:")
    print("  - A segunda busca usou CACHE (0 requisições)")
    print("  - Cache válido por 6 horas")
    print("  - Economize requisições buscando uma vez e reutilizando")
    print("  - Para apostas intraday, cache de 1-3 horas é suficiente")


def exemplo_criar_relatorio_diario():
    """Exemplo 5: Criar relatório diário de odds"""
    print("\n\n" + "=" * 80)
    print("EXEMPLO 5: RELATÓRIO DIÁRIO DE ODDS")
    print("=" * 80)
    
    client = OddsAPIClient()
    
    ligas = ['BSA', 'PL']  # Brasileirão e Premier League
    
    relatorio = []
    
    for liga in ligas:
        try:
            odds = client.get_odds_by_league_code(liga)
            
            for match in odds:
                best = client.get_best_odds(match)
                
                relatorio.append({
                    'Liga': liga,
                    'Casa': match['home_team'],
                    'Fora': match['away_team'],
                    'Data': match['commence_time'],
                    'Odd Casa': best['home']['value'],
                    'Odd Empate': best['draw']['value'],
                    'Odd Fora': best['away']['value'],
                    'Casas': len(match['bookmakers'])
                })
        except Exception as e:
            print(f"⚠️ Erro ao buscar {liga}: {e}")
    
    if relatorio:
        # Cria DataFrame
        df = pd.DataFrame(relatorio)
        
        print("\n📊 RELATÓRIO DE ODDS:\n")
        print(df.to_string(index=False))
        
        # Salva em CSV
        filename = 'relatorio_odds_diario.csv'
        df.to_csv(filename, index=False)
        print(f"\n💾 Relatório salvo em: {filename}")
    else:
        print("\n⚠️ Nenhuma partida disponível no momento")


def main():
    """Executa todos os exemplos"""
    print("\n")
    print("=" * 80)
    print("🎯 EXEMPLOS DE INTEGRAÇÃO - ODDS API + MODELOS")
    print("=" * 80)
    print()
    print("⚠️ IMPORTANTE:")
    print("   - Configure sua ODDS_API_KEY no arquivo .env")
    print("   - Estes exemplos usam dados SIMULADOS")
    print("   - Em produção, use seus modelos reais (Ensemble, Dixon-Coles, etc)")
    print()
    input("Pressione ENTER para continuar...")
    
    try:
        # Exemplo 1: Buscar odds
        exemplo_buscar_odds_partida()
        
        # Exemplo 2: Comparar com modelo
        exemplo_comparar_com_modelo()
        
        # Exemplo 3: Análise múltiplas partidas
        exemplo_analise_multiplas_partidas()
        
        # Exemplo 4: Economizar requisições
        exemplo_economizar_requisicoes()
        
        # Exemplo 5: Relatório diário
        exemplo_criar_relatorio_diario()
        
        print("\n\n" + "=" * 80)
        print("✅ TODOS OS EXEMPLOS CONCLUÍDOS!")
        print("=" * 80)
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Configure sua API Key")
        print("   2. Execute: python exemplo_integracao_odds.py")
        print("   3. Adapte os exemplos para seu sistema")
        print("   4. Integre com seus modelos reais")
        print("   5. Configure coleta diária automatizada")
        print()
        
    except ValueError as e:
        print(f"\n❌ Erro de configuração: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   1. Crie conta em: https://the-odds-api.com/")
        print("   2. Pegue sua API Key")
        print("   3. Configure no arquivo .env:")
        print("      ODDS_API_KEY=sua_key_aqui")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()

