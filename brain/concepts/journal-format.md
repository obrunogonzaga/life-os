---
title: "Journal Format"
date: 2026-01-30
type: concept
tags: [life-os, journals, format, writing]
---

# Journal Format

O formato padrão para journals no life-os. Time-based entries que capturam o que aconteceu ao longo do dia.

---

## Estrutura

```markdown
# YYYY-MM-DD — Weekday

---

## HH:MM AM/PM — Entry Title

**What happened:** Brief description of the event or topic.

### Key highlights
- Highlight 1
- Highlight 2
- Highlight 3

### Decisions
1. Decision made
2. Another decision

### Notes
Any additional context or thoughts.

---

## HH:MM AM/PM — Next Entry
...
```

---

## Elementos

### Header Principal
```markdown
# 2026-01-30 — Thursday
```
Data completa + dia da semana para contexto rápido.

### Entry de Tempo
```markdown
## 09:30 AM — Deploy Completo
```
Horário aproximado + título descritivo do que aconteceu.

### What happened
```markdown
**What happened:** Descrição em uma linha do evento.
```
Sempre presente. Responde "o que foi isso?"

### Subseções (opcionais)
```markdown
### Key highlights
### Decisions  
### Technical details
### Notes
### Next steps
```
Use conforme necessário. Renderizam em UPPERCASE para destaque.

### Separadores
```markdown
---
```
Entre cada entry para clareza visual.

---

## Exemplos de Titles

**Bons:**
- `07:30 AM — life-os Deploy Completo`
- `14:00 PM — Meeting with Client`
- `22:15 PM — Bug Fix: Auth Flow`

**Evitar:**
- `07:30 — deploy` (muito vago)
- `Morning stuff` (sem horário)

---

## Quando criar entries

- Decisões importantes
- Eventos significativos
- Problemas resolvidos
- Insights ou aprendizados
- Mudanças de contexto

Não precisa documentar cada minuto — foque no que importa para o futuro-eu.

---

## Relacionados

- [[decisions/auto-documentation-protocol]]
