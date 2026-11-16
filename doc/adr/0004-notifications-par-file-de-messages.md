# 4. Notifications par file de messages

## Statut
Accepte

## Contexte
Le système envoie des notifications aux usagers : confirmation d'emprunt, rappel de date
de retour, ouvrage réservé enfin disponible. L'envoi d'un e-mail ou d'un SMS est lent et
peut échouer. Si le **Service d'emprunt** l'effectuait lui-même, un fournisseur de
messagerie en panne ralentirait ou bloquerait les emprunts. L'architecture en
microservices ([ADR 2](0002-style-d-architecture-microservices.md)) impose de limiter le
couplage entre services.

## Decision
**Décision retenue : File de messages asynchrone (RabbitMQ) consommée par un Service de notification dédié.**

Les services d'emprunt et de réservation publient un événement (par exemple
`EmpruntCree`, `ReservationDisponible`) sur RabbitMQ puis continuent sans attendre. Le
**Service de notification** consomme ces événements et envoie les messages. Les messages
sont persistants avec accusé de réception, et les échecs répétés vont dans une file
d'échecs (dead-letter) pour reprise. Les notifications sont idempotentes : un message
rejoué ne produit pas un second envoi.

## Alternatives envisagees
- **Appels synchrones directs depuis le service d'emprunt** : rejetés car ils créent un
  couplage fort et ajoutent la latence et les pannes du fournisseur de messagerie au
  temps de réponse d'un emprunt.
- **Table « outbox » interrogée régulièrement (polling)** : rejetée car moins réactive,
  charge inutilement la base ([ADR 1](0001-choix-de-la-base-de-donnees.md)) et demande
  plus de code.
- **Kafka** : rejeté car trop lourd pour le volume attendu ; on n'a pas besoin de
  conserver et rejouer un historique d'événements.

## Consequences
- **Positives** : les emprunts ne dépendent plus du fournisseur de notifications, le
  Service de notification se met à l'échelle seul, les pics sont absorbés par la file.
- **Negatives** : un composant de plus à exploiter et à superviser ; les notifications
  sont livrées avec un léger retard (cohérence à terme) ; il faut sécuriser le broker
  (comptes dédiés par service, TLS) pour qu'un service compromis ne lise pas ou ne
  publie pas tous les messages.
