class User:
    """
    Class representing a User.

    Attributes:
        user_id (int, optional): The unique identifier for the user.
        username (str): The user's username.
        email (str): The user's email address.
        password_hash (str): The user's password, stored as a hash.
        bio (str): The user's biography.
    """

    def __init__(
        self,
        username,
        email,
        password_hash,
        bio="",
        user_id=None,
    ):
        """Constructor"""
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.bio = bio

    def __str__(self):
        """Returns a string representation of the user.

        Returns:
            str: A string containing the username and email.
        """
        return f"User({self.username}, email: {self.email})"

    def as_list(self) -> list[str]:
        """Returns the user's key attributes as a list.

        Returns:
            list[str]: A list containing [username, email, bio].
        """
        return [self.username, self.email, self.bio]