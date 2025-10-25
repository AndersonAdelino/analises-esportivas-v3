"""
Análise básica dos dados históricos da Premier League
"""
import pandas as pd
import os
from glob import glob


def encontrar_ultimo_csv():
    """Encontra o arquivo CSV mais recente na pasta data"""
    csv_files = glob('data/premier_league_matches_*.csv')
    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta data/")
    return max(csv_files, key=os.path.getctime)


def analise_basica():
    """Realiza análise básica dos dados da Premier League"""
    
    # Carrega o CSV mais recente
    csv_file = encontrar_ultimo_csv()
    print("=" * 70)
    print("ANALISE DE DADOS - PREMIER LEAGUE")
    print("=" * 70)
    print(f"Arquivo: {csv_file}\n")
    
    df = pd.read_csv(csv_file)
    
    # Informações gerais
    print("1. INFORMACOES GERAIS")
    print("-" * 70)
    print(f"Total de partidas: {len(df)}")
    print(f"Periodo: {df['data'].min()[:10]} ate {df['data'].max()[:10]}")
    print(f"Rodadas: {df['rodada'].min()} ate {df['rodada'].max()}")
    print(f"Times unicos: {len(set(df['time_casa'].unique()) | set(df['time_visitante'].unique()))}")
    
    # Estatísticas de gols
    print("\n2. ESTATISTICAS DE GOLS")
    print("-" * 70)
    total_gols = df['gols_casa'].sum() + df['gols_visitante'].sum()
    media_gols = total_gols / len(df)
    print(f"Total de gols: {total_gols}")
    print(f"Media de gols por partida: {media_gols:.2f}")
    print(f"Media de gols do time da casa: {df['gols_casa'].mean():.2f}")
    print(f"Media de gols do time visitante: {df['gols_visitante'].mean():.2f}")
    
    # Resultados
    print("\n3. DISTRIBUICAO DE RESULTADOS")
    print("-" * 70)
    vitorias_casa = len(df[df['vencedor'] == 'HOME_TEAM'])
    empates = len(df[df['vencedor'] == 'DRAW'])
    vitorias_fora = len(df[df['vencedor'] == 'AWAY_TEAM'])
    
    print(f"Vitorias do time da casa: {vitorias_casa} ({vitorias_casa/len(df)*100:.1f}%)")
    print(f"Empates: {empates} ({empates/len(df)*100:.1f}%)")
    print(f"Vitorias do visitante: {vitorias_fora} ({vitorias_fora/len(df)*100:.1f}%)")
    
    # Times com mais gols marcados
    print("\n4. TOP 10 TIMES - GOLS MARCADOS")
    print("-" * 70)
    
    # Gols como mandante
    gols_casa = df.groupby('time_casa')['gols_casa'].sum()
    # Gols como visitante
    gols_fora = df.groupby('time_visitante')['gols_visitante'].sum()
    
    # Total de gols por time
    todos_times = set(df['time_casa'].unique()) | set(df['time_visitante'].unique())
    gols_por_time = {}
    for time in todos_times:
        gols_casa_time = gols_casa.get(time, 0)
        gols_fora_time = gols_fora.get(time, 0)
        gols_por_time[time] = gols_casa_time + gols_fora_time
    
    # Ordena e exibe top 10
    top_gols = sorted(gols_por_time.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (time, gols) in enumerate(top_gols, 1):
        print(f"{i:2d}. {time:35s} - {gols:3d} gols")
    
    # Times com mais gols sofridos
    print("\n5. TOP 10 TIMES - GOLS SOFRIDOS")
    print("-" * 70)
    
    # Gols sofridos como mandante
    gols_sofridos_casa = df.groupby('time_casa')['gols_visitante'].sum()
    # Gols sofridos como visitante
    gols_sofridos_fora = df.groupby('time_visitante')['gols_casa'].sum()
    
    # Total de gols sofridos por time
    gols_sofridos_por_time = {}
    for time in todos_times:
        sofridos_casa = gols_sofridos_casa.get(time, 0)
        sofridos_fora = gols_sofridos_fora.get(time, 0)
        gols_sofridos_por_time[time] = sofridos_casa + sofridos_fora
    
    # Ordena e exibe top 10
    top_sofridos = sorted(gols_sofridos_por_time.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (time, gols) in enumerate(top_sofridos, 1):
        print(f"{i:2d}. {time:35s} - {gols:3d} gols sofridos")
    
    # Maiores goleadas
    print("\n6. MAIORES GOLEADAS")
    print("-" * 70)
    df['diferenca'] = abs(df['gols_casa'] - df['gols_visitante'])
    maiores_goleadas = df.nlargest(5, 'diferenca')
    
    for idx, row in maiores_goleadas.iterrows():
        data = row['data'][:10]
        casa = row['time_casa']
        fora = row['time_visitante']
        placar = f"{row['gols_casa']} x {row['gols_visitante']}"
        diff = row['diferenca']
        print(f"{data} - {casa:25s} {placar:7s} {fora:25s} (Diferenca: {int(diff)})")
    
    # Partidas com mais gols
    print("\n7. PARTIDAS COM MAIS GOLS")
    print("-" * 70)
    df['total_gols'] = df['gols_casa'] + df['gols_visitante']
    mais_gols = df.nlargest(5, 'total_gols')
    
    for idx, row in mais_gols.iterrows():
        data = row['data'][:10]
        casa = row['time_casa']
        fora = row['time_visitante']
        placar = f"{row['gols_casa']} x {row['gols_visitante']}"
        total = row['total_gols']
        print(f"{data} - {casa:25s} {placar:7s} {fora:25s} (Total: {int(total)} gols)")
    
    print("\n" + "=" * 70)
    print("FIM DA ANALISE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        analise_basica()
    except FileNotFoundError as e:
        print(f"Erro: {e}")
        print("Execute primeiro: python get_historical_data.py")
    except Exception as e:
        print(f"Erro durante a analise: {e}")

