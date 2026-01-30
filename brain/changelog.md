---
title: "Changelog"
date: 2026-01-30
type: reference
tags: [life-os, changelog, updates]
---

# Changelog

Histórico de mudanças do life-os.

---

## 2026-01-30

### ✨ Features
- **Editor inline** — criar documentos pela UI (`/new`)
- **Sidebar** com botão "+ New Document"
- **Journal format** — time-based entries documentado
- **Auto-documentation protocol** — regras para o Claw

### 🎨 UI Improvements
- Melhor hierarquia de headers (H2, H3)
- Mais espaçamento entre seções
- Separadores visuais entre entries
- Dia da semana no header de data
- Labels em bold destacados

### 🚀 Infrastructure
- Deploy automático via GitHub Actions
- Docker multi-arch (ARM64 + AMD64)
- Preview environments para PRs
- Traefik como reverse proxy

### 📝 Documentation
- `concepts/journal-format` — formato padrão de journals
- `decisions/auto-documentation-protocol` — regras de documentação

---

## Roadmap

### Em breve
- [ ] Busca de documentos
- [ ] Links internos clicáveis ([[doc]])
- [ ] Domínio próprio
- [ ] Suporte a SSL

### Futuro
- [ ] Graph view (conexões entre docs)
- [X] Editor com preview lado a lado
- [ ] Mobile-friendly improvements