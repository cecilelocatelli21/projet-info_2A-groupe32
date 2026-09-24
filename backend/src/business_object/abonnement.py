from datetime import datetime
 
from business_object.utilisateur import Utilisateur
 
 
class Abonnement:
    """
    Business object représentant un abonnement entre deux utilisateurs.
 
    follower est l'utilisateur qui s'abonne, followed est l'utilisateur
    suivi. Un abonnement n'est pas forcément réciproque.
 
    Attributes:
        id_abonnement (int, optional) : Identifiant unique de l'abonnement.
        follower (Utilisateur) : L'utilisateur qui s'abonne.
        followed (Utilisateur) : L'utilisateur suivi.
        date_abonnement (datetime) : Date et heure de l'abonnement.
    """
 
    def __init__(
        self,
        follower: Utilisateur,
        followed: Utilisateur,
        date_abonnement: datetime,
        id_abonnement: int = None,
    ):
        """Constructeur"""
        self.id_abonnement = id_abonnement
        self.follower = follower
        self.followed = followed
        self.date_abonnement = date_abonnement
 
    def __str__(self) -> str:
        """Retourne une représentation textuelle de l'abonnement.
 
        Returns:
            str : Une chaîne indiquant qui suit qui.
        """
        return f"Abonnement({self.follower.pseudo} suit {self.followed.pseudo})"