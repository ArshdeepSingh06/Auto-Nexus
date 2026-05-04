class Rental:
    def __init__(self, vehicle_id, customer_id, start_date, end_date, status="Active", id=None):
        self.id = id
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status