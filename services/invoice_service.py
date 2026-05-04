from config.db_config import DBConnection
from models.invoice import Invoice


class InvoiceService:

    SERVICE_PRICING = {
        "Basic": 2000,
        "Standard": 4000,
        "Premium": 7000
    }

    # ─────────────────────────────────────────────
    # GENERATE SERVICE INVOICE
    # ─────────────────────────────────────────────
    def generate_service_invoice(self, job_id):
        db = DBConnection()
        try:
            query = """
                SELECT id, vehicle_id, customer_id, service_type, status
                FROM service_jobs
                WHERE id = %s
            """
            result = db.fetch(query, (job_id,))

            if not result:
                raise ValueError("Service job not found")

            job = result[0]
            service_type = job[3]
            status = job[4]

            if status != "Completed":
                raise ValueError("Service not completed yet")

            labor_cost = self.SERVICE_PRICING.get(service_type, 3000)
            parts_cost = 1500
            total = labor_cost + parts_cost

            invoice = Invoice(ref_id=job_id, type="SERVICE", amount=total)

            insert_query = """
                INSERT INTO invoices (ref_id, type, amount)
                VALUES (%s, %s, %s)
            """
            db.execute(insert_query, (invoice.ref_id, invoice.type, invoice.amount))

            return invoice

        except Exception as e:
            print(f"[INVOICE ERROR]: {e}")
            return None

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET ALL INVOICES
    # ─────────────────────────────────────────────
    def get_all_invoices(self):
        db = DBConnection()
        try:
            rows = db.fetch("SELECT * FROM invoices")

            invoices = []
            for r in rows:
                inv = Invoice(ref_id=r[1], type=r[2], amount=r[3], id=r[0])
                invoices.append(inv)

            return invoices

        finally:
            db.close()