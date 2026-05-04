from config.db_config import DBConnection


class ReportService:

    # ─────────────────────────────────────────────
    # MONTHLY REVENUE
    # ─────────────────────────────────────────────
    def monthly_revenue(self, month: int, year: int) -> float:
        db = DBConnection()
        try:
            query = """
                SELECT IFNULL(SUM(price), 0)
                FROM sales
                WHERE MONTH(date) = %s AND YEAR(date) = %s
            """
            result = db.fetch(query, (month, year))
            return float(result[0][0]) if result else 0.0

        except Exception as e:
            print(f"[REPORT ERROR]: {e}")
            return 0.0

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # RENTAL INCOME
    # ─────────────────────────────────────────────
    def rental_income(self, start_date, end_date) -> float:
        db = DBConnection()
        try:
            query = """
                SELECT IFNULL(SUM(
                    DATEDIFF(end_date, start_date) * 1000
                ), 0)
                FROM rentals
                WHERE start_date >= %s AND end_date <= %s
                  AND status IN ('Active', 'Completed')
            """
            result = db.fetch(query, (start_date, end_date))
            return float(result[0][0]) if result else 0.0

        except Exception as e:
            print(f"[RENTAL INCOME ERROR]: {e}")
            return 0.0

        finally:
            db.close()