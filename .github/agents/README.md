# Annuaire des agents

> Ce dossier contient les 51 agents core (1 orchestrateur invocable + 46 agents spécialistes + 4 profils de filière) de l'équipe IA.
> Chaque fichier `.agent.md` définit l'identité, les responsabilités, les outils
> et les règles de comportement d'un agent.

---

## Sommaire

- <a href="#comment-invoquer-un-agent-">Comment invoquer un agent ?</a>
- <a href="#architecture-des-fichiers">Architecture des fichiers</a>
- <a href="#-orchestration">🧠 Orchestration</a>
- <a href="#️-architecture">🏛️ Architecture</a>
- <a href="#-développement">💻 Développement</a>
- <a href="#-qualité--sécurité">✅ Qualité & Sécurité</a>
- <a href="#-devops--plateforme">🔧 DevOps & Plateforme</a>
- <a href="#-data--ia">🤖 Data & IA</a>
- <a href="#-produit--design">📦 Produit & Design</a>
- <a href="#-business--finance">💼 Business & Finance</a>
- <a href="#️-conformité--gouvernance">⚖️ Conformité & Gouvernance</a>
- <a href="#-skills-système">📚 Skills système</a>
- <a href="#️-profils-_profiles">🗂️ Profils (_profiles/)</a>

---

## Comment invoquer un agent ?

La syntaxe est la même pour tous les agents invocables :

```

@nom-de-l-agent: <description de la tâche>

```

### Exemples :

```

@seiji: Implémenter le endpoint POST /api/v1/orders avec validation NestJS
@seiji: Auditer le flux d'authentification OAuth2 du service payments
@seiji: Mettre en place un système de notifications push temps réel

```

### Conventions de nommage

- Les noms d'agents invocables utilisent le **kebab-case** en minuscules.
- La forme attendue est `@backend-dev:` et non `@backend-dev:` ou `@BACKEND_DEV:`.
- Les noms de fichiers suivent la même convention : `backend-dev.agent.md`, `security-engineer.agent.md`, etc.

### Choisir le bon point d'entrée

- **Toute tâche** : invoquer `@seiji:` — c'est le seul agent directement invocable. Seiji planifie et dispatche les spécialistes appropriés.
- **Décision critique à arbitrer** : invoquer `@seiji consensus: <question>`.

### Contraintes de plateforme à connaître

- Seul `@seiji` peut réellement dispatcher des sous-agents via `runSubagent`.
- Une invocation directe d'un spécialiste est un point terminal : l'agent appelé ne re-dispatche pas lui-même d'autres agents.
- Les profils de filière et référentiels listés plus bas sont **lus** par seiji, mais ne sont pas des points d'entrée utilisateur.

> **Conseil :** pour une tâche complexe qui mobilise plusieurs agents,
> déléguer à l'orchestrateur plutôt qu'à un agent spécialisé directement.
> L'orchestrateur construit le plan d'exécution, dispatche les bons agents
> et consolide les résultats.

### Découverte rapide

| Besoin | Comment invoquer |
| --- | --- |
| Implémenter une API ou une logique métier | `@seiji: <description>` — seiji dispatche backend-dev (+ sécurité, QA, etc. si nécessaire) |
| Construire une interface ou un composant React | `@seiji: <description>` — seiji dispatche frontend-dev (+ UX, accessibilité si nécessaire) |
| Enquêter sur un bug difficile | `@seiji: <description>` — seiji dispatche debugger et les agents complémentaires |
| Coordonner un incident en production | `@seiji: <description>` — seiji dispatche incident-commander et les agents concernés |
| Auditer la sécurité d'un flux | `@seiji: <description>` — seiji dispatche security-engineer (+ conformité, risque si nécessaire) |
| Piloter une feature transverse | `@seiji: <description>` — seiji dispatche product-manager et les équipes concernées |
| Arbitrer une décision sensible | `@seiji consensus: <question>` — protocole de consensus multi-agents |

### Validation automatique

Pour vérifier que les fichiers du dossier agents restent cohérents entre eux :

```bash

python3 scripts/validate_agents.py

```

Pour réécrire automatiquement le frontmatter dans l'ordre canonique et resynchroniser la ligne `Domaine` avec la description du frontmatter :

```bash

python3 scripts/validate_agents.py --write

```

Pour vérifier qu'une session orchestrateur a bien persisté tous les rapports de subagents attendus :

```bash

python3 scripts/validate_subagent_reports.py --session <slug>

```

### Patterns de handoff

Quand plusieurs agents se succèdent sur un même sujet, éviter les transitions implicites. Chaque agent amont doit transmettre un **handoff exploitable** à l'agent aval.

Règles minimales :

- Le handoff doit préciser ce qui est **décidé**, ce qui reste **ouvert** et ce qui est **attendu** du prochain agent.
- Les hypothèses non validées doivent être nommées explicitement, jamais noyées dans le texte.
- Le prochain agent ne doit pas avoir à relire tout le raisonnement pour savoir quoi faire ensuite.

Chaînes de collaboration recommandées :

- **Stratégie produit → delivery** : `product-strategist` → `product-manager` → `proxy-po` → `qa-engineer` / `backend-dev` / `frontend-dev`
- **Delivery → mesure** : `product-manager` → `product-analytics` → `product-strategist`
- **Incident** : `incident-commander` → `observability-engineer` → `debugger` → `devops-engineer` → `incident-commander`
- **Observabilité et instrumentation** : `observability-engineer` ↔ `product-analytics` selon qu'on parle de santé technique ou d'usage produit

Format court recommandé dans chaque sortie d'agent :

```markdown

## Handoff

- **Pour** : [agent suivant]
- **Décisions figées** : [liste courte]
- **Questions ouvertes** : [liste courte ou "Aucune"]
- **Artefacts à reprendre** : [fichier, métrique, plan, issue, dashboard]
- **Prochaine action attendue** : [verbe d'action clair]

```

### Critères d'activation

Pour les agents les plus coûteux en contexte ou les plus faciles à sur-solliciter, la fiche doit aussi répondre explicitement à deux questions :

- **Quand solliciter** : quels signaux justifient vraiment l'appel de l'agent
- **Ne pas solliciter** : quels cas relèvent d'un autre agent, d'un cas simple, ou d'un point d'entrée orchestrateur

Ce garde-fou évite trois dérives classiques :

- appeler un spécialiste trop tôt alors que le problème n'est pas cadré
- faire doublon avec un agent voisin
- consommer du contexte expert sur une tâche qui devrait rester au niveau orchestrateur ou implémentation

### Qualité d'orchestration

Le système n'est pas conçu pour minimiser le nombre d'agents à tout prix. L'objectif est de mobiliser le bon niveau d'expertise avec le bon niveau de structuration.

Règle de conduite générale :

- ne pas exclure un agent pertinent au seul motif que cela coûterait plus de tokens
- préférer des prompts mieux bornés, des vagues cohérentes et des synthèses plus strictes
- n'accepter une réduction de couverture que si elle améliore objectivement la qualité ou répond à une contrainte métier explicite

### Audit exhaustif

Quand l'utilisateur demande explicitement un audit exhaustif ou la couverture la plus complète possible, l'objectif n'est plus de minimiser le nombre d'agents appelés, mais de maximiser la couverture pertinente.

Règle de conduite :

- ne pas exclure un agent pertinent au seul motif que cela consommerait plus de tokens
- préférer des prompts plus précis, des vagues mieux structurées et une synthèse finale plus stricte
- ne réduire le périmètre qu'avec une justification métier explicite ou un arbitrage utilisateur

### Matrice de recouvrement rapide

| Si tu hésites entre... | Prendre plutôt... | Et éviter si... |
| --- | --- | --- |
| `infra-architect` / `cloud-engineer` | `infra-architect` pour la topologie cible, `cloud-engineer` pour le choix et le dimensionnement des services | tu demandes à `cloud-engineer` de faire de l'ADR d'architecture globale ou à `infra-architect` du simple provisioning |
| `cloud-engineer` / `devops-engineer` | `cloud-engineer` pour les services cloud, `devops-engineer` pour la chaîne build-test-release-deploy | le vrai problème est le pipeline et pas le service cloud lui-même |
| `ux-ui-designer` / `frontend-dev` / `accessibility-engineer` | `ux-ui-designer` pour le parcours, `frontend-dev` pour l'implémentation, `accessibility-engineer` pour la conformité détaillée | tu demandes à un seul agent de couvrir à lui seul UX, code et audit WCAG |
| `database-engineer` / `data-engineer` / `data-scientist` | `database-engineer` pour le schéma transactionnel, `data-engineer` pour les pipelines, `data-scientist` pour l'analyse et les hypothèses | la demande mélange stockage, mouvement de données et interprétation sans priorité claire |
| `product-strategist` / `product-manager` / `proxy-po` | `product-strategist` pour la direction, `product-manager` pour le pilotage transverse, `proxy-po` pour le découpage backlog | tu attends d'un seul agent qu'il couvre vision, arbitrage delivery et rédaction détaillée des stories |
| `debugger` / `performance-engineer` / `security-engineer` | `debugger` pour la root cause, `performance-engineer` pour les goulots mesurés, `security-engineer` pour les vulnérabilités | le symptôme n'est pas encore qualifié et tu pars trop vite sur la mauvaise spécialité |
| `tech-writer` / `proxy-po` / `change-management` | `tech-writer` pour documenter, `proxy-po` pour spécifier le backlog, `change-management` pour l'adoption | tu demandes une doc alors que le besoin réel est un cadrage produit ou un plan d'accompagnement |

### Qualité de la section Collaboration

La ligne `Collaboration` ne doit pas être un inventaire paresseux. Pour les agents de coordination, gouvernance et cadrage, elle doit rester :

- assez courte pour aider au dispatch
- assez précise pour signaler les vrais voisins fonctionnels
- assez stable pour être validable automatiquement

Règle pratique :

- viser 3 à 5 collaborateurs top-level maximum
- éviter les listes fourre-tout qui mélangent exécution, gouvernance, produit et support sans hiérarchie
- spécialiser ensuite le `Contrat de handoff` pour expliquer comment le relais se fait réellement avec ces voisins

### Agents pouvant rester standards

Tous les agents n'ont pas besoin du même niveau de sophistication dans leur handoff. Un contrat standard reste acceptable quand l'agent est dans l'un de ces cas :

- **spécialité très étroite** : le voisinage fonctionnel est déjà évident et peu ambigu
- **agent principalement contributif** : il produit un artefact expert mais ne sert pas souvent de point d'entrée de cadrage
- **usage encore trop rare** : le sur-spécifier créerait plus de rigidité que de clarté pour le moment

Typiquement, cela couvre encore des profils comme animation, mobile, fullstack, ML, MLOps, prompt, direction créative, recherche IA, gestion du risque ou certains rôles transverses à faible fréquence. La règle n'est pas de tout spécialiser, mais de spécialiser d'abord là où les erreurs de dispatch coûtent le plus cher.

---

## Architecture des fichiers

```

.github/agents/
├── seiji.agent.md                 ← Point d'entrée pour toute tâche complexe
├── orchestrator-tech.agent.md     ← Profil de filière (référence, non invocable)
├── orchestrator-product.agent.md  ← Profil de filière (référence, non invocable)
├── orchestrator-data.agent.md     ← Profil de filière (référence, non invocable)
├── orchestrator-governance.agent.md ← Profil de filière (référence, non invocable)
├── <nom>.agent.md                 ← Agents spécialisés (invocables)
└── _profiles/                     ← Profils transverses (droits d'outils par catégorie)
    ├── advisory.profile.md        ← Profil sans exécution (conseil, conformité, stratégie)
    └── technical.profile.md       ← Profil avec exécution (dev, infra, data, ML)

```

> **Note sur les profils de filière** (`orchestrator-tech`, `orchestrator-product`,
> `orchestrator-data`, `orchestrator-governance`) : ce sont des **documents de référence**
> que seiji lit lors de la planification pour choisir les bons agents spécialisés.
> Ils ne sont **pas invocables** directement par l'utilisateur.

> **Note sur les protocoles** : les anciens référentiels `consensus-protocol` et `execution-modes`
> ont été convertis en **skills** (`.github/skills/`). Ils sont chargés nativement par Copilot
> via le frontmatter `skills:` de seiji — aucune lecture de fichier explicite n'est nécessaire.

---

## 🧠 Orchestration

Le cerveau opérationnel de l'équipe. À invoquer pour toute tâche nécessitant plusieurs agents ou une coordination.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **seiji** | Tour de contrôle de l'équipe — décompose la tâche, construit le DAG d'exécution (séquentiel / parallèle / vagues), dispatche les agents, contrôle la qualité des outputs et journalise les décisions dans `.github/logs/decisions-<slug>.md` | [seiji.agent.md](seiji.agent.md) |
| **orchestrator-tech** *(référence)* | Matrice de dispatch filière technique — aide seiji à choisir entre backend-dev, frontend-dev, qa-engineer, DevOps, etc. | [orchestrator-tech.agent.md](orchestrator-tech.agent.md) |
| **orchestrator-product** *(référence)* | Matrice de dispatch filière produit — proxy-po, ux-ui-designer, business-analyst, GTM | [orchestrator-product.agent.md](orchestrator-product.agent.md) |
| **orchestrator-data** *(référence)* | Matrice de dispatch filière Data/AI — data-scientist, ml-engineer, MLOps, data-engineer | [orchestrator-data.agent.md](orchestrator-data.agent.md) |
| **orchestrator-governance** *(référence)* | Triggers proactifs + critères de VETO pour la sécurité, la conformité, l'éthique IA et la gestion des risques | [orchestrator-governance.agent.md](orchestrator-governance.agent.md) |

---

## 🏛️ Architecture

Agents qui conçoivent et arbitrent les structures techniques avant toute implémentation.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **software-architect** | Définit l'architecture logicielle : bounded contexts, patterns (DDD, CQRS, Event Sourcing…), découpage en modules, ADR (Architecture Decision Records). Produit des recommandations opinionées, pas des listes d'options. | [software-architect.agent.md](software-architect.agent.md) |
| **infra-architect** | Conçoit la topologie d'infrastructure : IaC (Terraform), réseau, sécurité périmétrique, multi-cloud. Garantit la cohérence entre le code et l'infrastructure cible. | [infra-architect.agent.md](infra-architect.agent.md) |
| **cloud-engineer** | Spécialiste des services cloud (AWS en priorité) : provisioning, haute disponibilité, disaster recovery, politiques IAM, CDN, queues. | [cloud-engineer.agent.md](cloud-engineer.agent.md) |
| **database-engineer** | Modélisation des données, optimisation de requêtes (EXPLAIN ANALYZE), stratégie d'indexation, migrations, réplication et partitionnement PostgreSQL. | [database-engineer.agent.md](database-engineer.agent.md) |
| **api-designer** | Design-first API (OpenAPI, AsyncAPI), contrats d'interface, gouvernance API, developer experience. | [api-designer.agent.md](api-designer.agent.md) |
| **architecture-reviewer** | Revue transverse : vérifie la cohérence entre les décisions d'architecture des différents agents, détecte les contradictions et la dette technique émergente. | [architecture-reviewer.agent.md](architecture-reviewer.agent.md) |

---

## 💻 Développement

Agents qui écrivent du code. Chacun couvre un périmètre précis — ils collaborent systématiquement plutôt que de s'empiéter.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **backend-dev** | APIs REST/GraphQL/gRPC, services NestJS/FastAPI, logique métier, intégrations tiers. Produit du code production-ready : validation, gestion d'erreurs, logging structuré, tests inclus. | [backend-dev.agent.md](backend-dev.agent.md) |
| **frontend-dev** | Composants React (Next.js App Router, RSC), performance web (Core Web Vitals), accessibilité de base, intégration du design system. | [frontend-dev.agent.md](frontend-dev.agent.md) |
| **fullstack-dev** | Développement bout-en-bout quand la frontière frontend/backend n'est pas rigide — features complètes, intégration API, formulaires avec validation end-to-end. | [fullstack-dev.agent.md](fullstack-dev.agent.md) |
| **mobile-dev** | Applications mobiles React Native et Flutter, navigation, push notifications, accès aux APIs natives, publication stores. | [mobile-dev.agent.md](mobile-dev.agent.md) |

---

## ✅ Qualité & Sécurité

Agents qui testent, auditent et améliorent le code existant. Ils n'écrivent pas de fonctionnalités — ils garantissent leur fiabilité.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **qa-engineer** | Stratégie de test (TDD/BDD), écriture des specs Vitest/Playwright, couverture de code, automatisation des tests E2E. En mode TDD, il est en **wave 1** (tests `red`) avant le développeur (wave 2). | [qa-engineer.agent.md](qa-engineer.agent.md) |
| **debugger** | Investigation de bugs complexes : analyse root cause, reproduction minimale, lecture de stack traces, isolation du comportement inattendu. Escalade avec un rapport structuré. | [debugger.agent.md](debugger.agent.md) |
| **code-reviewer** | Revue de code ciblée : maintenabilité, respect des conventions, complexité cyclomatique, dette technique, cohérence des nommages. Produit des commentaires actionnables. | [code-reviewer.agent.md](code-reviewer.agent.md) |
| **security-engineer** | Audit OWASP : injection, broken auth, exposition de données, SSRF, misconfiguration. Toujours placé en **wave 0** quand qa-engineer est prévu — ses contraintes P0 alimentent les specs de test. | [security-engineer.agent.md](security-engineer.agent.md) |
| **performance-engineer** | Profiling, optimisation des goulots d'étranglement, définition des SLO/SLI, tests de charge, identification des régressions de performance. | [performance-engineer.agent.md](performance-engineer.agent.md) |
| **accessibility-engineer** | Conformité WCAG 2.2, ARIA, RGAA. Tests avec screen readers réels (NVDA, VoiceOver, JAWS). Audit des couleurs, du focus, des labels, des animations. | [accessibility-engineer.agent.md](accessibility-engineer.agent.md) |

---

## 🔧 DevOps & Plateforme

Agents qui automatisent les pipelines de livraison, maintiennent l'infrastructure et assurent l'observabilité.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **devops-engineer** | CI/CD (GitHub Actions), conteneurisation (Docker, Kubernetes/Helm), pipelines de déploiement, automatisation des releases, gestion des secrets. | [devops-engineer.agent.md](devops-engineer.agent.md) |
| **incident-commander** | Coordination d'incident : qualification de sévérité, war room, communication, pilotage du rollback, postmortems et suivi des actions. | [incident-commander.agent.md](incident-commander.agent.md) |
| **git-expert** | Stratégie de branches (GitFlow, trunk-based), résolution de conflits complexes, réécriture d'historique, bisect, cherry-pick, gestion des worktrees. | [git-expert.agent.md](git-expert.agent.md) |
| **mlops-engineer** | Infrastructure ML : pipelines d'entraînement, model serving (BentoML, TorchServe), feature store, monitoring de drift, versioning de modèles (MLflow). | [mlops-engineer.agent.md](mlops-engineer.agent.md) |
| **platform-engineer** | Developer experience interne : self-service infrastructure, templates, abstractions Kubernetes, Internal Developer Portal. Réduit la charge cognitive des équipes produit. | [platform-engineer.agent.md](platform-engineer.agent.md) |
| **observability-engineer** | OpenTelemetry (traces, métriques, logs), alerting Prometheus/Grafana, définition des SLO/SLI/SLA, runbooks, dashboards de production. | [observability-engineer.agent.md](observability-engineer.agent.md) |
| **chaos-engineer** | Ingénierie de la résilience : game days, injection de pannes (Chaos Monkey, Toxiproxy), validation des fallbacks, anti-fragilité. | [chaos-engineer.agent.md](chaos-engineer.agent.md) |

---

## 🤖 Data & IA

Agents spécialisés dans les données, les modèles de machine learning et l'intelligence artificielle.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **data-scientist** | Exploration et analyse de données, modélisation statistique, feature engineering, visualisation, interprétation des résultats pour des audiences non techniques. | [data-scientist.agent.md](data-scientist.agent.md) |
| **ml-engineer** | Entraînement de modèles (PyTorch, HuggingFace), fine-tuning, optimisation (quantization, distillation), déploiement et maintenance en production. | [ml-engineer.agent.md](ml-engineer.agent.md) |
| **ai-research-scientist** | Veille state-of-the-art, expérimentations avancées, implémentation de papers, benchmarks comparatifs, exploration de nouvelles architectures. | [ai-research-scientist.agent.md](ai-research-scientist.agent.md) |
| **ai-product-manager** | Stratégie produit IA, construction de la roadmap, évaluation comparative de modèles, calcul du ROI, arbitrage build vs buy vs fine-tune. | [ai-product-manager.agent.md](ai-product-manager.agent.md) |
| **data-engineer** | Pipelines ETL/ELT, data quality, orchestration (Airflow, Dagster), lakehouse, streaming (Kafka, Flink), contrats de données. | [data-engineer.agent.md](data-engineer.agent.md) |
| **prompt-engineer** | Conception de prompts système et few-shot, évaluation et red-teaming des LLMs, optimisation RAG, rédaction des instructions agents, itération sur les prompts existants. | [prompt-engineer.agent.md](prompt-engineer.agent.md) |

---

## 📦 Produit & Design

Agents qui définissent *quoi* construire, *pour qui* et *avec quelle expérience*.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **proxy-po** | Rédaction des user stories (format BDD), gestion du backlog, priorisation (RICE, MoSCoW), définition des critères d'acceptation. Point de contact entre les équipes métier et technique. | [proxy-po.agent.md](proxy-po.agent.md) |
| **product-manager** | Ownership d'une feature de bout en bout : cadrage, coordination transverse, arbitrages de scope, delivery et validation du résultat. | [product-manager.agent.md](product-manager.agent.md) |
| **product-analytics** | KPI produit, funnels, adoption, rétention, instrumentation et lecture décisionnelle post-lancement. | [product-analytics.agent.md](product-analytics.agent.md) |
| **scrum-master** | Facilitation des cérémonies agiles, suivi de la vélocité, détection et levée des impediments, amélioration continue des pratiques d'équipe. | [scrum-master.agent.md](scrum-master.agent.md) |
| **tech-writer** | Documentation technique (OpenAPI, ADR, guides d'intégration, READMEs), documentation utilisateur, changelogs, migration guides. | [tech-writer.agent.md](tech-writer.agent.md) |
| **ux-ui-designer** | Design d'interface : wireframes, maquettes haute fidélité, design system, tokens, accessibilité visuelle, prototypage. Applique les lois UX (Fitts, Hick, Miller…). | [ux-ui-designer.agent.md](ux-ui-designer.agent.md) |
| **ux-writer** | Microcopy : labels, messages d'erreur, tooltips, onboarding, tone of voice, cohérence terminologique, contenus d'interface. | [ux-writer.agent.md](ux-writer.agent.md) |
| **product-strategist** | Vision produit long terme, OKRs, roadmap stratégique, product-market fit, analyse concurrentielle, arbitrages make-or-buy. | [product-strategist.agent.md](product-strategist.agent.md) |
| **go-to-market-specialist** | Stratégie de lancement : segmentation, pricing, positionnement, adoption des features, métriques de succès, plans de communication. | [go-to-market-specialist.agent.md](go-to-market-specialist.agent.md) |

---

## 💼 Business & Finance

Agents qui alignent les décisions techniques sur les contraintes organisationnelles et financières.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **business-analyst** | Modélisation des processus métier (BPMN), analyse des écarts (gap analysis), expression de besoins, cartographie des flux existants, identification des opportunités d'optimisation. | [business-analyst.agent.md](business-analyst.agent.md) |
| **change-management** | Conduite du changement : plan d'adoption, formation des utilisateurs, communication interne, gestion de la résistance, métriques d'adoption. | [change-management.agent.md](change-management.agent.md) |
| **finops-engineer** | Optimisation des coûts cloud : analyse de la facture AWS/GCP/Azure, rightsizing, réservations, tagging des ressources, budgets, reporting FinOps. | [finops-engineer.agent.md](finops-engineer.agent.md) |
| **project-controller** | PMO : suivi de l'avancement (EVM), reporting budgétaire, gestion du registre des dépendances, risk register, jalons. | [project-controller.agent.md](project-controller.agent.md) |

---

## ⚖️ Conformité & Gouvernance

Agents qui garantissent que les décisions respectent les obligations légales, éthiques et de sécurité. Leur validation peut **bloquer** une livraison.

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **legal-compliance** | RGPD (licéité des traitements, minimisation, droits des personnes), EU AI Act (classification du risque), licences open source, CGU/CGV, contrats d'utilisation des APIs et modèles. | [legal-compliance.agent.md](legal-compliance.agent.md) |
| **ai-ethics-governance** | Détection de biais algorithmiques, explicabilité (SHAP, LIME), red teaming IA, rédaction de model cards, évaluation de l'impact social d'un système automatisé. | [ai-ethics-governance.agent.md](ai-ethics-governance.agent.md) |
| **risk-manager** | Cartographie des risques (impact × probabilité), DPIA (Data Protection Impact Assessment), plans de contingence, scénarios de crise, escalade. | [risk-manager.agent.md](risk-manager.agent.md) |

> Ces trois agents sont déclenchés **automatiquement** par l'orchestrateur dès que
> des données personnelles, un traitement IA ou une décision irréversible sont impliqués.

---

## 🎮 Plugins disponibles

Agents distribués en tant que plugins bundled dans `_plugins/`. Ces agents ne font pas partie du core et doivent être activés via `.renga.yml`.

### Pack `game-studio` (`_plugins/game-studio/`)

| Agent | Rôle | Fichier |
| --- | --- | --- |
| **animations-engineer** | Rendu graphique avancé : WebGL, shaders GLSL, Three.js, R3F/Drei, GSAP, canvas 2D, post-processing, Phaser 3 (jeu 2D), Babylon.js (jeu 3D). | [animations-engineer.agent.md](_plugins/game-studio/animations-engineer.agent.md) |
| **game-asset-generator** | Génère des kits d'assets visuels (images, sprites pixel art, animations, vidéos, UI) pour prototypes de jeux vidéo via l'API Replicate. | [game-asset-generator.agent.md](_plugins/game-studio/game-asset-generator.agent.md) |
| **audio-generator** | Génère des kits audio (SFX, musique/OST, ambiances, voix/dialogues) pour prototypes de jeux vidéo via l'API Replicate. | [audio-generator.agent.md](_plugins/game-studio/audio-generator.agent.md) |
| **creative-director** | Direction créative et artistique globale : identité visuelle, univers narratif, cohérence thématique, brand design, art direction. | [creative-director.agent.md](_plugins/game-studio/creative-director.agent.md) |
| **game-developer** | Développement gameplay, game loop, physique, collision, intégration moteur. | [game-developer.agent.md](_plugins/game-studio/game-developer.agent.md) |
| **game-balancer** | Équilibrage de jeu : courbes de progression, économie, difficulté, rétention. | [game-balancer.agent.md](_plugins/game-studio/game-balancer.agent.md) |
| **game-producer** | Production de jeu : planning, budget, milestones, coordination équipe. | [game-producer.agent.md](_plugins/game-studio/game-producer.agent.md) |
| **level-designer** | Conception de niveaux : flow, pacing, layout, progression spatiale. | [level-designer.agent.md](_plugins/game-studio/level-designer.agent.md) |
| **narrative-designer** | Design narratif : dialogues, lore, arcs narratifs, world-building. | [narrative-designer.agent.md](_plugins/game-studio/narrative-designer.agent.md) |

> Détails sur le système de plugins : voir [docs/plugin-system.md](../../docs/plugin-system.md)

---

## 📚 Skills système

Les protocoles d'exécution et de consensus ont été convertis en **skills** (chargés nativement par Copilot, sans lecture de fichier explicite). Ils sont déclarés dans le frontmatter `skills:` de seiji.

| Skill | Rôle | Fichier |
| --- | --- | --- |
| **execution-modes** | Référence des 5 modes d'exécution : séquentiel, parallèle, vagues (consensus), super-wave (cross-stream), mega-wave (mission stratégique). Inclut la matrice filesystem et les règles de fan-out. | [SKILL.md](../skills/execution-modes/SKILL.md) |
| **consensus-protocol** | Protocole de consensus multi-vagues pour les décisions critiques (architecture irréversible, sécurité, réglementaire, désaccord entre agents). Invocation via `@seiji consensus: <question>`. | [SKILL.md](../skills/consensus-protocol/SKILL.md) |

> Pour la liste complète des 15 skills, voir `CLAUDE.md` §Skills architecture.

---

## 🗂️ Profils (`_profiles/`)

Les profils définissent les **droits d'outils** accordés par catégorie d'agent. Ils évitent de répéter la liste des outils MCP dans chaque fichier agent.

| Profil | Agents concernés | Fichier |
| --- | --- | --- |
| **advisory** | Agents de conseil sans exécution de code (ai-ethics-governance, business-analyst, change-management, finops-engineer, go-to-market-specialist, legal-compliance, product-strategist) — accès lecture, recherche web et délégation uniquement | [_profiles/advisory.profile.md](_profiles/advisory.profile.md) |
| **technical** | Agents d'implémentation technique (backend-dev, frontend-dev, cloud-engineer, database-engineer, data-engineer, etc.) — accès complet lecture/écriture/exécution + context7 | [_profiles/technical.profile.md](_profiles/technical.profile.md) |

---

## Glossaire rapide

| Terme | Signification |
| --- | --- |
| **DAG** | *Directed Acyclic Graph* — graphe d'exécution des agents avec leurs dépendances |
| **Wave** | Groupe d'agents exécutés en parallèle à la même étape du DAG |
| **HITL** | *Human In The Loop* — validation humaine obligatoire avant de continuer |
| **ADR** | *Architecture Decision Record* — document traçant une décision d'architecture |
| **DPIA** | *Data Protection Impact Assessment* — analyse d'impact RGPD |
| **TDD red/green** | Cycle TDD : écrire les tests qui échouent (red) AVANT l'implémentation, puis les faire passer (green) |
| **L1/L2/L3/L4** | Niveaux de criticité d'une tâche : L1 locale/réversible → L4 critique/irréversible |
| **MCP** | *Model Context Protocol* — serveurs d'outils accessibles aux agents (context7, playwright, postgresql…) |
