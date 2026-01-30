---
title: "Avaliação Entrevista - Igor Gonçalves"
date: 2026-01-30
type: note
tags: [entrevista, picpay, avaliacao, candidato]
---

# Avaliação de Entrevista Técnica - Igor Gonçalves

## Resumo Geral

| Área | Nível |
|------|-------|
| Arquitetura (Micro vs Mono) | Bom |
| POO e SOLID | Bom |
| Spring Framework | Intermediário |
| Banco de Dados | Básico |
| Concorrência/Transações | Fraco |
| Design Patterns | Intermediário |
| Testes | Fraco |
| Observabilidade/Infra | Básico |
| Uso de IA | Básico |

---

## Detalhamento por Tópico

### 1. Microsserviços vs Monolito

**Pergunta:** Problemas e benefícios de migrar de monolito para microsserviços.

**Resposta do Igor:**
- ✅ Identificou corretamente que complexidade aumenta com microsserviços (banco separado, comunicação)
- ✅ Deu exemplo prático: página mais acessada do sistema que valida cadastro - seria ponto crítico para separar
- ✅ Mencionou resiliência como benefício: "pedido cai, mas catálogo funciona"
- ✅ Citou benefício organizacional: times grandes podem trabalhar separados
- ✅ Reconheceu que nem sempre precisa escalar - monolito pode atender bem a demanda

**Avaliação:** Bom entendimento dos trade-offs.

---

### 2. Escalabilidade / Alta Carga

**Pergunta:** Como garantir que uma API aguente carga alta (exemplo: carrinho do PicPay)?

**Resposta do Igor:**
- Sugeriu escalar horizontalmente
- Reconheceu que aumentaria complexidade
- Ponderou que às vezes nem precisa escalar tanto

**Avaliação:** Resposta superficial. Não mencionou cache, rate limiting, filas assíncronas, otimização de queries.

---

### 3. Observabilidade / Monitoramento

**Pergunta:** Como acompanham saúde dos serviços?

**Resposta do Igor:**
- Fez um "esquema particular" na AWS para verificar saúde do servidor
- Health checks básicos

**Avaliação:** Básico. Não mencionou ferramentas como Prometheus, Grafana, ELK, Datadog, métricas de APM.

---

### 4. Infraestrutura

**Pergunta:** Usa Kubernetes?

**Resposta do Igor:**
- Não usa K8s, sobe direto no EC2
- Conhece conceitos mas não usa no dia a dia

**Avaliação:** Sem experiência prática com orquestração de containers.

---

### 5. POO - Conceitos Básicos

**Respostas do Igor:**
- ✅ **Classe vs Objeto:** "Classe é uma fábrica de objetos"
- ✅ **Override vs Overload:** Explicou corretamente
- ✅ **Encapsulamento:** Entende o conceito de proteger dados
- ✅ **Classe final:** Impede que seja estendida

**Avaliação:** Sólido nos fundamentos.

---

### 6. SOLID e Boas Práticas

**Resposta do Igor:**
- ✅ Usa Single Responsibility tanto para classes quanto funções
- ✅ Facilita testes unitários
- ✅ Mencionou composição e injeção de dependência
- ✅ Citou inversão de dependência com Factory
- ✅ Valoriza nomes de variáveis claros

**Avaliação:** Bom conhecimento aplicado no dia a dia.

---

### 7. Lombok

**Pergunta:** Problemas de usar Lombok?

**Resposta do Igor:**
- ✅ "Pode abrir o encapsulamento" - gera getters/setters para tudo sem controle
- ✅ "Pode perder domínio da aplicação" - não saber o que está sendo gerado
- ✅ Risco de segurança: versão maliciosa do Lombok

**Avaliação:** Excelente consciência dos riscos.

---

### 8. Transações de Banco de Dados

**Pergunta:** Como lidar com erro no meio de uma transação (ex: alterar saldo + quantidade do pedido)?

**Resposta do Igor:**
- ❌ Mostrou incerteza: "não sei como trata isso"
- ❌ Não explicou claramente `@Transactional` e rollback automático

**Avaliação:** Ponto fraco. Precisa estudar gerenciamento de transações no Spring.

---

### 9. Migrations

**Pergunta:** Como gerenciar alterações de schema em produção?

**Resposta do Igor:**
- Mencionou necessidade de separar etapas de criação/alteração
- Faz de forma manual
- Não sabia se Java/Spring tinha suporte a migrations

**Avaliação:** Fraco. Não conhece ferramentas padrão como Flyway/Liquibase. Indica falta de experiência com práticas maduras de versionamento de banco de dados.

---

### 10. Injeção de Dependência no Spring

**Pergunta:** Formas de injetar dependência?

**Resposta do Igor:**
- Mencionou que injeta via interface
- Não detalhou as 3 formas (construtor, setter, field)

**Avaliação:** Conhecimento superficial do mecanismo.

---

### 11. Idempotência

**Pergunta:** Como garantir que operação não seja duplicada?

**Resposta do Igor:**
- ✅ Excelente exemplo: "Mando ID do pedido pro gateway de pagamento, se mandar duas vezes não vai pagar duas vezes"
- ✅ Entende o conceito e aplica na prática

**Avaliação:** Muito bom.

---

### 12. Concorrência / Race Conditions

**Pergunta:** Duas requisições chegam ao mesmo tempo para alterar saldo. Como garantir consistência?

**Resposta do Igor:**
- Sugeriu lock pelo banco de dados
- Não conseguiu evoluir a solução quando provocado pelos entrevistadores
- Não chegou na solução esperada (Redis / lock distribuído)

**Avaliação:** Fraco. Ficou preso na solução básica. Indica pouca experiência com cenários de alta concorrência e sistemas distribuídos.

---

### 13. Circuit Breaker

**Pergunta:** Quando usar Circuit Breaker?

**Resposta do Igor:**
- ❌ Não conhece o padrão

**Avaliação:** Gap de conhecimento em resiliência.

---

### 14. SQL vs NoSQL

**Resposta do Igor:**
- ✅ SQL: estruturado, relacionamentos definidos previamente
- ✅ NoSQL: sem estrutura rígida, flexível

**Avaliação:** Conceitos básicos OK.

---

### 15. Cache / Performance

**Pergunta:** Como melhorar performance de consulta que sempre retorna mesmos dados?

**Resposta do Igor:**
- Sugeriu cache no front-end
- Mencionou índices no banco
- Mencionou desnormalização
- Ficou superficial sobre soluções de cache no backend

**Avaliação:** Superficial. Conhece conceitos básicos mas não demonstrou profundidade em estratégias de cache server-side (Redis, Spring Cache, invalidação, TTL).

---

### 16. Problema N+1

**Resposta do Igor:**
- ✅ Reconheceu o problema: "usuário tem 100 pedidos, pedido tem 100 produtos, vai multiplicando"

**Avaliação:** Conhece o problema.

---

### 17. Design Patterns

**Respostas do Igor:**
- ❌ **Categorias (Criacionais, Comportamentais, Estruturais):** Não sabia, entrevistadores explicaram
- ⚠️ **Factory:** Tentou explicar mas ficou confuso
- ✅ **SAGA:** Citou o padrão e explicou a diferença entre orquestração (acoplamento maior, orquestrador central) e coreografia (eventos, serviços consomem independente)
- ✅ **Outbox Pattern:** Explicou corretamente - salva evento junto com dado na mesma transação, mencionou idempotência

**Avaliação:** Intermediário. Conhece patterns práticos de arquitetura distribuída (SAGA, Outbox) mas não domina a teoria/categorização dos patterns clássicos (GoF). Factory ficou confuso.

---

### 18. Testes

**Resposta do Igor:**
- Mencionou testes unitários e exploratórios
- Testes de integração foram citados pelos entrevistadores, não por ele
- Pareceu não ter familiaridade com testes integrados

**Avaliação:** Fraco. Conhecimento limitado a testes unitários básicos.

---

### 19. Uso de IA

**Resposta do Igor:**
- Usa GitHub Copilot com modelo Sonnet 4.5
- Às vezes usa Opus, mas acha mais caro
- Lê e revisa o código gerado
- Conta pessoal

**Avaliação:** Básico. Usa ferramentas de IA de forma simples, sem experiências avançadas de prompting ou agentes.

---

### 20. Desafio Prático - Mini PicPay com IA

**Dinâmica:** Criar um mini PicPay usando IA durante a entrevista.

**Abordagem do Igor:**
- Criou o projeto pelo Spring Initializr
- Colocou o markdown do desafio dentro do projeto
- Pediu pro Opus criar um plano de implementação e depois implementar
- Conseguiu fazer o projeto rodar

**Pontos de atenção observados:**
- ❌ **Deletou o Application de testes** porque "dava BO com o banco de dados" - em vez de configurar corretamente o contexto de teste
- ❌ **Desviou do assunto quando deu erro no Swagger** - não tentou debugar ou entender o problema
- ❌ **Questionou decisões válidas da LLM** como desnecessárias:
  - Annotations de documentação do Swagger
  - Retornos de HTTP Status codes apropriados

**Avaliação:** Preocupante. Demonstra:
1. Fuga de problemas em vez de resolvê-los
2. Confirma a falta de familiaridade com testes (deletar ao invés de corrigir)
3. Não valoriza boas práticas de API (documentação, status codes corretos)
4. Postura de questionar a ferramenta em vez de aprender com ela

---

## Pontos Fortes

1. Bom entendimento de trade-offs arquiteturais (microsserviços vs monolito)
2. Sólido em POO e SOLID
3. Consciência de riscos (Lombok, code generation)
4. Experiência prática com idempotência
5. Conhece patterns de arquitetura distribuída (SAGA, Outbox)

---

## Pontos a Desenvolver

1. **Transações no Spring** - Não domina `@Transactional` e rollback
2. **Concorrência** - Ficou no lock de banco, não conhece locks distribuídos (Redis)
3. **Circuit Breaker / Resiliência** - Gap de conhecimento
4. **Testes** - Pouca familiaridade, deleta ao invés de corrigir
5. **Observabilidade** - Muito básico, sem ferramentas de mercado
6. **Kubernetes** - Sem experiência prática
7. **Injeção de dependência** - Conhecimento superficial das formas
8. **Boas práticas de API** - Não valoriza documentação e HTTP status codes
9. **Postura de debugging** - Tendência a desviar de problemas

---

## Veredicto

Igor demonstra boa base conceitual em arquitetura e design patterns. Os gaps identificados (concorrência, testes, observabilidade, boas práticas de API) parecem ser reflexo de estar há bastante tempo em uma empresa de menor porte, onde a exposição a cenários de alta escala, práticas mais robustas de engenharia e ferramentas de mercado acaba sendo limitada.

O desafio prático mostrou uma tendência a contornar problemas ao invés de enfrentá-los, o que merece atenção — mas pode ser desenvolvido com mentoria adequada.

**Recomendação:** Candidato com perfil júnior/pleno. Tem potencial de crescimento, mas precisaria de acompanhamento próximo para desenvolver as áreas de gaps. Seria importante avaliar se o PicPay tem estrutura para esse investimento em mentoria.
