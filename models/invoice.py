class Invoice:
    def __init__(self, ref_id, type, amount, id=None):
        self.id = id
        self.ref_id = ref_id
        self.type = type
        self.amount = amount