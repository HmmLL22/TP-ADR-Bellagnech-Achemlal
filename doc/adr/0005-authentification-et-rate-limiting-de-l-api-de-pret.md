# 5. Authentification et rate limiting de l'API de prêt

## Statut
Accepte

## Contexte
L'API de prêt expose les opérations d'emprunt, de retour et de réservation à des clients
externes : application mobile, bornes de prêt en libre-service et systèmes de
bibliothèques partenaires. Elle manipule des **données personnelles** des usagers
(identité, historique d'emprunt). Menaces identifiées (STRIDE) : **usurpation d'identité**
(*Spoofing*) d'un compte lecteur, **divulgation d'informations** (*Information
disclosure*) par énumération de comptes, et **déni de service** (*Denial of service*) par
des robots qui réservent en masse. Cette API est le point d'entrée des microservices
([ADR 2](0002-style-d-architecture-microservices.md)) : tous les appels externes traversent
la frontière de confiance à ce niveau.

## Decision
**Décision retenue : OAuth2 + rate limiting sur l'API de prêt.**

L'API de prêt n'est joignable qu'avec un jeton OAuth2 : flux *client credentials* pour les
partenaires et les bornes, flux *authorization code* (avec PKCE) pour l'application mobile.
Un **Service d'authentification OAuth2** émet des jetons de courte durée et l'**API
Gateway** les valide à chaque requête. Elle applique aussi un **rate limiting par client**
(par exemple 100 requêtes par minute). Aucun microservice n'est joignable en contournant
la gateway (segmentation réseau). Les refus d'authentification et les dépassements de
débit sont journalisés.

## Alternatives envisagees
- **Clé API statique partagée** : rejetée car on ne peut pas révoquer un client
  individuellement, il n'y a aucune traçabilité par usager, et la fuite d'une seule clé
  compromet tous les clients.
- **Liste blanche d'adresses IP** : rejetée car incompatible avec l'application mobile
  (adresses dynamiques) et elle ne protège pas contre un client légitime compromis.
- **Authentification de base (identifiant et mot de passe à chaque appel)** : rejetée car
  elle expose les mots de passe à chaque requête et n'offre ni portée (*scope*) ni
  expiration.

## Consequences
- **Positives** : révocation fine par client, traçabilité des appels, protection contre
  les abus automatisés (robots, énumération), jetons à durée limitée, et **Conformité RGPD
  art. 32** (sécurité du traitement des données personnelles).
- **Negatives** : intégration plus complexe pour les partenaires (gestion des jetons),
  latence supplémentaire due à la validation des jetons, un composant de plus à exploiter
  (le Service d'authentification OAuth2 devient critique : sa panne bloque les appels) et
  un réglage du seuil de rate limiting à ajuster pour ne pas bloquer les pics légitimes
  de la rentrée.
