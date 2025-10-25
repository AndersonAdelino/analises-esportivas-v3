# 🔧 Comandos Git Úteis - Deploy e Manutenção

## 🚀 Deploy Inicial

### 1. Inicializar Repositório
```bash
cd C:\Users\Anderson\Documents\analises_esportivas_v3
git init
```

### 2. Adicionar Arquivos
```bash
# Adicionar todos os arquivos
git add .

# Verificar o que será commitado
git status
```

### 3. Primeiro Commit
```bash
git commit -m "Deploy inicial - Sistema de análises esportivas com Bingo"
```

### 4. Conectar ao GitHub
```bash
# Substitua SEU_USUARIO pelo seu username
git remote add origin https://github.com/SEU_USUARIO/analises-esportivas-v3.git

# Verificar remote
git remote -v
```

### 5. Enviar para GitHub
```bash
# Primeira vez (define branch principal)
git branch -M main
git push -u origin main

# Proximas vezes (mais simples)
git push
```

---

## 🔄 Atualizações Diárias

### Fluxo Básico
```bash
# 1. Ver o que mudou
git status

# 2. Adicionar mudanças
git add .

# 3. Commitar com mensagem
git commit -m "Descrição do que foi alterado"

# 4. Enviar para GitHub (deploy automático!)
git push
```

### Commit de Features Específicas
```bash
# Nova funcionalidade
git commit -m "feat: adiciona filtro por odd mínima no Bingo"

# Correção de bug
git commit -m "fix: corrige cálculo de EV na cartela múltipla"

# Melhoria
git commit -m "improve: otimiza velocidade de carregamento dos modelos"

# Documentação
git commit -m "docs: atualiza guia de uso do Bingo"
```

---

## 📋 Comandos de Verificação

### Ver Status
```bash
# O que mudou?
git status

# Diferenças detalhadas
git diff

# Ver últimos commits
git log --oneline -10
```

### Ver Histórico
```bash
# Histórico completo
git log

# Histórico resumido
git log --oneline

# Histórico gráfico
git log --graph --oneline --all
```

---

## 🔙 Desfazer Mudanças

### Antes de Commitar

#### Descartar mudanças em arquivo específico
```bash
git checkout -- arquivo.py
```

#### Descartar todas as mudanças
```bash
git reset --hard
```

#### Tirar arquivo do staging (git add)
```bash
git reset arquivo.py
```

### Depois de Commitar (Local)

#### Desfazer último commit (mantém mudanças)
```bash
git reset --soft HEAD~1
```

#### Desfazer último commit (descarta mudanças)
```bash
git reset --hard HEAD~1
```

### Depois de Push (Já no GitHub)

⚠️ **CUIDADO:** Evite se outras pessoas usam o repositório!

```bash
# Reverter commit específico (mais seguro)
git revert HASH_DO_COMMIT
git push

# Forçar reset (perigoso!)
git reset --hard HEAD~1
git push --force
```

---

## 🌿 Branches (Avançado)

### Criar e Usar Branches

```bash
# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Listar branches
git branch

# Trocar de branch
git checkout main

# Fazer merge da feature na main
git checkout main
git merge feature/nova-funcionalidade

# Deletar branch após merge
git branch -d feature/nova-funcionalidade
```

### Workflow com Branches

```bash
# 1. Criar branch para nova feature
git checkout -b feature/melhoria-bingo

# 2. Fazer mudanças e commitar
git add .
git commit -m "feat: adiciona validação avançada no Bingo"

# 3. Enviar branch para GitHub
git push -u origin feature/melhoria-bingo

# 4. Criar Pull Request no GitHub (via web)

# 5. Após merge, atualizar main local
git checkout main
git pull
```

---

## 🔍 Comandos de Consulta

### Ver Configurações
```bash
# Ver todas as configs
git config --list

# Ver nome/email configurado
git config user.name
git config user.email

# Configurar nome/email
git config user.name "Seu Nome"
git config user.email "seu@email.com"
```

### Ver Remotes
```bash
# Listar remotes
git remote -v

# Adicionar remote
git remote add origin URL

# Mudar URL do remote
git remote set-url origin NOVA_URL

# Remover remote
git remote remove origin
```

---

## 📥 Sincronização

### Puxar Mudanças do GitHub

```bash
# Puxar e fazer merge
git pull

# Puxar sem merge (fetch + merge manual)
git fetch origin
git merge origin/main
```

### Resolver Conflitos

Se houver conflito ao fazer pull/merge:

```bash
# 1. Git avisa sobre conflito
# 2. Abra os arquivos conflitantes
# 3. Edite e resolva manualmente
# 4. Adicione os arquivos resolvidos
git add arquivo_resolvido.py

# 5. Complete o merge
git commit -m "resolve: conflito no arquivo X"

# 6. Envie
git push
```

---

## 🗑️ Limpeza

### Remover Arquivos

```bash
# Remover arquivo do Git e do disco
git rm arquivo.py
git commit -m "remove: arquivo não utilizado"
git push

# Remover do Git mas manter no disco
git rm --cached arquivo.py
git commit -m "remove: arquivo do controle de versão"
git push
```

### Limpar Cache
```bash
# Limpar arquivos não rastreados
git clean -fd

# Ver o que seria removido (dry-run)
git clean -n
```

---

## 🔐 Segurança

### Remover Dados Sensíveis

Se commitou acidentalmente `.env` ou API keys:

```bash
# 1. Remover do Git
git rm --cached .env
git commit -m "remove: arquivo .env sensível"
git push

# 2. Adicionar ao .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: adiciona .env ao gitignore"
git push

# 3. IMPORTANTE: Revogar/mudar a API key exposta!
```

---

## 🆘 Comandos de Emergência

### App quebrou após push?

```bash
# Voltar para commit anterior que funcionava
git log --oneline  # encontre o hash do commit bom
git reset --hard HASH_DO_COMMIT_BOM
git push --force

# ⚠️ Use --force com cuidado!
```

### Perdeu mudanças não commitadas?

```bash
# Recuperar arquivo específico do último commit
git checkout HEAD -- arquivo.py

# Ver mudanças no stash (se usou)
git stash list
git stash pop
```

---

## 📊 Estatísticas

### Ver Contribuições

```bash
# Número de commits por autor
git shortlog -sn

# Estatísticas do repositório
git log --stat

# Mudanças por arquivo
git log --stat -- arquivo.py
```

---

## 🎯 Dicas Pro

### Aliases Úteis

Adicione ao seu `.gitconfig`:

```bash
# Configurar aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"

# Usar
git st   # = git status
git lg   # = log bonito
```

### Commit Rápido

```bash
# Add + commit em um comando
git commit -am "mensagem"

# ⚠️ Só funciona para arquivos já rastreados!
```

### Ver Diferenças Bonitas

```bash
# Diferenças coloridas
git diff --color-words

# Diferenças entre branches
git diff main..feature/nova-funcionalidade
```

---

## 📝 Boas Práticas

### Mensagens de Commit

**Formato:**
```
tipo: descrição curta (máx 50 caracteres)

Descrição mais detalhada se necessário (máx 72 caracteres por linha)
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (sem mudança de código)
- `refactor`: Refatoração
- `test`: Adicionar/modificar testes
- `chore`: Manutenção

**Exemplos:**
```bash
git commit -m "feat: adiciona suporte a múltiplas moedas no Bingo"
git commit -m "fix: corrige erro de divisão por zero no cálculo de EV"
git commit -m "docs: atualiza README com instruções de deploy"
```

### Frequência de Commits

✅ **Faça commits:**
- Ao completar uma funcionalidade
- Ao corrigir um bug
- Antes de fazer mudanças arriscadas
- No final do dia de trabalho

❌ **Evite:**
- Commits muito grandes
- Commits com código quebrado
- Commits sem mensagem clara

---

## 🔗 Links Úteis

- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub Docs](https://docs.github.com)
- [Git Tutorial](https://git-scm.com/docs/gittutorial)
- [Git Book](https://git-scm.com/book/pt-br/v2)

---

**Desenvolvido para Análises Esportivas v3**
*Última atualização: Outubro 2025*

