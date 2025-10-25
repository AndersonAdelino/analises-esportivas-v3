"""
Exemplos de uso do cliente da API Football-Data
"""
from api_client import FootballDataClient
import pandas as pd


def exemplo_basico():
    """Exemplo básico de uso"""
    print("="*60)
    print("EXEMPLO 1: Buscar partidas recentes da Premier League")
    print("="*60)
    
    client = FootballDataClient()
    
    # Busca últimas 10 partidas finalizadas
    matches = client.get_competition_matches('PL', status='FINISHED', limit=10)
    
    print(f"\nTotal de partidas encontradas: {matches.get('resultSet', {}).get('count', 0)}")
    
    for match in matches['matches'][:5]:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        score_home = match['score']['fullTime']['home']
        score_away = match['score']['fullTime']['away']
        date = match['utcDate'][:10]
        
        print(f"{date}: {home} {score_home} x {score_away} {away}")


def exemplo_time_especifico():
    """Busca partidas de um time específico"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Buscar partidas do Manchester United")
    print("="*60)
    
    client = FootballDataClient()
    
    # Manchester United ID = 66
    man_utd_id = 66
    
    matches = client.get_team_matches(man_utd_id, status='FINISHED', limit=5)
    
    print(f"\nÚltimas 5 partidas do Manchester United:")
    
    for match in matches['matches']:
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        score_home = match['score']['fullTime']['home']
        score_away = match['score']['fullTime']['away']
        date = match['utcDate'][:10]
        
        print(f"{date}: {home} {score_home} x {score_away} {away}")


def exemplo_classificacao():
    """Busca classificação da Premier League"""
    print("\n" + "="*60)
    print("EXEMPLO 3: Classificação da Premier League")
    print("="*60)
    
    client = FootballDataClient()
    
    standings = client.get_competition_standings('PL')
    
    table = standings['standings'][0]['table']
    
    print(f"\n{'Pos':<4} {'Time':<30} {'J':<4} {'V':<4} {'E':<4} {'D':<4} {'GP':<4} {'GC':<4} {'SG':<5} {'Pts':<4}")
    print("-" * 90)
    
    for team in table[:10]:  # Top 10
        pos = team['position']
        name = team['team']['name'][:28]
        played = team['playedGames']
        won = team['won']
        draw = team['draw']
        lost = team['lost']
        gf = team['goalsFor']
        ga = team['goalsAgainst']
        gd = team['goalDifference']
        pts = team['points']
        
        print(f"{pos:<4} {name:<30} {played:<4} {won:<4} {draw:<4} {lost:<4} {gf:<4} {ga:<4} {gd:<5} {pts:<4}")


def exemplo_times_competicao():
    """Lista todos os times de uma competição"""
    print("\n" + "="*60)
    print("EXEMPLO 4: Times da Premier League")
    print("="*60)
    
    client = FootballDataClient()
    
    teams_data = client.get_competition_teams('PL')
    
    teams = teams_data['teams']
    
    print(f"\nTotal de times: {len(teams)}\n")
    
    for team in teams:
        print(f"ID: {team['id']:<6} | {team['name']:<35} | Fundado em: {team.get('founded', 'N/A')}")


def exemplo_info_time():
    """Informações detalhadas de um time"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Informações do Liverpool FC")
    print("="*60)
    
    client = FootballDataClient()
    
    # Liverpool ID = 64
    liverpool_id = 64
    
    team_info = client.get_team_info(liverpool_id)
    
    print(f"\nNome: {team_info['name']}")
    print(f"Nome curto: {team_info['shortName']}")
    print(f"TLA: {team_info['tla']}")
    print(f"Fundado em: {team_info.get('founded', 'N/A')}")
    print(f"Estádio: {team_info.get('venue', 'N/A')}")
    print(f"Cores: {team_info.get('clubColors', 'N/A')}")
    print(f"Website: {team_info.get('website', 'N/A')}")
    
    if 'squad' in team_info and team_info['squad']:
        print(f"\nElenco: {len(team_info['squad'])} jogadores")


if __name__ == "__main__":
    try:
        exemplo_basico()
        exemplo_time_especifico()
        exemplo_classificacao()
        exemplo_times_competicao()
        exemplo_info_time()
        
        print("\n" + "="*60)
        print("✨ Todos os exemplos executados com sucesso!")
        print("="*60)
        
    except ValueError as e:
        print(f"\n❌ Erro: {e}")
        print("\n💡 Configure sua API Key no arquivo .env")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

