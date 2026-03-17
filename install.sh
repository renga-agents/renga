#!/usr/bin/env bash
# =============================================================================
# renga installer — Installe la CLI renga
# =============================================================================
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh
#
#   # ou avec une version spécifique :
#   curl -fsSL https://raw.githubusercontent.com/renga-agents/renga/main/install.sh | sh -s -- --version 1.2.0
#

set -euo pipefail

REPO="${RENGA_REPO:-renga-agents/renga}"
API_URL="https://api.github.com/repos/$REPO"
INSTALL_DIR="${RENGA_INSTALL_DIR:-$HOME/.local/bin}"
VERSION=""

# Couleurs
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; BOLD='\033[1m'; RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BOLD=''; RESET=''
fi
ok()   { printf "${GREEN}✓${RESET} %s\n" "$1"; }
fail() { printf "${RED}✗${RESET} %s\n" "$1"; }
info() { printf "${BOLD}→${RESET} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${RESET} %s\n" "$1"; }

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --install-dir) INSTALL_DIR="$2"; shift 2 ;;
    *) fail "Option inconnue : $1"; exit 1 ;;
  esac
done

# Detect OS
OS="$(uname -s)"
case "$OS" in
  Linux|Darwin) ;;
  *) fail "OS non supporté : $OS (macOS/Linux uniquement)"; exit 1 ;;
esac

# Check curl
if ! command -v curl &>/dev/null; then
  fail "curl est requis mais non trouvé"
  exit 1
fi

info "Installation de la CLI renga…"

# Fetch release
if [[ -z "$VERSION" ]]; then
  RELEASE_URL="$API_URL/releases/latest"
else
  RELEASE_URL="$API_URL/releases/tags/v$VERSION"
fi

RELEASE_JSON="$(curl -fsSL "$RELEASE_URL")" || {
  fail "Impossible de récupérer la release"
  exit 1
}

# Extract tarball URL
TARBALL_URL="$(echo "$RELEASE_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for a in data.get('assets', []):
    if a['name'].endswith('.tar.gz'):
        print(a['browser_download_url']); break
else:
    print(data.get('tarball_url', ''))
" 2>/dev/null)" || {
  fail "Impossible de parser la release (Python 3 requis)"
  exit 1
}

if [[ -z "$TARBALL_URL" ]]; then
  fail "Aucun artefact trouvé dans la release"
  exit 1
fi

# Download and extract CLI
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

info "Téléchargement…"
curl -fsSL "$TARBALL_URL" | tar xz -C "$TMP_DIR" --strip-components=1

# Find the CLI script
CLI_SRC="$TMP_DIR/renga"
if [[ ! -f "$CLI_SRC" ]]; then
  fail "Script renga introuvable dans l'artefact"
  exit 1
fi

# Install
mkdir -p "$INSTALL_DIR"
cp "$CLI_SRC" "$INSTALL_DIR/renga"
chmod +x "$INSTALL_DIR/renga"

INSTALLED_VERSION="$(echo "$RELEASE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tag_name','unknown'))")"
ok "renga $INSTALLED_VERSION installé dans $INSTALL_DIR/renga"

# ---------------------------------------------------------------------------
# Install hooks from distribution
# ---------------------------------------------------------------------------
HOOKS_SRC="$TMP_DIR/hooks"
if [[ -d "$HOOKS_SRC" ]]; then
  info "Installation des hooks…"

  # Determine target project dir (current working directory)
  PROJECT_DIR="${RENGA_PROJECT_DIR:-$(pwd)}"
  HOOKS_DEST="$PROJECT_DIR/.github/hooks"
  HOOKS_SCRIPTS_DEST="$HOOKS_DEST/scripts"

  # Create target directories
  mkdir -p "$HOOKS_DEST"
  mkdir -p "$HOOKS_SCRIPTS_DEST"

  # Copy managed hook config files (*.hooks.json)
  for f in "$HOOKS_SRC"/*.hooks.json; do
    [[ -f "$f" ]] || continue
    cp "$f" "$HOOKS_DEST/"
  done

  # Copy managed hook scripts, preserving _local/
  if [[ -d "$HOOKS_SRC/scripts" ]]; then
    for f in "$HOOKS_SRC/scripts/"*.sh; do
      [[ -f "$f" ]] || continue
      cp "$f" "$HOOKS_SCRIPTS_DEST/"
    done
  fi

  # chmod +x on all .sh scripts
  find "$HOOKS_SCRIPTS_DEST" -name '*.sh' -exec chmod +x {} +

  # Preserve _local/hooks/ — never overwrite user-owned hooks
  LOCAL_HOOKS_DIR="$PROJECT_DIR/.github/agents/_local/hooks"
  if [[ -d "$LOCAL_HOOKS_DIR" ]]; then
    ok "_local/hooks/ préservé (user-owned)"
  else
    mkdir -p "$LOCAL_HOOKS_DIR"
    ok "_local/hooks/ créé"
  fi

  ok "Hooks installés dans $HOOKS_DEST"

  # Add .copilot/reports/ to .gitignore if not already present
  GITIGNORE="$PROJECT_DIR/.gitignore"
  if [[ -f "$GITIGNORE" ]]; then
    if ! grep -qF '.copilot/reports/' "$GITIGNORE"; then
      printf '\n# renga reports\n.copilot/reports/\n' >> "$GITIGNORE"
      ok ".copilot/reports/ ajouté au .gitignore"
    fi
  else
    printf '# renga reports\n.copilot/reports/\n' > "$GITIGNORE"
    ok ".gitignore créé avec .copilot/reports/"
  fi
fi

# Check PATH
if ! echo "$PATH" | tr ':' '\n' | grep -q "^$INSTALL_DIR$"; then
  echo ""
  warn "$INSTALL_DIR n'est pas dans votre PATH"
  echo "  Ajoutez cette ligne à votre ~/.zshrc ou ~/.bashrc :"
  echo "    export PATH=\"$INSTALL_DIR:\$PATH\""
  echo ""
fi

ok "Installation terminée ! Lancez 'renga help' pour démarrer."

