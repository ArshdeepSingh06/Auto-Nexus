from config.db_config import DBConnection

class SalesService:
    def __init__(self):
        self.db = DBConnection()

    def calculate_tax(self, price):
        return price * 0.18  # 18% GST

    def calculate_total(self, price):
        return price + self.calculate_tax(price)

    def calculate_emi(self, price, months=12, interest_rate=0.1):
        total = price * (1 + interest_rate)
        return total / months

    def create_sale(self, vehicle_id, customer_id, price):
        query = """
        INSERT INTO sales (vehicle_id, customer_id, price)
        VALUES (%s, %s, %s)
        """
        self.db.execute(query, (vehicle_id, customer_id, price))

        # Update vehicle status
        update_query = "UPDATE vehicles SET status='Sold' WHERE id=%s"
        self.db.execute(update_query, (vehicle_id,))

    def get_sales_report(self):
        query = "SELECT * FROM sales"
        return self.db.fetch(query)