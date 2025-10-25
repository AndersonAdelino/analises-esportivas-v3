"""
Teste da Betfair API - Exchange de Apostas

IMPORTANTE: Betfair está bloqueada no Brasil
Você precisa de VPN ou Proxy para acessar

REQUISITOS:
1. Conta na Betfair (internacional)
2. App Key (grátis)
3. VPN/Proxy conectado

DOCUMENTAÇÃO:
https://docs.developer.betfair.com/
"""

import requests
import json
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO
# ==========================================

# 1. Suas credenciais Betfair
BETFAIR_USERNAME = 'SEU_USERNAME'  # ← Seu login
BETFAIR_PASSWORD = 'SUA_SENHA'     # ← Sua senha
BETFAIR_APP_KEY = 'SUA_APP_KEY'    # ← Pegue em: https://myaccount.betfair.com/developer/

# 2. URLs da API
LOGIN_URL = 'https://identitysso-cert.betfair.com/api/certlogin'
API_URL = 'https://api.betfair.com/exchange/betting/json-rpc/v1'

# 3. Configuração de Proxy/VPN (se necessário)
USE_PROXY = False  # Mude para True se usar proxy

PROXIES = {
    'http': 'http://seu-proxy:porta',
    'https': 'https://seu-proxy:porta'
} if USE_PROXY else None

# ==========================================
# FUNÇÕES DE AUTENTICAÇÃO
# ==========================================

def login_betfair(username, password, app_key):
    """
    Faz login na Betfair e retorna o session token
    
    IMPORTANTE: Betfair usa certificado SSL para login
    Para produção, você precisa de um certificado válido
    """
    print("=" * 80)
    print("TESTE 1: LOGIN NA BETFAIR")
    print("=" * 80)
    
    headers = {
        'X-Application': app_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'username': username,
        'password': password
    }
    
    try:
        print("\nTentando login...")
        print("⚠️ Se der erro de SSL, é porque precisa de certificado")
        print("⚠️ Se der timeout, é porque está bloqueado no Brasil")
        
        response = requests.post(
            LOGIN_URL,
            headers=headers,
            data=data,
            proxies=PROXIES,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('sessionToken'):
                print("✅ LOGIN OK!")
                print(f"Session Token: {result['sessionToken'][:20]}...")
                return result['sessionToken']
            else:
                print("❌ LOGIN FALHOU!")
                print(f"Status: {result.get('loginStatus')}")
                return None
        else:
            print(f"❌ ERRO HTTP: {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT!")
        print("\n🔒 BETFAIR ESTÁ BLOQUEADA NO BRASIL")
        print("\nSOLUÇÕES:")
        print("1. Use uma VPN (ExpressVPN, NordVPN, etc)")
        print("2. Use um proxy SOCKS5")
        print("3. Configure um servidor proxy próprio")
        return None
        
    except requests.exceptions.SSLError as e:
        print("❌ ERRO DE SSL!")
        print("\nPROBLEMA: Betfair requer certificado SSL para login")
        print("\nSOLUÇÕES:")
        print("1. Para teste: use requests com verify=False (INSEGURO)")
        print("2. Para produção: gere certificado em https://myaccount.betfair.com/developer/")
        return None
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


def call_betfair_api(session_token, app_key, method, params=None):
    """
    Faz chamada à API da Betfair
    """
    if params is None:
        params = {}
    
    headers = {
        'X-Application': app_key,
        'X-Authentication': session_token,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'jsonrpc': '2.0',
        'method': f'SportsAPING/v1.0/{method}',
        'params': params,
        'id': 1
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            proxies=PROXIES,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ ERRO: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


# ==========================================
# FUNÇÕES DE TESTE
# ==========================================

def list_event_types(session_token, app_key):
    """
    Lista tipos de eventos (esportes)
    """
    print("\n" + "=" * 80)
    print("TESTE 2: LISTAR ESPORTES")
    print("=" * 80)
    
    params = {
        'filter': {}
    }
    
    result = call_betfair_api(session_token, app_key, 'listEventTypes', params)
    
    if result and 'result' in result:
        event_types = result['result']
        
        print(f"\n✅ {len(event_types)} esportes encontrados\n")
        
        # Procura futebol
        football_id = None
        for event_type in event_types:
            name = event_type['eventType']['name']
            type_id = event_type['eventType']['id']
            count = event_type['marketCount']
            
            print(f"  {name:30s} (ID: {type_id}, Mercados: {count})")
            
            if 'Soccer' in name or 'Football' in name:
                football_id = type_id
        
        return football_id
    else:
        print("❌ Erro ao buscar esportes")
        return None


def list_competitions(session_token, app_key, event_type_id='1'):
    """
    Lista competições de futebol
    """
    print("\n" + "=" * 80)
    print("TESTE 3: LISTAR COMPETIÇÕES")
    print("=" * 80)
    
    params = {
        'filter': {
            'eventTypeIds': [event_type_id]
        }
    }
    
    result = call_betfair_api(session_token, app_key, 'listCompetitions', params)
    
    if result and 'result' in result:
        competitions = result['result']
        
        print(f"\n✅ {len(competitions)} competições encontradas\n")
        
        # Organiza por região
        brazilian = []
        european = []
        others = []
        
        for comp in competitions[:20]:  # Mostra só as 20 primeiras
            name = comp['competition']['name']
            comp_id = comp['competition']['id']
            count = comp['marketCount']
            
            info = f"{name:50s} (ID: {comp_id}, Mercados: {count})"
            
            if 'Brazil' in name or 'Brasileir' in name:
                brazilian.append(info)
            elif any(x in name for x in ['England', 'Spain', 'Italy', 'Germany', 'France', 'Champions']):
                european.append(info)
            else:
                others.append(info)
        
        if brazilian:
            print("BRASIL:")
            for item in brazilian:
                print(f"  {item}")
        
        if european:
            print("\nEUROPA:")
            for item in european[:10]:
                print(f"  {item}")
        
        # Retorna ID do Brasileirão se existir
        brasileirao = next((c for c in competitions if 'Brasileir' in c['competition']['name']), None)
        return brasileirao['competition']['id'] if brasileirao else None
    else:
        print("❌ Erro ao buscar competições")
        return None


def list_market_catalogue(session_token, app_key, competition_id=None):
    """
    Lista mercados (partidas) de uma competição
    """
    print("\n" + "=" * 80)
    print("TESTE 4: LISTAR PARTIDAS E ODDS")
    print("=" * 80)
    
    filter_params = {
        'eventTypeIds': ['1'],  # Futebol
        'marketTypeCodes': ['MATCH_ODDS'],  # 1X2
        'marketStartTime': {
            'from': datetime.now().isoformat() + 'Z'
        }
    }
    
    if competition_id:
        filter_params['competitionIds'] = [competition_id]
    
    params = {
        'filter': filter_params,
        'maxResults': 10,
        'marketProjection': [
            'RUNNER_DESCRIPTION',
            'MARKET_START_TIME'
        ]
    }
    
    result = call_betfair_api(session_token, app_key, 'listMarketCatalogue', params)
    
    if result and 'result' in result:
        markets = result['result']
        
        print(f"\n✅ {len(markets)} partidas encontradas\n")
        
        for idx, market in enumerate(markets[:5], 1):
            print(f"[{idx}] {market['event']['name']}")
            print(f"    Market ID: {market['marketId']}")
            print(f"    Data: {market['marketStartTime']}")
            print(f"    Competição: {market['competition']['name']}")
            print()
        
        # Retorna primeiro market_id para buscar odds
        return markets[0]['marketId'] if markets else None
    else:
        print("❌ Erro ao buscar partidas")
        return None


def get_market_odds(session_token, app_key, market_id):
    """
    Busca odds de um mercado específico
    """
    print("\n" + "=" * 80)
    print("TESTE 5: BUSCAR ODDS (BACK/LAY)")
    print("=" * 80)
    
    params = {
        'marketIds': [market_id],
        'priceProjection': {
            'priceData': ['EX_BEST_OFFERS']  # Melhores odds disponíveis
        }
    }
    
    result = call_betfair_api(session_token, app_key, 'listMarketBook', params)
    
    if result and 'result' in result:
        market_book = result['result'][0]
        
        print(f"\nMarket ID: {market_book['marketId']}")
        print(f"Status: {market_book['status']}")
        print(f"Total Matched: £{market_book.get('totalMatched', 0):,.2f}\n")
        
        print("ODDS DISPONÍVEIS:")
        print("-" * 80)
        print(f"{'Seleção':30s} {'Back (Apostar)':>20s} {'Lay (Contra)':>20s}")
        print("-" * 80)
        
        for runner in market_book['runners']:
            selection_id = runner['selectionId']
            status = runner['status']
            
            # Back odds (apostar a favor)
            back_odds = runner.get('ex', {}).get('availableToBack', [])
            back_str = f"{back_odds[0]['price']:.2f} (£{back_odds[0]['size']:,.0f})" if back_odds else "N/A"
            
            # Lay odds (apostar contra)
            lay_odds = runner.get('ex', {}).get('availableToLay', [])
            lay_str = f"{lay_odds[0]['price']:.2f} (£{lay_odds[0]['size']:,.0f})" if lay_odds else "N/A"
            
            # Nome da seleção (você precisaria buscar do market catalogue)
            selection_name = f"Selection {selection_id}"
            
            print(f"{selection_name:30s} {back_str:>20s} {lay_str:>20s}")
        
        print("\n💡 EXPLICAÇÃO:")
        print("  BACK = Apostar que VAI acontecer (como casa de aposta normal)")
        print("  LAY = Apostar que NÃO VAI acontecer (você é a casa)")
        print("  Preço (£Volume) = Odd disponível e quanto está disponível para apostar")
        
        return market_book
    else:
        print("❌ Erro ao buscar odds")
        return None


# ==========================================
# SOLUÇÕES PARA BLOQUEIO
# ==========================================

def show_vpn_solutions():
    """
    Mostra soluções para contornar bloqueio
    """
    print("\n" + "=" * 80)
    print("SOLUÇÕES PARA BLOQUEIO GEOGRÁFICO")
    print("=" * 80)
    
    print("\n1️⃣ VPN (Mais Fácil)")
    print("-" * 80)
    print("VPNs Recomendadas:")
    print("  • ExpressVPN - Rápido, estável")
    print("  • NordVPN - Barato, muitos servidores")
    print("  • ProtonVPN - Plano grátis disponível")
    print("\nComo usar:")
    print("  1. Instale a VPN")
    print("  2. Conecte em servidor UK/Europa")
    print("  3. Execute o script")
    
    print("\n2️⃣ Proxy SOCKS5 (Avançado)")
    print("-" * 80)
    print("Serviços de Proxy:")
    print("  • Bright Data (ex-Luminati)")
    print("  • Oxylabs")
    print("  • SmartProxy")
    print("\nConfigure em test_betfair_api.py:")
    print("  USE_PROXY = True")
    print("  PROXIES = {'http': 'socks5://user:pass@host:port'}")
    
    print("\n3️⃣ Servidor Próprio (Profissional)")
    print("-" * 80)
    print("  1. Alugue VPS fora do Brasil (DigitalOcean, AWS, etc)")
    print("  2. Configure proxy/VPN no VPS")
    print("  3. Conecte seu script ao VPS")
    
    print("\n4️⃣ requests-VPN (Python)")
    print("-" * 80)
    print("Instale:")
    print("  pip install requests[socks]")
    print("  pip install pysocks")
    print("\nUse com SOCKS5:")
    print("  session = requests.Session()")
    print("  session.proxies = {'http': 'socks5://...', 'https': 'socks5://...'}")


# ==========================================
# MAIN
# ==========================================

def main():
    print("\n")
    print("=" * 80)
    print("BETFAIR API - TESTE COMPLETO")
    print("=" * 80)
    
    print("\n⚠️ IMPORTANTE:")
    print("Betfair está bloqueada no Brasil.")
    print("Você PRECISA de VPN ou Proxy para testar.")
    
    # Verifica configuração
    if BETFAIR_USERNAME == 'SEU_USERNAME':
        print("\n❌ CONFIGURE SUAS CREDENCIAIS PRIMEIRO!")
        print("\nPASSOS:")
        print("1. Crie conta na Betfair (internacional)")
        print("2. Pegue App Key em: https://myaccount.betfair.com/developer/")
        print("3. Configure neste arquivo:")
        print("   - BETFAIR_USERNAME")
        print("   - BETFAIR_PASSWORD")
        print("   - BETFAIR_APP_KEY")
        print("4. Conecte VPN em servidor UK/Europa")
        print("5. Execute novamente")
        
        show_vpn_solutions()
        return
    
    print("\n🔐 Conectando VPN...")
    print("Se você NÃO está usando VPN, conecte agora e execute novamente!")
    input("\nPressione ENTER quando estiver conectado na VPN...")
    
    # Tenta login
    session_token = login_betfair(BETFAIR_USERNAME, BETFAIR_PASSWORD, BETFAIR_APP_KEY)
    
    if not session_token:
        print("\n❌ NÃO FOI POSSÍVEL FAZER LOGIN")
        show_vpn_solutions()
        return
    
    # Testes
    football_id = list_event_types(session_token, BETFAIR_APP_KEY)
    
    if football_id:
        comp_id = list_competitions(session_token, BETFAIR_APP_KEY, football_id)
        market_id = list_market_catalogue(session_token, BETFAIR_APP_KEY, comp_id)
        
        if market_id:
            get_market_odds(session_token, BETFAIR_APP_KEY, market_id)
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO!")
    print("=" * 80)
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Se funcionou → Posso integrar no Streamlit")
    print("2. Se não funcionou → Tente outra solução de VPN/Proxy")
    print("3. Dúvidas → Me pergunte!")


if __name__ == "__main__":
    main()

