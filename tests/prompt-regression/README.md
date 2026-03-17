# Tests de régression des prompts

> **Public visé** : mainteneurs du framework, contributeurs modifiant des fichiers `.agent.md` ou `.instructions.md`
> **Prérequis** : comprendre les niveaux L0-L4 (voir [complexity-profiles.md](../../docs/complexity-profiles.md))
> **Dernière mise à jour** : 2026-03-17
> **Durée de lecture estimée** : 5 min

---

## Table des matières

- [Pourquoi ce framework de test](#pourquoi-ce-framework-de-test)
- [Principe de fonctionnement](#principe-de-fonctionnement)
- [Structure d'un scénario](#structure-dun-scénario)
- [Niveaux de couverture](#niveaux-de-couverture)
- [Exécuter les tests](#exécuter-les-tests)
- [Ajouter un scénario](#ajouter-un-scénario)
- [Interpréter les résultats](#interpréter-les-résultats)
- [Intégration future](#intégration-future)

---

## Pourquoi ce framework de test

Quand un prompt d'agent est modifié (reformulation, ajout de règle, restructuration), il n'existe aucun moyen automatique de vérifier que le **comportement attendu est préservé**. Un changement anodin peut :

- Casser le routage de l'orchestrateur (un L0 traité comme L3)
- Supprimer un garde-fou de sécurité
- Modifier le format de sortie attendu par un agent aval
- Introduire un biais dans la classification de complexité

Ce framework de test fournit un **jeu de scénarios de référence** qui décrivent des situations concrètes et le comportement attendu du système. Après chaque modification de prompt, le mainteneur replay les scénarios pertinents pour valider que rien n'a régressé.

---

## Principe de fonctionnement

### Validation manuelle structurée

Les tests de régression de prompts ne sont **pas automatisés** au sens classique (pas de `assert` ni de CI). Ils fonctionnent comme un **protocole de validation manuelle** :

1. **Lire le scénario** — comprendre le contexte, la requête et le comportement attendu
2. **Soumettre la requête** au système (agent direct ou orchestrateur) dans un workspace de test
3. **Vérifier les comportements attendus** — chaque point de la liste `expected` doit être satisfait
4. **Vérifier les anti-patterns** — aucun point de la liste `anti_patterns` ne doit apparaître
5. **Documenter le résultat** — PASS, FAIL ou PARTIAL avec notes

### Quand exécuter les tests

| Événement | Scénarios à exécuter |
| --- | --- |
| Modification d'un `.agent.md` | Tous les scénarios impliquant cet agent |
| Modification de l'orchestrateur | **Tous** les scénarios (L0-L4) |
| Modification d'un `.instructions.md` | Scénarios du domaine concerné |
| Ajout d'un nouvel agent | Scénarios L2+ pour vérifier l'intégration |
| Avant une release | Suite complète (22 scénarios) |

---

## Structure d'un scénario

Chaque scénario est un fichier YAML dans `scenarios/` avec la structure suivante :

```yaml

id: "PTEST-001"                    # Identifiant unique
title: "L0 — Titre descriptif"    # Niveau + description courte
level: "L0"                       # L0 | L1 | L2 | L3 | L4
tags: ["orchestrator", "routing"]  # Tags pour filtrage

context: |
  Description de la situation initiale.
  Quel est l'état du workspace, quels fichiers existent, etc.

request: |
  La requête exacte que l'utilisateur soumet.

expected:
  - "Comportement attendu #1"
  - "Comportement attendu #2"
  - "Comportement attendu #3"

anti_patterns:
  - "Ce qui ne DOIT PAS arriver #1"
  - "Ce qui ne DOIT PAS arriver #2"

notes: |
  Contexte supplémentaire, justification des choix,
  liens vers la documentation pertinente.

```

### Champs obligatoires

| Champ | Description |
| --- | --- |
| `id` | Identifiant unique au format `PTEST-XXX` |
| `title` | Niveau + description courte |
| `level` | Niveau de complexité : L0, L1, L2, L3 ou L4 |
| `context` | Situation initiale décrite en langage naturel |
| `request` | Requête utilisateur exacte |
| `expected` | Liste des comportements attendus (tous doivent être vrais) |
| `anti_patterns` | Liste des comportements interdits (aucun ne doit apparaître) |

### Champs optionnels

| Champ | Description |
| --- | --- |
| `tags` | Liste de tags pour filtrage (`orchestrator`, `security`, `routing`, etc.) |
| `notes` | Contexte additionnel, justification, liens |

---

## Niveaux de couverture

| Niveau | Scénarios | Focus |
| --- | --- | --- |
| **L0** | 2 | Fast-track, bypass orchestrateur, agent direct |
| **L1** | 4 | Tâche locale, formatting, bug fix simple |
| **L2** | 7 | Multi-fichier, feature standard, refactoring, plugins |
| **L3** | 7 | API, migration BDD, sécurité, déploiement |
| **L4** | 2 | Décision architecture irréversible, incident critique |
| **Total** | **22** | Couverture équilibrée L0-L4 |

---

## Exécuter les tests

### Protocole complet (avant release)

```bash

# 1. Lister les scénarios
ls tests/prompt-regression/scenarios/

# 2. Pour chaque scénario :
#    a. Lire le fichier YAML
#    b. Ouvrir VS Code avec un workspace de test
#    c. Soumettre la requête au système
#    d. Vérifier expected + anti_patterns
#    e. Documenter le résultat

```

### Protocole ciblé (après modification d'un agent)

1. Identifier l'agent modifié
2. Trouver les scénarios qui l'impliquent (via `tags` ou lecture des `expected`)
3. Rejouer uniquement ces scénarios
4. Si un scénario échoue → annuler la modification ou adapter le scénario (avec justification)

### Grille de résultats

| Résultat | Critère |
| --- | --- |
| ✅ PASS | Tous les `expected` satisfaits, aucun `anti_pattern` observé |
| ⚠️ PARTIAL | Certains `expected` satisfaits, aucun `anti_pattern` critique |
| ❌ FAIL | Un `anti_pattern` observé OU un `expected` critique non satisfait |

---

## Ajouter un scénario

### Quand ajouter un scénario

- Un bug de routage a été découvert et corrigé → scénario de non-régression
- Un nouveau type de tâche est supporté → scénario de couverture
- Une règle de gouvernance est ajoutée → scénario de vérification

### Processus

1. Créer un fichier `PTEST-XXX.yml` dans `scenarios/`
2. Choisir un `id` séquentiel (`PTEST-016`, `PTEST-017`…)
3. Remplir tous les champs obligatoires
4. Vérifier que le scénario est **reproductible** (contexte suffisamment précis)
5. Valider manuellement au moins une fois avant de committer

### Bonnes pratiques

- Un scénario teste **un seul comportement** — pas de scénarios fourre-tout
- Les `expected` sont **vérifiables objectivement** — pas de « l'agent devrait bien faire »
- Les `anti_patterns` sont **concrets** — décrire ce qui serait observé (fichier créé, agent invoqué, etc.)
- Le `context` est **auto-suffisant** — pas de référence à un état implicite
- Préférer des requêtes **réalistes** que des cas artificiels

---

## Interpréter les résultats

### Un scénario FAIL — que faire ?

1. **Vérifier le scénario** — est-il toujours pertinent ? Les règles du framework ont-elles changé ?
2. **Si le scénario est valide** → la modification du prompt a introduit une régression → corriger le prompt
3. **Si le scénario est obsolète** → mettre à jour le scénario avec justification dans `notes`
4. **En cas de doute** → discuter avec l'équipe avant de modifier le scénario ou le prompt

### Scénario obsolète vs régression

Un scénario peut devenir obsolète quand une règle de gouvernance change intentionnellement. Dans ce cas :

- Mettre à jour le scénario (pas le supprimer)
- Documenter le changement dans `notes`
- Vérifier que les autres scénarios du même niveau ne sont pas impactés

---

## Intégration future

### Court terme — Validation manuelle assistée

Le processus actuel est entièrement manuel. Les améliorations planifiées :

- Script de listing des scénarios impactés par un fichier modifié
- Template de rapport de test (PASS/FAIL par scénario)
- Hook pre-commit rappelant les scénarios à vérifier

### Moyen terme — Semi-automatisation avec PromptFoo

Intégration potentielle avec [PromptFoo](https://www.promptfoo.dev/) pour :

- Exécuter les requêtes automatiquement contre le système
- Évaluer les réponses via LLM-as-judge
- Générer des rapports de régression

### Long terme — CI/CD intégré

- Exécution automatique sur chaque PR modifiant un `.agent.md`
- Score de régression (% de scénarios PASS)
- Blocage de merge si score < seuil configurable
