---
name: handoff-protocol
description: "Standardizes handoffs between agents with a structured block (recipient, fixed decisions, open questions, artifacts, next action) and commit discipline."
argument-hint: "Describe the handoff to prepare or the transition context between agents"
user-invocable: true
---
# Skill: Inter-Agent Handoff Protocol

Standardizes transitions between agents to ensure traceability and information continuity.

---

## Mandatory Handoff Block

Each dispatched agent must produce a final handoff block in its report:

```markdown
### Handoff

**For**: <recipient agent or orchestrator>
**Fixed decisions**:
- <decision 1 with justification>
- <decision 2 with justification>

**Open questions**:
- <question 1 — context>
- <question 2 — context>

**Artifacts**:
- <path/file1> — <description>
- <path/file2> — <description>

**Next action**: <description of what the recipient must do>
```

---

## Standard Handoff Chains

### Product Chain

```
ProductStrategist → ProductManager → ProxyPO → Devs
```

- **ProductStrategist**: vision, OKRs, strategic constraints
- **ProductManager**: prioritization, tradeoffs, coordination
- **ProxyPO**: user stories, acceptance criteria, backlog
- **Devs**: implementation according to the specs

### Analytics Chain

```
ProductManager ↔ ProductAnalytics ↔ ProductStrategist
```

Two-way loop: data → insights → decisions → measurement.

### Incident Chain

```
IncidentCommander → ObservabilityEngineer → Debugger → DevOpsEngineer → IncidentCommander
```

Closed loop: detection → diagnosis → fix → validation → postmortem.

---

#### Exemples de chaînes de handoff

### Chaîne product

**ProductStrategist → ProductManager → ProxyPO → Devs**

#### Handoff: ProductStrategist → ProductManager

```markdown
### Handoff

**For**: ProductManager

**Fixed decisions**:
- Vision produit : plateforme SaaS multi-tenant pour la gestion de projets collaboratifs
- OKR Q1 : acquérir 1000 entreprises clientes (ARR cible: 2M€)
- Contraintes stratégiques : RGPD strict, intégration native avec Slack/Notion

**Open questions**:
- Quel stack technique privilégier (Next.js vs Remix) ?
- Priorité fonctionnelle : collaboration temps réel ou intégrations tierces ?

**Artifacts**:
- `docs/product-vision-q1.md` — vision produit et OKR
- `docs/strategic-constraints.md` — contraintes RGPD et intégrations

**Next action**: Définir le backlog priorisé et les user stories principales
```

#### Handoff: ProductManager → ProxyPO

```markdown
### Handoff

**For**: ProxyPO

**Fixed decisions**:
- Priorité P0 : collaboration temps réel (éditeurs simultanés, commentaires)
- Priorité P1 : intégrations Slack/Notion
- Priorité P2 : reporting avancé

**Open questions**:
- Acceptance criteria pour la latence temps réel (< 200ms) ?
- Scope des intégrations : Slack uniquement ou aussi Teams ?

**Artifacts**:
- `docs/backlog-prioritized.md` — backlog trié par priorité
- `docs/feature-spec-collaboration.md` — spécifications fonctionnelles

**Next action**: Rédiger les user stories et acceptance criteria détaillés
```

#### Handoff: ProxyPO → Devs

```markdown
### Handoff

**For**: backend-dev ‖ frontend-dev

**Fixed decisions**:
- Architecture : micro-frontends avec Next.js + WebSocket (Socket.io)
- Stack : TypeScript, PostgreSQL, Redis, Docker
- Definition of Done : tests unitaires (80% coverage), E2E (Playwright)

**Open questions**:
- Design technique des WebSockets à valider avec l'architecte
- API design pour les intégrations externes

**Artifacts**:
- `docs/user-stories.md` — user stories détaillées
- `docs/acceptance-criteria.md` — critères d'acceptation
- `docs/technical-requirements.md` — exigences techniques

**Next action**: Implémenter le MVP avec les fonctionnalités P0
```

---

### Chaîne incident

**IncidentCommander → ObservabilityEngineer → Debugger → DevOpsEngineer → IncidentCommander**

#### Handoff: IncidentCommander → ObservabilityEngineer

```markdown
### Handoff

**For**: ObservabilityEngineer

**Fixed decisions**:
- Incident : P0 - Indisponibilité totale de la plateforme de paiement
- Impact : 100% des transactions bloquées, revenus arrêtés
- Hypothèse initiale : panne infrastructure AWS us-east-1

**Open questions**:
- Quelle est la métrique de dégradation ?
- Quel service est en premier sur le chemin critique ?

**Artifacts**:
- `incident-2026-03-20-p0-payment.md` — contexte incident
- `pagerduty-ticket-12345.md` — ticket PagerDuty

**Next action**: Analyser les logs et métriques pour identifier la racine du problème
```

#### Handoff: ObservabilityEngineer → Debugger

```markdown
### Handoff

**For**: Debugger

**Fixed decisions**:
- Service affecté : payment-processor (microservice Node.js)
- Erreur observée : 500 Internal Server Error sur toutes les requêtes POST /charge
- Stack trace disponible :见附件 `error-stack-payment-processor.log`

**Open questions**:
- Est-ce un bug de code ou une dépendance externe ?
- Le problème est-il réplicable en environnement de staging ?

**Artifacts**:
- `observability-analysis-payment-processor.md` — analyse métriques/logs
- `error-stack-payment-processor.log` — stack traces récentes
- `metrics-degradation-chart.png` — graphique dégradation

**Next action**: Reproduire et debugger l'erreur dans le code
```

#### Handoff: Debugger → DevOpsEngineer

```markdown
### Handoff

**For**: DevOpsEngineer

**Fixed decisions**:
- Cause racine identifiée : mémoire épuisée dans le pool de connexions PostgreSQL
- Solution proposée : augmenter `max_connections` et activer connection pooling
- Risque : requête de changement de configuration en production

**Open questions**:
- Faut-il un rollback si la solution échoue ?
- Qui valide l'application du fix ?

**Artifacts**:
- `debug-report-memory-leak.md` — rapport de debugging
- `postgresql-connection-pool-config.md` — configuration recommandée

**Next action**: Appliquer le fix en production avec monitoring renforcé
```

#### Handoff: DevOpsEngineer → IncidentCommander

```markdown
### Handoff

**For**: IncidentCommander

**Fixed decisions**:
- Fix appliqué : `max_connections` augmenté de 100 à 500, PgBouncer activé
- Validation : 1000 requêtes de test réussies en 5 minutes
- Service restauré : 99.9% de succès sur les transactions de paiement

**Open questions**:
- Postmortem à rédiger dans les 24h
- Actions correctives à long terme (scaling automatique, alerting amélioré)

**Artifacts**:
- `devops-fix-applied-log.md` — logs d'application du fix
- `validation-test-results.md` — résultats tests post-fix

**Next action**: Clôturer l'incident et initier le postmortem
```

---

### Chaîne consensus

**seiji → agents → seiji**

#### Handoff: seiji → agents (Wave 0)

```markdown
### Handoff

**For**: software-architect ‖ security-engineer ‖ devops-engineer

**Fixed decisions**:
- Session : `sso-auth-redesign`
- Objectif : Redesign du système d'authentification SSO
- Contraintes : OAuth2/OIDC, MFA obligatoire, audit trail complet

**Open questions**:
- Architecture cible : on-premise ou cloud-native ?
- Intégrations existantes : Active Directory, Okta, Azure AD ?

**Artifacts**:
- `.renga/memory/scratchpad-sso-auth-redesign.md` — contexte session
- `.renga/memory/project-context.md` — contexte projet
- `user-requirements-sso.md` — exigences utilisateurs

**Next action**: Architecture & Governance (Wave 0) — lecture et analyse
```

#### Handoff: agents → seiji (Post-Wave 0)

```markdown
### Handoff

**For**: seiji

**Fixed decisions**:
- Architecture retenue : OIDC avec Keycloak (self-hosted)
- MFA : TOTP + backup codes
- Intégrations : Okta (fédération SAML), Azure AD (OIDC)

**Open questions**:
- Validation architecture par le CTO ?
- Budget infrastructure pour Keycloak ?

**Artifacts**:
- `docs/architecture-sso-final.md` — architecture complète
- `docs/security-review-sso.md` — revue sécurité
- `docs/infrastructure-plan.md` — plan infrastructure

**Next action**: Évaluer le plan et décider du dispatch (plan-only ou dispatch)
```

---

## Related Skills

Commit rules, dispatch sequencing, and report persistence are governed by dedicated skills:

- **Commit discipline** (batches, multiline, wave cadence, asset separation) → skill `commit-discipline`
- **Dispatch rules** (QA scope, security brief, wave 0 read-only, coverage) → skill `dispatch-protocol`
- **Report persistence and output evaluation** → skill `quality-control`
