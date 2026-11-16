#!/usr/bin/env python3
"""Genere les deux vues ArchiMate du TD2 :
  - doc/archimate/bibliotheque.archimate  (modele ouvrable dans Archi >= 4.9)
  - doc/archimate/vue1-motivation-composant.png
  - doc/archimate/vue2-chaine-du-risque.png

Les noms des elements reprennent MOT POUR MOT les phrases "Decision retenue"
des ADR 2 et 5 (tracabilite ADR <-> modele). Un controle automatique en fin
de script verifie cette correspondance.

Usage : python3 scripts/make_views.py
"""
import re
import textwrap
import uuid
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
ADR_DIR = ROOT / "doc" / "adr"
OUT = ROOT / "doc" / "archimate"


def new_id(prefix="id"):
    return f"{prefix}-{uuid.uuid4().hex}"


def decision_of(adr_glob):
    """Phrase 'Decision retenue : ...' d'un ADR (sans le gras Markdown)."""
    f = next(ADR_DIR.glob(adr_glob))
    m = re.search(r"^\*\*Décision retenue : (.+?)\.\*\*\s*$", f.read_text(encoding="utf-8"), re.M)
    if not m:
        raise SystemExit(f"Phrase 'Décision retenue' introuvable dans {f.name}")
    return m.group(1)


# --------------------------------------------------------------------------
# Vocabulaire (identique aux ADR)
# --------------------------------------------------------------------------
REQ_ADR2 = decision_of("0002-*.md")          # Requirement de la vue 1
CM_ADR5 = decision_of("0005-*.md")           # Control Measure de la vue 2
OBJ_RGPD = "Conformité RGPD art. 32"         # consequence positive de l'ADR 5

# Couleurs ArchiMate usuelles
COL = {
    "Driver": "#CCCCFF", "Goal": "#CCCCFF", "Requirement": "#CCCCFF",
    "Assessment": "#CCCCFF", "BusinessEvent": "#FFFFB5",
    "ApplicationComponent": "#B5FFFF", "ApplicationService": "#B5FFFF",
}

# --------------------------------------------------------------------------
# Description des deux vues : elements, positions (x, y, w, h), relations
# --------------------------------------------------------------------------
# element : cle -> (type ArchiMate, nom, specialisation ou None)
ELEMENTS = {
    # vue 1
    "driver":  ("Driver", "Pics de charge à la rentrée universitaire", None),
    "goal":    ("Goal", "Faire monter en charge indépendamment les fonctions critiques", None),
    "req":     ("Requirement", REQ_ADR2, None),
    "c_emp":   ("ApplicationComponent", "Service d'emprunt", None),
    "c_res":   ("ApplicationComponent", "Service de réservation", None),
    "c_not":   ("ApplicationComponent", "Service de notification", None),
    "c_cat":   ("ApplicationComponent", "Service de catalogue", None),
    # vue 2
    "vuln":    ("Assessment", "API de prêt sans authentification forte", "Vulnerability"),
    "threat":  ("BusinessEvent", "Usurpation de compte lecteur", "Threat Event"),
    "risk":    ("Assessment", "Emprunts frauduleux et fuite de données des usagers", "Risk"),
    "cm":      ("Requirement", CM_ADR5, "Control Measure"),
    "co":      ("Goal", OBJ_RGPD, "Control Objective"),
    "svc":     ("ApplicationService", "Service d'authentification OAuth2", None),
}

# relation : (type, source, cible, nom, strength)
RELATIONS = [
    # vue 1
    ("Influence", "driver", "goal", "influence", None),
    ("Realization", "req", "goal", "réalise", None),
    ("Realization", "c_emp", "req", "réalise", None),
    ("Realization", "c_res", "req", "réalise", None),
    ("Realization", "c_not", "req", "réalise", None),
    ("Realization", "c_cat", "req", "réalise", None),
    # vue 2
    ("Association", "vuln", "threat", "exploite", None),
    ("Influence", "threat", "risk", "cause", None),
    ("Realization", "cm", "co", "réalise", None),
    ("Influence", "co", "risk", "atténue", "-"),
    ("Realization", "svc", "cm", "réalise", None),
]

W, H = 250, 85
VIEWS = {
    "Vue 1 - Motivation vers composant (ADR 2)": {
        "file": "vue1-motivation-composant.png",
        "size": (1250, 520),
        "nodes": {
            "driver": (30, 205, 220, 105), "goal": (330, 205, 240, 105),
            "req": (650, 195, 270, 125),
            "c_emp": (1000, 40, 210, 70), "c_res": (1000, 160, 210, 70),
            "c_not": (1000, 280, 210, 70), "c_cat": (1000, 400, 210, 70),
        },
    },
    "Vue 2 - Chaine du risque (ADR 5)": {
        "file": "vue2-chaine-du-risque.png",
        "size": (1250, 580),
        "nodes": {
            "vuln": (30, 60, 260, H), "threat": (480, 60, 260, H), "risk": (930, 60, 280, 100),
            "co": (930, 260, 280, H), "cm": (480, 260, 260, 110),
            "svc": (480, 450, 260, 85),
        },
    },
}
VIEW_NODES = {name: set(v["nodes"]) for name, v in VIEWS.items()}


def view_relations(vname):
    keys = VIEW_NODES[vname]
    return [(i, r) for i, r in enumerate(RELATIONS) if r[1] in keys and r[2] in keys]


# --------------------------------------------------------------------------
# Rendu image
# --------------------------------------------------------------------------
def anchor(box, other):
    """Point du bord de `box` le plus proche de `other` (centre a centre)."""
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    ox, oy = other[0] + other[2] / 2, other[1] + other[3] / 2
    dx, dy = ox - cx, oy - cy
    if dx == 0 and dy == 0:
        return cx, cy
    sx = (w / 2) / abs(dx) if dx else float("inf")
    sy = (h / 2) / abs(dy) if dy else float("inf")
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def render(vname, spec):
    wpx, hpx = spec["size"]
    fig, ax = plt.subplots(figsize=(wpx / 100, hpx / 100), dpi=130)
    ax.set_xlim(0, wpx)
    ax.set_ylim(hpx, 0)
    ax.axis("off")
    ax.text(wpx / 2, 22, vname, ha="center", va="center", fontsize=13, fontweight="bold")

    for key, (x, y, w, h) in spec["nodes"].items():
        etype, name, spe = ELEMENTS[key]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=6",
                                    fc=COL[etype], ec="#555555", lw=1.2))
        label = textwrap.fill(name, 25)
        if spe:
            ax.text(x + w / 2, y + 14, f"«{spe}»", ha="center", va="center",
                    fontsize=8.5, style="italic", color="#333333")
            ax.text(x + w / 2, y + h / 2 + 8, label, ha="center", va="center", fontsize=9.5)
        else:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9.5)
        ax.text(x + w - 5, y + h - 6, etype, ha="right", va="bottom", fontsize=6.5, color="#777777")

    for _, (rtype, s, t, name, strength) in view_relations(vname):
        bs, bt = spec["nodes"][s], spec["nodes"][t]
        p1, p2 = anchor(bs, bt), anchor(bt, bs)
        style, ls = "-|>", "-"
        if rtype == "Realization":
            style, ls = "-|>", "--"
        if rtype == "Influence":
            style, ls = "->", "--"
        if rtype == "Association":
            style, ls = "->", "-"
        arrow = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=16, lw=1.3,
                                color="#222222", linestyle=ls, shrinkA=0, shrinkB=0)
        if rtype == "Realization":
            arrow.set_facecolor("white")
        ax.add_patch(arrow)
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        txt = f"{name} ({strength})" if strength else name
        ax.text(mx, my - 8, txt, ha="center", va="bottom", fontsize=8, color="#222222",
                bbox=dict(fc="white", ec="none", pad=1.2, alpha=0.9))

    fig.savefig(OUT / spec["file"], bbox_inches="tight", facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------
# Modele Archi (.archimate)
# --------------------------------------------------------------------------
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def build_archimate():
    el_id = {k: new_id() for k in ELEMENTS}
    profiles = {}  # nom -> (id, conceptType)
    for etype, _, spe in ELEMENTS.values():
        if spe and spe not in profiles:
            profiles[spe] = (new_id(), etype)
    rel_id = [new_id() for _ in RELATIONS]

    def element_xml(k):
        etype, name, spe = ELEMENTS[k]
        prof = f' profiles="{profiles[spe][0]}"' if spe else ""
        return f'    <element xsi:type="archimate:{etype}" name="{esc(name)}" id="{el_id[k]}"{prof}/>'

    folders = {
        "Business": [k for k, v in ELEMENTS.items() if v[0] == "BusinessEvent"],
        "Application": [k for k, v in ELEMENTS.items() if v[0].startswith("Application")],
        "Motivation": [k for k, v in ELEMENTS.items()
                       if v[0] in ("Driver", "Goal", "Requirement", "Assessment")],
    }

    def rel_xml(i, r):
        rtype, s, t, name, strength = r
        extra = ""
        if rtype == "Association":
            extra = ' directed="true"'
        if rtype == "Influence" and strength:
            extra = f' strength="{strength}"'
        return (f'    <element xsi:type="archimate:{rtype}Relationship" name="{esc(name)}" '
                f'id="{rel_id[i]}" source="{el_id[s]}" target="{el_id[t]}"{extra}/>')

    views_xml = []
    for vname, spec in VIEWS.items():
        node_id = {k: new_id() for k in spec["nodes"]}
        conns = view_relations(vname)
        conn_id = {i: new_id() for i, _ in conns}
        children = []
        for k, (x, y, w, h) in spec["nodes"].items():
            incoming = [conn_id[i] for i, r in conns if r[2] == k]
            tc = f' targetConnections="{" ".join(incoming)}"' if incoming else ""
            lines = [f'      <child xsi:type="archimate:DiagramObject" id="{node_id[k]}"{tc} '
                     f'archimateElement="{el_id[k]}">',
                     f'        <bounds x="{x}" y="{y}" width="{w}" height="{h}"/>']
            for i, r in conns:
                if r[1] == k:
                    lines.append(f'        <sourceConnection xsi:type="archimate:Connection" '
                                 f'id="{conn_id[i]}" source="{node_id[k]}" target="{node_id[r[2]]}" '
                                 f'archimateRelationship="{rel_id[i]}"/>')
            lines.append("      </child>")
            children.append("\n".join(lines))
        views_xml.append(f'    <element xsi:type="archimate:ArchimateDiagramModel" '
                         f'name="{esc(vname)}" id="{new_id()}">\n' + "\n".join(children) +
                         "\n    </element>")

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:archimate="http://www.archimatetool.com/archimate" '
        f'name="Système de gestion de bibliothèque" id="{new_id()}" version="5.0.0">',
        '  <folder name="Strategy" id="%s" type="strategy"/>' % new_id(),
        '  <folder name="Business" id="%s" type="business">' % new_id(),
        *[element_xml(k) for k in folders["Business"]],
        "  </folder>",
        '  <folder name="Application" id="%s" type="application">' % new_id(),
        *[element_xml(k) for k in folders["Application"]],
        "  </folder>",
        '  <folder name="Technology &amp; Physical" id="%s" type="technology"/>' % new_id(),
        '  <folder name="Motivation" id="%s" type="motivation">' % new_id(),
        *[element_xml(k) for k in folders["Motivation"]],
        "  </folder>",
        '  <folder name="Implementation &amp; Migration" id="%s" type="implementation_migration"/>' % new_id(),
        '  <folder name="Other" id="%s" type="other"/>' % new_id(),
        '  <folder name="Relations" id="%s" type="relations">' % new_id(),
        *[rel_xml(i, r) for i, r in enumerate(RELATIONS)],
        "  </folder>",
        '  <folder name="Views" id="%s" type="diagrams">' % new_id(),
        *views_xml,
        "  </folder>",
        *[f'  <profile name="{esc(n)}" id="{i}" conceptType="{c}"/>' for n, (i, c) in profiles.items()],
        "</archimate:model>",
        "",
    ]
    (OUT / "bibliotheque.archimate").write_text("\n".join(parts), encoding="utf-8")


def check_traceability():
    """Les noms du modele doivent figurer tels quels dans les ADR."""
    def norm(t):  # insensible aux retours a la ligne et au gras Markdown
        return re.sub(r"\s+", " ", t.replace("**", ""))

    adr2 = norm(next(ADR_DIR.glob("0002-*.md")).read_text(encoding="utf-8"))
    adr5 = norm(next(ADR_DIR.glob("0005-*.md")).read_text(encoding="utf-8"))
    checks = [
        (ELEMENTS["req"][1], adr2, "Requirement <-> ADR 2"),
        (ELEMENTS["cm"][1], adr5, "Control Measure <-> ADR 5"),
        (ELEMENTS["co"][1], adr5, "Control Objective <-> ADR 5"),
        (ELEMENTS["svc"][1], adr5, "Service d'authentification <-> ADR 5"),
    ]
    for key in ("c_emp", "c_res", "c_not", "c_cat"):
        checks.append((ELEMENTS[key][1], adr2, f"{ELEMENTS[key][1]} <-> ADR 2"))
    ok = True
    for name, text, label in checks:
        found = name in text
        print(f"  [{'OK' if found else 'KO'}] {label} : {name}")
        ok &= found
    if not ok:
        raise SystemExit("Incoherence entre les vues et les ADR")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for vname, spec in VIEWS.items():
        render(vname, spec)
    build_archimate()
    print("Traçabilité vues <-> ADR :")
    check_traceability()
    print("Fichiers générés dans", OUT)
