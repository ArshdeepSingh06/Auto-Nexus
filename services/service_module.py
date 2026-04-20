from config.db_config import DBConnection

class ServiceModule:
    def __init__(self):
        self.db = DBConnection()

    def book_service(self, customer_id, vehicle_id, service_type):
        query = """
        INSERT INTO services (customer_id, vehicle_id, service_type, status)
        VALUES (%s, %s, %s, %s)
        """
        self.db.execute(query, (customer_id, vehicle_id, service_type, "Pending"))

    def update_status(self, service_id, status):
        query = "UPDATE services SET status=%s WHERE id=%s"
        self.db.execute(query, (status, service_id))

    def get_all_services(self):
        query = "SELECT * FROM services"
        return self.db.fetch(query)