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

# Fetch release (to a temp file to avoid control character issues in variables)
if [[ -z "$VERSION" ]]; then
  RELEASE_URL="$API_URL/releases/latest"
else
  RELEASE_URL="$API_URL/releases/tags/v$VERSION"
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
RELEASE_JSON_FILE="$TMP_DIR/release.json"

curl -fsSL "$RELEASE_URL" -o "$RELEASE_JSON_FILE" || {
  fail "Impossible de récupérer la release"
  exit 1
}

# Extract tarball URL and tag name
TARBALL_URL="$(python3 -c "
import json
data = json.load(open('$RELEASE_JSON_FILE'))
for a in data.get('assets', []):
    if a['name'].endswith('.tar.gz'):
        print(a['browser_download_url']); break
else:
    print(data.get('tarball_url', ''))
")" || {
  fail "Impossible de parser la release (Python 3 requis)"
  exit 1
}

CHECKSUM_URL="$(python3 -c "
import json
data = json.load(open('$RELEASE_JSON_FILE'))
for a in data.get('assets', []):
    if a['name'].endswith('.sha256'):
        print(a['browser_download_url']); break
")"

INSTALLED_VERSION="$(python3 -c "import json; print(json.load(open('$RELEASE_JSON_FILE')).get('tag_name','unknown'))")"

if [[ -z "$TARBALL_URL" ]]; then
  fail "Aucun artefact trouvé dans la release"
  exit 1
fi

# Download and verify CLI
info "Téléchargement…"
TARBALL_FILE="$TMP_DIR/renga.tar.gz"
curl -fsSL "$TARBALL_URL" -o "$TARBALL_FILE" || { fail "Téléchargement échoué"; exit 1; }

if [[ -n "$CHECKSUM_URL" ]]; then
  EXPECTED_HASH="$(curl -fsSL "$CHECKSUM_URL")"
  if command -v sha256sum &>/dev/null; then
    ACTUAL_HASH="$(sha256sum "$TARBALL_FILE" | awk '{print $1}')"
  else
    ACTUAL_HASH="$(shasum -a 256 "$TARBALL_FILE" | awk '{print $1}')"
  fi
  info "SHA256 : $ACTUAL_HASH"
  if [[ "$ACTUAL_HASH" != "$EXPECTED_HASH" ]]; then
    fail "Vérification d'intégrité échouée !"
    fail "  Attendu : $EXPECTED_HASH"
    fail "  Obtenu  : $ACTUAL_HASH"
    exit 1
  fi
  ok "Intégrité vérifiée (SHA256)"
else
  warn "Pas de checksum disponible pour cette release — vérification ignorée"
fi

tar xz -C "$TMP_DIR" --strip-components=1 -f "$TARBALL_FILE"

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
ok "renga $INSTALLED_VERSION installé dans $INSTALL_DIR/renga"

# Install Python helper scripts to the system share dir
SHARE_SCRIPTS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/renga/scripts"
mkdir -p "$SHARE_SCRIPTS_DIR"
if [[ -d "$TMP_DIR/scripts" ]]; then
  for py_script in "$TMP_DIR/scripts"/*.py; do
    [[ -f "$py_script" ]] || continue
    cp "$py_script" "$SHARE_SCRIPTS_DIR/"
  done
  ok "Scripts Python installés dans $SHARE_SCRIPTS_DIR"
fi

# Copy RENGA.md to share dir for use by 'renga install'
if [[ -f "$TMP_DIR/RENGA.md" ]]; then
  cp "$TMP_DIR/RENGA.md" "${XDG_DATA_HOME:-$HOME/.local/share}/renga/RENGA.md"
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

