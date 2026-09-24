class Livre:
    """
    Classe représentant un Livre.
 
    id_livre est notre clé interne (indépendante d'Open Library).
    id_work est l'identifiant de l'œuvre fourni par Open Library.
 
    Attributes:
        id_livre (int, optional) : Identifiant interne unique du livre.
        id_work (str) : L'identifiant de l'œuvre fourni par Open Library.
        titre (str) : Le titre du livre.
        auteurs (str) : Le(s) auteur(s) du livre.
        cover_url (str, optional) : URL de l'image de couverture, quand disponible.
    """
 
    def __init__(
        self,
        id_work,
        titre,
        auteurs,
        cover_url=None,
        id_livre=None,
    ):
        """Constructeur"""
        self.id_livre = id_livre
        self.id_work = id_work
        self.titre = titre
        self.auteurs = auteurs
        self.cover_url = cover_url
 
    def __str__(self):
        """Retourne une représentation textuelle du livre.
 
        Returns:
            str : Une chaîne contenant le titre et le(s) auteur(s).
        """
        return f"Livre({self.titre}, auteurs: {self.auteurs})"
 
    def as_list(self) -> list[str]:
        """Retourne les principaux attributs du livre sous forme de liste.
 
        Returns:
            list[str] : Une liste contenant [titre, auteurs, cover_url].
        """
        return [self.titre, self.auteurs, self.cover_url]