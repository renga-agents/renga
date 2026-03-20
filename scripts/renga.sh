#!/usr/bin/env bash
# =============================================================================
# renga CLI — Point d'entrée unifié du framework renga
# =============================================================================
#
# Usage: ./scripts/renga.sh <command>
#
# Commands:
#   install   — Installe les agents depuis une release GitHub (crée .renga.yml si absent)
#   update    — Met à jour les agents vers la dernière version
#   list      — Liste les agents et plugins installés
#   plugin    — Gestion des plugins (add, remove, list)
#   validate  — Lance scripts/validate_agents.py
#   doctor    — Vérifie la santé du setup (Python, fichiers, schéma)
#   dashboard — Lance scripts/generate_dashboard.py
#   build     — Construit l'artefact de distribution
#   version   — Affiche la version
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Version (replaced by build_dist.py at build time)
# ---------------------------------------------------------------------------
RENGA_VERSION="__RENGA_VERSION__"

# ---------------------------------------------------------------------------
# Couleurs & symboles
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  GREEN=$'\033[0;32m'
  RED=$'\033[0;31m'
  YELLOW=$'\033[0;33m'
  BOLD=$'\033[1m'
  RESET=$'\033[0m'
else
  GREEN='' RED='' YELLOW='' BOLD='' RESET=''
fi

ok()   { printf "${GREEN}✓${RESET} %s\n" "$1"; }
fail() { printf "${RED}✗${RESET} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${RESET} %s\n" "$1"; }
info() { printf "${BOLD}→${RESET} %s\n" "$1"; }

# ---------------------------------------------------------------------------
# Résolution du répertoire racine du projet
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(pwd)"
# ROOT_DIR is always the working directory from which the CLI is invoked

# ---------------------------------------------------------------------------
# Configuration distrib
# ---------------------------------------------------------------------------
RENGA_REPO="${RENGA_REPO:-renga-agents/renga}"
RENGA_API="https://api.github.com/repos/$RENGA_REPO"
RENGA_DIR="$ROOT_DIR/.github/agents"
INSTRUCTIONS_DIR="$ROOT_DIR/.github/instructions"
SKILLS_DIR="$ROOT_DIR/.github/skills"
HOOKS_DIR="$ROOT_DIR/.github/hooks"
LOCK_FILE="$ROOT_DIR/.renga.lock"
CONFIG_FILE="$ROOT_DIR/.renga.yml"
RENGA_SHARE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/renga"

# ---------------------------------------------------------------------------
# Hooks installation helper
# ---------------------------------------------------------------------------

install_hooks() {
  local hooks_src="$1"
  if [[ ! -d "$hooks_src" ]]; then
    warn "Pas de répertoire hooks/ dans l'artefact — hooks ignorés"
    return 0
  fi

  info "Installation des hooks..."
  mkdir -p "$HOOKS_DIR"
  mkdir -p "$HOOKS_DIR/scripts"

  local hook_count=0

  # Copy managed hook config files (*.hooks.json)
  for f in "$hooks_src"/*.hooks.json; do
    [[ -f "$f" ]] || continue
    cp "$f" "$HOOKS_DIR/"
    hook_count=$((hook_count + 1))
  done

  # Copy managed hook scripts
  if [[ -d "$hooks_src/scripts" ]]; then
    for f in "$hooks_src/scripts/"*.sh; do
      [[ -f "$f" ]] || continue
      cp "$f" "$HOOKS_DIR/scripts/"
    done
  fi

  # chmod +x on all .sh scripts in hooks/scripts/
  find "$HOOKS_DIR/scripts" -name '*.sh' -exec chmod +x {} +

  # Cache hooks schema in share dir (available via 'renga local init schemas')
  if [[ -f "$hooks_src/../schemas/hooks.schema.json" ]]; then
    mkdir -p "$RENGA_SHARE_DIR/schemas"
    cp "$hooks_src/../schemas/hooks.schema.json" "$RENGA_SHARE_DIR/schemas/"
  fi

  ok "$hook_count fichier(s) hooks installé(s)"

  # Check jq dependency (required by hook scripts)
  if ! command -v jq &>/dev/null; then
    warn "jq non trouvé — les hooks de sécurité seront désactivés jusqu'à son installation."
    warn "  → brew install jq   (macOS)"
    warn "  → apt-get install jq  (Linux)"
  fi
}

init_working_memory() {
  local memory_dir="$ROOT_DIR/.renga/memory"
  mkdir -p "$memory_dir"

  # scratchpad.md — session index (append-only), create if absent
  local scratchpad="$memory_dir/scratchpad.md"
  if [[ ! -f "$scratchpad" ]]; then
    cat > "$scratchpad" <<'SCRATCHPAD'
# Session Index

> Append-only master index. Each entry represents an orchestration session.
> Format: `- YYYY-MM-DDTHH:MM | <slug> | <status> | <summary>`

<!-- Sessions (append below) -->
SCRATCHPAD
    ok "Created .renga/memory/scratchpad.md"
  fi

  # project-context.md — stack and structuring decisions, create if absent
  local ctx="$memory_dir/project-context.md"
  if [[ ! -f "$ctx" ]]; then
    cat > "$ctx" <<'CONTEXT'
# Project Context

> Fill in this file after your first session. Seiji reads it at session start.

## Stack

<!-- e.g. Next.js 15, PostgreSQL, Vercel, TypeScript -->

## Key constraints

<!-- e.g. Bash 3.2 compat, no mapfile, Python 3.9+ -->

## Structuring decisions

<!-- Record irreversible architectural decisions here -->
CONTEXT
    ok "Created .renga/memory/project-context.md"
  fi
}

ensure_gitignore_reports() {
  local gitignore="$ROOT_DIR/.gitignore"
  if [[ -f "$gitignore" ]]; then
    if ! grep -qF '.renga/reports/' "$gitignore"; then
      printf '\n# renga reports\n.renga/reports/\n' >> "$gitignore"
      ok "Added .renga/reports/ to .gitignore"
    fi
  else
    printf '# renga reports\n.renga/reports/\n' > "$gitignore"
    ok "Created .gitignore with .renga/reports/"
  fi
}

normalize_profile() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

write_profile_config() {
  local profile="$1"
  local dest="$2"

  case "$profile" in
    lite)
      cat > "$dest" <<EOF
agents:
  mode: "whitelist"
  include:
    - seiji
    - backend-dev
    - frontend-dev
    - qa-engineer
    - code-reviewer
    - software-architect
    - debugger
    - git-expert
    - tech-writer

waivers: []
EOF
      ;;
    standard)
      cat > "$dest" <<EOF
agents:
  mode: "whitelist"
  include:
    - backend-dev
    - frontend-dev
    - qa-engineer
    - code-reviewer
    - software-architect
    - debugger
    - git-expert
    - tech-writer
    - seiji
    - security-engineer
    - database-engineer
    - devops-engineer
    - ux-ui-designer
    - api-designer
    - performance-engineer
    - product-manager
    - prompt-engineer
    - platform-engineer
    - fullstack-dev
    - mobile-dev

waivers: []
EOF
      ;;
    full)
      cat > "$dest" <<EOF
agents:
  mode: "all"
  include: []
  exclude: []

waivers: []
EOF
      ;;
    *)
      fail "Unsupported profile: $profile"
      return 1
      ;;
  esac
}

# ---------------------------------------------------------------------------
# Commandes
# ---------------------------------------------------------------------------

_create_validate_workflow() {
  local workflow_dir="$ROOT_DIR/.github/workflows"
  local workflow_file="$workflow_dir/agent-validate.yml"
  mkdir -p "$workflow_dir"
  cat > "$workflow_file" <<'WORKFLOW'
name: Agent Validation

on:
  push:
    paths:
      - '.github/agents/**'
      - '.github/instructions/**'
      - '.github/skills/**'
      - '.renga.yml'
  pull_request:
    paths:
      - '.github/agents/**'
      - '.github/instructions/**'
      - '.github/skills/**'
      - '.renga.yml'

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install renga CLI
        run: |
          curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh

      - name: Validate agents
        run: renga validate
WORKFLOW
}

cmd_validate() {
  info "Validation des agents..."

  # Look for the script in the system share dir (installed by install.sh)
  local script="$RENGA_SHARE_DIR/scripts/validate_agents.py"
  if [[ ! -f "$script" ]]; then
    fail "Script introuvable. Relancez l'installation : curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh"
    return 1
  fi

  local rc=0
  python3 "$script" --agents-dir "$RENGA_DIR" || rc=$?

  case $rc in
    0) ok "Validation terminée — tous les agents sont valides" ;;
    1) warn "Validation terminée — des warnings ont été détectés" ;;
    2) fail "Validation terminée — des erreurs ont été détectées" ; return 1 ;;
    *) fail "Validation échouée (code de sortie: $rc)" ; return 1 ;;
  esac
}

cmd_doctor() {
  info "Diagnostic du setup renga..."
  local errors=0

  # 1. Python ≥ 3.9
  if command -v python3 &>/dev/null; then
    local py_version
    py_version="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
      ok "Python $py_version détecté (≥ 3.9)"
    else
      fail "Python $py_version détecté — version 3.9+ requise"
      errors=$((errors + 1))
    fi
  else
    fail "Python 3 non trouvé dans le PATH"
    errors=$((errors + 1))
  fi

  # 2. Fichier de config
  if [[ -f "$ROOT_DIR/.renga.yml" ]]; then
    ok ".renga.yml présent"
  else
    warn ".renga.yml absent — lancez 'renga install'"
    errors=$((errors + 1))
  fi

  # 3. Répertoire agents
  local agents_dir="$ROOT_DIR/.github/agents"
  if [[ -d "$agents_dir" ]]; then
    local agent_count
    agent_count="$(find "$agents_dir" -maxdepth 1 -name '*.agent.md' | wc -l | tr -d ' ')"
    if [[ "$agent_count" -gt 0 ]]; then
      ok "$agent_count fichiers .agent.md trouvés dans .github/agents/"
    else
      fail "Aucun fichier .agent.md dans .github/agents/"
      errors=$((errors + 1))
    fi
  else
    fail "Répertoire .github/agents/ introuvable"
    errors=$((errors + 1))
  fi

  # 4. Schéma JSON
  if [[ -f "$ROOT_DIR/schemas/agent.schema.json" ]]; then
    ok "schemas/agent.schema.json présent"
    # Vérification basique : le fichier est du JSON valide
    if python3 -c "import json, pathlib, sys; json.loads(pathlib.Path(sys.argv[1]).read_text())" "$ROOT_DIR/schemas/agent.schema.json" 2>/dev/null; then
      ok "Schéma JSON syntaxiquement valide"
    else
      fail "Schéma JSON invalide (erreur de syntaxe)"
      errors=$((errors + 1))
    fi
  else
    info "schemas/ non installé (optionnel — utilisez 'renga local init schemas' pour activer la validation IDE)"
  fi

  # 5. Skills directory
  if [[ -d "$SKILLS_DIR" ]]; then
    local skill_count
    skill_count="$(find "$SKILLS_DIR" -name 'SKILL.md' -not -path '*/_local/*' 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "$skill_count" -gt 0 ]]; then
      ok "$skill_count fichier(s) SKILL.md trouvé(s) dans .github/skills/"
    else
      warn "Aucun SKILL.md dans .github/skills/"
    fi
  else
    warn ".github/skills/ introuvable — lancez 'renga install'"
  fi

  # 6. Hooks directory
  if [[ -d "$HOOKS_DIR" ]]; then
    local hooks_count
    hooks_count="$(find "$HOOKS_DIR" -maxdepth 1 -name '*.hooks.json' 2>/dev/null | wc -l | tr -d ' ')"
    if [[ "$hooks_count" -gt 0 ]]; then
      ok "$hooks_count fichier(s) .hooks.json trouvé(s) dans .github/hooks/"
    else
      warn "Aucun .hooks.json dans .github/hooks/"
    fi
    if [[ -d "$HOOKS_DIR/scripts" ]]; then
      local scripts_count
      scripts_count="$(find "$HOOKS_DIR/scripts" -name '*.sh' 2>/dev/null | wc -l | tr -d ' ')"
      ok "$scripts_count script(s) hooks trouvé(s) dans .github/hooks/scripts/"
    else
      warn ".github/hooks/scripts/ introuvable"
    fi
  else
    warn ".github/hooks/ introuvable — lancez 'renga install'"
  fi


  # Résumé
  echo ""
  if [[ "$errors" -eq 0 ]]; then
    ok "Diagnostic OK — aucun problème détecté"
  else
    fail "Diagnostic terminé — $errors problème(s) détecté(s)"
    return 1
  fi
}

cmd_dashboard() {
  info "Génération du dashboard..."

  # Look for the script in the system share dir (installed by install.sh)
  local script="$RENGA_SHARE_DIR/scripts/generate_dashboard.py"
  if [[ ! -f "$script" ]]; then
    fail "Script introuvable. Relancez l'installation : curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh"
    return 1
  fi

  python3 "$script" \
    --memory-dir "$ROOT_DIR/.renga/memory" \
    --output "$ROOT_DIR/.renga/reports/dashboard.md"
  ok "Dashboard généré dans .renga/reports/dashboard.md"
}

cmd_build() {
  info "Build de l'artefact de distribution..."
  local script="$ROOT_DIR/scripts/build_dist.py"
  if [[ ! -f "$script" ]]; then
    fail "Script introuvable : scripts/build_dist.py"
    return 1
  fi
  python3 "$script" "$@"
  ok "Build terminé"
}

# ---------------------------------------------------------------------------
# Helpers model
# ---------------------------------------------------------------------------

# _apply_models — lit la section models: de .renga.yml et stamp le champ model:
# dans chaque fichier *.agent.md de RENGA_DIR. N'écrase que les valeurs par
# défaut ; les overrides par agent sont appliqués depuis models.overrides.
_apply_models() {
  local config="$ROOT_DIR/.renga.yml"
  [[ -f "$config" ]] || return 0

  local py_script
  py_script="$(mktemp /tmp/renga_apply_models_XXXXXX.py)"
  cat > "$py_script" << 'PYEOF'
import re, pathlib, sys

config_p = pathlib.Path(sys.argv[1])
agents_p = pathlib.Path(sys.argv[2])
text = config_p.read_text()

# Extract models: section from .renga.yml
m = re.search(r'^models:\s*\n((?:  [^\n]*\n?)*)', text, re.M)
if not m:
    sys.exit(0)
models_section = m.group(1)

# Parse default model (indented: "  default: ...")
m2 = re.search(r'^  default:\s*["\']?([^"\'#\n]+)', models_section, re.M)
default_model = m2.group(1).strip().strip('"\'') if m2 else None
if not default_model:
    sys.exit(0)

# Parse per-agent overrides (indented under "  overrides:")
overrides = {}
in_ov = False
for line in models_section.splitlines():
    if re.match(r'  overrides:', line):
        in_ov = True
        continue
    if in_ov:
        mm = re.match(r'    (\S+):\s*["\']?([^"\'#\n]+)', line)
        if mm:
            overrides[mm.group(1)] = mm.group(2).strip().strip('"\'')
        elif not line.startswith('    ') and line.strip():
            in_ov = False

count = 0
for f in sorted(agents_p.glob('*.agent.md')):
    name = f.name.replace('.agent.md', '')
    model = overrides.get(name, default_model)
    c = f.read_text()
    if re.search(r'^model:', c, re.M):
        new = re.sub(r'^model:.*', f'model: {model}', c, flags=re.M)
    else:
        # Insérer model: juste après la première ligne ---
        new = c.replace('---\n', f'---\nmodel: {model}\n', 1)
    if new != c:
        f.write_text(new)
    count += 1

print(count)
PYEOF

  local count
  count="$(python3 "$py_script" "$config" "$RENGA_DIR" 2>/dev/null)" || count=0
  rm -f "$py_script"
  if [[ -n "$count" && "$count" -gt 0 ]]; then
    ok "Modèle LLM appliqué à $count agents (depuis .renga.yml section models:)"
  fi
}

cmd_models() {
  local subcmd="${1:-apply}"
  shift 2>/dev/null || true

  case "$subcmd" in
    apply)
      if [[ ! -f "$ROOT_DIR/.renga.yml" ]]; then
        fail "Fichier introuvable : .renga.yml"
        return 1
      fi
      if ! grep -q '^models:' "$ROOT_DIR/.renga.yml" 2>/dev/null; then
        fail "Section 'models:' absente de .renga.yml"
        echo "Ajoutez dans .renga.yml :"
        echo "  models:"
        echo "    default: \"Claude Opus 4.6 (copilot)\""
        return 1
      fi
      info "Application de la configuration modèles LLM..."
      _apply_models
      ;;
    *)
      fail "Sous-commande inconnue : $subcmd"
      echo "Usage: renga models apply"
      return 1
      ;;
  esac
}

cmd_install() {
  local version="latest"
  local profile=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --version) version="$2"; shift 2 ;;
      --profile)
        profile="$(normalize_profile "$2")"
        shift 2
        ;;
      *) fail "Option inconnue : $1"; return 1 ;;
    esac
  done

  # Créer .renga.yml si absent (phase init intégrée)
  if [[ ! -f "$CONFIG_FILE" ]]; then
    if [[ -z "$profile" ]]; then
      if [[ -t 0 && -t 1 ]]; then
        local _profile_ans=""
        printf 'Select a profile [lite/standard/full] (default: lite): '
        read -r _profile_ans || true
        _profile_ans="$(normalize_profile "$_profile_ans")"
        case "$_profile_ans" in
          ""|lite|l) profile="lite" ;;
          standard|s) profile="standard" ;;
          full|f) profile="full" ;;
          *) warn "Profile inconnu '$_profile_ans' — utilisation de lite"; profile="lite" ;;
        esac
      else
        profile="lite"
      fi
    fi
    write_profile_config "$profile" "$CONFIG_FILE"
    ok ".renga.yml créé (profil $profile)"
  fi

  info "Installation de renga (version: $version)..."

  # Déterminer l'URL de la release
  local release_url
  if [[ "$version" == "latest" ]]; then
    release_url="$RENGA_API/releases/latest"
  else
    release_url="$RENGA_API/releases/tags/v${version}"
  fi

  # Télécharger et extraire dans un répertoire temporaire
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  # Save any existing EXIT trap and chain our cleanup
  local _prev_trap
  _prev_trap="$(trap -p EXIT | sed "s/^trap -- '//;s/' EXIT$//" 2>/dev/null || true)"
  trap "rm -rf '$tmp_dir'; ${_prev_trap:-true}" EXIT

  # Récupérer les infos de la release dans un fichier (évite la corruption par caractères de contrôle)
  local release_json_file="$tmp_dir/release.json"
  curl -fsSL "$release_url" -o "$release_json_file" || {
    fail "Impossible de récupérer la release $version"
    return 1
  }

  # Extraire l'URL du tarball (premier asset .tar.gz)
  local tarball_url
  tarball_url="$(python3 -c "
import json
data = json.load(open('$release_json_file', encoding='utf-8'))
assets = data.get('assets', [])
for a in assets:
    if a['name'].endswith('.tar.gz'):
        print(a['browser_download_url']); break
else:
    print(data.get('tarball_url', ''))
")" || {
    fail "Impossible de trouver l'artefact de la release"
    return 1
  }

  if [[ -z "$tarball_url" ]]; then
    fail "Aucun artefact trouvé dans la release"
    return 1
  fi

  info "Téléchargement depuis $tarball_url..."
  curl -fsSL "$tarball_url" | tar xz -C "$tmp_dir" --strip-components=1 || {
    fail "Échec du téléchargement/extraction"
    return 1
  }

  # Vérifier que le manifest existe
  local manifest="$tmp_dir/manifest.json"
  if [[ ! -f "$manifest" ]]; then
    fail "manifest.json introuvable dans l'artefact"
    return 1
  fi

  local installed_version
  installed_version="$(python3 -c "import json; print(json.load(open('$manifest', encoding='utf-8'))['version'])")"

  # Lire la whitelist depuis .renga.yml
  local whitelist_mode="all"
  # Note: `local -a` works on Bash 3.2+ (macOS default), unlike `declare -A`
  local -a whitelist_agents=()
  if [[ -f "$CONFIG_FILE" ]]; then
    whitelist_mode="$(python3 -c "
for line in open('$CONFIG_FILE', encoding='utf-8'):
    s = line.strip()
    if s.startswith('mode:'):
        val = s.split(':',1)[1].strip().strip('\"\'')
        print(val if val else 'all')
        break
else:
    print('all')
" 2>/dev/null || echo "all")"

    if [[ "$whitelist_mode" == "whitelist" ]]; then
      # Parse include list from YAML — boucle while compatible bash 3.2 (macOS)
      while IFS= read -r _agent_name; do
        [[ -n "$_agent_name" ]] && whitelist_agents+=("$_agent_name")
      done < <(python3 -c "
import re
text = open('$CONFIG_FILE', encoding='utf-8').read()
m = re.search(r'include:\s*\n((?:\s+-\s+\S+\n?)+)', text)
if m:
    for line in m.group(1).strip().splitlines():
        name = line.strip().lstrip('- ').strip()
        if name:
            print(name)
" 2>/dev/null)
    fi
  fi

  # Copier les agents
  info "Installation des agents..."
  mkdir -p "$RENGA_DIR"

  local agents_src="$tmp_dir/agents"
  local agent_count=0

  if [[ -d "$agents_src" ]]; then
    for agent_file in "$agents_src"/*.agent.md; do
      [[ -f "$agent_file" ]] || continue
      local agent_name
      agent_name="$(basename "$agent_file" .agent.md)"

      # Filtrage whitelist
      if [[ "$whitelist_mode" == "whitelist" ]] && [[ ${#whitelist_agents[@]} -gt 0 ]]; then
        local found=false
        for w in "${whitelist_agents[@]}"; do
          if [[ "$w" == "$agent_name" ]]; then
            found=true
            break
          fi
        done
        if [[ "$found" == "false" ]]; then
          continue
        fi
      fi

      cp "$agent_file" "$RENGA_DIR/"
      agent_count=$((agent_count + 1))
    done
  fi

  # Copier _references
  if [[ -d "$agents_src/_references" ]]; then
    mkdir -p "$RENGA_DIR/_references"
    cp -R "$agents_src/_references/"* "$RENGA_DIR/_references/" 2>/dev/null || true
  fi

  # Copier instructions
  info "Installation des instructions..."
  mkdir -p "$INSTRUCTIONS_DIR"
  local instr_src="$tmp_dir/instructions"
  local instr_count=0
  if [[ -d "$instr_src" ]]; then
    for f in "$instr_src"/*; do
      [[ -f "$f" ]] || continue
      cp "$f" "$INSTRUCTIONS_DIR/"
      instr_count=$((instr_count + 1))
    done
  fi

  # Installer copilot-instructions.md (seulement si absent — préserve les personnalisations)
  local copilot_instr_src="$tmp_dir/copilot-instructions.md"
  if [[ -f "$copilot_instr_src" ]]; then
    if [[ ! -f "$ROOT_DIR/.github/copilot-instructions.md" ]]; then
      cp "$copilot_instr_src" "$ROOT_DIR/.github/copilot-instructions.md"
      ok ".github/copilot-instructions.md créé"
    else
      info ".github/copilot-instructions.md déjà présent — ignoré (personnalisations préservées)"
    fi
  fi

  # Installer .vscode/settings.json si absent; sinon déposer settings.renga.json comme référence
  local vscode_src="$tmp_dir/vscode-settings.json"
  if [[ -f "$vscode_src" ]]; then
    mkdir -p "$ROOT_DIR/.vscode"
    if [[ ! -f "$ROOT_DIR/.vscode/settings.json" ]]; then
      cp "$vscode_src" "$ROOT_DIR/.vscode/settings.json"
      ok ".vscode/settings.json créé"
    else
      cp "$vscode_src" "$ROOT_DIR/.vscode/settings.renga.json"
      info ".vscode/settings.json déjà présent — référence déposée dans .vscode/settings.renga.json"
    fi
  fi

  # Copier skills
  info "Installation des skills..."
  mkdir -p "$SKILLS_DIR"
  local skills_src="$tmp_dir/skills"
  local skill_count=0
  if [[ -d "$skills_src" ]]; then
    for skill_dir in "$skills_src"/*/; do
      [[ -d "$skill_dir" ]] || continue
      local skill_name
      skill_name="$(basename "$skill_dir")"
      [[ "$skill_name" == "_local" ]] && continue
      mkdir -p "$SKILLS_DIR/$skill_name"
      cp -R "$skill_dir"* "$SKILLS_DIR/$skill_name/" 2>/dev/null || true
      skill_count=$((skill_count + 1))
    done
  fi

  # Mettre en cache les schémas dans le répertoire partagé (disponibles via 'renga local init schemas')
  if [[ -d "$tmp_dir/schemas" ]]; then
    mkdir -p "$RENGA_SHARE_DIR/schemas"
    for schema_file in "$tmp_dir/schemas/"*.json; do
      [[ -f "$schema_file" ]] || continue
      cp "$schema_file" "$RENGA_SHARE_DIR/schemas/"
    done
  fi

  # Copier les scripts Python essentiels dans le répertoire système partagé
  if [[ -d "$tmp_dir/scripts" ]]; then
    mkdir -p "$RENGA_SHARE_DIR/scripts"
    for script in "$tmp_dir/scripts"/*.py; do
      [[ -f "$script" ]] || continue
      cp "$script" "$RENGA_SHARE_DIR/scripts/"
    done
  fi

  # Installer les hooks
  install_hooks "$tmp_dir/hooks"

  # .gitignore reports
  ensure_gitignore_reports

  # Initialize .renga/memory/ with scratchpad.md and project-context.md
  init_working_memory

  # Appliquer la configuration des modèles LLM sur les agents installés
  _apply_models

  # Mettre en cache le manifest pour plugin list
  mkdir -p "$RENGA_SHARE_DIR"
  cp "$manifest" "$RENGA_SHARE_DIR/manifest.json"

  # Proposer les plugins disponibles
  local available_plugins=""
  available_plugins="$(python3 -c "
import json
m = json.load(open('$manifest', encoding='utf-8'))
plugins = list(m.get('plugins', {}).keys())
print(' '.join(plugins))
" 2>/dev/null)"

  if [[ -n "$available_plugins" && -t 0 && -t 1 ]]; then
    echo ""
    info "Plugins disponibles : $available_plugins"
    printf 'Activer des plugins ? (noms séparés par un espace, entrée pour ignorer) : '
    local _plugins_ans=""
    read -r _plugins_ans || true
    if [[ -n "$_plugins_ans" ]]; then
      for _p in $_plugins_ans; do
        local _plugin_src="$tmp_dir/plugins/$_p"
        if [[ -d "$_plugin_src" ]]; then
          _install_plugin_flat "$_p" "$_plugin_src"
          _add_plugin_to_config "$_p"
        else
          warn "Plugin '$_p' introuvable dans la release — ignoré"
        fi
      done
    fi
  fi

  # Écrire le lockfile
  cat > "$LOCK_FILE" <<LOCK
version: "$installed_version"
plugins: []
LOCK

  # Copier RENGA.md depuis le répertoire partagé
  if [[ ! -f "$ROOT_DIR/RENGA.md" ]] && [[ -f "$RENGA_SHARE_DIR/RENGA.md" ]]; then
    cp "$RENGA_SHARE_DIR/RENGA.md" "$ROOT_DIR/RENGA.md"
    ok "RENGA.md généré"
  fi

  ok "renga v$installed_version installé ($agent_count agents, $instr_count instructions, $skill_count skills)"
}

cmd_update() {
  local dry_run=false
  local version="latest"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) dry_run=true; shift ;;
      --version) version="$2"; shift 2 ;;
      *) fail "Option inconnue : $1"; return 1 ;;
    esac
  done

  if [[ ! -f "$LOCK_FILE" ]]; then
    warn "Pas de .renga.lock — lancez 'renga install' d'abord"
    return 1
  fi

  local current_version
  current_version="$(python3 -c "
import re
text = open('$LOCK_FILE', encoding='utf-8').read()
m = re.search(r'version:\s*\"?([^\"\\n]+)', text)
print(m.group(1) if m else 'unknown')
")"

  info "Version actuelle : $current_version"

  if [[ "$dry_run" == "true" ]]; then
    local tmp_dr
    tmp_dr="$(mktemp -d)"
    local remote_json="$tmp_dr/latest.json"
    curl -fsSL "$RENGA_API/releases/latest" -o "$remote_json" 2>/dev/null || {
      warn "Impossible de vérifier la version distante"
      rm -rf "$tmp_dr"
      return 0
    }
    local remote_version
    remote_version="$(python3 -c "
import json
d = json.load(open('$remote_json', encoding='utf-8'))
print(d.get('tag_name', '?').lstrip('v'))
")"
    rm -rf "$tmp_dr"
    if [[ "$remote_version" == "$current_version" ]]; then
      ok "Déjà à jour (v$current_version)"
    else
      info "Mise à jour disponible : v$current_version → v$remote_version — relancez sans --dry-run"
    fi
  else
    if [[ "$version" == "latest" ]]; then
      cmd_install
    else
      cmd_install --version "$version"
    fi
  fi
}

cmd_list() {
  info "Agents installés :"
  if [[ -d "$RENGA_DIR" ]]; then
    for f in "$RENGA_DIR"/*.agent.md; do
      [[ -f "$f" ]] || continue
      echo "  $(basename "$f" .agent.md)"
    done
  else
    warn "Aucun agent installé"
  fi

  # Skills
  if [[ -d "$SKILLS_DIR" ]]; then
    local skill_dirs
    skill_dirs="$(find "$SKILLS_DIR" -name 'SKILL.md' -not -path '*/_local/*' 2>/dev/null)"
    if [[ -n "$skill_dirs" ]]; then
      echo ""
      info "Skills installés :"
      while IFS= read -r skill_file; do
        local sname
        sname="$(basename "$(dirname "$skill_file")")"
        echo "  $sname"
      done <<< "$skill_dirs"  # <<< herestring: Bash 3.2+ compatible (unlike mapfile)
    fi
  fi

  # Plugins
  if [[ -d "$RENGA_DIR/_plugins" ]]; then
    local found_plugins=0
    for d in "$RENGA_DIR/_plugins"/*/; do
      [[ -d "$d" ]] && [[ -f "$d/agents.md" ]] || continue
      if [[ $found_plugins -eq 0 ]]; then
        echo ""
        info "Plugins installés :"
      fi
      found_plugins=1
      local plugin_name count
      plugin_name="$(basename "$d")"
      count="$(wc -l < "$d/agents.md" | tr -d ' ')"
      echo "  $plugin_name ($count agents)"
    done
  fi
}

# Sync plugins list in .renga.lock from .renga.yml
_sync_lock_plugins() {
  [[ -f "$LOCK_FILE" ]] || return 0
  python3 -c "
import re, pathlib
lock = pathlib.Path('$LOCK_FILE')
config = pathlib.Path('$CONFIG_FILE')
text = lock.read_text()
if not config.exists():
    new_plugins = 'plugins: []'
else:
    cfg = config.read_text()
    if re.search(r'plugins:\s*\[\]', cfg):
        new_plugins = 'plugins: []'
    else:
        m = re.search(r'plugins:\n((?:  - [^\n]+\n?)+)', cfg)
        if m:
            new_plugins = 'plugins:\n' + m.group(1).rstrip()
        else:
            new_plugins = 'plugins: []'
text = re.sub(r'plugins:(?:\s*\[\]|(?:\n  - [^\n]+)+)', new_plugins, text)
lock.write_text(text)
" 2>/dev/null
}

# Install plugin agents flat into RENGA_DIR and record metadata
# Usage: _install_plugin_flat <plugin_name> <plugin_src_dir>
_install_plugin_flat() {
  local plugin_name="$1"
  local src_dir="$2"

  if [[ ! -d "$src_dir" ]]; then
    fail "Plugin '$plugin_name' introuvable dans la release"
    return 1
  fi

  # Metadata dir — not loaded by Copilot, tracks which agents belong to this plugin
  local meta_dir="$RENGA_DIR/_plugins/$plugin_name"
  mkdir -p "$meta_dir"

  local count=0
  local agents_list=""
  for agent_file in "$src_dir"/*.agent.md; do
    [[ -f "$agent_file" ]] || continue
    local agent_name
    agent_name="$(basename "$agent_file" .agent.md)"
    cp "$agent_file" "$RENGA_DIR/"
    agents_list="${agents_list}${agent_name}
"
    count=$((count + 1))
  done

  # Save agent list for uninstall
  printf '%s' "$agents_list" > "$meta_dir/agents.md"

  # Copy README if present
  [[ -f "$src_dir/README.md" ]] && cp "$src_dir/README.md" "$meta_dir/"

  ok "Plugin '$plugin_name' installé ($count agents)"
}

# Add plugin name to plugins: section in .renga.yml
_add_plugin_to_config() {
  local plugin_name="$1"
  [[ -f "$CONFIG_FILE" ]] || return 0
  python3 -c "
import re, pathlib, sys
cfg = sys.argv[1]
name = sys.argv[2]
path = pathlib.Path(cfg)
text = path.read_text()
if '  - ' + name in text:
    sys.exit(0)
# plugins: [] -> plugins:\n  - name
text = re.sub(r'plugins:\s*\[\]', 'plugins:\n  - ' + name, text)
# plugins:\n  - other\n -> add new entry
if '  - ' + name not in text:
    text = re.sub(r'(plugins:\n(?:  - [^\n]+\n)+)', r'\1  - ' + name + '\n', text)
path.write_text(text)
" "$CONFIG_FILE" "$plugin_name" 2>/dev/null
}

# Remove plugin name from plugins: section in .renga.yml
_remove_plugin_from_config() {
  local plugin_name="$1"
  [[ -f "$CONFIG_FILE" ]] || return 0
  python3 -c "
import re, pathlib, sys
cfg = sys.argv[1]
name = sys.argv[2]
path = pathlib.Path(cfg)
text = path.read_text()
text = re.sub(r'\n  - ' + re.escape(name) + r'\b[^\n]*', '', text)
# If plugins: section is now empty, normalize to plugins: []
text = re.sub(r'plugins:\n(?=\S|\Z)', 'plugins: []\n', text)
path.write_text(text)
" "$CONFIG_FILE" "$plugin_name" 2>/dev/null
}

cmd_plugin() {
  if [[ $# -eq 0 ]]; then
    fail "Usage: renga plugin <add|remove|list> [name]"
    return 1
  fi

  local subcmd="$1"; shift

  case "$subcmd" in
    add)
      [[ $# -ge 1 ]] || { fail "Usage: renga plugin add <name>"; return 1; }
      local plugin_name="$1"
      info "Ajout du plugin '$plugin_name'..."

      # Check if already installed (metadata dir exists)
      if [[ -f "$RENGA_DIR/_plugins/$plugin_name/agents.md" ]]; then
        warn "Plugin '$plugin_name' déjà installé"
        return 0
      fi

      # Fetch from latest release (use temp file to avoid control char corruption)
      local tmp_dir
      tmp_dir="$(mktemp -d)"
      # Save any existing EXIT trap and chain our cleanup
      local _prev_trap
      _prev_trap="$(trap -p EXIT | sed "s/^trap -- '//;s/' EXIT$//" 2>/dev/null || true)"
      trap "rm -rf '$tmp_dir'; ${_prev_trap:-true}" EXIT

      local release_json_file="$tmp_dir/release.json"
      curl -fsSL "$RENGA_API/releases/latest" -o "$release_json_file" || {
        fail "Impossible de récupérer la dernière release"
        return 1
      }

      local tarball_url
      tarball_url="$(python3 -c "
import json
data = json.load(open('$release_json_file', encoding='utf-8'))
for a in data.get('assets', []):
    if a['name'].endswith('.tar.gz'):
        print(a['browser_download_url']); break
else:
    print(data.get('tarball_url', ''))
")" || {
        fail "Impossible de parser la release"
        return 1
      }

      curl -fsSL "$tarball_url" | tar xz -C "$tmp_dir" --strip-components=1

      _install_plugin_flat "$plugin_name" "$tmp_dir/plugins/$plugin_name"
      _add_plugin_to_config "$plugin_name"
      _sync_lock_plugins
      ;;

    remove)
      [[ $# -ge 1 ]] || { fail "Usage: renga plugin remove <name>"; return 1; }
      local plugin_name="$1"
      local meta_dir="$RENGA_DIR/_plugins/$plugin_name"
      if [[ ! -f "$meta_dir/agents.md" ]]; then
        warn "Plugin '$plugin_name' non installé"
        return 0
      fi
      # Remove flat-installed agents
      while IFS= read -r agent_name; do
        [[ -n "$agent_name" ]] || continue
        rm -f "$RENGA_DIR/${agent_name}.agent.md"
      done < "$meta_dir/agents.md"
      rm -rf "$meta_dir"
      _remove_plugin_from_config "$plugin_name"
      ok "Plugin '$plugin_name' supprimé"
      _sync_lock_plugins
      ;;

    list)
      local cached_manifest="$RENGA_SHARE_DIR/manifest.json"
      echo ""
      info "Plugins :"
      if [[ -f "$cached_manifest" ]]; then
        python3 -c "
import json, pathlib
cached = pathlib.Path('$cached_manifest')
meta_base = pathlib.Path('$RENGA_DIR/_plugins')
m = json.load(cached.open(encoding='utf-8'))
plugins = m.get('plugins', {})
if not plugins:
    print('  Aucun plugin disponible.')
for name, data in plugins.items():
    installed = (meta_base / name / 'agents.md').exists()
    marker = '[installed]' if installed else '[available]'
    count = len(data.get('agents', []))
    print(f'  {marker} {name} ({count} agents)')
" 2>/dev/null
      elif [[ -d "$RENGA_DIR/_plugins" ]]; then
        local found=0
        for d in "$RENGA_DIR/_plugins"/*/; do
          [[ -d "$d" ]] && [[ -f "$d/agents.md" ]] || continue
          found=1
          local pname pcount
          pname="$(basename "$d")"
          pcount="$(wc -l < "$d/agents.md" | tr -d ' ')"
          echo "  [installed] $pname ($pcount agents)"
        done
        [[ $found -eq 0 ]] && echo "  Aucun plugin installé."
        echo ""
        warn "Lancez 'renga install' pour voir tous les plugins disponibles."
      else
        echo "  Aucun plugin installé."
        echo ""
        warn "Lancez 'renga install' pour voir tous les plugins disponibles."
      fi
      ;;

    *)
      fail "Sous-commande inconnue : '$subcmd'"
      echo "Usage: renga plugin <add|remove|list> [name]"
      return 1
      ;;
  esac
}

cmd_local() {
  if [[ $# -eq 0 ]]; then
    cat <<EOF
Usage: renga local init <target>

Crée un espace de customisation locale pour renga.
Ces dossiers ne sont jamais écrasés par 'renga update'.

Targets:
  agents        Crée .github/agents/_local/ pour des agents personnalisés
  hooks         Crée .github/agents/_local/hooks/ pour des hooks personnalisés
                (propose l'activation du workflow CI si remote GitHub détecté)
  skills        Crée .github/skills/_local/ pour des skills personnalisés
  instructions  Crée .github/instructions/_local/ pour des instructions personnalisées
  schemas       Copie les schémas JSON dans schemas/ (validation IDE des fichiers .agent.md)
EOF
    return 0
  fi

  local subcmd="$1"; shift

  case "$subcmd" in
    init)
      [[ $# -ge 1 ]] || {
        fail "Usage: renga local init <agents|hooks|skills|instructions>"
        return 1
      }
      local target="$1"
      case "$target" in
        agents)
          mkdir -p "$RENGA_DIR/_local"
          ok "Créé : .github/agents/_local/"
          ;;
        hooks)
          mkdir -p "$RENGA_DIR/_local/hooks"
          ok "Créé : .github/agents/_local/hooks/"
          # Propose CI workflow if GitHub remote detected
          if git -C "$ROOT_DIR" remote -v 2>/dev/null | grep -q 'github\.com'; then
            if [[ -f "$ROOT_DIR/.github/workflows/agent-validate.yml" ]]; then
              ok "Workflow CI déjà présent (.github/workflows/agent-validate.yml)"
            elif [[ -t 0 && -t 1 ]]; then
              echo ""
              info "Un workflow GitHub Actions peut valider automatiquement vos agents à chaque push."
              printf 'Activer la validation automatique sur GitHub ? [Y/n] : '
              local _ci_ans=""
              read -r _ci_ans || true
              if [[ "${_ci_ans:-y}" =~ ^[Yy]?$ ]]; then
                _create_validate_workflow
                ok "Workflow CI créé dans .github/workflows/agent-validate.yml"
              fi
            fi
          fi
          ;;
        skills)
          mkdir -p "$SKILLS_DIR/_local"
          ok "Créé : .github/skills/_local/"
          ;;
        instructions)
          mkdir -p "$INSTRUCTIONS_DIR/_local"
          ok "Créé : .github/instructions/_local/"
          ;;
        schemas)
          local schema_src="$RENGA_SHARE_DIR/schemas"
          if [[ ! -d "$schema_src" ]]; then
            fail "Schémas non disponibles — lancez 'renga install' d'abord"
            return 1
          fi
          mkdir -p "$ROOT_DIR/schemas"
          local schema_count=0
          for f in "$schema_src/"*.json; do
            [[ -f "$f" ]] || continue
            cp "$f" "$ROOT_DIR/schemas/"
            schema_count=$((schema_count + 1))
          done
          ok "Schémas JSON copiés dans schemas/ ($schema_count fichiers)"
          ;;
        *)
          fail "Cible inconnue : '$target'"
          echo "Targets disponibles : agents, hooks, skills, instructions, schemas"
          return 1
          ;;
      esac
      ;;
    *)
      fail "Sous-commande inconnue : '$subcmd'"
      echo "Usage: renga local init <agents|hooks|skills|instructions>"
      return 1
      ;;
  esac
}

cmd_skill() {
  if [[ $# -eq 0 ]]; then
    fail "Usage: renga skill <list|validate>"
    return 1
  fi

  local subcmd="$1"; shift

  case "$subcmd" in
    list)
      info "Skills disponibles :"
      if [[ -d "$SKILLS_DIR" ]]; then
        local found=false
        for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
          [[ -f "$skill_md" ]] || continue
          found=true
          local sname
          sname="$(basename "$(dirname "$skill_md")")"
          # Extract description from frontmatter
          local sdesc
          sdesc="$(python3 -c "
import re
text = open('$skill_md', encoding='utf-8').read()
m = re.search(r'description:\s*[\"\x27]?(.+?)[\"\x27]?\s*$', text, re.M)
print(m.group(1) if m else '—')
" 2>/dev/null || echo '—')"
          echo "  $sname — $sdesc"
        done
        if [[ "$found" == "false" ]]; then
          warn "Aucun SKILL.md trouvé dans .github/skills/"
        fi
      else
        warn "Répertoire .github/skills/ introuvable"
      fi
      ;;

    validate)
      info "Validation des skills..."
      local errors=0
      if [[ -d "$SKILLS_DIR" ]]; then
        for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
          [[ -f "$skill_md" ]] || continue
          local sname
          sname="$(basename "$(dirname "$skill_md")")"
          # Check frontmatter has name and description
          local valid
          valid="$(python3 -c "
import re, sys
text = open('$skill_md', encoding='utf-8').read()
if not text.startswith('---'):
    print('ERR:no-frontmatter'); sys.exit()
m_name = re.search(r'^name:\s*(.+)', text, re.M)
m_desc = re.search(r'^description:\s*(.+)', text, re.M)
if not m_name:
    print('ERR:no-name'); sys.exit()
if not m_desc:
    print('ERR:no-description'); sys.exit()
fm_name = m_name.group(1).strip().strip('\"\x27')
if fm_name != '$sname':
    print(f'ERR:name-mismatch:{fm_name}'); sys.exit()
print('OK')
" 2>/dev/null || echo 'ERR:parse-error')"
          case "$valid" in
            OK) ok "$sname — valide" ;;
            ERR:no-frontmatter) fail "$sname — frontmatter YAML manquant"; errors=$((errors + 1)) ;;
            ERR:no-name) fail "$sname — champ 'name' manquant"; errors=$((errors + 1)) ;;
            ERR:no-description) fail "$sname — champ 'description' manquant"; errors=$((errors + 1)) ;;
            ERR:name-mismatch*) fail "$sname — name ne correspond pas au répertoire ($valid)"; errors=$((errors + 1)) ;;
            *) fail "$sname — erreur de parsing"; errors=$((errors + 1)) ;;
          esac
        done
      else
        warn "Répertoire .github/skills/ introuvable"
      fi
      if [[ "$errors" -gt 0 ]]; then
        fail "$errors skill(s) invalide(s)"
        return 1
      fi
      ok "Tous les skills sont valides"
      ;;

    *)
      fail "Sous-commande inconnue : '$subcmd'"
      echo "Usage: renga skill <list|validate>"
      return 1
      ;;
  esac
}

cmd_version() {
  echo "renga $RENGA_VERSION"
}

cmd_help() {
  cat <<EOF
${BOLD}renga CLI${RESET} — Framework de gouvernance IA

${BOLD}Usage:${RESET} renga <command> [options]

${BOLD}Commands:${RESET}
  install [--profile] [--version]  Installe renga (crée .renga.yml si absent, installe agents/hooks/skills)
  update [--dry-run]               Met à jour les agents et hooks
  list                             Liste les agents et plugins installés
  local init <target>              Crée un espace de customisation locale (agents|hooks|skills|instructions|schemas)
  models apply              Applique la section models: de .renga.yml sur tous les agents
  plugin <sub>              Gestion des plugins (add, remove, list)
  validate                  Valide les fichiers .agent.md
  doctor                    Vérifie la santé du setup
  skill <sub>               Gestion des skills (list, validate)
  dashboard                 Génère le dashboard de performance
  build                     Construit l'artefact de distribution
  version                   Affiche la version
  help                      Affiche cette aide

EOF
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

if [[ $# -eq 0 ]]; then
  cmd_help
  exit 1
fi

case "${1}" in
  install)   shift; cmd_install "$@" ;;
  update)    shift; cmd_update "$@" ;;
  list)      cmd_list ;;
  local)     shift; cmd_local "$@" ;;
  models)    shift; cmd_models "$@" ;;
  plugin)    shift; cmd_plugin "$@" ;;
  skill)     shift; cmd_skill "$@" ;;
  validate)  cmd_validate ;;
  doctor)    cmd_doctor ;;
  dashboard) cmd_dashboard ;;
  build)     shift; cmd_build "$@" ;;
  version|--version|-v) cmd_version ;;
  help|--help|-h) cmd_help ;;
  *)
    fail "Commande inconnue : '${1}'"
    echo ""
    cmd_help
    exit 1
    ;;
esac
