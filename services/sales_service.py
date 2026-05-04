from config.db_config import DBConnection
from models.sale import Sale


class SalesService:

    # ─────────────────────────────────────────────
    # FINANCING PLANS (pre-set business rates)
    # Key   → display label shown in UI
    # Value → (tenure_months, annual_interest_rate)
    # ─────────────────────────────────────────────
    FINANCING_PLANS = {
        "6 months  @ 8% p.a.":  ( 6, 0.08),
        "12 months @ 10% p.a.": (12, 0.10),
        "24 months @ 12% p.a.": (24, 0.12),
        "36 months @ 14% p.a.": (36, 0.14),
        "48 months @ 15% p.a.": (48, 0.15),
    }

    # ─────────────────────────────────────────────
    # GST SLABS (Indian Automotive — on ex-showroom price)
    #
    # All passenger vehicles attract 28% GST base.
    # The cess varies by price band:
    #   ≤ ₹10,00,000  → cess  1%  → effective 29%
    #   ₹10L – ₹20L  → cess  3%  → effective 31%
    #   > ₹20,00,000  → cess 22%  → effective 50%
    #
    # Road tax / registration is state-specific and
    # NOT included here (show-room scope only).
    # ─────────────────────────────────────────────
    GST_SLABS = [
        # (upper_limit_inclusive, gst_rate, cess_rate, label)
        (1_000_000,  0.28, 0.01, "28% GST + 1% Cess  (≤ ₹10 L)"),
        (2_000_000,  0.28, 0.03, "28% GST + 3% Cess  (₹10 L – ₹20 L)"),
        (float("inf"), 0.28, 0.22, "28% GST + 22% Cess (> ₹20 L / Luxury)"),
    ]

    def get_gst_breakdown(self, ex_showroom_price: float) -> dict:
        """
        Returns a dict with full GST breakdown for a given ex-showroom price.
        Keys:
            ex_showroom     – base price entered
            gst_rate        – decimal e.g. 0.28
            cess_rate       – decimal e.g. 0.01
            gst_amount      – rupee value of GST component
            cess_amount     – rupee value of cess component
            total_tax       – gst_amount + cess_amount
            on_road_price   – ex_showroom + total_tax
            effective_rate  – total tax as % of ex_showroom
            slab_label      – human-readable slab description
        """
        p = float(ex_showroom_price)
        for limit, gst, cess, label in self.GST_SLABS:
            if p <= limit:
                gst_amt  = round(p * gst,  2)
                cess_amt = round(p * cess, 2)
                total_tax = round(gst_amt + cess_amt, 2)
                return {
                    "ex_showroom":    round(p, 2),
                    "gst_rate":       gst,
                    "cess_rate":      cess,
                    "gst_amount":     gst_amt,
                    "cess_amount":    cess_amt,
                    "total_tax":      total_tax,
                    "on_road_price":  round(p + total_tax, 2),
                    "effective_rate": round((gst + cess) * 100, 1),
                    "slab_label":     label,
                }

    def calculate_tax(self, price: float) -> float:
        """Returns total GST+cess for the given ex-showroom price (backward-compat)."""
        return self.get_gst_breakdown(price)["total_tax"]

    def calculate_total(self, price: float) -> float:
        """Returns on-road price (ex-showroom + GST + cess)."""
        return self.get_gst_breakdown(price)["on_road_price"]

    def calculate_emi(self, price, months=12, interest_rate=0.10):
        """Simple flat-rate EMI (kept for backward compat)."""
        return (price * (1 + interest_rate)) / months

    def calculate_reducing_emi(self, principal, annual_rate, tenure_months):
        """
        Reducing-balance EMI formula:
            EMI = P * r * (1+r)^n / ((1+r)^n - 1)
        where r = monthly interest rate, n = tenure in months.
        Returns 0 if principal or tenure is zero.
        """
        if principal <= 0 or tenure_months <= 0:
            return 0.0
        r = annual_rate / 12
        if r == 0:
            return principal / tenure_months
        n = tenure_months
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return round(emi, 2)

    # ─────────────────────────────────────────────
    # CREATE SALE
    # Accepts optional financing fields on the Sale object.
    # If is_financed=True the extra columns are written to DB.
    # ─────────────────────────────────────────────
    def create_sale(self, sale: Sale):
        db = DBConnection()
        try:
            status_query = "SELECT status FROM vehicles WHERE id = %s"
            result = db.fetch(status_query, (sale.vehicle_id,))

            if not result:
                raise ValueError("Vehicle not found")

            if result[0][0] == "Sold":
                raise ValueError("Vehicle already sold")

            if result[0][0] == "Rented":
                raise ValueError("Vehicle is currently rented and cannot be sold")

            if result[0][0] == "In Service":
                raise ValueError("Vehicle is currently in service and cannot be sold")

            # ── Try inserting with financing columns (requires migration) ──
            try:
                insert_query = """
                INSERT INTO sales
                    (vehicle_id, customer_id, price,
                     is_financed, down_payment, loan_tenure, interest_rate, monthly_emi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                db.execute(insert_query, (
                    sale.vehicle_id,
                    sale.customer_id,
                    sale.price,
                    1 if sale.is_financed else 0,
                    sale.down_payment if sale.is_financed else 0,
                    sale.loan_tenure  if sale.is_financed else None,
                    sale.interest_rate if sale.is_financed else None,
                    sale.monthly_emi  if sale.is_financed else None,
                ))
            except Exception:
                # Fallback: columns not yet added — insert without financing cols
                insert_query = """
                INSERT INTO sales (vehicle_id, customer_id, price)
                VALUES (%s, %s, %s)
                """
                db.execute(insert_query, (
                    sale.vehicle_id,
                    sale.customer_id,
                    sale.price,
                ))

            update_query = "UPDATE vehicles SET status='Sold' WHERE id=%s"
            db.execute(update_query, (sale.vehicle_id,))

            return True

        except Exception as e:
            print(f"[SALE ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET ALL SALES (OBJECTS)
    # ─────────────────────────────────────────────
    def get_sales_report(self):
        db = DBConnection()
        try:
            rows = db.fetch("SELECT * FROM sales")

            sales = []
            for r in rows:
                s = Sale(
                    id=r[0],
                    vehicle_id=r[1],
                    customer_id=r[2],
                    price=r[3],
                    date=r[4]
                )
                sales.append(s)

            return sales

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET SALES WITH DETAILS (FOR UI)
    # Tries to fetch financing cols; gracefully falls
    # back if the DB hasn't been migrated yet.
    # ─────────────────────────────────────────────
    def get_sales_with_details(self):
        db = DBConnection()
        try:
            # Attempt rich query with financing columns
            try:
                query = """
                SELECT
                    s.id,
                    c.name,
                    v.brand,
                    v.model,
                    s.price,
                    s.date,
                    COALESCE(s.is_financed, 0)    AS is_financed,
                    COALESCE(s.down_payment, 0)   AS down_payment,
                    s.loan_tenure,
                    s.interest_rate,
                    s.monthly_emi
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                JOIN vehicles  v ON s.vehicle_id  = v.id
                ORDER BY s.date DESC
                """
                return db.fetch(query)
            except Exception:
                # Fallback — old schema without financing columns
                query = """
                SELECT s.id, c.name, v.brand, v.model, s.price, s.date
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                JOIN vehicles  v ON s.vehicle_id  = v.id
                ORDER BY s.date DESC
                """
                rows = db.fetch(query)
                # Pad with None cols so callers always get 11 fields
                return [r + (0, 0, None, None, None) for r in rows]

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # DELETE SALE
    # Removes sale record and resets vehicle status to Available
    # ─────────────────────────────────────────────
    def delete_sale(self, sale_id):
        db = DBConnection()
        try:
            result = db.fetch(
                "SELECT vehicle_id FROM sales WHERE id = %s", (sale_id,)
            )
            if not result:
                print(f"[DELETE SALE]: Sale {sale_id} not found")
                return False

            vehicle_id = result[0][0]

            db.execute("DELETE FROM sales WHERE id = %s", (sale_id,))

            db.execute(
                "UPDATE vehicles SET status='Available' WHERE id=%s",
                (vehicle_id,)
            )
            return True

        except Exception as e:
            print(f"[DELETE SALE ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # SALES STATS
    # ─────────────────────────────────────────────
    def get_sales_stats(self):
        db = DBConnection()
        try:
            total_sales = db.fetch("SELECT COUNT(*) FROM sales")[0][0]
            total_revenue = db.fetch(
                "SELECT IFNULL(SUM(price),0) FROM sales"
            )[0][0]

            return total_sales, total_revenue

        finally:
            db.close()