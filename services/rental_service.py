from config.db_config import DBConnection
from models.rental import Rental


class RentalService:

    # ─────────────────────────────────────────────
    # CHECK AVAILABILITY
    # Only dealer-owned (never sold) vehicles can be rented.
    # A vehicle is dealer-owned if it has NO record in the sales table.
    # Additionally it must be status=Available and have no active rental.
    # ─────────────────────────────────────────────
    def is_available(self, vehicle_id):
        db = DBConnection()
        try:
            # Must be Available status (not Sold / Rented / In Service)
            status_result = db.fetch(
                "SELECT status FROM vehicles WHERE id = %s", (vehicle_id,)
            )
            if not status_result or status_result[0][0] != "Available":
                return False

            # Must have never been sold — dealer-only vehicles only
            sold_check = db.fetch(
                "SELECT COUNT(*) FROM sales WHERE vehicle_id = %s", (vehicle_id,)
            )
            if sold_check[0][0] > 0:
                return False

            # Must have no currently active rental
            active_check = db.fetch(
                "SELECT COUNT(*) FROM rentals WHERE vehicle_id = %s AND status = 'Active'",
                (vehicle_id,)
            )
            return active_check[0][0] == 0

        except Exception as e:
            print(f"[AVAILABILITY ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # BOOK VEHICLE
    # Inserts rental row + marks vehicle as Rented
    # ─────────────────────────────────────────────
    def book_vehicle(self, rental: Rental):
        db = DBConnection()
        try:
            if not self.is_available(rental.vehicle_id):
                raise ValueError("Vehicle is not available for rental")

            insert_query = """
                INSERT INTO rentals (vehicle_id, customer_id, start_date, end_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            db.execute(insert_query, (
                rental.vehicle_id,
                rental.customer_id,
                rental.start_date,
                rental.end_date,
                "Active"
            ))

            # Keep vehicle status in sync
            db.execute(
                "UPDATE vehicles SET status='Rented' WHERE id=%s",
                (rental.vehicle_id,)
            )

            return True

        except Exception as e:
            print(f"[BOOKING ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # GET ALL RENTALS
    # ─────────────────────────────────────────────
    def get_all_rentals(self):
        db = DBConnection()
        try:
            rows = db.fetch("SELECT * FROM rentals")

            rentals = []
            for r in rows:
                rent = Rental(
                    id=r[0],
                    vehicle_id=r[1],
                    customer_id=r[2],
                    start_date=r[3],
                    end_date=r[4],
                    status=r[5]
                )
                rentals.append(rent)

            return rentals

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # COMPLETE RENTAL
    # Marks rental Completed + frees vehicle back to Available
    # ─────────────────────────────────────────────
    def complete_rental(self, rental_id):
        db = DBConnection()
        try:
            # Get vehicle_id before updating
            result = db.fetch(
                "SELECT vehicle_id FROM rentals WHERE id = %s", (rental_id,)
            )
            if not result:
                print(f"[COMPLETE RENTAL]: Rental {rental_id} not found")
                return False

            vehicle_id = result[0][0]

            db.execute(
                "UPDATE rentals SET status='Completed' WHERE id=%s",
                (rental_id,)
            )
            db.execute(
                "UPDATE vehicles SET status='Available' WHERE id=%s",
                (vehicle_id,)
            )
            return True

        except Exception as e:
            print(f"[COMPLETE RENTAL ERROR]: {e}")
            return False

        finally:
            db.close()

    # ─────────────────────────────────────────────
    # LATE PENALTY
    # ─────────────────────────────────────────────
    def calculate_penalty(self, days_late, daily_rate):
        return max(0, days_late * daily_rate)

    # ─────────────────────────────────────────────
    # GENERATE AGREEMENT
    # ─────────────────────────────────────────────
    def generate_agreement(self, booking_id):
        db = DBConnection()
        try:
            query = """
                SELECT r.id, c.name, v.brand, v.model, r.start_date, r.end_date
                FROM rentals r
                JOIN customers c ON r.customer_id = c.id
                JOIN vehicles v ON r.vehicle_id = v.id
                WHERE r.id = %s
            """
            result = db.fetch(query, (booking_id,))

            if not result:
                return "Booking not found"

            r = result[0]

            return f"""
            ─────────────────────────────
            RENTAL AGREEMENT
            ─────────────────────────────
            Booking ID : {r[0]}
            Customer   : {r[1]}
            Vehicle    : {r[2]} {r[3]}
            Start Date : {r[4]}
            End Date   : {r[5]}

            Terms:
            - Vehicle must be returned on time
            - Late return will incur penalty
            - Damage charges applicable

            Thank you for choosing AutoNexus 🚗
            """

        except Exception as e:
            print(f"[AGREEMENT ERROR]: {e}")
            return "Error generating agreement"

        finally:
            db.close()