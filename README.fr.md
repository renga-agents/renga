# renga

> **renga** est le collectif qui manquait à votre agent IA.
> **Public visé** : développeurs, tech leads, équipes produit
> **Prérequis** : VS Code, GitHub Copilot en mode agent
> **Dernière mise à jour** : 2026-03-17
> **Durée de lecture estimée** : 4 min

---

## Sommaire

- [renga](#renga)
	- [Sommaire](#sommaire)
	- [Ce que fait renga](#ce-que-fait-renga)
	- [Démarrage rapide](#démarrage-rapide)
	- [Profil Lite](#profil-lite)
	- [Documentation](#documentation)
	- [Version anglaise](#version-anglaise)

---

## Ce que fait renga

renga organise une équipe d'agents spécialisés au lieu de surcharger un seul assistant.

Concrètement, cela apporte:

- un architecte pour les choix structurants
- un reviewer pour la maintenabilité
- un QA pour les tests et la qualité
- un debugger pour la recherche de cause racine
- un rédacteur technique pour la documentation

Vous pouvez commencer petit avec le profil Lite, puis élargir vers Standard ou Full si votre projet gagne en complexité.

---

## Démarrage rapide

Installez la CLI :

```bash

curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh

```

Depuis la racine de votre projet :

```bash

renga init
renga install
code .

```

Ensuite, dans Copilot Chat :

```text

@backend-dev: Add a GET /api/health route that returns { status: 'ok' }

```

Pour un parcours détaillé, voir [docs/getting-started.md](docs/getting-started.md).

---

## Profil Lite

Le profil Lite active 8 agents essentiels:

- backend-dev
- frontend-dev
- qa-engineer
- code-reviewer
- software-architect
- debugger
- git-expert
- tech-writer

Le CLI `renga init` sélectionne Lite par défaut.

---

## Documentation

- [docs/getting-started.md](docs/getting-started.md) : prise en main rapide
- [docs/ide-setup.md](docs/ide-setup.md) : prérequis VS Code et MCP
- [docs/complexity-profiles.md](docs/complexity-profiles.md) : Lite, Standard, Full
- [docs/architecture.md](docs/architecture.md) : vue d'ensemble de l'architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) : contribuer au projet

---

## Version anglaise

La documentation principale se trouve dans [README.md](README.md).
