#!/usr/bin/env python3
"""Bonus : genere doc/adr/INDEX.md (sommaire des ADR) a partir de doc/adr/NNNN-*.md.

Usage : python3 scripts/gen_adr_index.py
Le README.md du dossier (regles de contribution) n'est pas ecrase.
"""
import re
from pathlib import Path

adr_dir = Path(__file__).resolve().parent.parent / "doc" / "adr"
rows = []
for f in sorted(adr_dir.glob("[0-9]*.md")):
    text = f.read_text(encoding="utf-8")
    title = re.search(r"^#\s*(.+)$", text, re.M).group(1).strip()
    status = re.search(r"^##\s*Statut\s*\n+(.+)", text, re.M).group(1).strip()
    rows.append((f.name, title, status))

out = ["# Sommaire des ADR", "",
       "_Fichier généré par `scripts/gen_adr_index.py` : ne pas modifier à la main._", "",
       "| Fichier | Titre | Statut |", "|---|---|---|"]
out += [f"| [{name}]({name}) | {title} | {status} |" for name, title, status in rows]
(adr_dir / "INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{len(rows)} ADR indexés dans doc/adr/INDEX.md")
