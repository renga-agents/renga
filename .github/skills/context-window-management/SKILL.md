---
name: context-window-management
description: "Context window optimisation across waves — summarisation strategies, prioritisation, compression"
argument-hint: "[description]"
user-invocable: true
---

# Optimisation de l'utilisation des fenêtres de contexte entre les waves et agents


---

## Principe fondamental

Les context windows sont une **ressource limitée** qui doit être utilisée avec une stratégie d'optimisation rigoureuse. L'objectif est de maximiser l'information utile tout en minimisant la charge cognitive et le coût.

L'objectif est de :
- **Summariser** efficacement les rapports d'agents
- **Gérer** les contextes entre waves (ce qui est conservé, ce qui est perdu)
- **Prioriser** le contenu à inclure/exclure dans le contexte
- **Compresser** sans perte d'information critique

---

## Stratégies de summarization des rapports d'agents

### Pourquoi summariser ?

Les context windows ont des limites :
- **Longueur maximale** : 128K tokens (Claude Opus)
- **Coût** : Plus de tokens = plus cher
- **Performance** : Plus de tokens = temps de réponse plus long
- **Qualité** : Trop de contexte = dilution de l'attention

### Méthodologie de summarization

#### Niveau 1 : Summarization immédiate (après chaque agent)

**Quand** : Après chaque agent termine sa tâche

**Objectif** : Réduire le rapport complet à un résumé exécutable pour le wave suivant

**Template** :

```markdown
## Résumé Agent [NOM_AGENT] — [TÂCHE]

**Statut** : [Terminé/En cours/Bloqué]

**Résultat principal** :
{1-2 phrases sur le résultat principal}

**Actions effectuées** :
- [action 1]
- [action 2]
- [action 3]

**Fichiers modifiés** :
- `fichier1.md` : {modification}
- `fichier2.md` : {modification}

**Décisions prises** :
- {décision 1}
- {décision 2}

**Blocs** :
- [bloc 1] : {description}
- [bloc 2] : {description}

**Problèmes rencontrés** :
- {problème 1}
- {problème 2}

**Prochaines étapes** :
- {étape 1}
- {étape 2}

**Code généré** : {nombre} fichiers, {nombre} lignes

**Confiance** : [Haute/Moyenne/Faible]
```

**Règles de summarization** :
1. **Max 500 tokens** par résumé
2. **Pas de code complet** : seulement les références
3. **Pas de détails inutiles** : seulement l'essentiel
4. **Actions claires** : ce qui a été fait, ce qui reste

---

#### Niveau 2 : Summarization de wave (après chaque wave)

**Quand** : Après chaque wave complète

**Objectif** : Créer un résumé exécutable pour le wave suivant

**Template** :

```markdown
## Résumé Wave [N] — [SUJET]

**Statut global** : [Terminé/En cours/Bloqué]

**Objectifs atteints** :
- [objectif 1] : {pourcentage}%
- [objectif 2] : {pourcentage}%
- [objectif 3] : {pourcentage}%

**Objectifs non atteints** :
- [objectif 4] : {raison}
- [objectif 5] : {raison}

**Fichiers créés/modifiés** :
{liste des fichiers importants}

**Décisions clés** :
- {décision 1}
- {décision 2}
- {décision 3}

**Blocs créés** :
- [bloc 1] : {description}
- [bloc 2] : {description}

**Problèmes bloquants** :
- {problème 1}
- {problème 2}

**Code généré** : {nombre} fichiers, {nombre} lignes

**Prochaines étapes (Wave N+1)** :
- {étape 1}
- {étape 2}
- {étape 3}

**Ressources nécessaires** :
- {ressource 1}
- {ressource 2}

**Confiance globale** : [Haute/Moyenne/Faible]
```

**Règles de summarization** :
1. **Max 1000 tokens** par résumé de wave
2. **Focus sur les décisions** : pas de détails d'implémentation
3. **Focus sur les blocages** : problèmes à résoudre
4. **Focus sur les prochaines étapes** : ce qui suit

---

#### Niveau 3 : Summarization de projet (après chaque projet)

**Quand** : À la fin d'un projet ou d'une phase majeure

**Objectif** : Créer une mémoire de projet réutilisable

**Template** :

```markdown
## Mémoire de Projet — [PROJET]

**Période** : {date début} - {date fin}

**Objectifs atteints** :
- {objectif 1}
- {objectif 2}
- {objectif 3}

**Architecture finale** :
{description de l'architecture}

**Décisions architecturales** :
- {décision 1}
- {décision 2}
- {décision 3}

**Patterns utilisés** :
- {pattern 1}
- {pattern 2}
- {pattern 3}

**Leçons apprises** :
- {leçon 1}
- {leçon 2}
- {leçon 3}

**Erreurs évitables** :
- {erreur 1}
- {erreur 2}

**Ressources créées** :
- {ressource 1}
- {ressource 2}

**Liens utiles** :
- {lien 1}
- {lien 2}
```

**Règles de summarization** :
1. **Max 2000 tokens** par mémoire de projet
2. **Focus sur l'architecture** : décisions durables
3. **Focus sur les leçons** : éviter de répéter les erreurs
4. **Focus sur les patterns** : réutilisables

---

## Gestion des contextes entre waves

### Ce qui est conservé

#### 1. Décisions architecturales

**Pourquoi** : Les décisions architecturales sont durables et impactent tout le projet.

**Comment** :
- Stocker dans `docs/adr/`
- Inclure les références dans le contexte du wave suivant
- Lier les décisions aux implémentations

**Template** :

```markdown
## Décisions conservées pour Wave N+1

**ADR-001** : {titre}
- Décision : {décision}
- Impact : {impact}
- Lien : `docs/adr/ADR-001.md`

**ADR-002** : {titre}
- Décision : {décision}
- Impact : {impact}
- Lien : `docs/adr/ADR-002.md`
```

#### 2. Fichiers modifiés

**Pourquoi** : Les agents suivants ont besoin de connaître les modifications existantes.

**Comment** :
- Lister les fichiers modifiés avec leur état
- Inclure les changements importants
- Lier aux commits

**Template** :

```markdown
## Fichiers modifiés conservés pour Wave N+1

**Créés** :
- `fichier1.md` : {description}
- `fichier2.md` : {description}

**Modifiés** :
- `fichier3.md` : {modification}
- `fichier4.md` : {modification}

**Supprimés** :
- `fichier5.md` : {raison}
```

#### 3. Décisions de consensus

**Pourquoi** : Les décisions de consensus sont contraignantes pour les agents suivants.

**Comment** :
- Inclure le verdict de consensus
- Lister les agents en accord/désaccord
- Lier aux décisions

**Template** :

```markdown
## Décisions de consensus conservées pour Wave N+1

**Consensus-001** : {sujet}
- Verdict : {verdict}
- Agents en accord : {liste}
- Agents en désaccord : {liste}
- Lien : `.github/logs/decisions-consensus-001.md`
```

---

### Ce qui est perdu

#### 1. Détails d'implémentation

**Pourquoi** : Les détails d'implémentation sont spécifiques à un agent et ne sont pas réutilisables.

**Ce qui est perdu** :
- Code complet généré (référé par les fichiers)
- Tentatives d'implémentation échouées
- Discussions techniques détaillées

**Ce qui est conservé** :
- Fichiers finaux créés
- Décisions architecturales
- Patterns utilisés

#### 2. Contexte conversationnel

**Pourquoi** : Les conversations entre agents ne sont pas nécessaires pour les agents suivants.

**Ce qui est perdu** :
- Questions/réponses détaillées
- Discussions de clarification
- Itérations de code

**Ce qui est conservé** :
- Questions ouvertes (si non résolues)
- Décisions prises
- Problèmes identifiés

#### 3. État intermédiaire

**Pourquoi** : L'état intermédiaire est temporaire et sera soit validé, soit abandonné.

**Ce qui est perdu** :
- Fichiers temporaires
- Essais de code
- Versions intermédiaires

**Ce qui est conservé** :
- Fichiers validés
- Fichiers commités
- Fichiers dans le dépôt

---

## Priorisation du contenu à inclure/exclure dans le contexte

### Hiérarchie de priorité

| Priorité | Contenu | Action |
|----------|---------|--------|
| P0 | Décisions architecturales | **Toujours inclure** |
| P1 | Fichiers modifiés | **Toujours inclure** |
| P2 | Problèmes bloquants | **Toujours inclure** |
| P3 | Décisions de consensus | **Toujours inclure** |
| P4 | Résumé d'agents | **Inclure si espace disponible** |
| P5 | Détails d'implémentation | **Exclure** |
| P6 | Conversations | **Exclure** |
| P7 | Tentatives échouées | **Exclure** |

### Matrice de décision d'inclusion

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATRICE D'INCLUSION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Type de contenu        │  Priorité │  Inclure ? │  Comment │
│  ───────────────────────┼──────────┼───────────┼──────────┤
│  Décisions architecturales │    P0    │   OUI     │  Full    │
│  Fichiers modifiés        │    P1    │   OUI     │  Full    │
│  Problèmes bloquants      │    P2    │   OUI     │  Full    │
│  Décisions de consensus   │    P3    │   OUI     │  Full    │
│  Résumé d'agents          │    P4    │  SI ESPACE│  Condensé│
│  Détails d'implémentation │    P5    │   NON     │  -       │
│  Conversations            │    P6    │   NON     │  -       │
│  Tentatives échouées      │    P7    │   NON     │  -       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Règles de priorisation

1. **Règle P0-P3** : Le contenu P0-P3 est **toujours inclus**, peu importe la taille du contexte.

2. **Règle P4** : Le contenu P4 est inclus **si le contexte a de l'espace**. Si le contexte est plein, les résumés les plus récents sont prioritaires.

3. **Règle P5-P7** : Le contenu P5-P7 est **toujours exclu** pour maximiser l'espace pour le contenu important.

4. **Règle de compression** : Si le contexte dépasse la limite, compresser le contenu P4 en gardant seulement l'essentiel.

---

## Techniques de compression sans perte d'information critique

### Technique 1 : Compression par résumé hiérarchique

**Principe** : Créer plusieurs niveaux de résumé, du plus détaillé au plus condensé.

**Niveaux** :
1. **Niveau 1** : Résumé complet (500 tokens)
2. **Niveau 2** : Résumé condensé (200 tokens)
3. **Niveau 3** : Résumé ultra-condensé (100 tokens)

**Utilisation** :
- Inclure le niveau 1 si espace disponible
- Inclure le niveau 2 si espace limité
- Inclure le niveau 3 si contexte plein

**Exemple** :

```markdown
## Résumé Wave 5 — [SUJET]

### Niveau 1 (500 tokens)
{détails complets}

### Niveau 2 (200 tokens)
{résumé condensé}

### Niveau 3 (100 tokens)
{résumé ultra-condensé}
```

---

### Technique 2 : Compression par extraction de patterns

**Principe** : Extraire les patterns réutilisables plutôt que les détails spécifiques.

**Patterns à extraire** :
- Patterns de code
- Patterns de décision
- Patterns de problème/résolution

**Exemple** :

```markdown
## Patterns extraits

### Pattern de code : Validation de fichier
```
def validate_file(path):
    # Pattern : validation de chemin + existence + permissions
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if not os.access(path, os.R_OK):
        raise PermissionError(path)
    return True
```

### Pattern de décision : Choix de stack
- Critère 1 : Performance
- Critère 2 : Écosystème
- Critère 3 : Maintenance
- Décision : Python > Node.js > PHP

### Pattern de problème/résolution
- Problème : Timeout DB
- Cause : Pool épuisé
- Solution : Augmenter pool + backoff
```

---

### Technique 3 : Compression par référence croisée

**Principe** : Remplacer les détails par des références à des documents externes.

**Types de références** :
- Références à des ADR
- Références à des fichiers
- Références à des décisions de consensus
- Références à des logs

**Exemple** :

```markdown
## Résumé Wave 5 — [SUJET]

**Architecture** : Voir `docs/adr/ADR-001.md`

**Fichiers modifiés** : Voir `.renga/memory/wave-5/files.md`

**Décisions** : Voir `.github/logs/decisions-*.md`

**Problèmes** : Voir `.renga/logs/errors/wave-5.md`

**Code généré** : 15 fichiers (voir `.renga/memory/wave-5/code.md`)
```

---

### Technique 4 : Compression par agrégation

**Principe** : Agréger les informations similaires en une seule entrée.

**Exemples** :

```markdown
## Résumé Wave 5 — [SUJET]

### Fichiers créés (15)
- `src/` : 8 fichiers
- `tests/` : 5 fichiers
- `docs/` : 2 fichiers

### Agents actifs (4)
- backend-dev
- frontend-dev
- code-reviewer
- qa-engineer

### Types d'erreurs (3)
- ERR-DB-001 : 5 occurrences
- ERR-NET-001 : 3 occurrences
- ERR-VAL-001 : 2 occurrences
```

---

## Exemples de prompts de summarization

### Prompt pour summarization immédiate

```markdown
## Prompt de summarization immédiate

Tu es un assistant de summarization. Ton objectif est de créer un résumé exécutable de {agent_name} pour la tâche {task_name}.

**Règles** :
1. Max 500 tokens
2. Pas de code complet
3. Focus sur les actions, décisions, problèmes
4. Format Markdown structuré

**Entrée** :
{rapport complet de l'agent}

**Sortie attendue** :
## Résumé Agent {agent_name} — {task_name}

**Statut** : [Terminé/En cours/Bloqué]

**Résultat principal** :
{1-2 phrases}

**Actions effectuées** :
- [action 1]
- [action 2]
- [action 3]

**Fichiers modifiés** :
- `fichier1.md` : {modification}
- `fichier2.md` : {modification}

**Décisions prises** :
- {décision 1}
- {décision 2}

**Blocs** :
- [bloc 1] : {description}
- [bloc 2] : {description}

**Problèmes rencontrés** :
- {problème 1}
- {problème 2}

**Prochaines étapes** :
- {étape 1}
- {étape 2}

**Code généré** : {nombre} fichiers, {nombre} lignes

**Confiance** : [Haute/Moyenne/Faible]
```

---

### Prompt pour summarization de wave

```markdown
## Prompt de summarization de wave

Tu es un assistant de summarization. Ton objectif est de créer un résumé exécutable du wave {wave_number} pour le wave suivant.

**Règles** :
1. Max 1000 tokens
2. Focus sur les décisions et blocages
3. Pas de détails d'implémentation
4. Format Markdown structuré

**Entrée** :
{rapports de tous les agents du wave}

**Sortie attendue** :
## Résumé Wave {wave_number} — {subject}

**Statut global** : [Terminé/En cours/Bloqué]

**Objectifs atteints** :
- [objectif 1] : {pourcentage}%
- [objectif 2] : {pourcentage}%
- [objectif 3] : {pourcentage}%

**Objectifs non atteints** :
- [objectif 4] : {raison}
- [objectif 5] : {raison}

**Fichiers créés/modifiés** :
{liste des fichiers importants}

**Décisions clés** :
- {décision 1}
- {décision 2}
- {décision 3}

**Blocs créés** :
- [bloc 1] : {description}
- [bloc 2] : {description}

**Problèmes bloquants** :
- {problème 1}
- {problème 2}

**Code généré** : {nombre} fichiers, {nombre} lignes

**Prochaines étapes (Wave N+1)** :
- {étape 1}
- {étape 2}
- {étape 3}

**Ressources nécessaires** :
- {ressource 1}
- {ressource 2}

**Confiance globale** : [Haute/Moyenne/Faible]
```

---


## Structure de mémoire de travail

```
.renga/
├── memory/
│   ├── wave-1/
│   │   ├── summary.md          # Résumé du wave 1
│   │   ├── agents/             # Résumés d'agents
│   │   │   ├── agent-1-summary.md
│   │   │   └── agent-2-summary.md
│   │   ├── decisions/          # Décisions du wave
│   │   └── files/              # Fichiers modifiés
│   ├── wave-2/
│   │   └── ...
│   └── project/
│       └── summary.md          # Mémoire de projet
├── logs/
│   ├── errors/                 # Logs d'erreurs
│   └── decisions/              # Logs de décisions
└── reports/
    └── dashboard.md            # Dashboard de progression
```

**Résumé du wave 1** : `memory/wave-1/summary.md`
**Résumés d'agents** : `memory/wave-1/agents/*.md`
**Décisions** : `memory/wave-1/decisions/*.md`
**Fichiers** : `memory/wave-1/files/*.md`
```

---

## Checklist d'implémentation

### Pour les nouveaux projets

- [ ] Définir la stratégie de summarization (niveaux 1, 2, 3)
- [ ] Configurer la structure de mémoire de travail
- [ ] Mettre en place les templates de résumé
- [ ] Configurer les règles de priorisation
- [ ] Implémenter les prompts de summarization

### Pour les projets existants

- [ ] Auditer l'utilisation actuelle du contexte
- [ ] Identifier les contenus non essentiels
- [ ] Mettre en place la summarization hiérarchique
- [ ] Créer des prompts de summarization
- [ ] Optimiser la taille du contexte

---
