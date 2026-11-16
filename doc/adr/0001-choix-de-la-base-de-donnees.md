# 1. Choix de la base de données

## Statut
Accepte

## Contexte
Le système de gestion de bibliothèque enregistre des emprunts, des retours et des
réservations. Ces opérations modifient plusieurs tables à la fois (exemplaire, usager,
prêt) et ne doivent jamais laisser un état incohérent : un même exemplaire ne peut pas
être prêté deux fois. La charge est très variable (pic à la rentrée universitaire) et la
base est le composant dont dépend tout le reste : elle doit rester disponible si un
serveur tombe. Les données des usagers (identité, historique d'emprunt) sont des données
personnelles.

## Decision
**Décision retenue : PostgreSQL avec réplication en streaming comme base de données relationnelle.**

PostgreSQL gère les transactions ACID, les contraintes d'intégrité (clés étrangères,
unicité) et propose la sécurité au niveau des lignes (RLS) et l'audit. Un serveur
principal et au moins un réplica en réplication « streaming » assurent la disponibilité
(bascule) et déchargent les lectures du catalogue. La base du service de réservation est
exposée uniquement via ce service (voir [ADR 2](0002-style-d-architecture-microservices.md)).

## Alternatives envisagees
- **MongoDB** : rejetée car la cohérence transactionnelle multi-documents est moins
  naturelle et plus coûteuse, alors que les emprunts sont par nature transactionnels.
- **MySQL** : rejetée car moins complet que PostgreSQL pour les requêtes complexes
  (statistiques d'emprunt, recherches croisées) et pour la sécurité au niveau des lignes.
- **Base unique sans réplication** : rejetée car elle constitue un point de défaillance
  unique, incompatible avec l'exigence de fiabilité.

## Consequences
- **Positives** : cohérence transactionnelle forte, requêtes complexes possibles,
  disponibilité grâce à la réplication, outillage mature (sauvegarde, RLS).
- **Negatives** : configuration et exploitation plus lourdes qu'une base NoSQL ; la
  réplication asynchrone peut servir des données légèrement en retard sur les lectures ;
  le passage à l'échelle en écriture est plus difficile (une seule base principale).
  Ce dernier point motive le découpage par domaine de l'[ADR 2](0002-style-d-architecture-microservices.md)
  et la gestion de la concurrence de l'[ADR 3](0003-concurrence-sur-les-reservations.md).
