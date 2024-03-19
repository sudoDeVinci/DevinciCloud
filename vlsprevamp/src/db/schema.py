import mysql.connector as mysql
from analysis.config import debug



def apply(mydb:mysql.MySQLConnection):
    myCursor = mydb.cursor()
    # Create the cook book database 
    myCursor.execute("CREATE DATABASE IF NOT EXISTS weather")

    # Select the database
    myCursor.execute("USE weather")

    # Create the named device table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Devices(
            MAC VARCHAR(25) PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            device_model VARCHAR(10) NOT NULL,
            camera_model VARCHAR(10) NOT NULL,
            altitude FLOAT(10) NOT NULL,
            latitude FLOAT(10) NOT NULL,
            longitude FLOAT(10) NOT NULL
        );
    """)

    # Create readings table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Readings(
        timestamp DATETIME,
        MAC VARCHAR(20),
        temperature FLOAT(10),
        relative_humidity FLOAT(10),
        pressure FLOAT(10),
        dewpoint FLOAT(10),
        filepath VARCHAR(100),
        PRIMARY KEY (MAC, timestamp),
        FOREIGN KEY (MAC) REFERENCES Devices(MAC)
    );
""")
                    
    # Create status table
    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Status(
            MAC VARCHAR(20) PRIMARY KEY,
            SHT BOOLEAN NOT NULL,
            BMP BOOLEAN NOT NULL,
            CAM BOOLEAN NOT NULL,
            WIFI BOOLEAN NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (MAC) REFERENCES Devices(MAC)
        );
    """)

    myCursor.execute("""
        CREATE TABLE IF NOT EXISTS Locations(
            country VARCHAR(30),
            region VARCHAR(30),
            city VARCHAR(30),
            latitude FLOAT(10) NOT NULL,
            longitude FLOAT(10) NOT NULL,
            PRIMARY KEY (latitude, longitude)
        );
    """)


    # Commit
    mydb.commit()
