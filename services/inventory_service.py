from config.db_config import DBConnection
from models.vehicle import Vehicle

class InventoryService:
    def __init__(self):
        self.db = DBConnection()

    def add_vehicle(self, vehicle: Vehicle):
        query = """
        INSERT INTO vehicles (vin, brand, model, price, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (vehicle.vin, vehicle.brand, vehicle.model, vehicle.price, vehicle.status)
        self.db.execute(query, values)

    def get_all_vehicles(self):
        query = "SELECT * FROM vehicles"
        return self.db.fetch(query)