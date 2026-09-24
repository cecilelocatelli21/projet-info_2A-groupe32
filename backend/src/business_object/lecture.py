from datetime import date
 
from business_object.utilisateur import Utilisateur
from business_object.livre import Livre
 
 
class Lecture:
    """
    Business object représentant le fait qu'un utilisateur ait ajouté
    un livre à sa bibliothèque, avec un statut de lecture.
 
    Attributes:
        id_lecture (int, optional) : Identifiant unique de la lecture.
        utilisateur (Utilisateur) : L'utilisateur propriétaire de cette lecture.
        livre (Livre) : Le livre concerné par cette lecture.
        statut (str) : Statut de lecture ("à lire", "en cours", "lu", "abandonné").
        date_ajout (date) : Date à laquelle le livre a été ajouté à la bibliothèque.
        date_lu (date, optional) : Date à laquelle le statut est passé à "lu".
            Renseignée uniquement une fois le livre lu.
        note (int, optional) : Note attribuée au livre (de 0 à 5).
            Renseignée uniquement une fois le livre lu ou abandonné.
    """
 
    def __init__(
        self,
        utilisateur: Utilisateur,
        livre: Livre,
        statut: str,
        date_ajout: date,
        date_lu: date = None,
        note: int = None,
        id_lecture: int = None,
    ):
        """Constructeur"""
        self.id_lecture = id_lecture
        self.utilisateur = utilisateur
        self.livre = livre
        self.statut = statut
        self.date_ajout = date_ajout
        self.date_lu = date_lu
        self.note = note
 
    def __str__(self) -> str:
        """Retourne une représentation textuelle de la lecture.
 
        Returns:
            str : Une chaîne contenant le titre du livre, le statut et la note.
        """
        return (
            f"Lecture({self.livre.titre}, statut: {self.statut}, "
            f"note: {self.note})"
        )