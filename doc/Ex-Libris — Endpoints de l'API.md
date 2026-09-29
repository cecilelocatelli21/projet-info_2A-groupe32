# Ex-Libris — Endpoints de l'API

Sep 29, 2026 · @Cécile

## Niveaux d'accès

Toutes les routes exigent d'être connecté, sauf la connexion et la création de compte, conformément au diagramme de cas d'utilisation (le Visiteur ne peut que s'authentifier et créer un compte).

| Accès | Signification | Refus |
| --- | --- | --- |
| sans jeton | route utilisable sans être connecté | — |
| connecté | n'importe quel utilisateur authentifié (jeton valide) | 401 Unauthorized |
| titulaire | connecté **et** propriétaire de la ressource visée | 403 Forbidden |

La différence entre « connecté » et « titulaire » s'explique de la manière suivante : un titulaire est connecté, mais il a des accès réservés à son compte. Par exemple, lui seul doit pouvoir modifier sa bio, son mot de passe, ses ajouts à sa bibliothèque, etc.

Ainsi, dans le code, cela se traduit de la manière suivante :

- **connecté** : une dépendance FastAPI `get_current_user` vérifie le jeton et renvoie le `User` ; sans jeton valide, la réponse est 401 ;
- **titulaire** : on compare en plus `current_user.user_id` au propriétaire de la ressource ; si ce n'est pas lui, la réponse est 403.

Exemple : Alice (user 10), connectée, envoie `PUT /users/5`. Elle passe le premier contrôle (elle est connectée) mais échoue au second, car elle tente de modifier le profil d'un autre utilisateur (user 5).

En revanche, si elle envoie `PUT /users/10`, elle passe les deux contrôles : elle est connectée et elle peut modifier SA bio et SON email.

## Liste des endpoints mises à jour&#32;

## Authentification

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/login` | se connecter, renvoie un jeton | sans jeton |
| POST | `/logout` | se déconnecter | connecté |
| GET | `/users/me` | récupérer son propre profil | connecté |

## Users

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/users` | créer un compte | sans jeton |
| GET | `/users?username=...` | rechercher des utilisateurs | connecté |
| GET | `/users/{user_id}` | fiche utilisateur | connecté |
| PUT | `/users/{user_id}` | modifier la bio et l'email | titulaire |
| PUT | `/users/{user_id}/password` | changer de mot de passe | titulaire |
| DELETE | `/users/{user_id}` | supprimer son compte | titulaire |

## Books

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| GET | `/books/search?q=...` | rechercher dans OpenLibrary | connecté |
| GET | `/books/{work_id}` | fiche livre, avec la note moyenne | connecté |
| GET | `/books/{work_id}/reviews` | critiques d'un livre | connecté |

## Readings (bibliothèque)

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/readings` | ajouter un livre à sa bibliothèque (corps : `work_id`, `status`) | connecté |
| GET | `/users/{user_id}/readings?status=...` | bibliothèque d'un utilisateur, filtrable par statut | connecté |
| GET | `/readings/{reading_id}` | une fiche lecture | connecté |
| PUT | `/readings/{reading_id}` | modifier le statut ou la note | titulaire |
| DELETE | `/readings/{reading_id}` | retirer le livre de sa bibliothèque | titulaire |

## Reviews

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/readings/{reading_id}/review` | écrire une critique, si la lecture est lue ou abandonnée | titulaire |
| GET | `/readings/{reading_id}/review` | critique d'une lecture | connecté |
| GET | `/reviews/{review_id}` | une critique | connecté |
| PUT | `/reviews/{review_id}` | modifier sa critique | titulaire |
| DELETE | `/reviews/{review_id}` | supprimer sa critique | titulaire |
| GET | `/users/{user_id}/reviews` | critiques d'un utilisateur | connecté |

## Likes

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| PUT | `/reviews/{review_id}/like` | poser ou changer sa réaction (corps : `liked: true/false`) | connecté |
| DELETE | `/reviews/{review_id}/like` | retirer sa réaction | connecté |
| GET | `/reviews/{review_id}/likes` | compteurs de likes et dislikes | connecté |

« Connecté » suffit : l'utilisateur qui agit est toujours celui du jeton.

## Follows

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| POST | `/users/{user_id}/follow` | suivre cet utilisateur | connecté |
| DELETE | `/users/{user_id}/follow` | ne plus le suivre | connecté |
| GET | `/users/{user_id}/followers` | ses abonnés | connecté |
| GET | `/users/{user_id}/following` | ses abonnements | connecté |

« Connecté » suffit : l'abonné est toujours l'utilisateur du jeton.

## Recommendations

| Méthode | Route | Rôle | Accès |
| --- | --- | --- | --- |
| GET | `/recommendations` | recommandations de l'utilisateur connecté | connecté |

## Choix de conception et points à valider

- **Identifiant des livres dans les URL** : `work_id` (connu du front après une recherche OpenLibrary) ; `book_id` reste la clé interne en base.
- **Recherche** : deux routes séparées (livres et utilisateurs) plutôt qu'un `/search` générique, car leurs réponses n'ont pas la même forme.
- **Ordre de déclaration FastAPI** : `/books/search` avant `/books/{work_id}`, et `/users/me` avant `/users/{user_id}`.
- **Utilisateur qui agit** : toujours déduit du jeton, jamais passé dans l'URL.

### Connexion : mot de passe et jeton

Deux mécanismes interviennent l'un après l'autre.

- **Le hash salé protège le mot de passe.** On n'enregistre jamais le mot de passe en base, mais une version brouillée, impossible à retransformer en mot de passe. Le « sel » est un ingrédient ajouté avant de brouiller, pour que deux mots de passe identiques ne donnent pas le même résultat. À la connexion, on brouille ce que la personne tape de la même façon et on compare.
- **Le jeton évite de redemander le mot de passe à chaque action.** Une fois le mot de passe vérifié, on remet à l'utilisateur une sorte de ticket de vestiaire. Il le présente ensuite à chaque demande pour prouver qui il est.

Exemple avec Alice :

1. Elle se connecte avec son nom et son mot de passe (`POST /login`). On vérifie son mot de passe grâce au hash salé.
2. Si c'est bon, on lui remet un jeton.
3. Pour toutes ses actions suivantes (voir sa bibliothèque, écrire une critique…), elle présente ce jeton. On ne touche plus au mot de passe.
4. Quand elle se déconnecte (`POST /logout`), le jeton est effacé et ne marche plus.

**Pour l'utilisateur final, le jeton est invisible.** L'application le garde et le joint automatiquement à chaque demande : l'utilisateur a juste l'impression de « rester connecté », comme sur un site où l'on revient sans retaper son mot de passe.

**Pendant le développement, on le manipule à la main**, dans la page de documentation que FastAPI génère toute seule (`/docs`) :

1. On appelle `POST /login` ; la réponse affiche le jeton, une longue suite de caractères.
2. On clique sur le bouton « Authorize » de la page et on y colle ce jeton.
3. La page le joint ensuite automatiquement à toutes les demandes, comme le ferait une vraie application.

**Choix retenu : le ticket ****e****s****t ****noté en base.** À la connexion, l'application crée un jeton au hasard (`secrets.token_urlsafe(32)`) et l'enregistre dans une nouvelle colonne `access_token` de la table des utilisateurs. À chaque demande, elle vérifie que ce jeton figure bien en base ; à la déconnexion, elle l'efface. C'est la méthode vue en TP2, et elle permet une vraie déconnexion.&#32;
