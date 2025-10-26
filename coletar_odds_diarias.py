"""
Script para coletar odds diárias das principais ligas
Execute diariamente para ter dados atualizados
"""
import os
import json
from datetime import datetime
from odds_api_client import OddsAPIClient
from config import LEAGUES


def coletar_odds_todas_ligas(save_summary: bool = True):
    """
    Coleta odds de todas as ligas configuradas
    
    Args:
        save_summary: Se True, salva um resumo consolidado
    """
    try:
        client = OddsAPIClient()
        
        print("=" * 80)
        print("🎯 COLETA DIÁRIA DE ODDS")
        print("=" * 80)
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print()
        
        todas_odds = {}
        resumo = {
            'timestamp': datetime.now().isoformat(),
            'ligas': {},
            'total_partidas': 0
        }
        
        # Para cada liga configurada
        for league_name, league_info in LEAGUES.items():
            league_code = league_info['code']
            
            print(f"\n📊 {league_name} ({league_code})")
            print("-" * 80)
            
            try:
                # Busca odds (usa cache se disponível e recente)
                odds = client.get_odds_by_league_code(
                    league_code,
                    regions='us,uk,eu',
                    markets='h2h,totals'
                )
                
                num_matches = len(odds)
                print(f"✅ {num_matches} partidas encontradas")
                
                # Guarda dados
                todas_odds[league_code] = odds
                
                # Atualiza resumo
                resumo['ligas'][league_code] = {
                    'nome': league_name,
                    'num_partidas': num_matches,
                    'partidas': []
                }
                resumo['total_partidas'] += num_matches
                
                # Adiciona resumo das partidas
                for match in odds:
                    best_odds = client.get_best_odds(match)
                    
                    partida_resumo = {
                        'home_team': match['home_team'],
                        'away_team': match['away_team'],
                        'commence_time': match['commence_time'],
                        'odds_casa': best_odds['home']['value'],
                        'odds_empate': best_odds['draw']['value'],
                        'odds_fora': best_odds['away']['value'],
                        'num_bookmakers': len(match.get('bookmakers', []))
                    }
                    
                    resumo['ligas'][league_code]['partidas'].append(partida_resumo)
                    
                    print(f"  • {match['home_team']} vs {match['away_team']}")
                    print(f"    Odds: {best_odds['home']['value']:.2f} / "
                          f"{best_odds['draw']['value']:.2f} / "
                          f"{best_odds['away']['value']:.2f}")
                
            except ValueError as e:
                print(f"⚠️ Liga não disponível: {e}")
            except Exception as e:
                print(f"❌ Erro ao coletar {league_name}: {e}")
        
        # Salva resumo consolidado
        if save_summary and resumo['total_partidas'] > 0:
            os.makedirs('data/odds_daily', exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = f"data/odds_daily/resumo_{timestamp}.json"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(resumo, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 80)
            print(f"💾 Resumo salvo em: {summary_file}")
            print(f"📊 Total: {resumo['total_partidas']} partidas coletadas")
            print("=" * 80)
        
        return todas_odds, resumo
        
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        return None, None


def coletar_odds_liga_especifica(league_code: str):
    """
    Coleta odds de uma liga específica
    
    Args:
        league_code: Código da liga (BSA, PL, etc)
    """
    try:
        client = OddsAPIClient()
        
        print("=" * 80)
        print(f"🎯 COLETA DE ODDS - {league_code}")
        print("=" * 80)
        
        odds = client.get_odds_by_league_code(
            league_code,
            regions='us,uk,eu',
            markets='h2h,totals'
        )
        
        print(f"\n✅ {len(odds)} partidas encontradas\n")
        
        for idx, match in enumerate(odds, 1):
            print(f"[{idx}] {match['home_team']} vs {match['away_team']}")
            print(f"    Data: {match['commence_time']}")
            
            best = client.get_best_odds(match)
            
            print(f"    Melhores Odds:")
            print(f"      Casa:   {best['home']['value']:.2f} ({best['home']['bookmaker']})")
            print(f"      Empate: {best['draw']['value']:.2f} ({best['draw']['bookmaker']})")
            print(f"      Fora:   {best['away']['value']:.2f} ({best['away']['bookmaker']})")
            print()
        
        return odds
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def mostrar_ultimas_coletas():
    """Mostra as últimas coletas realizadas"""
    daily_dir = 'data/odds_daily'
    
    if not os.path.exists(daily_dir):
        print("⚠️ Nenhuma coleta realizada ainda")
        return
    
    files = sorted(
        [f for f in os.listdir(daily_dir) if f.startswith('resumo_')],
        reverse=True
    )
    
    if not files:
        print("⚠️ Nenhuma coleta encontrada")
        return
    
    print("=" * 80)
    print("📚 ÚLTIMAS COLETAS")
    print("=" * 80)
    
    for idx, filename in enumerate(files[:5], 1):  # Mostra últimas 5
        filepath = os.path.join(daily_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        timestamp = datetime.fromisoformat(data['timestamp'])
        
        print(f"\n[{idx}] {timestamp.strftime('%d/%m/%Y %H:%M')}")
        print(f"    Total: {data['total_partidas']} partidas")
        print(f"    Ligas: {', '.join(data['ligas'].keys())}")


def main():
    """Menu interativo"""
    import sys
    
    print("\n")
    print("=" * 80)
    print("🎯 COLETOR DE ODDS - THE ODDS API")
    print("=" * 80)
    print("\nOpções:")
    print("1. Coletar odds de TODAS as ligas")
    print("2. Coletar odds do BRASILEIRÃO (BSA)")
    print("3. Coletar odds da PREMIER LEAGUE (PL)")
    print("4. Ver últimas coletas")
    print("5. Sair")
    
    if len(sys.argv) > 1:
        # Modo command line
        opcao = sys.argv[1]
    else:
        # Modo interativo
        opcao = input("\nEscolha uma opção (1-5): ").strip()
    
    if opcao == '1':
        coletar_odds_todas_ligas()
    elif opcao == '2':
        coletar_odds_liga_especifica('BSA')
    elif opcao == '3':
        coletar_odds_liga_especifica('PL')
    elif opcao == '4':
        mostrar_ultimas_coletas()
    elif opcao == '5':
        print("👋 Até logo!")
    else:
        print("❌ Opção inválida")


if __name__ == "__main__":
    main()

