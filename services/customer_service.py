from config.db_config import DBConnection

class CustomerService:

    def get_all_customers(self):
        db = DBConnection()
        try:
            return db.fetch("SELECT * FROM customers")
        finally:
            db.close()

    def delete_customer(self, customer_id):
        db = DBConnection()
        try:
            query = "DELETE FROM customers WHERE id = %s"
            db.execute(query, (customer_id,))
        finally:
            db.close()