---
name: incident-response
description: "Structured incident response protocol — chain activation, role coordination, post-mortem"
argument-hint: "[description]"
user-invocable: true
---

# Protocole opérationnel de réponse aux incidents critiques


---

## Principe fondamental

La réponse aux incidents critiques doit être **rapide, structurée et collaborative**. L'objectif est de restaurer le service le plus rapidement possible, puis d'analyser la cause racine pour éviter la récurrence.

L'objectif est de :
- **Activer** une chaîne d'incident standardisée
- **Coordonner** la réponse entre les rôles spécialisés
- **Communiquer** efficacement pendant l'incident
- **Documenter** l'incident et les actions correctives

---

## Chaîne d'incident standardisée

### Rôles de la chaîne d'incident

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHAÎNE D'INCIDENT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IncidentCommander  →  ObservabilityEngineer  →  Debugger      │
│       │                    │                        │           │
│       │                    │                        │           │
│       ▼                    ▼                        ▼           │
│  Coordination    Diagnostic    Résolution                    │
│                                                                 │
│  DevOpsEngineer  ←───────────────────────────────────────────┐ │
│       │                                                      │ │
│       │ (support infrastructure)                             │ │
│       ▼                                                      │ │
│  Infrastructure                                             │ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Rôle 1 : IncidentCommander

**Responsabilité** : Coordination globale de l'incident

**Objectifs** :
- Activer la chaîne d'incident
- Assigner les rôles
- Coordonner les actions
- Communiquer avec les stakeholders
- Déclarer la fin de l'incident

**Actions** :

1. **Activation** (0-5 min)
   - Recevoir l'alerte
   - Évaluer la sévérité
   - Activer la chaîne d'incident
   - Assigner les rôles

2. **Coordination** (pendant l'incident)
   - Tenir les réunions d'incident
   - Suivre les actions en cours
   - Gérer les communications
   - Prendre les décisions critiques

3. **Closure** (après résolution)
   - Déclarer la fin de l'incident
   - Lancer le post-mortem
   - Suivre les actions correctives

**Template de communication** :

```markdown
## Incident #INC-001 — [SUJET]

**Date** : [DATE]
**Heure** : [HEURE]
**Sévérité** : [P1/P2/P3]
**Statut** : [En cours/Résolu]

**Équipe** :
- IncidentCommander : {nom}
- ObservabilityEngineer : {nom}
- Debugger : {nom}
- DevOpsEngineer : {nom}

**Timeline** :
- [HEURE] : Incident détecté
- [HEURE] : Chaîne d'incident activée
- [HEURE] : Diagnostic en cours
- [HEURE] : Résolution en cours
- [HEURE] : Service restauré

**Actions en cours** :
- [action 1]
- [action 2]
- [action 3]

**Prochaines étapes** :
- Post-mortem à [DATE]
- Actions correctives à suivre
```

---

### Rôle 2 : ObservabilityEngineer

**Responsabilité** : Diagnostic et visibilité sur l'incident

**Objectifs** :
- Analyser les métriques
- Analyser les logs
- Analyser les traces
- Identifier la cause racine

**Actions** :

1. **Analyse initiale** (0-10 min)
   - Vérifier les métriques de santé
   - Vérifier les logs d'erreur
   - Vérifier les traces distribuées
   - Identifier les patterns d'erreur

2. **Analyse approfondie** (10-30 min)
   - Analyser les métriques en détail
   - Analyser les logs en détail
   - Analyser les traces en détail
   - Corréler les événements

3. **Identification de la cause** (30-60 min)
   - Identifier la cause racine
   - Identifier l'impact
   - Proposer des solutions

**Outils utilisés** :
- Dashboard API
- Dashboard Base de données
- Dashboard ML/AI
- Dashboard Infrastructure
- Logs structurés
- Traces distribuées
- Métriques en temps réel

**Template de rapport** :

```markdown
## Rapport Observability — Incident #INC-001

**Date** : [DATE]
**Heure** : [HEURE]

**Métriques analysées** :
- Disponibilité : {valeur}%
- Latence P99 : {valeur}ms
- Erreurs : {valeur}%
- Requêtes/sec : {valeur}

**Logs analysés** :
- Nombre de logs : {nombre}
- Patterns d'erreur : {patterns}
- Erreurs critiques : {nombre}

**Traces analysées** :
- Nombre de traces : {nombre}
- Traces avec erreur : {nombre}
- Services impactés : {services}

**Cause racine identifiée** :
{description de la cause racine}

**Impact** :
- Services impactés : {services}
- Utilisateurs impactés : {nombre}
- Données impactées : {description}

**Solutions proposées** :
- {solution 1}
- {solution 2}
- {solution 3}
```

---

### Rôle 3 : Debugger

**Responsabilité** : Résolution technique de l'incident

**Objectifs** :
- Reproduire l'erreur
- Débugger le code
- Implémenter la correction
- Tester la correction

**Actions** :

1. **Reproduction** (0-15 min)
   - Reproduire l'erreur en environnement de staging
   - Identifier les conditions de reproduction
   - Préparer l'environnement de test

2. **Débuggage** (15-45 min)
   - Analyser le code
   - Identifier le bug
   - Comprendre la cause racine

3. **Correction** (45-90 min)
   - Implémenter la correction
   - Tester la correction
   - Préparer le déploiement

**Outils utilisés** :
- IDE
- Terminal
- Logs locaux
- Base de données locale
- Environnement de staging

**Template de rapport** :

```markdown
## Rapport Debugger — Incident #INC-001

**Date** : [DATE]
**Heure** : [HEURE]

**Erreur reproduite** :
{description de l'erreur reproduite}

**Conditions de reproduction** :
- {condition 1}
- {condition 2}
- {condition 3}

**Cause racine identifiée** :
{description de la cause racine}

**Correction implémentée** :
{description de la correction}

**Code modifié** :
- `fichier1.md` : {modification}
- `fichier2.md` : {modification}

**Tests effectués** :
- [x] Test de reproduction
- [x] Test de correction
- [x] Test de régression

**Prêt pour déploiement** : [x] Oui / [ ] Non
```

---

### Rôle 4 : DevOpsEngineer

**Responsabilité** : Support infrastructure et déploiement

**Objectifs** :
- Préparer l'environnement
- Déployer la correction
- Surveiller le déploiement
- Restaurer l'infrastructure si nécessaire

**Actions** :

1. **Préparation** (0-10 min)
   - Préparer l'environnement de déploiement
   - Préparer les scripts de déploiement
   - Préparer les scripts de rollback

2. **Déploiement** (10-30 min)
   - Déployer la correction
   - Surveiller le déploiement
   - Vérifier la santé du service

3. **Post-déploiement** (30-60 min)
   - Surveiller les métriques
   - Surveiller les logs
   - Surveiller les traces
   - Valider la résolution

**Outils utilisés** :
- CI/CD pipeline
- Infrastructure as Code
- Scripts de déploiement
- Scripts de rollback
- Outils de monitoring

**Template de rapport** :

```markdown
## Rapport DevOps — Incident #INC-001

**Date** : [DATE]
**Heure** : [HEURE]

**Environnement préparé** :
- {environnement 1}
- {environnement 2}

**Déploiement effectué** :
- {description du déploiement}
- {version déployée}
- {timestamp}

**Scripts utilisés** :
- `deploy.sh`
- `rollback.sh`
- `health-check.sh`

**Santé post-déploiement** :
- Disponibilité : {valeur}%
- Latence P99 : {valeur}ms
- Erreurs : {valeur}%

**Validation** :
- [x] Service disponible
- [x] Métriques normales
- [x] Logs propres
- [x] Traces propres

**Rollback prêt** : [x] Oui / [ ] Non
```

---

## Templates de post-mortem

### Template de post-mortem complet

```markdown
# Post-Mortem — Incident #INC-001

**Date de l'incident** : [DATE]
**Date du post-mortem** : [DATE]
**Sévérité** : [P1/P2/P3]
**Durée** : [HEURE]

## Résumé

{description concise de l'incident en 1-2 paragraphes}

## Timeline

| Heure | Événement | Responsable |
|-------|-----------|-------------|
| [HEURE] | Incident détecté | {nom} |
| [HEURE] | Chaîne d'incident activée | {nom} |
| [HEURE] | Diagnostic commencé | {nom} |
| [HEURE] | Cause racine identifiée | {nom} |
| [HEURE] | Correction implémentée | {nom} |
| [HEURE] | Déploiement effectué | {nom} |
| [HEURE] | Service restauré | {nom} |
| [HEURE] | Incident clos | {nom} |

## Impact

### Services impactés
- {service 1}
- {service 2}
- {service 3}

### Utilisateurs impactés
- {nombre} utilisateurs
- {pourcentage}% des utilisateurs

### Données impactées
- {description des données impactées}

### Revenus impactés
- {montant estimé}

## Cause racine

### Description
{description détaillée de la cause racine}

### Catégorie
- [ ] Erreur humaine
- [ ] Bug de code
- [ ] Problème d'infrastructure
- [ ] Problème de configuration
- [ ] Problème de sécurité
- [ ] Autre

### Preuves
{preuves de la cause racine}

## Actions correctives

### Actions immédiates (faites)
- [x] {action 1}
- [x] {action 2}
- [x] {action 3}

### Actions à court terme (à faire)
- [ ] {action 1} - {responsable} - {deadline}
- [ ] {action 2} - {responsable} - {deadline}
- [ ] {action 3} - {responsable} - {deadline}

### Actions à long terme (à faire)
- [ ] {action 1} - {responsable} - {deadline}
- [ ] {action 2} - {responsable} - {deadline}
- [ ] {action 3} - {responsable} - {deadline}

## Leçons apprises

### Ce que nous avons appris
- {leçon 1}
- {leçon 2}
- {leçon 3}

### Ce que nous allons améliorer
- {amélioration 1}
- {amélioration 2}
- {amélioration 3}

## Prévention

### Mesures de prévention
- {mesure 1}
- {mesure 2}
- {mesure 3}

### Tests de résilience
- {test 1}
- {test 2}
- {test 3}

## Annexes

- Logs de l'incident : {lien}
- Dashboard de l'incident : {lien}
- Code modifié : {lien}
- Déploiement : {lien}
```

---

## Protocole de communication pendant l'incident

### Communication interne

#### Canal #incident (chat)

**Utilisation** : Communication en temps réel pendant l'incident

**Règles** :
1. **Un seul message par personne par 15 min** : Éviter le spam
2. **Format structuré** : Utiliser le template de communication
3. **Mises à jour régulières** : Mettre à jour toutes les 15-30 min
4. **Pas de panique** : Garder un ton calme et professionnel

**Template de mise à jour** :

```
🔔 [MISE À JOUR] Incident #INC-001

**Statut** : {en cours/résolu}
**Dernière mise à jour** : {heure}

**Progression** :
- Diagnostic : {pourcentage}%
- Résolution : {pourcentage}%

**Actions en cours** :
- {action 1}
- {action 2}

**Prochaine mise à jour** : {heure}
```

---

#### Canal #incident-internal (email)

**Utilisation** : Communication avec les équipes internes

**Règles** :
1. **Email initial** : Notification de l'incident
2. **Emails réguliers** : Mise à jour toutes les 30 min
3. **Email final** : Notification de la résolution

**Template d'email initial** :

```
Sujet : [INCIDENT] {service} - {description}

Équipe,

Un incident a été détecté sur {service}.

**Sévérité** : {P1/P2/P3}
**Impact** : {description}
**Statut** : En cours

**Équipe d'intervention** :
- IncidentCommander : {nom}
- ObservabilityEngineer : {nom}
- Debugger : {nom}
- DevOpsEngineer : {nom}

**Actions en cours** :
- {action 1}
- {action 2}

**Prochaine mise à jour** : {heure}

Voir le chat #incident pour les mises à jour en temps réel.
```

---

#### Canal #incident-external (status page)

**Utilisation** : Communication avec les utilisateurs externes

**Règles** :
1. **Status page** : Mettre à jour la status page
2. **Emails aux utilisateurs** : Si impact utilisateur
3. **Ton transparent** : Être transparent sans révéler de détails sensibles

**Template de status page** :

```
## Incident #INC-001

**Statut** : Investigating

**Description** : Nous avons détecté un problème sur {service} qui affecte {description}.

**Impact** : {description de l'impact}

**Actions en cours** :
- Investigation en cours
- Équipe d'intervention mobilisée

**Mise à jour prévue** : Dans 30 minutes

**Contact** : {email de support}
```

---

### Communication externe

#### Email aux utilisateurs

**Utilisation** : Notification aux utilisateurs impactés

**Règles** :
1. **Email initial** : Notification de l'incident
2. **Emails réguliers** : Mise à jour toutes les 30 min
3. **Email final** : Notification de la résolution

**Template d'email initial** :

```
Sujet : [INCIDENT] Problème sur {service}

Cher utilisateur,

Nous avons détecté un problème sur {service} qui affecte {description}.

**Impact** : {description de l'impact}

**Actions en cours** :
- Notre équipe d'intervention est mobilisée
- Investigation en cours

**Mise à jour prévue** : Dans 30 minutes

Nous vous tiendrons informé de l'évolution de la situation.

Cordialement,
L'équipe {nom}
```

---

#### Email de résolution

**Utilisation** : Notification de la résolution

**Règles** :
1. **Email de résolution** : Notification de la résolution
2. **Lien vers le post-mortem** : Lien vers le post-mortem
3. **Remerciements** : Remercier les utilisateurs pour leur patience

**Template d'email de résolution** :

```
Sujet : [RÉSOLU] Problème sur {service} résolu

Cher utilisateur,

Nous tenons à vous informer que le problème sur {service} a été résolu.

**Heure de résolution** : {heure}
**Durée de l'incident** : {durée}

**Actions effectuées** :
- {action 1}
- {action 2}
- {action 3}

**Post-mortem** : Un post-mortem détaillé sera publié dans les jours à venir.

Nous vous remercions pour votre patience et votre compréhension.

Cordialement,
L'équipe {nom}
```

---

## Critères de closure d'incident

### Critères techniques

**L'incident peut être clos si** :

1. **Service restauré** : Le service est de nouveau disponible
2. **Métriques normales** : Les métriques sont retournées à la normale
3. **Logs propres** : Les logs ne montrent plus d'erreurs
4. **Traces propres** : Les traces ne montrent plus d'erreurs
5. **Tests passés** : Les tests de validation ont réussi

**Checklist de closure** :

- [ ] Service disponible
- [ ] Métriques normales pendant 15 min
- [ ] Logs propres pendant 15 min
- [ ] Traces propres pendant 15 min
- [ ] Tests de validation passés
- [ ] Rollback possible si nécessaire

---

### Critères de post-mortem

**Le post-mortem peut être lancé si** :

1. **Incident résolu** : L'incident est techniquement résolu
2. **Équipe disponible** : L'équipe est disponible pour le post-mortem
3. **Données collectées** : Les données nécessaires sont collectées

**Checklist de post-mortem** :

- [ ] Incident techniquement résolu
- [ ] Équipe disponible
- [ ] Logs collectés
- [ ] Métriques collectées
- [ ] Traces collectées
- [ ] Code modifié identifié

---

### Critères de closure finale

**L'incident peut être clos définitivement si** :

1. **Post-mortem publié** : Le post-mortem est publié
2. **Actions correctives assignées** : Les actions correctives sont assignées
3. **Stakeholders informés** : Les stakeholders sont informés

**Checklist de closure finale** :

- [ ] Post-mortem publié
- [ ] Actions correctives assignées
- [ ] Stakeholders informés
- [ ] Status page mise à jour
- [ ] Emails envoyés aux utilisateurs
- [ ] Incident clos dans le système

---

## Exemples de scénarios d'incident

### Scénario 1 : Dégradation de service

**Description** : Le service API répond lentement et avec des erreurs.

**Symptômes** :
- Latence P99 > 1s
- Taux d'erreur > 5%
- Requêtes/sec en baisse

**Chaîne d'incident** :
1. **IncidentCommander** : Active la chaîne, assigne les rôles
2. **ObservabilityEngineer** : Analyse les métriques, identifie le pic de charge
3. **Debugger** : Identifie le bug de mémoire dans le code
4. **DevOpsEngineer** : Déploie la correction

**Cause racine** : Bug de mémoire dans le code qui sature la mémoire.

**Actions correctives** :
- [x] Déployer la correction
- [ ] Ajouter des tests de mémoire
- [ ] Mettre en place du monitoring de mémoire

---

### Scénario 2 : Fuite de données

**Description** : Des données sensibles sont exposées publiquement.

**Symptômes** :
- Alertes de sécurité
- Données sensibles dans les logs
- Données sensibles dans les traces

**Chaîne d'incident** :
1. **IncidentCommander** : Active la chaîne, escalade P1
2. **ObservabilityEngineer** : Identifie la fuite, localise les données
3. **Debugger** : Identifie la vulnérabilité, implémente la correction
4. **DevOpsEngineer** : Déploie la correction, révoque les accès

**Cause racine** : Vulnérabilité de sécurité dans l'authentification.

**Actions correctives** :
- [x] Révoquer les accès compromis
- [x] Déployer la correction
- [ ] Audit de sécurité complet
- [ ] Formation de l'équipe

---

### Scénario 3 : Panne infrastructure

**Description** : Le serveur principal est hors ligne.

**Symptômes** :
- Service indisponible
- Métriques d'infrastructure anormales
- Logs d'erreur sur l'infrastructure

**Chaîne d'incident** :
1. **IncidentCommander** : Active la chaîne, assigne les rôles
2. **ObservabilityEngineer** : Identifie la panne, vérifie l'état de l'infrastructure
3. **Debugger** : Analyse les logs, identifie la cause
4. **DevOpsEngineer** : Restaure l'infrastructure, déploie sur un nouveau serveur

**Cause racine** : Panne matérielle du serveur.

**Actions correctives** :
- [x] Restaurer l'infrastructure
- [ ] Mettre en place du monitoring prédictif
- [ ] Ajouter de la redondance

---


## Déclenchement automatique pour incident

**Déclencheur** : Alertes critiques détectées

**Actions** :
1. Déclencher la chaîne d'incident
2. Notifier l'IncidentCommander
3. Assigner les rôles
4. Configurer les canaux de communication

**Validation** :
- [x] Chaîne d'incident activée
- [x] Rôles assignés
- [x] Canaux configurés
- [x] Communication initiée
```

---


## Transfert d'incident

**Incident** : #INC-001

**Transfert de** : {équipe actuelle}
**Transfert à** : {équipe cible}

**Raison** : {raison du transfert}

**Contexte** :
- {description du contexte}
- {actions déjà effectuées}
- {prochaines étapes}

**Documentation** :
- Post-mortem : {lien}
- Logs : {lien}
- Dashboard : {lien}
```

---

## Checklist d'implémentation

### Pour les nouveaux services

- [ ] Définir la chaîne d'incident
- [ ] Configurer les canaux de communication
- [ ] Configurer les alertes
- [ ] Configurer la status page
- [ ] Créer les templates de communication
- [ ] Former l'équipe au protocole

### Pour les services existants

- [ ] Auditer la réponse aux incidents
- [ ] Identifier les lacunes
- [ ] Mettre à jour la chaîne d'incident
- [ ] Configurer les canaux manquants
- [ ] Créer les templates manquants
- [ ] Former l'équipe au protocole

---
