# 3. Concurrence sur les réservations

## Statut
Accepte

## Contexte
À la rentrée, plusieurs usagers peuvent réserver le même ouvrage au même instant. Sans
contrôle, deux réservations peuvent écraser l'une l'autre (mise à jour perdue) ou une
place de la file d'attente peut être attribuée deux fois. Le **Service de réservation**
([ADR 2](0002-style-d-architecture-microservices.md)) s'appuie sur PostgreSQL
([ADR 1](0001-choix-de-la-base-de-donnees.md)). Les conflits réels sont rares par rapport
au nombre total de réservations, car la plupart portent sur des ouvrages différents.

## Decision
**Décision retenue : Verrouillage optimiste des réservations (colonne version et nouvelle tentative).**

Chaque ligne de réservation et chaque exemplaire porte une colonne `version`. La mise à
jour est de la forme `UPDATE ... SET ..., version = version + 1 WHERE id = ? AND version = ?`.
Si aucune ligne n'est modifiée, un autre usager a gagné : le service relit l'état puis
retente (au plus trois fois, avec un court délai aléatoire) avant de répondre à l'usager
que l'ouvrage n'est plus disponible.

## Alternatives envisagees
- **Verrouillage pessimiste (`SELECT ... FOR UPDATE`)** : rejeté car les verrous bloquent
  les autres requêtes pendant la transaction ; à la rentrée la contention serait forte et
  des attentes ou des interblocages ralentiraient tout le service.
- **Aucun contrôle de concurrence** : rejeté car il provoque des réservations perdues ou
  en double.
- **File de traitement sérialisée (un seul consommateur)** : rejetée car elle fait de la
  file un goulot d'étranglement et complique la reprise après incident.

## Consequences
- **Positives** : aucun verrou long, bonne performance quand les conflits sont rares,
  adapté à la montée en charge horizontale du service.
- **Negatives** : l'usager peut recevoir un échec et devoir réessayer ; chaque requête
  doit gérer le cas « conflit » ; sous très forte contention sur un même ouvrage
  populaire, beaucoup de tentatives sont perdues. Il faut surveiller le taux de conflits
  pour revoir cette décision si nécessaire.
