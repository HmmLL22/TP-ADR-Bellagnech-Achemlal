#!/usr/bin/env bash
# Valide que chaque ADR respecte le template du TD2.
# Usage : scripts/check_adr.sh [fichier.md ...]   (sans argument : tous les ADR de doc/adr)
# Code de sortie : 0 si tout est conforme, 1 sinon.
set -u

required_sections=("## Statut" "## Contexte" "## Decision" "## Alternatives envisagees" "## Consequences")
allowed_status='^(Accepte|Rejete|Obsolete|En discussion)$'
status=0

if [ "$#" -gt 0 ]; then
  files=("$@")
else
  files=(doc/adr/[0-9]*.md)
fi

for f in "${files[@]}"; do
  [ -f "$f" ] || continue

  # Titre : "# <numero>. <titre>"
  if ! grep -Eq '^# [0-9]+\. .+' "$f"; then
    echo "ERREUR: $f : titre manquant ou mal forme (attendu : '# <numero>. <titre>')"
    status=1
  fi

  # Les cinq sections obligatoires
  for section in "${required_sections[@]}"; do
    if ! grep -Eq "^${section}[[:space:]]*$" "$f"; then
      echo "ERREUR: $f : section '${section}' manquante"
      status=1
    fi
  done

  # Valeur du statut : premiere ligne non vide apres "## Statut"
  value=$(awk '/^## Statut/{s=1; next} s && NF {print; exit}' "$f" | sed 's/[[:space:]]*$//')
  if ! printf '%s\n' "$value" | grep -Eq "$allowed_status"; then
    echo "ERREUR: $f : statut '${value}' invalide (Accepte / Rejete / Obsolete / En discussion)"
    status=1
  fi
done

[ "$status" -eq 0 ] && echo "OK : ${#files[@]} fichier(s) ADR conforme(s) au template."
exit $status
