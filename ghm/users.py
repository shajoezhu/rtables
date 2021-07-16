class Users:
    """
    Users
    """

    def __init__(self, users_conf, filter, client):
        """
        Constructor
        """
        if filter in ["source", "destination"]:
            self.users = [client.get_user(u[filter]) for u in users_conf]
