from datetime import datetime
 
from business_object.lecture import Lecture
 
 
class Critique:
    """
    Business object représentant une critique rédigée par un utilisateur
    pour une de ses lectures.
 
    Une critique est rattachée à une Lecture (et non directement à un
    utilisateur ou un livre) : cela garantit qu'un utilisateur ne peut
    critiquer qu'un livre qu'il a effectivement lu ou abandonné.
 
    Attributes:
        id_critique (int, optional) : Identifiant unique de la critique.
        lecture (Lecture) : La lecture sur laquelle porte la critique.
        texte (str) : Le contenu de la critique.
        date_publication (datetime) : Date et heure de publication de la critique.
    """
 
    def __init__(
        self,
        lecture: Lecture,
        texte: str,
        date_publication: datetime,
        id_critique: int = None,
    ):
        """Constructeur"""
        self.id_critique = id_critique
        self.lecture = lecture
        self.texte = texte
        self.date_publication = date_publication
 
    def __str__(self) -> str:
        """Retourne une représentation textuelle de la critique.
 
        Returns:
            str : Une chaîne contenant le titre du livre et le texte de la critique.
        """
        return f"Critique({self.lecture.livre.titre}): {self.texte}"