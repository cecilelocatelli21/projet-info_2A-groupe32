class Utilisateur:
    """
    Classe représentant un Utilisateur.

    Attributes:
        id_user (int, optional) : Identifiant unique de l'utilisateur.
        pseudo (str) : Le pseudo de l'utilisateur.
        email (str) : L'adresse email de l'utilisateur.
        password_hash (str) : Le mot de passe de l'utilisateur, stocké sous forme de hash.
        bio (str) : La biographie de l'utilisateur.
    """

    def __init__(
        self,
        pseudo,
        email,
        password_hash,
        bio="",
        id_user=None,
    ):
        """Constructeur"""
        self.id_user = id_user
        self.pseudo = pseudo
        self.email = email
        self.password_hash = password_hash
        self.bio = bio

    def __str__(self):
        """Retourne une représentation textuelle de l'utilisateur.

        Returns:
            str : Une chaîne contenant le pseudo et l'email.
        """
        return f"Utilisateur({self.pseudo}, email: {self.email})"

    def as_list(self) -> list[str]:
        """Retourne les principaux attributs de l'utilisateur sous forme de liste.

        Returns:
            list[str] : Une liste contenant [pseudo, email, bio].
        """
        return [self.pseudo, self.email, self.bio]