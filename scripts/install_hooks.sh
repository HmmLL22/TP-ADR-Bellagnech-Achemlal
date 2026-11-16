#!/usr/bin/env bash
# Active les hooks versionnes du depot (dossier hooks/).
git config core.hooksPath hooks
echo "Hooks actives : core.hooksPath = hooks"
