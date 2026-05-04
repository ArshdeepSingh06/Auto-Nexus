from config.db_config import DBConnection
from models.vehicle import Vehicle


class InventoryService:

    # ─────────────────────────────────────────────
    # ADD VEHICLE
    # ─────────────────────────────────────────────
    def add_vehicle(self, vehicle: Vehicle):
        db = DBConnection()
        try:
            query = """
            INSERT INTO vehicles (vin, brand, model, price, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (
                vehicle.vin,
                vehicle.brand,
                vehicle.model,
                vehicle.price,
                vehicle.status
            )
            db.execute(query, values)
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET ALL VEHICLES (RETURN OBJECTS ✅)
    # ─────────────────────────────────────────────
    def get_all_vehicles(self):
        db = DBConnection()
        try:
            rows = db.fetch("SELECT * FROM vehicles")

            vehicles = []
            for r in rows:
                v = Vehicle(
                    vin=r[1],
                    brand=r[2],
                    model=r[3],
                    price=r[4],
                    status=r[5]
                )
                v.id = r[0]   # 👈 attach id dynamically
                vehicles.append(v)

            return vehicles

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # DELETE VEHICLE
    # ─────────────────────────────────────────────
    def delete_vehicle(self, vehicle_id):
        db = DBConnection()
        try:
            query = "DELETE FROM vehicles WHERE id = %s"
            db.execute(query, (vehicle_id,))
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # UPDATE STATUS (NEW 🔥 useful everywhere)
    # ─────────────────────────────────────────────
    def update_status(self, vehicle_id, status):
        db = DBConnection()
        try:
            query = "UPDATE vehicles SET status=%s WHERE id=%s"
            db.execute(query, (status, vehicle_id))
        finally:
            db.close()

    # ─────────────────────────────────────────────
    # VEHICLE STATS
    # ─────────────────────────────────────────────
    def get_vehicle_stats(self):
        db = DBConnection()
        try:
            total = db.fetch("SELECT COUNT(*) FROM vehicles")[0][0]
            available = db.fetch(
                "SELECT COUNT(*) FROM vehicles WHERE status='Available'"
            )[0][0]

            return total, available

        finally:
            db.close()