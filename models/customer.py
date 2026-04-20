class Customer:
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

    def get_details(self):
        return f"{self.name} | {self.phone} | {self.email}"