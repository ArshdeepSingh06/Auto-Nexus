from config.db_config import DBConnection
from models.service import Service


class ServiceModule:

    # ─────────────────────────────────────────────
    # BOOK SERVICE
    # Only Available vehicles can be booked for service.
    # Sets vehicle status → "In Service" on booking.
    # ─────────────────────────────────────────────
    def book_service(self, service: Service):
        db = DBConnection()
        try:
            v_result = db.fetch("SELECT id, status FROM vehicles WHERE id = %s", (service.vehicle_id,))
            if not v_result:
                raise ValueError("Vehicle not found")

            v_status = v_result[0][1]
            if v_status == "Rented":
                raise ValueError("Vehicle is currently rented and cannot be booked for service")
            if v_status == "In Service":
                raise ValueError("Vehicle is already in service")
            # Available (dealer) and Sold (customer-owned) are both allowed

            c_check = db.fetch("SELECT id FROM customers WHERE id = %s", (service.customer_id,))
            if not c_check:
                raise ValueError("Customer not found")

            query = """
            INSERT INTO service_jobs (customer_id, vehicle_id, service_type, status)
            VALUES (%s, %s, %s, %s)
            """
            db.execute(query, (
                service.customer_id,
                service.vehicle_id,
                service.service_type,
                "Pending"
            ))

            # Lock vehicle while it's in for service
            db.execute(
                "UPDATE vehicles SET status='In Service' WHERE id=%s",
                (service.vehicle_id,)
            )

            return True

        except Exception as e:
            print(f"[SERVICE ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # UPDATE STATUS
    # When a job is marked Completed, check if the vehicle
    # has any other active (Pending / In Progress) jobs.
    # If none remain, free the vehicle → "Available".
    # ─────────────────────────────────────────────
    def update_status(self, service_id, status):
        db = DBConnection()
        try:
            valid = ["Pending", "In Progress", "Completed"]
            if status not in valid:
                raise ValueError("Invalid status")

            # Fetch vehicle_id before updating
            job = db.fetch(
                "SELECT vehicle_id FROM service_jobs WHERE id = %s", (service_id,)
            )
            if not job:
                raise ValueError("Service job not found")

            vehicle_id = job[0][0]

            db.execute(
                "UPDATE service_jobs SET status=%s WHERE id=%s",
                (status, service_id)
            )

            if status == "Completed":
                # Check if any other active jobs still exist for this vehicle
                still_active = db.fetch("""
                    SELECT COUNT(*) FROM service_jobs
                    WHERE vehicle_id = %s
                      AND id != %s
                      AND status IN ('Pending', 'In Progress')
                """, (vehicle_id, service_id))

                if still_active[0][0] == 0:
                    # Restore correct pre-service status
                    sold_check = db.fetch(
                        "SELECT COUNT(*) FROM sales WHERE vehicle_id = %s", (vehicle_id,)
                    )
                    restore_status = "Sold" if sold_check[0][0] > 0 else "Available"
                    db.execute(
                        "UPDATE vehicles SET status=%s WHERE id=%s",
                        (restore_status, vehicle_id)
                    )
            else:
                # Pending or In Progress — keep vehicle locked as In Service
                db.execute(
                    "UPDATE vehicles SET status='In Service' WHERE id=%s",
                    (vehicle_id,)
                )

            return True

        except Exception as e:
            print(f"[STATUS ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET ALL SERVICES
    # ─────────────────────────────────────────────
    def get_all_services(self):
        db = DBConnection()
        try:
            query = """
            SELECT
                sj.id,
                COALESCE(c.name, 'Dealer') AS owner,
                v.brand,
                v.model,
                sj.service_type,
                sj.status,
                sj.date
            FROM service_jobs sj
            JOIN vehicles v ON sj.vehicle_id = v.id
            LEFT JOIN customers c ON sj.customer_id = c.id
            ORDER BY sj.date DESC
            """
            return db.fetch(query)

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # DELETE SERVICE
    # If deleting the last active job for a vehicle,
    # release the vehicle back to Available.
    # ─────────────────────────────────────────────
    def delete_service(self, service_id):
        db = DBConnection()
        try:
            job = db.fetch(
                "SELECT vehicle_id, status FROM service_jobs WHERE id = %s",
                (service_id,)
            )
            if not job:
                return False

            vehicle_id = job[0][0]
            job_status = job[0][1]

            db.execute("DELETE FROM service_jobs WHERE id = %s", (service_id,))

            # If the deleted job was still active, check if vehicle can be freed
            if job_status in ("Pending", "In Progress"):
                remaining = db.fetch("""
                    SELECT COUNT(*) FROM service_jobs
                    WHERE vehicle_id = %s
                      AND status IN ('Pending', 'In Progress')
                """, (vehicle_id,))

                if remaining[0][0] == 0:
                    sold_check = db.fetch(
                        "SELECT COUNT(*) FROM sales WHERE vehicle_id = %s", (vehicle_id,)
                    )
                    restore_status = "Sold" if sold_check[0][0] > 0 else "Available"
                    db.execute(
                        "UPDATE vehicles SET status=%s WHERE id=%s",
                        (restore_status, vehicle_id)
                    )

            return True

        except Exception as e:
            print(f"[DELETE ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # SERVICE STATS
    # ─────────────────────────────────────────────
    def get_service_stats(self):
        db = DBConnection()
        try:
            total = db.fetch("SELECT COUNT(*) FROM service_jobs")[0][0]
            completed = db.fetch(
                "SELECT COUNT(*) FROM service_jobs WHERE status='Completed'"
            )[0][0]
            return total, completed

        finally:
            db.close()