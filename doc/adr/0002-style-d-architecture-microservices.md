# 2. Style d'architecture : microservices

## Statut
Accepte

## Contexte
Le système doit être **scalable**, **fiable** et **maintenable**. Les différentes
fonctions n'ont pas la même charge : la réservation et l'emprunt subissent de forts pics
à la rentrée universitaire, alors que le catalogue ou les notifications sont sollicités
de façon plus régulière. Plusieurs personnes doivent pouvoir faire évoluer des fonctions
différentes sans se bloquer mutuellement. Le choix de la base de données
([ADR 1](0001-choix-de-la-base-de-donnees.md)) limite le passage à l'échelle d'une base
unique partagée par tous les domaines.

## Decision
**Décision retenue : Découper le système en microservices par domaine métier, déployables indépendamment.**

Quatre services : **Service d'emprunt**, **Service de réservation**, **Service de
notification** et **Service de catalogue**. Chaque service possède ses données (pas de
base partagée entre services), est construit, testé et déployé séparément, et expose
uniquement une API. Les clients passent par une API Gateway, point d'entrée unique
(voir [ADR 5](0005-authentification-et-rate-limiting-de-l-api-de-pret.md)). Les échanges
asynchrones passent par une file de messages
([ADR 4](0004-notifications-par-file-de-messages.md)).

## Alternatives envisagees
- **Monolithe modulaire** : rejeté car on ne peut pas faire monter en charge uniquement
  la réservation aux heures de pointe ; tout le monolithe doit être dupliqué.
- **Monolithe classique** : rejeté car le couplage fort entre fonctions ralentit les
  évolutions et fait peser un risque de régression sur l'ensemble à chaque livraison.

## Consequences
- **Positives** : montée en charge ciblée par service, déploiements indépendants,
  isolation des pannes (un service en panne n'arrête pas tout), équipes autonomes,
  frontières de confiance explicites entre services.
- **Negatives** : complexité d'exploitation (orchestration, supervision), latence des
  appels réseau, cohérence des données entre services plus difficile (pas de transaction
  globale), davantage de surfaces réseau à sécuriser. Chaque service doit éviter l'accès
  direct à la base d'un autre service.
