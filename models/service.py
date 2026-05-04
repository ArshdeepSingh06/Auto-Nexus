class Service:
    def __init__(self, vehicle_id, customer_id, service_type, status="Pending"):
        self.vehicle_id = vehicle_id
        self.customer_id = customer_id
        self.service_type = service_type
        self.status = status