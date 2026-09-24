from datetime import datetime
 
from business_object.utilisateur import Utilisateur
from business_object.critique import Critique
 
 
class Like:
    """
    Business object représentant la réaction d'un utilisateur à une critique.
 
    aime = True  -> "j'aime"
    aime = False -> "je n'aime pas"
 
    Attributes:
        utilisateur (Utilisateur) : L'utilisateur à l'origine de la réaction.
        critique (Critique) : La critique concernée par la réaction.
        aime (bool) : True pour "j'aime", False pour "je n'aime pas".
        date_like (datetime) : Date et heure de la réaction.
    """
 
    def __init__(
        self,
        utilisateur: Utilisateur,
        critique: Critique,
        aime: bool,
        date_like: datetime,
    ):
        """Constructeur"""
        self.utilisateur = utilisateur
        self.critique = critique
        self.aime = aime
        self.date_like = date_like
 
    def __str__(self) -> str:
        """Retourne une représentation textuelle de la réaction.
 
        Returns:
            str : Une chaîne indiquant qui a réagi et comment.
        """
        reaction = "aime" if self.aime else "n'aime pas"
        return f"Like({self.utilisateur.pseudo} {reaction} la critique)"