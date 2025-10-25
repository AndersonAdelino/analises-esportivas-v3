# 🔄 Como Limpar o Cache do Streamlit

## ⚡ Solução Rápida (NOVO!)

### Botão Direto no Streamlit

Agora você tem um botão **"🔄 Limpar Cache"** na barra lateral esquerda!

```
┌─────────────────────────────┐
│ ⚙️ Configurações            │
│                             │
│ ℹ️ Sobre                    │
│ - Dixon-Coles (55%)         │
│ - Offensive-Defensive (30%) │
│ - Heurísticas (15%)         │
│                             │
│ ─────────────────────────── │
│                             │
│ [🔄 Limpar Cache]          │  ← CLIQUE AQUI!
│                             │
│ ─────────────────────────── │
└─────────────────────────────┘
```

**Passos:**
1. Clique no botão **"🔄 Limpar Cache"** na barra lateral
2. Aguarde a mensagem: "✅ Cache limpo!"
3. Recarregue a página: **F5** ou **Ctrl+R**
4. Pronto! Os 3 modelos vão funcionar

---

## 📋 Outras Formas de Limpar Cache

### Método 1: Tecla Atalho (Nativo do Streamlit)

1. Com o Streamlit aberto
2. Pressione: **`C`**
3. Menu aparece no canto superior direito
4. Clique: **"Clear cache"**
5. Recarregue: **F5**

### Método 2: Terminal

```bash
streamlit cache clear
```

### Método 3: Reiniciar Servidor

```bash
# 1. Pare o servidor
Ctrl + C

# 2. Inicie novamente
streamlit run app_betting.py
```

---

## 🎯 Quando Limpar o Cache?

Limpe o cache se:

- ❌ **Só aparece Heurísticas** nas predições
- ❌ **Modelos aparecem como "Falhou"** no status
- ❌ **Mudou os dados** (coletou novos jogos)
- ❌ **Atualizou o código** dos modelos
- ❌ **Trocou de liga** e algo parece errado

**Não precisa limpar** se:
- ✅ Os 3 modelos aparecem ativos
- ✅ As predições estão funcionando
- ✅ Está tudo normal

---

## ✅ Como Verificar se Funcionou?

### 1. Status dos Modelos

Após limpar cache e recarregar, você deve ver:

```
📊 Status dos Modelos

┌─────────────────┬──────────────────────┬─────────────┐
│ Dixon-Coles     │ Offensive-Defensive  │ Heurísticas │
│ ✅ Ativo (55%)  │ ✅ Ativo (30%)       │ ✅ Ativo (15%) │
└─────────────────┴──────────────────────┴─────────────┘
```

### 2. Banner Azul

Após analisar partida:
```
ℹ️ 🤖 Ensemble combinando 3 modelos: 
Dixon-Coles (55%) + Offensive-Defensive (30%) + Heurísticas (15%)
```

### 3. Probabilidades Diferentes

Ao expandir "Ver Probabilidades Individuais":

| Modelo | Casa | Empate | Fora |
|--------|------|--------|------|
| Dixon-Coles | 58% | 15% | 27% |
| Offensive-Defensive | 35% | 24% | 40% |
| Heurísticas | 78% | 13% | 9% |

Se cada modelo mostrar valores diferentes = **FUNCIONANDO! ✅**

---

## 💡 Dica Pro

Configure o Streamlit para não cachear tanto:

Crie arquivo `.streamlit/config.toml`:

```toml
[server]
runOnSave = true
maxUploadSize = 200

[client]
showErrorDetails = true

[runner]
fastReruns = true
```

Isso faz o Streamlit recarregar automaticamente quando você edita arquivos.

---

## 🆘 Ainda Não Funciona?

Se mesmo após limpar cache ainda só aparecer Heurísticas:

### 1. Verifique os Dados

```bash
python -c "from ensemble import EnsembleModel; e = EnsembleModel(); e.fit('BSA')"
```

Deve mostrar:
```
[1/3] Treinando Dixon-Coles...
OK - Dixon-Coles treinado  ← Deve aparecer isso!

[2/3] Treinando Offensive-Defensive...
OK - Offensive-Defensive treinado  ← Deve aparecer isso!

[3/3] Carregando Heuristicas...
OK - Heuristicas carregadas  ← Deve aparecer isso!
```

### 2. Colete Dados Novamente

```bash
python get_team_matches.py
```

Escolha: **Brasileirão Série A**

### 3. Atualize Dependências

```bash
pip install --upgrade -r requirements.txt
```

---

## 📞 Checklist Final

Antes de pedir ajuda, verifique:

- [ ] Limpou o cache (botão ou Ctrl+C)
- [ ] Recarregou a página (F5)
- [ ] Viu o "Status dos Modelos" ao carregar
- [ ] Os 3 modelos aparecem como ✅ Ativo
- [ ] Tentou reiniciar o servidor
- [ ] Testou no terminal (comando acima)
- [ ] Tem dados do Brasileirão em `data/`

Se tudo isso foi feito e ainda não funciona, aí sim pode ser bug! 🐛

---

**Lembre-se:** Na Premier League funciona porque o cache está correto. No Brasileirão não funcionava porque o cache tinha um erro antigo. Limpar o cache resolve! 🚀

