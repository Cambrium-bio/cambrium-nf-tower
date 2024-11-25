import jaydebeapi
import os

class DatabaseConnection:
    def __init__(self):
        # H2 JDBC connection parameters matching application-livedev.yml
        self.jdbc_driver = 'org.h2.Driver'
        self.jdbc_url = 'jdbc:h2:file:./.db/h2/tower'  # Updated to match yml file
        self.user = 'sa'
        self.password = ''
        self.conn = None

    def connect(self):
        """Establish connection to H2 database"""
        try:
            # Look for H2 JAR in the backend build directory
            jar_path = '../tower-backend/build/libs/h2-*.jar'  # Common location in Gradle builds
            
            self.conn = jaydebeapi.connect(
                self.jdbc_driver,
                self.jdbc_url,
                [self.user, self.password],
                jar_path
            )
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            print("Hint: H2 JAR should be in tower-backend/build/libs/")
            return False

    def disconnect(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall() if cursor.description else None
            cursor.close()
            return results
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def execute_update(self, query, params=None):
        """Execute an update query (INSERT, UPDATE, DELETE)"""
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Exception as e:
            print(f"Error executing update: {e}")
            self.conn.rollback()
            return -1

# Example usage:
def get_db():
    """Get a database connection instance"""
    db = DatabaseConnection()
    if db.connect():
        return db
    return None
