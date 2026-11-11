
from sqlalchemy import text
from app.database import engine

try:
    # Establish connection to PostgreSQL
    with engine.connect() as connection:

        # Execute a test query
        result = connection.execute(text("SELECT version()"))

        print("Database connected successfully!")

        # Display PostgreSQL version
        print(result.scalar())

except Exception as e:
    print("Database connection failed:")
    print(e)
