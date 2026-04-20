class Vehicle:
    def __init__(self, vin, brand, model, price, status="Available"):
        self.vin = vin
        self.brand = brand
        self.model = model
        self.price = price
        self.status = status

    def display(self):
        return f"{self.brand} {self.model} - ₹{self.price} ({self.status})"