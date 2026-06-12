#!/usr/bin/env bash
# Run this ON YOUR OWN MAC (Thibault / Ali) to set up an SSH key for GitHub.
#   Usage:  bash setup_ssh.sh your-github-email@example.com
# It generates a key if you don't have one, wires it into the macOS keychain,
# and prints the public key for you to paste into GitHub. It NEVER touches your
# private key beyond your own machine.
set -e

EMAIL="${1:-}"
if [ -z "$EMAIL" ]; then
  echo "Usage: bash setup_ssh.sh your-github-email@example.com"
  exit 1
fi

KEY="$HOME/.ssh/id_ed25519"
mkdir -p "$HOME/.ssh" && chmod 700 "$HOME/.ssh"

if [ -f "$KEY" ]; then
  echo "✓ You already have a key at $KEY — reusing it."
else
  echo "→ Generating a new ed25519 SSH key (no passphrase)..."
  ssh-keygen -t ed25519 -C "$EMAIL" -f "$KEY" -N ""
fi

# Make ssh use the macOS keychain so you never re-enter anything
CONFIG="$HOME/.ssh/config"
touch "$CONFIG"
if ! grep -q "id_ed25519" "$CONFIG" 2>/dev/null; then
  cat >> "$CONFIG" <<'EOF'

Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
EOF
fi
eval "$(ssh-agent -s)" >/dev/null
ssh-add --apple-use-keychain "$KEY" 2>/dev/null || ssh-add "$KEY"

echo
echo "================  COPY THE LINE BELOW  ================"
cat "$KEY.pub"
echo "======================================================"
echo
echo "Next steps:"
echo "  1. Copy the whole line above (starts with 'ssh-ed25519')."
echo "  2. Open  https://github.com/settings/ssh/new"
echo "  3. Title it (e.g. 'Thibault MacBook'), paste the key, click 'Add SSH key'."
echo "  4. Test:   ssh -T git@github.com      (should say: Hi <username>!)"
echo "  5. Clone:  git clone git@github.com:leomcf/SCAI-presentation.git"
