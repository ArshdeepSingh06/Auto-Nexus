from config.db_config import DBConnection
from models.customer import Customer


class CustomerService:

    # ─────────────────────────────────────────────
    # GET ALL CUSTOMERS
    # Returns Customer objects with .id attached
    # ─────────────────────────────────────────────
    def get_all_customers(self):
        db = DBConnection()
        try:
            rows = db.fetch("SELECT * FROM customers")

            customers = []
            for r in rows:
                customer = Customer(
                    name=r[1],
                    phone=r[2],
                    email=r[3],
                )
                customer.id = r[0]   # attach id dynamically
                customers.append(customer)

            return customers

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # ADD CUSTOMER
    # ─────────────────────────────────────────────
    def add_customer(self, customer: Customer):
        db = DBConnection()
        try:
            query = """
            INSERT INTO customers (name, phone, email)
            VALUES (%s, %s, %s)
            """
            db.execute(query, (customer.name, customer.phone, customer.email))

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # DELETE CUSTOMER
    # ─────────────────────────────────────────────
    def delete_customer(self, customer_id):
        db = DBConnection()
        try:
            query = "DELETE FROM customers WHERE id = %s"
            db.execute(query, (customer_id,))
            return True
        except Exception as e:
            print(f"[DELETE CUSTOMER ERROR]: {e}")
            return False
        finally:
            db.close()