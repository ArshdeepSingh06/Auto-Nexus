from config.db_config import DBConnection

class SalesService:

    def calculate_tax(self, price):
        return price * 0.18  # 18% GST

    def calculate_total(self, price):
        return price + self.calculate_tax(price)

    def calculate_emi(self, price, months=12, interest_rate=0.1):
        total = price * (1 + interest_rate)
        return total / months

    def create_sale(self, vehicle_id, customer_id, price):
        db = DBConnection()
        try:
            query = """
            INSERT INTO sales (vehicle_id, customer_id, price)
            VALUES (%s, %s, %s)
            """
            db.execute(query, (vehicle_id, customer_id, price))

            # Update vehicle status
            update_query = "UPDATE vehicles SET status='Sold' WHERE id=%s"
            db.execute(update_query, (vehicle_id,))

        finally:
            db.close()

    def get_sales_report(self):
        db = DBConnection()
        try:
            query = "SELECT * FROM sales"
            return db.fetch(query)
        finally:
            db.close()

    def get_sales_with_details(self):
        db = DBConnection()
        try:
            query = """
            SELECT s.id, c.name, v.brand, v.model, s.price, s.date
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            JOIN vehicles v ON s.vehicle_id = v.id
            ORDER BY s.date DESC
            """
            return db.fetch(query)
        finally:
            db.close()

    def delete_sale(self, sale_id):
        db = DBConnection()
        try:
            query = "DELETE FROM sales WHERE id = %s"
            db.execute(query, (sale_id,))
        finally:
            db.close()
    
    def get_sales_stats(self):
        db = DBConnection()
        try:
            total_sales = db.fetch("SELECT COUNT(*) FROM sales")[0][0]
            total_revenue = db.fetch("SELECT IFNULL(SUM(price),0) FROM sales")[0][0]
            return total_sales, total_revenue
        finally:
            db.close()

