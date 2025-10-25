"""
Análise detalhada dos dados por time da Premier League
"""
import pandas as pd
import os
from glob import glob


def encontrar_ultimo_csv_times():
    """Encontra o arquivo CSV de times mais recente"""
    csv_files = glob('data/all_teams_matches_*.csv')
    if not csv_files:
        csv_files = glob('data/test_teams_matches_*.csv')
    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo de times encontrado. Execute primeiro: python get_team_matches.py")
    return max(csv_files, key=os.path.getctime)


def analise_por_time():
    """Análise detalhada por time"""
    
    # Carrega dados
    csv_file = encontrar_ultimo_csv_times()
    print("=" * 80)
    print("ANALISE DETALHADA POR TIME - PREMIER LEAGUE")
    print("=" * 80)
    print(f"Arquivo: {csv_file}\n")
    
    df = pd.read_csv(csv_file)
    
    # Informações gerais
    print("1. VISAO GERAL")
    print("-" * 80)
    print(f"Total de partidas analisadas: {len(df)}")
    print(f"Times analisados: {df['time'].nunique()}")
    print(f"Competicoes: {', '.join(df['competicao'].unique())}")
    print(f"Periodo: {df['data'].min()} ate {df['data'].max()}")
    
    # Calcula estatísticas por time
    times = df['time'].unique()
    stats_por_time = []
    
    for time in times:
        df_time = df[df['time'] == time]
        
        jogos = len(df_time)
        vitorias = len(df_time[df_time['resultado'] == 'Vitoria'])
        empates = len(df_time[df_time['resultado'] == 'Empate'])
        derrotas = len(df_time[df_time['resultado'] == 'Derrota'])
        
        gols_marcados = df_time['gols_marcados'].sum()
        gols_sofridos = df_time['gols_sofridos'].sum()
        saldo = gols_marcados - gols_sofridos
        
        # Aproveitamento (vitória = 3 pts, empate = 1 pt)
        pontos = vitorias * 3 + empates * 1
        aproveitamento = (pontos / (jogos * 3)) * 100 if jogos > 0 else 0
        
        # Desempenho casa vs fora
        casa = df_time[df_time['local'] == 'Casa']
        fora = df_time[df_time['local'] == 'Fora']
        
        vit_casa = len(casa[casa['resultado'] == 'Vitoria'])
        vit_fora = len(fora[fora['resultado'] == 'Vitoria'])
        
        stats_por_time.append({
            'Time': time,
            'Jogos': jogos,
            'V': vitorias,
            'E': empates,
            'D': derrotas,
            'GP': gols_marcados,
            'GC': gols_sofridos,
            'SG': saldo,
            'Pts': pontos,
            'Aprov%': aproveitamento,
            'V_Casa': vit_casa,
            'V_Fora': vit_fora
        })
    
    df_stats = pd.DataFrame(stats_por_time)
    df_stats = df_stats.sort_values('Pts', ascending=False).reset_index(drop=True)
    
    # Ranking geral
    print("\n2. RANKING GERAL (BASEADO EM TODAS AS COMPETICOES)")
    print("-" * 80)
    print(f"{'Pos':<4} {'Time':<35} {'J':<4} {'V':<4} {'E':<4} {'D':<4} {'GP':<4} {'GC':<4} {'SG':<5} {'Pts':<5} {'Aprov%':<7}")
    print("-" * 80)
    
    for idx, row in df_stats.head(20).iterrows():
        pos = idx + 1
        print(f"{pos:<4} {row['Time']:<35} {row['Jogos']:<4} {row['V']:<4} {row['E']:<4} {row['D']:<4} "
              f"{row['GP']:<4} {row['GC']:<4} {row['SG']:<5} {row['Pts']:<5} {row['Aprov%']:<7.1f}")
    
    # Top atacantes
    print("\n3. MELHORES ATAQUES")
    print("-" * 80)
    top_ataques = df_stats.nlargest(10, 'GP')
    for idx, row in top_ataques.iterrows():
        media_gols = row['GP'] / row['Jogos']
        print(f"{row['Time']:<40} {row['GP']:>3} gols em {row['Jogos']:>2} jogos (media: {media_gols:.2f})")
    
    # Melhores defesas
    print("\n4. MELHORES DEFESAS")
    print("-" * 80)
    melhores_defesas = df_stats.nsmallest(10, 'GC')
    for idx, row in melhores_defesas.iterrows():
        media_sofridos = row['GC'] / row['Jogos']
        print(f"{row['Time']:<40} {row['GC']:>3} gols sofridos em {row['Jogos']:>2} jogos (media: {media_sofridos:.2f})")
    
    # Melhor saldo de gols
    print("\n5. MELHOR SALDO DE GOLS")
    print("-" * 80)
    melhor_saldo = df_stats.nlargest(10, 'SG')
    for idx, row in melhor_saldo.iterrows():
        print(f"{row['Time']:<40} Saldo: {row['SG']:>+4} (GP: {row['GP']:>3}, GC: {row['GC']:>3})")
    
    # Aproveitamento
    print("\n6. MELHOR APROVEITAMENTO")
    print("-" * 80)
    melhor_aprov = df_stats.nlargest(10, 'Aprov%')
    for idx, row in melhor_aprov.iterrows():
        print(f"{row['Time']:<40} {row['Aprov%']:>5.1f}% ({row['V']}V {row['E']}E {row['D']}D em {row['Jogos']} jogos)")
    
    # Desempenho casa vs fora
    print("\n7. DESEMPENHO: CASA vs FORA")
    print("-" * 80)
    print(f"{'Time':<40} {'Vit Casa':<10} {'Vit Fora':<10} {'Total Vit':<10}")
    print("-" * 80)
    for idx, row in df_stats.head(20).iterrows():
        print(f"{row['Time']:<40} {row['V_Casa']:<10} {row['V_Fora']:<10} {row['V']:<10}")
    
    # Análise por competição
    print("\n8. DESEMPENHO POR COMPETICAO")
    print("-" * 80)
    for comp in df['competicao'].unique():
        print(f"\n{comp}:")
        df_comp = df[df['competicao'] == comp]
        
        stats_comp = []
        for time in df_comp['time'].unique():
            df_time_comp = df_comp[df_comp['time'] == time]
            vit = len(df_time_comp[df_time_comp['resultado'] == 'Vitoria'])
            emp = len(df_time_comp[df_time_comp['resultado'] == 'Empate'])
            der = len(df_time_comp[df_time_comp['resultado'] == 'Derrota'])
            jogos = len(df_time_comp)
            pts = vit * 3 + emp
            
            stats_comp.append({
                'Time': time,
                'Jogos': jogos,
                'Pontos': pts,
                'V': vit,
                'E': emp,
                'D': der
            })
        
        df_comp_stats = pd.DataFrame(stats_comp).sort_values('Pontos', ascending=False)
        print(f"  {'Time':<40} {'J':<4} {'V':<4} {'E':<4} {'D':<4} {'Pts':<5}")
        for idx, row in df_comp_stats.head(10).iterrows():
            print(f"  {row['Time']:<40} {row['Jogos']:<4} {row['V']:<4} {row['E']:<4} {row['D']:<4} {row['Pontos']:<5}")
    
    # Sequências recentes
    print("\n9. FORMA RECENTE (ULTIMOS 5 JOGOS)")
    print("-" * 80)
    
    for time in sorted(df['time'].unique()):
        df_time = df[df['time'] == time].sort_values('data', ascending=False).head(5)
        
        forma = []
        for _, jogo in df_time.iterrows():
            if jogo['resultado'] == 'Vitoria':
                forma.append('V')
            elif jogo['resultado'] == 'Empate':
                forma.append('E')
            else:
                forma.append('D')
        
        forma_str = ' '.join(forma)
        vit_5 = forma.count('V')
        print(f"{time:<40} {forma_str:<15} ({vit_5} vitorias)")
    
    print("\n" + "=" * 80)
    print("FIM DA ANALISE")
    print("=" * 80)
    
    return df_stats


if __name__ == "__main__":
    try:
        analise_por_time()
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Erro durante a analise: {e}")
        import traceback
        traceback.print_exc()

