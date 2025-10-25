"""
Teste da The Odds API - Sistema de Busca de Odds
https://the-odds-api.com/

PASSO 1: Crie sua conta gratuita em:
https://the-odds-api.com/

PASSO 2: Pegue sua API Key em:
https://the-odds-api.com/account/

PASSO 3: Cole sua API Key abaixo e execute este script
"""

import requests
import json
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO
# ==========================================

# Cole sua API Key aqui (grátis: 500 requisições/mês)
API_KEY = 'SUA_API_KEY_AQUI'  # ← SUBSTITUA AQUI

# Regiões disponíveis
REGIONS = 'br,us,uk,eu'  # Brasil, USA, UK, Europa

# Mercados disponíveis
MARKETS = 'h2h,totals,btts'  # 1X2, Over/Under, Ambos Marcam

# Formato das odds
ODDS_FORMAT = 'decimal'  # decimal, american, fractional

# ==========================================
# FUNÇÕES DE TESTE
# ==========================================

def test_connection(api_key):
    """Testa conexão com a API"""
    print("=" * 80)
    print("TESTE 1: CONEXAO COM A API")
    print("=" * 80)
    
    url = 'https://api.the-odds-api.com/v4/sports'
    
    params = {
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print("✅ CONEXAO OK!")
            print(f"Status: {response.status_code}")
            
            # Mostra uso da quota
            remaining = response.headers.get('x-requests-remaining')
            used = response.headers.get('x-requests-used')
            
            if remaining:
                print(f"\nQuota Restante: {remaining} requisições")
                print(f"Quota Usada: {used} requisições")
            
            return True
        elif response.status_code == 401:
            print("❌ ERRO: API Key inválida")
            print("Verifique se você copiou a key corretamente")
            return False
        else:
            print(f"❌ ERRO: Status {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERRO DE CONEXAO: {e}")
        return False


def list_sports(api_key):
    """Lista todos os esportes disponíveis"""
    print("\n" + "=" * 80)
    print("TESTE 2: ESPORTES DISPONIVEIS")
    print("=" * 80)
    
    url = 'https://api.the-odds-api.com/v4/sports'
    
    params = {
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            sports = response.json()
            
            # Filtra apenas futebol
            soccer_sports = [s for s in sports if 'soccer' in s['key']]
            
            print(f"\nTotal de esportes: {len(sports)}")
            print(f"Ligas de Futebol disponíveis: {len(soccer_sports)}\n")
            
            print("LIGAS DE FUTEBOL:")
            print("-" * 80)
            
            # Organiza por continente
            leagues = {
                'Brasil': [],
                'Europa': [],
                'América': [],
                'Outros': []
            }
            
            for sport in soccer_sports:
                name = sport['title']
                key = sport['key']
                active = '🟢' if sport.get('active', False) else '🔴'
                
                if 'brazil' in key.lower():
                    leagues['Brasil'].append(f"{active} {name} ({key})")
                elif any(x in key.lower() for x in ['england', 'spain', 'italy', 'germany', 'france']):
                    leagues['Europa'].append(f"{active} {name} ({key})")
                elif any(x in key.lower() for x in ['usa', 'mexico', 'argentina']):
                    leagues['América'].append(f"{active} {name} ({key})")
                else:
                    leagues['Outros'].append(f"{active} {name} ({key})")
            
            for region, items in leagues.items():
                if items:
                    print(f"\n{region}:")
                    for item in items:
                        print(f"  {item}")
            
            # Retorna key do Brasileirão se existir
            brasileirao = next((s for s in soccer_sports if 'brazil' in s['key'].lower()), None)
            return brasileirao['key'] if brasileirao else None
            
        else:
            print(f"❌ ERRO: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


def get_odds_for_league(api_key, sport_key='soccer_brazil_campeonato'):
    """Busca odds de uma liga específica"""
    print("\n" + "=" * 80)
    print(f"TESTE 3: ODDS DA LIGA ({sport_key})")
    print("=" * 80)
    
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    
    params = {
        'apiKey': api_key,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Partidas encontradas: {len(data)}")
            
            if len(data) == 0:
                print("\n⚠️ Nenhuma partida disponível no momento")
                print("Isso pode significar:")
                print("  - Não há jogos agendados")
                print("  - A liga não está ativa")
                print("  - Tente outro sport_key")
                return None
            
            print("\n" + "-" * 80)
            print("PRIMEIRAS 3 PARTIDAS:")
            print("-" * 80)
            
            for idx, match in enumerate(data[:3], 1):
                print(f"\n[{idx}] {match['home_team']} vs {match['away_team']}")
                print(f"    Data: {match['commence_time']}")
                
                # Lista casas de apostas
                bookmakers = match.get('bookmakers', [])
                print(f"    Casas: {len(bookmakers)} disponíveis")
                
                if bookmakers:
                    # Pega primeira casa como exemplo
                    bookmaker = bookmakers[0]
                    print(f"\n    Exemplo: {bookmaker['title']}")
                    
                    for market in bookmaker.get('markets', []):
                        market_key = market['key']
                        
                        if market_key == 'h2h':  # 1X2
                            outcomes = market['outcomes']
                            for outcome in outcomes:
                                label = outcome['name']
                                odd = outcome['price']
                                
                                if label == match['home_team']:
                                    print(f"      Casa:   {odd}")
                                elif label == match['away_team']:
                                    print(f"      Fora:   {odd}")
                                else:
                                    print(f"      Empate: {odd}")
                        
                        elif market_key == 'totals':  # Over/Under
                            outcomes = market['outcomes']
                            for outcome in outcomes:
                                label = outcome['name']
                                odd = outcome['price']
                                point = outcome.get('point', '?')
                                print(f"      {label} {point}: {odd}")
                        
                        elif market_key == 'btts':  # Ambos Marcam
                            outcomes = market['outcomes']
                            for outcome in outcomes:
                                label = outcome['name']
                                odd = outcome['price']
                                print(f"      BTTS {label}: {odd}")
            
            # Salva dados completos em JSON
            filename = f'odds_api_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📁 Dados completos salvos em: {filename}")
            
            # Mostra quota restante
            remaining = response.headers.get('x-requests-remaining')
            if remaining:
                print(f"\n💰 Requisições restantes: {remaining}")
            
            return data
            
        elif response.status_code == 401:
            print("❌ ERRO: API Key inválida")
            return None
        elif response.status_code == 404:
            print(f"❌ ERRO: Liga '{sport_key}' não encontrada")
            return None
        else:
            print(f"❌ ERRO: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


def compare_bookmakers(api_key, sport_key='soccer_epl'):
    """Compara odds entre diferentes casas"""
    print("\n" + "=" * 80)
    print("TESTE 4: COMPARACAO DE CASAS DE APOSTAS")
    print("=" * 80)
    
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    
    params = {
        'apiKey': api_key,
        'regions': REGIONS,
        'markets': 'h2h',
        'oddsFormat': ODDS_FORMAT
    }
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                print("\n⚠️ Nenhuma partida disponível")
                return None
            
            # Pega primeira partida
            match = data[0]
            print(f"\nPartida: {match['home_team']} vs {match['away_team']}")
            print("-" * 80)
            
            bookmakers = match.get('bookmakers', [])
            
            if not bookmakers:
                print("Nenhuma odd disponível")
                return None
            
            print(f"\nComparando {len(bookmakers)} casas de apostas:\n")
            print(f"{'Casa':30s} {'Casa':>8s} {'Empate':>8s} {'Fora':>8s}")
            print("-" * 80)
            
            best_odds = {'home': 0, 'draw': 0, 'away': 0}
            best_bookmakers = {'home': '', 'draw': '', 'away': ''}
            
            for bookmaker in bookmakers:
                name = bookmaker['title']
                markets = bookmaker.get('markets', [])
                
                if markets and markets[0]['key'] == 'h2h':
                    outcomes = markets[0]['outcomes']
                    
                    odds = {}
                    for outcome in outcomes:
                        if outcome['name'] == match['home_team']:
                            odds['home'] = outcome['price']
                        elif outcome['name'] == match['away_team']:
                            odds['away'] = outcome['price']
                        else:
                            odds['draw'] = outcome['price']
                    
                    # Atualiza melhores odds
                    if odds.get('home', 0) > best_odds['home']:
                        best_odds['home'] = odds['home']
                        best_bookmakers['home'] = name
                    if odds.get('draw', 0) > best_odds['draw']:
                        best_odds['draw'] = odds['draw']
                        best_bookmakers['draw'] = name
                    if odds.get('away', 0) > best_odds['away']:
                        best_odds['away'] = odds['away']
                        best_bookmakers['away'] = name
                    
                    home_str = f"{odds.get('home', 0):.2f}"
                    draw_str = f"{odds.get('draw', 0):.2f}"
                    away_str = f"{odds.get('away', 0):.2f}"
                    
                    # Destaca melhores odds
                    if odds.get('home') == best_odds['home'] and best_odds['home'] > 0:
                        home_str = f"⭐{home_str}"
                    if odds.get('draw') == best_odds['draw'] and best_odds['draw'] > 0:
                        draw_str = f"⭐{draw_str}"
                    if odds.get('away') == best_odds['away'] and best_odds['away'] > 0:
                        away_str = f"⭐{away_str}"
                    
                    print(f"{name:30s} {home_str:>8s} {draw_str:>8s} {away_str:>8s}")
            
            print("\n" + "-" * 80)
            print("MELHORES ODDS:")
            print(f"  Casa:   {best_odds['home']:.2f} ({best_bookmakers['home']})")
            print(f"  Empate: {best_odds['draw']:.2f} ({best_bookmakers['draw']})")
            print(f"  Fora:   {best_odds['away']:.2f} ({best_bookmakers['away']})")
            
            return data
            
        else:
            print(f"❌ ERRO: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


def show_usage_stats(api_key):
    """Mostra estatísticas de uso da API"""
    print("\n" + "=" * 80)
    print("ESTATISTICAS DE USO")
    print("=" * 80)
    
    # Faz uma requisição leve só para pegar os headers
    url = 'https://api.the-odds-api.com/v4/sports'
    params = {'apiKey': api_key}
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            used = response.headers.get('x-requests-used', 'N/A')
            
            print(f"\n📊 Requisições Usadas: {used}")
            print(f"📊 Requisições Restantes: {remaining}")
            
            if remaining != 'N/A':
                total = int(remaining) + int(used)
                percent_used = (int(used) / total) * 100
                print(f"📊 Total: {total}")
                print(f"📊 Uso: {percent_used:.1f}%")
                
                # Barra de progresso
                bar_length = 50
                filled = int(bar_length * percent_used / 100)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\n[{bar}] {percent_used:.1f}%")
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")


# ==========================================
# MAIN
# ==========================================

def main():
    print("\n")
    print("=" * 80)
    print("THE ODDS API - TESTE COMPLETO")
    print("=" * 80)
    print("\n📋 ANTES DE COMEÇAR:")
    print("1. Crie conta gratuita em: https://the-odds-api.com/")
    print("2. Pegue sua API Key em: https://the-odds-api.com/account/")
    print("3. Cole a key no início deste arquivo (linha 19)")
    print("\n")
    
    if API_KEY == 'SUA_API_KEY_AQUI':
        print("❌ ERRO: Você precisa configurar sua API Key!")
        print("\nPASSOS:")
        print("1. Abra: test_odds_api.py")
        print("2. Linha 19: API_KEY = 'SUA_API_KEY_AQUI'")
        print("3. Substitua por sua key: API_KEY = 'abc123...'")
        print("4. Salve o arquivo")
        print("5. Execute novamente: python test_odds_api.py")
        return
    
    # Testa conexão
    if not test_connection(API_KEY):
        print("\n❌ Teste falhou na conexão")
        return
    
    # Lista esportes
    sport_key = list_sports(API_KEY)
    
    # Testa busca de odds
    if sport_key:
        get_odds_for_league(API_KEY, sport_key)
    
    # Testa Premier League (sempre disponível)
    print("\n\nTestando Premier League (geralmente tem mais dados)...")
    get_odds_for_league(API_KEY, 'soccer_epl')
    
    # Compara casas
    compare_bookmakers(API_KEY, 'soccer_epl')
    
    # Mostra uso
    show_usage_stats(API_KEY)
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO!")
    print("=" * 80)
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Se gostou, posso integrar no Streamlit")
    print("2. Você poderá buscar odds automaticamente")
    print("3. Sistema comparará com o modelo e mostrará value bets")
    print("\n")


if __name__ == "__main__":
    main()

