class User:
    id: int
    username: str
    password: str
    email: str
    cvLink: str

    def __init__(self, userProps):
        self.id = userProps['id']
        self.username = userProps['username']
        self.password = userProps['password']
        self.email = userProps['email']

        if userProps['cvLink']:
            self.cvLink = userProps['cvLink']