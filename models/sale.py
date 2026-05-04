class Sale:
    def __init__(self, vehicle_id, customer_id, price,
                 id=None, date=None,
                 is_financed=False, down_payment=0,
                 loan_tenure=None, interest_rate=None,
                 monthly_emi=None):
        self.id            = id
        self.vehicle_id    = vehicle_id
        self.customer_id   = customer_id
        self.price         = price
        self.date          = date
        # Financing fields
        self.is_financed   = is_financed
        self.down_payment  = down_payment
        self.loan_tenure   = loan_tenure      # in months
        self.interest_rate = interest_rate    # annual rate as decimal e.g. 0.10
        self.monthly_emi   = monthly_emi