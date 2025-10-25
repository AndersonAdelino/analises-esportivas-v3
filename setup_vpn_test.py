"""
Script auxiliar para testar se VPN está funcionando
Execute ANTES de tentar a Betfair API
"""

import requests
import json

def check_ip():
    """Verifica seu IP atual e localização"""
    print("=" * 80)
    print("TESTE 1: VERIFICAR SEU IP E LOCALIZAÇÃO")
    print("=" * 80)
    
    try:
        # Serviço gratuito de geolocalização
        response = requests.get('https://ipapi.co/json/', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Seu IP: {data.get('ip')}")
            print(f"✅ País: {data.get('country_name')} ({data.get('country_code')})")
            print(f"✅ Cidade: {data.get('city')}")
            print(f"✅ ISP: {data.get('org')}")
            
            if data.get('country_code') == 'BR':
                print("\n⚠️ VOCÊ ESTÁ NO BRASIL!")
                print("Betfair será BLOQUEADA.")
                print("\n👉 CONECTE A VPN e execute este script novamente.")
                return False
            else:
                print(f"\n✅ VOCÊ ESTÁ EM {data.get('country_name').upper()}!")
                print("Betfair deve funcionar! 🎉")
                return True
        else:
            print(f"❌ Erro ao verificar IP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def test_betfair_access():
    """Testa se consegue acessar o site da Betfair"""
    print("\n" + "=" * 80)
    print("TESTE 2: ACESSO AO SITE DA BETFAIR")
    print("=" * 80)
    
    try:
        print("\nTentando acessar www.betfair.com...")
        
        response = requests.get(
            'https://www.betfair.com',
            timeout=10,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            print("✅ SITE ACESSÍVEL!")
            print(f"Status: {response.status_code}")
            return True
        elif response.status_code == 403:
            print("❌ BLOQUEADO (403 Forbidden)")
            print("Seu IP está sendo bloqueado pela Betfair.")
            return False
        else:
            print(f"⚠️ Status: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT!")
        print("Não conseguiu conectar (pode estar bloqueado)")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_api_endpoint():
    """Testa endpoint da API (sem autenticação)"""
    print("\n" + "=" * 80)
    print("TESTE 3: ENDPOINT DA API")
    print("=" * 80)
    
    try:
        print("\nTentando ping na API...")
        
        # Endpoint simples que não requer autenticação
        response = requests.get(
            'https://api.betfair.com/exchange/betting/rest/v1.0/',
            timeout=10
        )
        
        # Qualquer resposta diferente de timeout significa que está acessível
        print(f"✅ API ACESSÍVEL!")
        print(f"Status: {response.status_code}")
        print("(Status 401/403 é normal sem autenticação)")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT!")
        print("API não está acessível")
        return False
    except Exception as e:
        print(f"⚠️ Erro: {e}")
        print("Mas isso pode ser normal sem autenticação")
        return None


def show_vpn_recommendations():
    """Mostra recomendações de VPN"""
    print("\n" + "=" * 80)
    print("RECOMENDAÇÕES DE VPN")
    print("=" * 80)
    
    print("\n🥇 OPÇÃO 1: ProtonVPN (GRÁTIS)")
    print("-" * 80)
    print("Link: https://protonvpn.com/")
    print("Custo: R$ 0")
    print("Servidores grátis: Holanda, Japão, EUA")
    print("\nPASSOS:")
    print("  1. Baixe: https://protonvpn.com/download")
    print("  2. Crie conta (grátis)")
    print("  3. Instale o app")
    print("  4. Conecte em servidor Holanda ou EUA")
    print("  5. Execute este script novamente")
    
    print("\n🥈 OPÇÃO 2: NordVPN (PAGO)")
    print("-" * 80)
    print("Link: https://nordvpn.com/")
    print("Custo: R$ 30/mês (ou R$ 15/mês anual)")
    print("Trial: 30 dias garantia devolução")
    print("\nPASSOS:")
    print("  1. Assine: https://nordvpn.com/pricing/")
    print("  2. Baixe app")
    print("  3. Login")
    print("  4. Conecte em UK")
    print("  5. Execute este script novamente")
    
    print("\n🥉 OPÇÃO 3: ExpressVPN (PREMIUM)")
    print("-" * 80)
    print("Link: https://www.expressvpn.com/")
    print("Custo: R$ 50/mês (ou R$ 35/mês anual)")
    print("Trial: 30 dias garantia")
    print("\nMais rápido e estável, mas mais caro")


def main():
    print("\n")
    print("=" * 80)
    print("TESTE DE CONEXÃO - VPN/BETFAIR")
    print("=" * 80)
    print("\nEste script verifica:")
    print("  1. Seu IP e localização atual")
    print("  2. Se consegue acessar Betfair")
    print("  3. Se a API está acessível")
    print("\n")
    
    # Teste 1: IP
    in_brazil = check_ip()
    
    if in_brazil is False:
        # Está no Brasil
        show_vpn_recommendations()
        
        print("\n" + "=" * 80)
        print("PRÓXIMOS PASSOS")
        print("=" * 80)
        print("\n1. Instale uma VPN (recomendo ProtonVPN grátis)")
        print("2. Conecte em servidor fora do Brasil")
        print("3. Execute este script novamente:")
        print("   python setup_vpn_test.py")
        print("4. Se passar nos testes, execute:")
        print("   python test_betfair_api.py")
        return
    
    elif in_brazil is True:
        # Está fora do Brasil (VPN conectada)
        print("\n👍 VPN conectada com sucesso!")
        
        # Teste 2: Site
        site_ok = test_betfair_access()
        
        # Teste 3: API
        api_ok = test_api_endpoint()
        
        # Resumo
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        
        print(f"\n1. IP fora do Brasil: {'✅' if in_brazil else '❌'}")
        print(f"2. Site acessível: {'✅' if site_ok else '❌'}")
        print(f"3. API acessível: {'✅' if api_ok else '❌'}")
        
        if in_brazil and (site_ok or api_ok):
            print("\n" + "=" * 80)
            print("🎉 TUDO OK! VOCÊ PODE USAR A BETFAIR API!")
            print("=" * 80)
            print("\nPRÓXIMOS PASSOS:")
            print("1. Configure suas credenciais em test_betfair_api.py")
            print("2. Execute: python test_betfair_api.py")
        else:
            print("\n" + "=" * 80)
            print("⚠️ ALGUNS TESTES FALHARAM")
            print("=" * 80)
            print("\nPOSSÍVEIS CAUSAS:")
            print("- VPN instável (tente outro servidor)")
            print("- Betfair detectou VPN (use VPN premium)")
            print("- Firewall bloqueando conexão")
            print("\nRECOMENDAÇÃO:")
            print("- Tente NordVPN ou ExpressVPN")
            print("- Conecte em servidor UK")
    
    else:
        # Erro ao verificar
        print("\n⚠️ Não foi possível verificar seu IP")
        print("Mas você pode tentar continuar mesmo assim...")


if __name__ == "__main__":
    main()

