import mysql.connector as mysql
from db.Entities import *
from db.Management import Manager
from analysis.config import debug
from abc import ABC
from analysis.config import *


class Service(ABC):
    @staticmethod
    def get_all() -> List[Entity]:
        pass

    @staticmethod
    def get(MAC:str, *args) -> List[Entity]:
        pass

    @staticmethod
    def add(PK:str, *args) -> None:
        pass

    @staticmethod
    def update(PK:str, *args) -> None:
        pass

    @staticmethod
    def delete(PK:str, *args) -> None:
        pass

    @staticmethod
    def exists(PK:str) -> bool:
        pass


class DeviceService(Service):
    @staticmethod
    def get_all() -> List[DeviceEntity]:
        query_string = "SELECT * FROM Devices;"
        devices = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                device = DeviceEntity(
                    row["MAC"],
                    row["name"],
                    row["device_model"],
                    row["camera_model"],
                    row["altitude"],
                    row["latitude"],
                    row["longitude"]
                )
                devices.append(device)

        except mysql.Error as e:
            debug(f"Couldn't fetch device list -> {e}")

        finally:
            if cursor: cursor.close()

        return devices

    @staticmethod
    def get(MAC:str) -> DeviceEntity | None:
        query_string = "SELECT * FROM Devices WHERE MAC=%s LIMIT 1;"
        device = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))
            row = cursor.fetchone()
            if row:
                device = DeviceEntity(
                    row["MAC"],
                    row["name"],
                    row["device_model"],
                    row["camera_model"],
                    row["altitude"],
                    row["latitude"],
                    row["longitude"],
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch device list -> {e}")

        finally:
            if cursor: cursor.close()

        return device

    @staticmethod
    def add(MAC, name, dev_model, cam_model, altitude, latitude, longitude) -> None:
        conn = Manager.get_conn()

        # Insert records into the database.
        insert_string = "INSERT INTO Devices VALUES(%s, %s, %s, %s, %s, %s, %s);"

        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, name, dev_model, cam_model, altitude, latitude, longitude)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert device record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, name:str) -> None:
        conn = Manager.get_conn()
        update_string = "UPDATE Devices SET name=%s WHERE MAC=%s;";
        try:
            cursor = conn.cursor()
            cursor.execute(update_string, (name, MAC))
            conn.commit()
            #debug("Updated database record!")
        except mysql.Error as e:
            print(f"Couldn't update device name -> {e}")

        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def exists(MAC:str) -> bool:
        query_string = "SELECT * FROM Devices WHERE MAC=%s LIMIT 1;"

        # If no device is retrieved, return False.
        device:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))
            device = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't check for existence of device record -> {e}")
            return False

        finally:
            if cursor: cursor.close()

        return device


class ReadingService(Service):
    @staticmethod
    def get_all() -> List[ReadingEntity]:
        query_string = "SELECT * FROM Readings;"
        readings = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                reading = ReadingEntity(
                    row["MAC"],
                    row["temperature"],
                    row["relative_humidity"],
                    row["pressure"],
                    row["dewpoint"],
                    row["timestamp"],
                    row["filepath"]
                )
                readings.append(reading)

        except mysql.Error as e:
            debug(f"Couldn't fetch reading data list -> {e}")

        finally:
            if cursor: cursor.close()

        return readings

    @staticmethod
    def get(MAC:str, timetsamp:str) -> ReadingEntity | None:
        query_string = "SELECT * FROM Readings WHERE timestamp=%s AND MAC=%s LIMIT 1;"
        reading = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (timestamp, MAC)
            )

            row = cursor.fetchone()
            if row:
                reading = ReadingEntity(
                    row["MAC"],
                    row["temperature"],
                    row["relative_humidity"],
                    row["pressure"],
                    row["dewpoint"],
                    row["timestamp"],
                    row["filepath"]
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return reading

    @staticmethod
    def add(MAC:str, temp:float, hum:float, pres:float, dew:float, timestamp:str, filepath:str = "") -> None:
        conn = Manager.get_conn()
        insert_string = "INSERT INTO Readings VALUES(%s, %s, %s, %s, %s, %s, %s);"
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (timestamp, MAC, temp, hum, pres, dew, filepath)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert sensor reading record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update_path(MAC:str, timestamp:str, filepath:str):
        conn = Manager.get_conn()
        update_string = "UPDATE Readings SET filepath=%s WHERE MAC=%s AND timestamp=%s;"

        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (filepath, MAC, timestamp)
            )

            conn.commit()
        
        except mysql.Error as e:
            debug(f"Couldn't update sensor reading record -> {e}")

        finally:
            if cursor: cursor.close()
    
    @staticmethod
    def update_readings(MAC:str, temp:float, hum:float, pres:float, dew:float, timestamp:str):
        conn = Manager.get_conn()
        update_string = "UPDATE Readings SET temperature=%s, relative_humidity=%s,pressure=%s,dewpoint=%s WHERE MAC=%s AND timestamp=%s;"

        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (temp, hum, pres, dew, MAC, timestamp)
            )

            conn.commit()
        
        except mysql.Error as e:
            debug(f"Couldn't update sensor reading record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def exists(MAC:str, timestamp:str) -> bool:
        query_string = "SELECT * FROM Readings WHERE timestamp=%s AND MAC=%s LIMIT 1;"
        reading:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (timestamp, MAC)
            )

            reading = cursor.fetchone() is not None
            
        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return reading


class StatusService(Service):
    @staticmethod
    def get_all() -> List[SensorEntity]:
        query_string = "SELECT * FROM Status;"
        statuses = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                status = SensorEntity(
                    row["MAC"],
                    row["timestamp"],
                    row["SHT"],
                    row["BMP"],
                    row["CAM"],
                    row["WIFI"]
                )
                statuses.append(status)

        except mysql.Error as e:
            debug(f"Couldn't fetch sensor status records list -> {e}")

        finally:
            if cursor: cursor.close()

        return status

    @staticmethod
    def get(MAC:str) -> SensorEntity | None:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        status = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC, ))

            row = cursor.fetchone()
            if row:
                status = SensorEntity(
                    row["MAC"],
                    row["timestamp"],
                    row["SHT"],
                    row["BMP"],
                    row["CAM"],
                    row["WIFI"]
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch reading records list -> {e}")

        finally:
            if cursor: cursor.close()

        return status

    @staticmethod
    def add(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool = True) -> None:
        conn = Manager.get_conn()
        insert_string = "INSERT INTO Status VALUES(%s, %s, %s, %s, %s, %s);"
        try:
            cursor = conn.cursor()
            cursor.execute(
                insert_string, (MAC, sht, bmp, cam, wifi, timestamp)
            )

            conn.commit()

        except mysql.Error as e:
            debug(f"Couldn't insert sensor status record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def update(MAC:str, timestamp:str, sht:bool, bmp:bool, cam:bool, wifi:bool = True) -> None:
        conn = Manager.get_conn()
        update_string = "UPDATE Status SET SHT=%s, BMP=%s, CAM=%s, WIFI=%s, timestamp=%s WHERE MAC=%s;"

        try:
            cursor = conn.cursor()
            cursor.execute(
                update_string, (sht, bmp, cam, wifi, timestamp, MAC)
            )

            conn.commit()
        
        except mysql.Error as e:
            debug(f"Couldn't update sensor status record -> {e}")

        finally:
            if cursor: cursor.close()

    @staticmethod
    def exists(MAC:str) -> bool:
        query_string = "SELECT * FROM Status WHERE MAC=%s LIMIT 1;"
        stats:bool = False

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string, (MAC,))

            stats = cursor.fetchone() is not None
            
        except mysql.Error as e:
            debug(f"Couldn't fetch sensor status records list -> {e}")

        finally:
            if cursor: cursor.close()

        return stats


class LocationService(Service):
    @staticmethod
    def country_exists(region:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE country=%s;"
        location = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (region, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch country location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location

    @staticmethod
    def region_exists(region:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE region=%s;"
        location = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (region, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch region location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location


    @staticmethod
    def city_exists(city:str) -> bool:
        query_string = "SELECT * FROM Locations WHERE city=%s;"
        location = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (city, )
            )

            location = cursor.fetchone() is not None

        except mysql.Error as e:
            debug(f"Couldn't fetch city location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location

    @staticmethod
    def exists(latitude:float, longitude:float) -> bool:
        query_string = "SELECT * FROM Locations WHERE latitude=%s AND longitude=%s LIMIT 1;"
        location = None
        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (latitude, longitude)
            )

            row = cursor.fetchone() is not None
        
        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location
        

    @staticmethod
    def get_all() -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations;"
        locs = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(query_string)

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs

    def get(latitude:float, longitude:float) -> LocationEntity:
        query_string = "SELECT * FROM Locations WHERE latitude=%s AND longitude=%s LIMIT 1;"
        location = None

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (latitude, longitude)
            )

            row = cursor.fetchone()
            if row:
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    row["city"],
                    latitude,
                    longitude
                )

        except mysql.Error as e:
            debug(f"Couldn't fetch location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return location
    
    def get_city(city:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE city=%s;"
        location = None
        locs = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (city, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    row["region"],
                    city,
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch city location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs
        
    def get_region(region:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE region=%s;"
        location = None
        locs = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (region, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    row["country"],
                    region,
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch region location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs

    def get_country(country:str) -> List[LocationEntity]:
        query_string = "SELECT * FROM Locations WHERE country=%s;"
        location = None
        locs = []

        try:
            cursor = Manager.get_conn().cursor(dictionary=True)
            cursor.execute(
                query_string, (country, )
            )

            for row in cursor.fetchall():
                location = LocationEntity(
                    country,
                    row["region"],
                    row["city"],
                    row["latitude"],
                    row["longitude"]
                )
                locs.append(location)

        except mysql.Error as e:
            debug(f"Couldn't fetch country location records list -> {e}")

        finally:
            if cursor: cursor.close()

        return locs
    
