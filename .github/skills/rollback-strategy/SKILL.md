---
name: rollback-strategy
description: "Rollback cost estimation and reversibility classification before committing to irreversible decisions"
argument-hint: "[description]"
user-invocable: true
---

# Méthodologie d'estimation de coût de rollback et décision sur les choix irréversibles


---

## Principe fondamental

Toute décision technique doit être prise avec une **conscience claire de sa réversibilité**. Le coût de rollback n'est pas seulement technique, il inclut les données, les dépendances, le temps et la confiance des équipes.

L'objectif est de :
- **Estimer** le coût de rollback avant de prendre une décision
- **Classifier** les décisions par niveau de réversibilité
- **Valider** les décisions irréversibles avec des checklists rigoureuses
- **Documenter** les choix pour traçabilité future

---

## Méthodologie d'estimation de coût de rollback

### Dimensions du coût de rollback

Le coût de rollback se mesure sur 4 dimensions :

#### 1. Coût en person-weeks

**Définition** : Nombre de semaines-homme nécessaires pour revenir à l'état précédent.

**Facteurs** :
- Complexité du code modifié
- Nombre de fichiers touchés
- Dépendances à inverser
- Tests à réécrire

**Estimation** :

| Complexité | Person-weeks | Exemple |
|------------|--------------|---------|
| Faible | 0.1-0.5 | Modification de configuration |
| Moyenne | 0.5-2 | Ajout de fonctionnalité simple |
| Élevée | 2-4 | Refactoring de module |
| Critique | 4+ | Changement d'architecture |

**Formulaire d'estimation** :

```markdown
## Estimation de coût de rollback

**Décision** : [description de la décision]

**Composants affectés** :
- [composant 1] : {complexité} → {person-weeks}
- [composant 2] : {complexité} → {person-weeks}
- [composant 3] : {complexité} → {person-weeks}

**Total estimé** : {total} person-weeks

**Confiance** : [Haute/Moyenne/Faible]
**Justification** : [pourquoi cette estimation]
```

#### 2. Coût en données

**Définition** : Impact sur les données existantes (perte, corruption, migration nécessaire).

**Facteurs** :
- Données à migrer
- Données à supprimer
- Données à conserver
- Intégrité des données

**Classification** :

| Niveau | Impact | Exemple |
|--------|--------|---------|
| L0 - Aucun | Aucune donnée affectée | Modification de logique métier |
| L1 - Mineur | Données à migrer (< 1000 lignes) | Ajout de colonne optionnelle |
| L2 - Moyen | Données à migrer (1000-10000 lignes) | Changement de schéma |
| L3 - Élevé | Données à migrer (> 10000 lignes) | Migration de base de données |
| L4 - Critique | Perte de données possible | Suppression de tables, changement de format |

**Checklist de validation des données** :

- [ ] Données existantes sauvegardées
- [ ] Plan de migration réversible
- [ ] Tests de migration exécutés
- [ ] Rollback des données testé
- [ ] Validation d'intégrité prévue

#### 3. Coût en dépendances

**Définition** : Impact sur les autres services, agents et composants.

**Facteurs** :
- Services dépendants
- Agents impactés
- API contractées
- Workflows affectés

**Cartographie des dépendances** :

```markdown
## Cartographie des dépendances

**Décision** : [description]

**Dépendances directes** :
- [service 1] : dépend de {feature}
- [service 2] : dépend de {feature}

**Dépendances indirectes** :
- [service 3] : dépend de {service 1}
- [agent 1] : utilise {feature}

**Impact sur les workflows** :
- [workflow 1] : {impact}
- [workflow 2] : {impact}
```

#### 4. Coût en temps d'indisponibilité

**Définition** : Temps pendant lequel le service sera indisponible pour le rollback.

**Facteurs** :
- Durée du déploiement
- Temps de validation
- Temps de rollback
- Temps de test post-rollback

**Estimation** :

| Durée | Niveau | Acceptabilité |
|-------|--------|---------------|
| < 15 min | Faible | Acceptable |
| 15-60 min | Moyen | Requiert validation |
| 1-4h | Élevé | Requiert consensus |
| > 4h | Critique | Requiert décision irréversible |

---

## Classification des décisions par réversibilité

### Niveau L0 - Réversible instantanément

**Définition** : Décision qui peut être annulée immédiatement sans coût significatif.

**Caractéristiques** :
- Pas de données modifiées
- Pas de dépendances affectées
- Rollback automatique possible

**Exemples** :
- Modification de configuration (variable d'environnement)
- Activation/désactivation de feature flag
- Changement de paramètre d'agent
- Suppression de fichier temporaire

**Processus de décision** :
1. Estimation rapide (< 5 min)
2. Validation par l'agent responsable
3. Exécution immédiate
4. Logging pour traçabilité

**Template de décision** :

```markdown
## Décision L0 - [SUJET]

**Date** : [DATE]
**Décideur** : [AGENT]

**Décision** : [description]

**Réversibilité** : L0 - Instantanée

**Coût de rollback** :
- Person-weeks : 0
- Données : Aucun
- Dépendances : Aucun
- Indisponibilité : 0 min

**Validation** : [x] Auto-validée
```

---

### Niveau L1 - Réversible avec effort mineur

**Définition** : Décision qui peut être annulée avec un effort limité (< 1 jour).

**Caractéristiques** :
- Données modifiées mais réversibles
- Dépendances mineures
- Rollback manuel possible

**Exemples** :
- Ajout de fonctionnalité simple
- Modification de logique métier
- Ajout de dépendances optionnelles
- Changement de comportement non critique

**Processus de décision** :
1. Estimation formelle (< 1h)
2. Validation par le lead technique
3. Plan de rollback documenté
4. Exécution avec monitoring

**Template de décision** :

```markdown
## Décision L1 - [SUJET]

**Date** : [DATE]
**Décideur** : [AGENT]

**Décision** : [description]

**Réversibilité** : L1 - Effort mineur

**Coût de rollback** :
- Person-weeks : 0.1-0.5
- Données : L1 - Mineur
- Dépendances : 1-2 services
- Indisponibilité : < 30 min

**Plan de rollback** :
1. [étape 1]
2. [étape 2]
3. [étape 3]

**Validation** : [x] Validée par {lead}
```

---

### Niveau L2 - Réversible avec effort significatif

**Définition** : Décision qui nécessite un effort important (1-2 jours) pour être annulée.

**Caractéristiques** :
- Données modifiées nécessitant migration
- Dépendances multiples
- Rollback manuel complexe

**Exemples** :
- Refactoring de module
- Changement de schéma de base de données
- Migration de framework
- Ajout de fonctionnalités complexes

**Processus de décision** :
1. Estimation détaillée (1-2 jours)
2. Validation par le consensus protocol
3. Plan de rollback testé en environnement de staging
4. Fenêtre de déploiement planifiée
5. Communication aux parties prenantes

**Template de décision** :

```markdown
## Décision L2 - [SUJET]

**Date** : [DATE]
**Décideur** : [AGENT]

**Décision** : [description]

**Réversibilité** : L2 - Effort significatif

**Coût de rollback** :
- Person-weeks : 1-2
- Données : L2 - Moyen
- Dépendances : 3-5 services
- Indisponibilité : 1-4h

**Plan de rollback** :
1. [étape 1 - préparation]
2. [étape 2 - exécution]
3. [étape 3 - validation]
4. [étape 4 - rollback si nécessaire]

**Tests de rollback** :
- [x] Testé en staging
- [x] Durée : {durée}
- [x] Succès : {résultat}

**Validation** : [x] Validée par consensus protocol
```

---

### Niveau L3 - Partiellement irréversible

**Définition** : Décision qui peut être annulée mais avec un coût élevé et des risques résiduels.

**Caractéristiques** :
- Données modifiées avec risques de perte
- Dépendances étendues
- Rollback possible mais imparfait

**Exemples** :
- Changement d'architecture majeur
- Migration de base de données complète
- Refactoring transverse
- Adoption de nouvelle stack technique

**Processus de décision** :
1. Estimation approfondie (1-2 semaines)
2. Validation par consensus protocol avec 3 vagues
3. Plan de rollback exhaustif testé en production
4. Fenêtre de déploiement longue planifiée
5. Communication aux toutes les parties prenantes
6. Période de transition avec dualité

**Template de décision** :

```markdown
## Décision L3 - [SUJET]

**Date** : [DATE]
**Décideur** : [AGENT]

**Décision** : [description]

**Réversibilité** : L3 - Partiellement irréversible

**Coût de rollback** :
- Person-weeks : 2-4
- Données : L3 - Élevé (risques de perte)
- Dépendances : 5+ services
- Indisponibilité : > 4h

**Risques résiduels** :
- [risque 1] : {impact}
- [risque 2] : {impact}

**Plan de rollback** :
1. [étape 1 - préparation]
2. [étape 2 - exécution]
3. [étape 3 - validation]
4. [étape 4 - rollback si nécessaire]

**Tests de rollback** :
- [x] Testé en staging
- [x] Testé en production (canary)
- [x] Durée : {durée}
- [x] Succès : {résultat}

**Validation** : [x] Validée par consensus protocol (3 vagues)
```

---

### Niveau L4 - Irréversible

**Définition** : Décision qui ne peut pas être annulée ou dont le rollback est impossible.

**Caractéristiques** :
- Données perdues définitivement
- Dépendances fondamentales modifiées
- Pas de rollback possible

**Exemples** :
- Choix de stack technique principale
- Migration de base de données avec perte de données
- Changement de schéma fondamental
- Abandon de projet

**Processus de décision** :
1. Estimation exhaustive (1-4 semaines)
2. Validation par consensus protocol avec 3 vagues + escalade humaine
3. Plan de migration irréversible documenté
4. Communication aux toutes les parties prenantes
5. Période de réflexion longue (minimum 1 semaine)
6. Approbation formelle requise

**Template de décision** :

```markdown
## Décision L4 - [SUJET]

**Date** : [DATE]
**Décideur** : [AGENT]

**Décision** : [description]

**Réversibilité** : L4 - Irréversible

**Coût de rollback** : IMPOSSIBLE

**Données perdues** :
- [donnée 1] : {description}
- [donnée 2] : {description}

**Dépendances affectées** :
- [service 1] : {impact}
- [service 2] : {impact}

**Justification de l'irréversibilité** :
{explication détaillée}

**Validation** : [x] Validée par consensus protocol + escalade humaine
**Approbation** : [x] Approuvée par {stakeholders}
```

---

## Checklists de validation avant décision irréversible

### Checklist L3 - Partiellement irréversible

**Avant toute décision L3, les éléments suivants DOIVENT être validés** :

#### Documentation
- [ ] Estimation de coût de rollback complète
- [ ] Plan de rollback détaillé et testé
- [ ] Analyse d'impact sur toutes les dépendances
- [ ] Documentation des risques résiduels
- [ ] ADR (Architecture Decision Record) créé

#### Validation
- [ ] Consensus protocol exécuté (3 vagues)
- [ ] Tests de rollback en staging
- [ ] Tests de rollback en production (canary)
- [ ] Validation par au moins 2 agents indépendants
- [ ] Validation par le lead technique

#### Communication
- [ ] Notification aux équipes impactées
- [ ] Communication aux stakeholders
- [ ] Plan de communication en cas d'échec
- [ ] Fenêtre de déploiement annoncée

#### Sécurité
- [ ] Audit de sécurité effectué
- [ ] Plan de réponse aux incidents prêt
- [ ] Sauvegarde des données critiques
- [ ] Rollback des données testé

---

### Checklist L4 - Irréversible

**Avant toute décision L4, les éléments suivants DOIVENT être validés** :

#### Documentation
- [ ] Estimation de coût exhaustive
- [ ] Plan de migration irréversible documenté
- [ ] Analyse d'impact complète (toutes les dépendances)
- [ ] Documentation des données perdues
- [ ] ADR créé avec justification détaillée
- [ ] Post-mortem potentiel documenté

#### Validation
- [ ] Consensus protocol exécuté (3 vagues)
- [ ] Tests de rollback impossibles documentés
- [ ] Validation par au moins 3 agents indépendants
- [ ] Validation par le lead technique
- [ ] Validation par les stakeholders clés
- [ ] Escalade humaine effectuée

#### Communication
- [ ] Notification formelle aux équipes impactées
- [ ] Communication aux toutes les parties prenantes
- [ ] Plan de communication en cas d'échec
- [ ] Fenêtre de déploiement annoncée
- [ ] Communication sur les données perdues

#### Sécurité
- [ ] Audit de sécurité complet
- [ ] Plan de réponse aux incidents prêt
- [ ] Sauvegarde des données critiques (si possible)
- [ ] Plan de récupération documenté

#### Post-décision
- [ ] Décision enregistrée dans `.github/logs/decisions-<slug>.md`
- [ ] ADR publié dans `docs/adr/`
- [ ] Notification d'escalade dans `.github/logs/escalades.md`
- [ ] Suivi des impacts à long terme planifié

---

## Matrice de décision rollback vs consensus

### Quand utiliser le rollback vs le consensus

| Situation | Action recommandée | Justification |
|-----------|-------------------|---------------|
| Erreur mineure, L0 | Rollback immédiat | Coût nul, pas de consensus nécessaire |
| Erreur mineure, L1 | Rollback avec validation | Coût faible, validation simple |
| Erreur moyenne, L2 | Consensus protocol | Coût significatif, nécessite validation |
| Erreur majeure, L3 | Consensus protocol + checklist | Coût élevé, risques résiduels |
| Erreur critique, L4 | Consensus protocol + escalade humaine | Irréversible, nécessite approbation formelle |

### Matrice de décision

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATRICE DE DÉCISION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Coût de rollback ↓      │  L0  │  L1  │  L2  │  L3  │  L4   │
│  ────────────────────────┼──────┼──────┼──────┼──────┼───────┤
│  Erreur détectée         │Rollback│Rollback│Consensus│Consensus│Consensus│
│  (déjà déployée)         │      │      │       │       │+Escalade│
│  ────────────────────────┼──────┼──────┼──────┼──────┼───────┤
│  Décision à prendre      │Rollback│Consensus│Consensus│Consensus│Consensus│
│  (pas encore déployée)   │      │+Checklist│+Checklist│+Checklist│+Escalade│
│  ────────────────────────┼──────┼──────┼──────┼──────┼───────┤
│  Erreur critique         │Rollback│Rollback│Consensus│Consensus│Consensus│
│  (sécurité, données)     │      │      │       │       │+Escalade│
│  ────────────────────────┼──────┼──────┼──────┼──────┼───────┤
│  Choix architecturaux    │Rollback│Rollback│Consensus│Consensus│Consensus│
│  (stack, schéma, etc.)   │      │      │       │       │+Escalade│
│  ────────────────────────┼──────┼──────┼──────┼──────┼───────┤
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Règles de décision

1. **Règle d'or** : Si le coût de rollback > 2 person-weeks, le consensus protocol est obligatoire.

2. **Règle de sécurité** : Toute décision affectant la sécurité ou les données sensibles nécessite une validation L3 minimum.

3. **Règle d'irréversibilité** : Toute décision L4 nécessite une escalade humaine, peu importe le contexte.

4. **Règle de transparence** : Toutes les décisions L2+ doivent être documentées dans un ADR.

---

## Exemples de décisions irréversibles

### Exemple 1 : Choix de stack technique

**Contexte** : Migration d'un service de 500k lignes de code de PHP à Python.

**Classification** : L4 - Irréversible

**Coût de rollback** : IMPOSSIBLE

**Justification** :
- Code entièrement réécrit
- Base de données migrée avec changement de schéma
- Écosystème et dépendances différents
- Équipe formée sur Python

**Décision documentée** :
```markdown
## ADR-001 : Migration PHP → Python

**Date** : 2026-03-20
**Décideur** : SoftwareArchitect

**Décision** : Migrer le service catalogue de PHP 7.4 à Python 3.11

**Réversibilité** : L4 - Irréversible

**Coût de rollback** : IMPOSSIBLE

**Justification** :
- Performance : Python 3x plus rapide pour les requêtes complexes
- Écosystème : Meilleure couverture des besoins ML/AI
- Maintenance : Réduction de 40% du temps de maintenance
- Coût : Réduction de 30% des coûts d'infrastructure

**Validation** :
- Consensus protocol : 3 vagues exécutées
- Escalade humaine : Approuvée par le CTO
- Stakeholders : Produit, Tech, Data, Gouvernance

**ADR** : `docs/adr/ADR-001-php-to-python.md`
```

---

### Exemple 2 : Migration de base de données

**Contexte** : Migration de MySQL à PostgreSQL pour le service principal.

**Classification** : L4 - Irréversible

**Coût de rollback** : IMPOSSIBLE (données perdues)

**Justification** :
- Changement de moteur de base de données
- Migration de 10M+ lignes de données
- Changement de schéma fondamental
- Dépendances SQL incompatibles

**Décision documentée** :
```markdown
## ADR-002 : Migration MySQL → PostgreSQL

**Date** : 2026-03-20
**Décideur** : DatabaseEngineer

**Décision** : Migrer la base de données principale de MySQL 8.0 à PostgreSQL 15

**Réversibilité** : L4 - Irréversible

**Coût de rollback** : IMPOSSIBLE

**Données perdues** :
- Données historiques non supportées par PostgreSQL
- Indexs personnalisés MySQL non compatibles
- Procédures stockées MySQL non compatibles

**Validation** :
- Consensus protocol : 3 vagues exécutées
- Escalade humaine : Approuvée par le CTO
- Tests de migration : 100% succès en staging
- Backup complet effectué

**ADR** : `docs/adr/ADR-002-mysql-to-postgres.md`
```

---

### Exemple 3 : Changement de schéma fondamental

**Contexte** : Refactoring de la base de données de documents JSON à tables relationnelles.

**Classification** : L3 - Partiellement irréversible

**Coût de rollback** : 3-4 person-weeks, risque de perte de données

**Justification** :
- Meilleure performance pour les requêtes complexes
- Meilleure intégrité des données
- Compatibilité avec les outils d'analyse
- Risque : Perte potentielle de données JSON non structurées

**Décision documentée** :
```markdown
## ADR-003 : Refactoring JSON → Relationnel

**Date** : 2026-03-20
**Décideur** : DataEngineer

**Décision** : Migrer le stockage de documents JSON à un schéma relationnel

**Réversibilité** : L3 - Partiellement irréversible

**Coût de rollback** :
- Person-weeks : 3-4
- Données : Risque de perte des données JSON non structurées
- Dépendances : 8 services impactés

**Validation** :
- Consensus protocol : 3 vagues exécutées
- Tests de rollback : 80% succès en staging
- Validation par consensus protocol

**ADR** : `docs/adr/ADR-003-json-to-relational.md`
```

---


## Section Consensus : Décision [SUJET]

**Niveau de réversibilité** : L{2|3|4}

**Déclenchement consensus** : [x] Obligatoire (coût > 2 person-weeks)

**Vagues exécutées** :
- Vague 1 : {date} - {résultat}
- Vague 2 : {date} - {résultat}
- Vague 3 : {date} - {résultat}

**Verdict** : [x] Validé par consensus

**Référence** : `docs/adr/ADR-XXX-{sujet}.md`
```

---

## Checklist d'implémentation

### Pour les nouveaux projets

- [ ] Définir le niveau de réversibilité de chaque décision
- [ ] Estimer le coût de rollback avant de prendre des décisions
- [ ] Documenter les décisions irréversibles dans des ADR
- [ ] Mettre en place le consensus protocol pour les décisions L2+
- [ ] Créer des checklists de validation spécifiques

### Pour les projets existants

- [ ] Auditer les décisions passées et leur réversibilité
- [ ] Documenter les décisions non documentées
- [ ] Mettre à jour les ADR existants
- [ ] Créer un registre des décisions irréversibles
- [ ] Établir un processus de validation formel

---
