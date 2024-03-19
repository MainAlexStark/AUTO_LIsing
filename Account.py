

class Account():
    def __init__(self, api, sec) -> None:
        self.api_key = api
        self.secret_key = sec

        self.balance = None