class Employee:
    def __init__(self, name, role, salary):
        self.name = name
        self.role = role  # Admin / Sales / Technician
        self.salary = salary
        self.performance_score = 0

    def update_performance(self, score):
        self.performance_score += score

    def get_details(self):
        return f"{self.name} ({self.role}) - Score: {self.performance_score}"