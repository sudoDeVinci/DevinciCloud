from analysis.config import *
import mysql.connector as mysql
from db.schema import apply
import toml

class Manager:
    """
    Static Database Manager.
    """
    __conn:mysql.MySQLConnection = None
    __config_path:str = "db_cfg.toml"

    @staticmethod
    def get_conn():
        """
        Get database connection object to write to local db.
        """
        return Manager.__conn
    

    @staticmethod
    def get_config_path() -> str:
        """
        Get the config path for the Database connection.
        """
        return Manager.__config_path


    @staticmethod
    def connect(drop_schema:bool) -> None:
        """
        Connect to database specified in the 
        """
        conf_dict = Manager.__load(Manager.__config_path)
        if conf_dict is None: raise RuntimeError(str(e) + " -> Couldn't read database config file.")

        username =  conf_dict['user']
        passw = conf_dict['pass']
        hostname = conf_dict['host']

        try:
            Manager.__conn = mysql.connect(
                user = username,
                password = passw,
                host = hostname)

            Manager.apply_schema(drop_schema)

            cursor = Manager.__conn.cursor()
            cursor.execute("USE weather")
            cursor.close()
            debug("successfully connected to the database")

        except mysql.Error as e:
            Manager.__conn = None
            raise RuntimeError(str(e) + " -> Couldn't connect to db 'weather'.")

    
    @staticmethod
    def __load(file_path:str) -> Dict | None:
        """
        Attempt to load the database config file.
        """
        toml_data = None
        try:
            with open(file_path, 'r') as file:
                toml_data = toml.load(file)
                if not toml_data: return None
        except FileNotFoundError:
            debug(f"Error: File '{file_path}' not found.")
            return None
        except toml.TomlDecodeError as e:
            debug(f"Error decoding TOML file: {e}")
            return None

        conf = toml_data.get('mysql', {})
        return {'host': conf.get('host'),
                'user': conf.get('user'),
                'port': conf.get('port'),
                'pass': conf.get('pass')}


    @staticmethod
    def apply_schema(should_drop_schema:bool):
        """
        Apply the schema to the Database.
        """
        exists = False

        try:
            cursor = Manager.__conn.cursor()
            cursor.execute("SHOW DATABASES LIKE 'weather'")
            result = cursor.fetchone()
            exists = result is not None
            cursor.close()
        except mysql.Error:
            raise RuntimeError("Couldn't run DB Query to find DB 'weather'.")

        if should_drop_schema and exists:
            try:
                cursor = Manager.__conn.cursor()
                cursor.execute("DROP DATABASE weather")
                cursor.close()
            except mysql.Error:
                raise RuntimeError("Couldn't drop DB 'weather'")

        if should_drop_schema or not exists:
            try:
                apply(Manager.__conn)
            except Exception as e:
                raise RuntimeError(str(e) + " -> Couldn't load schema for Database: 'weather.'")
