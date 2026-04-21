from config.db_config import DBConnection

class ServiceModule:

    def book_service(self, customer_id, vehicle_id, service_type):
        db = DBConnection()
        try:
            query = """
            INSERT INTO services (customer_id, vehicle_id, service_type, status)
            VALUES (%s, %s, %s, %s)
            """
            db.execute(query, (customer_id, vehicle_id, service_type, "Pending"))
        finally:
            db.close()

    def update_status(self, service_id, status):
        db = DBConnection()
        try:
            query = "UPDATE services SET status=%s WHERE id=%s"
            db.execute(query, (status, service_id))
        finally:
            db.close()

    def get_all_services(self):
        db = DBConnection()
        try:
            query = "SELECT * FROM services"
            return db.fetch(query)
        finally:
            db.close()

    def delete_service(self, service_id):
        db = DBConnection()
        try:
            query = "DELETE FROM services WHERE id = %s"
            db.execute(query, (service_id,))
        finally:
            db.close()

    def get_service_stats(self):
        db = DBConnection()
        try:
            total_services = db.fetch("SELECT COUNT(*) FROM services")[0][0]
            return total_services
        finally:
            db.close()

