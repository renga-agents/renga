# Plugin : Game Studio

Pack d'agents spécialisés pour le développement de jeux vidéo.

## Agents inclus

| Agent | Rôle |
| --- | --- |
| game-developer | Développement gameplay, game loop, physique |
| game-balancer | Test et équilibrage du gameplay |
| game-producer | Gestion de production de jeux vidéo |
| game-asset-generator | Génération d'assets visuels via Replicate |
| audio-generator | Génération audio (SFX, musique, voix) via Replicate |
| level-designer | Conception d'architecture de niveaux |
| narrative-designer | Écriture scénaristique et dialogues |
| animations-engineer | WebGL, shaders, Three.js, animations |

## Activation

Dans `.renga.yml` :

```yaml

plugins:
  - game-studio

```

## Dépendances

Ce plugin est autonome. Il ne nécessite pas d'agents core spécifiques.
Les agents du plugin peuvent interagir avec les agents core standard (qa-engineer, code-reviewer, etc.).
