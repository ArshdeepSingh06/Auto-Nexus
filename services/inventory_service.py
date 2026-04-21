from config.db_config import DBConnection
from models.vehicle import Vehicle

class InventoryService:

    def add_vehicle(self, vehicle: Vehicle):
        db = DBConnection()
        try:
            query = """
            INSERT INTO vehicles (vin, brand, model, price, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (vehicle.vin, vehicle.brand, vehicle.model, vehicle.price, vehicle.status)
            db.execute(query, values)
        finally:
            db.close()

    def get_all_vehicles(self):
        db = DBConnection()
        try:
            query = "SELECT * FROM vehicles"
            return db.fetch(query)
        finally:
            db.close()
    
    def delete_vehicle(self, vehicle_id):
        db = DBConnection()
        try:
            query = "DELETE FROM vehicles WHERE id  = %s"
            db.execute(query, (vehicle_id,))
        finally:
            db.close()

    def get_vehicle_stats(self):
        db = DBConnection()
        try:
            total = db.fetch("SELECT COUNT(*) FROM vehicles")[0][0]
            available = db.fetch("SELECT COUNT(*) FROM vehicles WHERE status='Available'")[0][0]
            return total, available
        finally:
            db.close()

