from config.db_config import DBConnection

class AuthService:

    def login(self, username, password):
        db = DBConnection()
        try:
            query = "SELECT id, role FROM users WHERE username=%s AND password=%s"
            result = db.fetch(query, (username, password))
            return result[0] if result else None
        finally:
            db.close()