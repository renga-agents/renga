#!/usr/bin/env bash
# =============================================================================
# install-local.sh — Installe renga depuis les sources locales
# =============================================================================
#
# Usage (depuis la racine du repo) :
#   bash scripts/install-local.sh
#   bash scripts/install-local.sh --install-dir /usr/local/bin
#
# Équivalent de install.sh mais sans passer par GitHub :
#   1. Récupère le dernier tag git comme version
#   2. Build dist/ via build_dist.py
#   3. Installe depuis dist/ localement
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="${RENGA_INSTALL_DIR:-$HOME/.local/bin}"
SHARE_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/renga"

# Couleurs
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; BOLD='\033[1m'; RESET='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BOLD=''; RESET=''
fi
ok()   { printf "${GREEN}✓${RESET} %s\n" "$1"; }
fail() { printf "${RED}✗${RESET} %s\n" "$1" >&2; }
info() { printf "${BOLD}→${RESET} %s\n" "$1"; }
warn() { printf "${YELLOW}⚠${RESET} %s\n" "$1"; }

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir) INSTALL_DIR="$2"; shift 2 ;;
    *) fail "Option inconnue : $1"; exit 1 ;;
  esac
done

# Vérifications
if ! command -v python3 &>/dev/null; then
  fail "python3 est requis mais non trouvé"; exit 1
fi
if [[ ! -f "$REPO_ROOT/scripts/build_dist.py" ]]; then
  fail "Lancer ce script depuis la racine du repo renga"; exit 1
fi

# Version = dernier tag git
VERSION="$(git -C "$REPO_ROOT" describe --tags --abbrev=0 2>/dev/null || echo "0.0.0-dev")"
VERSION="${VERSION#v}"   # retirer le préfixe "v"

info "Build renga v${VERSION} depuis les sources locales…"

# Build
OUTPUT_DIR="$REPO_ROOT/dist"
python3 "$REPO_ROOT/scripts/build_dist.py" \
  --version "$VERSION" \
  --output-dir "$OUTPUT_DIR" \
  --quiet 2>/dev/null || python3 "$REPO_ROOT/scripts/build_dist.py" \
  --version "$VERSION" \
  --output-dir "$OUTPUT_DIR"
ok "dist/ construit (v${VERSION})"

# Vérifier l'artefact
CLI_SRC="$OUTPUT_DIR/renga"
if [[ ! -f "$CLI_SRC" ]]; then
  fail "Script renga introuvable dans dist/ — build échoué ?"; exit 1
fi

# Installer le CLI
mkdir -p "$INSTALL_DIR"
cp "$CLI_SRC" "$INSTALL_DIR/renga"
chmod +x "$INSTALL_DIR/renga"
ok "renga v${VERSION} installé dans $INSTALL_DIR/renga"

# Installer les scripts Python dans le share dir
SHARE_SCRIPTS_DIR="$SHARE_DIR/scripts"
mkdir -p "$SHARE_SCRIPTS_DIR"
if [[ -d "$OUTPUT_DIR/scripts" ]]; then
  for py in "$OUTPUT_DIR/scripts"/*.py; do
    [[ -f "$py" ]] || continue
    cp "$py" "$SHARE_SCRIPTS_DIR/"
  done
  ok "Scripts Python installés dans $SHARE_SCRIPTS_DIR"
fi

# Installer RENGA.md dans le share dir
if [[ -f "$OUTPUT_DIR/RENGA.md" ]]; then
  cp "$OUTPUT_DIR/RENGA.md" "$SHARE_DIR/RENGA.md"
fi

# Vérifier PATH
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$INSTALL_DIR"; then
  echo ""
  warn "$INSTALL_DIR n'est pas dans votre PATH"
  echo "  Ajoutez cette ligne à votre ~/.zshrc ou ~/.bashrc :"
  echo "    export PATH=\"$INSTALL_DIR:\$PATH\""
  echo ""
fi

ok "Installation locale terminée ! Lancez 'renga help' pour démarrer."
