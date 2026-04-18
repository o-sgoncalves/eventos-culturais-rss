# Como Contribuir — Goiânia Cultural

Obrigado pelo interesse! Este é um projeto FOSS e toda contribuição é bem-vinda.

## Ambiente de desenvolvimento

```bash
# Backend
cd backend
pip install -r requirements.txt
pytest tests/ -v

# RSS Scraper
cd rss-scraper
pip install -r requirements.txt
pytest tests/ -v

# Frontend
cd frontend
npm install
npm test
npm run dev
```

## Fluxo de contribuição

1. Fork do repositório
2. Crie uma branch: `git checkout -b feat/minha-feature`
3. Faça suas mudanças com testes
4. Verifique que os testes passam
5. Commit: `git commit -m "feat: descrição da mudança"`
6. Push e abra um Pull Request

## Convenções

- **Commits:** inglês, estilo conventional commits (`feat:`, `fix:`, `docs:`)
- **Código:** inglês (variáveis, funções, classes)
- **Comentários e UI:** português
- **Python:** formatado com `ruff format`, lintado com `ruff check`
- **TypeScript:** ESLint

## O que precisa de ajuda

- Melhorar os padrões de regex para extração de eventos
- Adicionar mais contas do Instagram ao config
- Melhorar a UI/UX do frontend
- Testes adicionais
- Documentação e tradução
