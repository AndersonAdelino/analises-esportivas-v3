# 🌐 Como Usar a Interface Web (Streamlit)

## 📦 Instalação do Streamlit

### Opção 1: Via pip (Recomendado)
```bash
pip install streamlit
```

### Opção 2: Atualizar requirements.txt
```bash
pip install -r requirements.txt
```

---

## 🚀 Executar a Aplicação

### Comando
```bash
streamlit run app_betting.py
```

**O que acontece:**
1. Streamlit inicia um servidor local
2. Navegador abre automaticamente em `http://localhost:8501`
3. Interface carrega os modelos (aguarde ~10 segundos)
4. Pronto para usar!

---

## 🖥️ Usando a Interface

### 1️⃣ Tela Inicial
- Aguarde enquanto os 3 modelos são treinados
- Verá mensagem: "✅ Modelos carregados com sucesso!"

### 2️⃣ Selecionar Partida
- Dropdown mostra próximas partidas da Premier League
- Exemplo: "Arsenal FC vs Liverpool FC - 27/10/2024 15:00"
- Clique para selecionar

### 3️⃣ Inserir Odds

**Resultado (1X2):**
- 🏠 Vitória Casa (ex: 2.00)
- 🤝 Empate (ex: 3.50)
- ✈️ Vitória Fora (ex: 3.80)

**Over/Under 2.5 Gols:**
- 📈 Over 2.5 (ex: 1.85)
- 📉 Under 2.5 (ex: 2.00)

**Both Teams to Score:**
- ✅ BTTS Sim (ex: 1.70)
- ❌ BTTS Não (ex: 2.10)

💡 **Dica:** Use odds reais de casas como Bet365, Betfair, etc.

### 4️⃣ Configurar Banca

**Banca Total:**
- Digite seu capital disponível (ex: R$ 1000)

**Fração de Kelly:**
- Slider de 0.1 a 1.0
- **Recomendado: 0.25** (conservador)
- 0.5 = moderado
- 1.0 = agressivo (não recomendado)

### 5️⃣ Analisar

Clique no botão **"🔍 ANALISAR APOSTAS"**

**O sistema irá:**
1. Calcular probabilidades do ensemble
2. Comparar com odds da casa
3. Calcular EV de cada mercado
4. Aplicar Kelly Criterion
5. Identificar value bets
6. Recomendar stakes

---

## 📊 Interpretando Resultados

### Probabilidades do Ensemble
```
🏠 Vitória Casa: 69.5%
🤝 Empate: 21.0%
✈️ Vitória Fora: 9.5%
📈 Over 2.5: 42.5%
✅ BTTS Sim: 37.0%
```

Essas são as probabilidades calculadas pelos seus modelos combinados.

### Value Bets Identificados

Se aparecer:
```
✅ 2 Value Bet(s) identificado(s)!

🎯 🏠 Vitória Casa - APOSTE R$ 31.50
```

Clique para expandir e ver:
- **Odds & Probabilidades**
  - Comparação modelo vs casa
  - Edge (sua vantagem)
- **Expected Value**
  - EV%, ROI esperado
- **Kelly Criterion**
  - Percentual recomendado
- **Stake**
  - Valor exato a apostar

### Tabela Resumo

Mostra TODOS os mercados:
```
| Mercado       | Odds | Prob.Modelo | Edge  | EV%   | Kelly% | Apostar  | Value? |
|---------------|------|-------------|-------|-------|--------|----------|--------|
| 🏠 Vit. Casa  | 2.00 | 69.5%       | +19.5%| +39.0%| 3.2%   | R$ 31.50 | ✅     |
| 🤝 Empate     | 3.50 | 21.0%       | -7.6% | -13.0%| 0.0%   | R$ 0.00  | ❌     |
| ...           | ...  | ...         | ...   | ...   | ...    | ...      | ...    |
```

---

## 💡 Dicas de Uso

### 1. Sempre use odds reais
- Não invente odds
- Compare múltiplas casas
- Use as melhores odds disponíveis

### 2. Confie nos value bets
- ✅ = Apostar
- ❌ = Não apostar
- Simples assim!

### 3. Respeite o Kelly
- Sistema já calcula quanto apostar
- **NUNCA** aposte mais que o recomendado
- Reduza se achar muito (mas não aumente!)

### 4. Não force apostas
- Nem toda partida terá value
- Paciência é fundamental
- Busque oportunidades, não "ação"

### 5. Registre tudo
- Anote cada aposta feita
- Acompanhe resultados
- Ajuste estratégia conforme aprende

---

## 🔧 Problemas Comuns

### "Erro ao buscar partidas"
**Causa:** API Key inválida ou sem próximas partidas
**Solução:**
1. Verifique `.env` com sua API key
2. Tente novamente mais tarde
3. Use modo manual (criar partida customizada)

### "Modelos não carregam"
**Causa:** Falta de dados
**Solução:**
```bash
python get_team_matches.py  # Coletar dados primeiro
```

### Interface não abre
**Causa:** Streamlit não instalado
**Solução:**
```bash
pip install streamlit
```

### Fica carregando infinitamente
**Causa:** Modelos demorando para treinar
**Solução:** Aguarde ~10-15 segundos. É normal na primeira vez.

---

## ⌨️ Atalhos

- **Ctrl + R** (no navegador): Recarregar página
- **Ctrl + C** (no terminal): Parar servidor
- **Seta ↑ / ↓**: Navegar pelos inputs

---

## 🎨 Personalização

### Alterar porta
```bash
streamlit run app_betting.py --server.port 8502
```

### Modo escuro
1. Canto superior direito: ⚙️ Settings
2. Theme → Dark

### Ocultar menu
Editar `app_betting.py`:
```python
st.set_page_config(
    ...,
    menu_items={'Get help': None}
)
```

---

## 📱 Acessar de Outro Dispositivo

### Na mesma rede local:

1. No terminal, veja:
```
Network URL: http://192.168.x.x:8501
```

2. Acesse esse URL do celular/tablet

3. Use normalmente!

---

## 🚀 Deploy Online (Avançado)

### Streamlit Cloud (Gratuito)

1. Suba projeto para GitHub
2. Vá em https://streamlit.io/cloud
3. Conecte repositório
4. Deploy automático!

**Limitações:**
- Requer API key pública (cuidado!)
- Recursos limitados (free tier)
- Cold start pode ser lento

---

## 📈 Workflow Recomendado

```
1. Abrir interface
   ↓
2. Buscar partidas do dia
   ↓
3. Para cada partida:
   - Inserir odds reais
   - Analisar
   - Se tiver value → Anotar
   ↓
4. Revisar todos os value bets
   ↓
5. Fazer apostas recomendadas
   ↓
6. Registrar na planilha
   ↓
7. Repetir regularmente
```

---

## ✅ Checklist Pré-Aposta

Antes de fazer qualquer aposta:
- [ ] Value bet confirmado (✅ no sistema)
- [ ] EV% > +5%
- [ ] Edge > +3%
- [ ] Kelly < 5%
- [ ] Odds verificadas (ainda disponíveis?)
- [ ] Banca permite o stake
- [ ] Planilha pronta para registro
- [ ] Emocionalmente estável

---

## 🎯 Metas de Uso

### Curto Prazo (1 mês)
- Familiarizar-se com interface
- Fazer 20-30 apostas
- Registrar tudo

### Médio Prazo (3 meses)
- 100+ apostas realizadas
- ROI positivo consistente
- Ajustar estratégia conforme aprende

### Longo Prazo (6+ meses)
- Crescimento composto da banca
- Disciplina estabelecida
- Sistema refinado

---

## 📞 Suporte

**Problemas técnicos:**
- Verifique instalação do Streamlit
- Confira API key no `.env`
- Certifique-se que dados foram coletados

**Dúvidas sobre apostas:**
- Leia `GUIA_VALUE_BETTING.md`
- Estude conceitos de EV e Kelly
- Comece com stakes baixos

---

**Interface criada para facilitar Value Betting! 🎯💰**

*Boa sorte e aposte com responsabilidade!* 🍀

*Última atualização: Outubro 2024*

