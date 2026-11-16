# Décisions d'architecture (ADR)

Ce dossier est l'historique des décisions d'architecture du système de gestion de
bibliothèque. Le sommaire à jour est dans [INDEX.md](INDEX.md).

## Écrire un nouvel ADR

1. Copier [adr-template.md](adr-template.md) vers `NNNN-titre-court.md`
   (`NNNN` = numéro suivant, sur 4 chiffres).
2. Renseigner les cinq sections : `Statut`, `Contexte`, `Decision`,
   `Alternatives envisagees`, `Consequences`. Un ADR = **une** décision.
3. Statut initial : `En discussion`. Valeurs autorisées : `Accepte`, `Rejete`,
   `Obsolete`, `En discussion`.
4. Lier les ADR entre eux avec des liens Markdown relatifs
   (`[ADR 2](0002-style-d-architecture-microservices.md)`) quand une décision en influence
   une autre.
5. Si la décision apparaît dans une vue ArchiMate, reprendre **exactement** la phrase
   « Décision retenue : … » comme nom de l'élément (traçabilité).

## Règles

- **Numérotation** : incrémentale, jamais réutilisée, même pour un ADR obsolète.
- **Un ADR accepté ne se modifie pas.** Pour changer d'avis, on écrit un nouvel ADR qui
  remplace l'ancien : l'ancien passe à `Obsolete` et pointe vers son remplaçant.
- **Processus** : toute proposition passe par une Pull Request. Le passage
  `En discussion` → `Accepte` demande la revue d'au moins un pair (et du ou de la
  responsable sécurité si la décision touche la sécurité).
- **Un commit par ADR** (commits atomiques), message du type `ADR 0003: ...`.

## Validation automatique

```bash
./scripts/install_hooks.sh   # active le hook pre-commit
./scripts/check_adr.sh       # validation manuelle
```

Le hook refuse le commit si un ADR modifié n'a pas le titre `# N. Titre`, une des cinq
sections ou un statut valide. La même vérification tourne en CI
(`.github/workflows/adr-lint.yml`).
