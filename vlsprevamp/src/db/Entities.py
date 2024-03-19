from abc import ABC, abstractmethod

class Entity(ABC):
    """
    Abstract Parent class representing a given row in a db table, either devices, sensors or readings. 
    """
    __MAC:str
    __timestamp:str

    def __init__(self):
        pass

    def __init__(self, mac:str, stamp:str):
        self.__MAC = mac
        self.__timestamp = stamp
    
    def get_mac(self) -> str:
        return self.__MAC
    
    def get_timetstamp(self) -> str:
        return self.__timestamp


class DeviceEntity(Entity):
    """
    Row of data in the Devices table.
    """
    __name:str
    __dev_model:str
    __cam_model:str
    __altitude:float
    __latitude:float
    __longitude:float

    def __init__(self, mac:str, name:str, devmodel:str, cammodel:str,
                 alt:float, lat:float, long:float, timestamp:str = None):
        Entity.__init__(self, mac, timestamp)
        self.__name = name
        self.__dev_model = devmodel
        self.__cam_model = cammodel
        self.__altitude = alt
        self.__latitude = lat
        self.__longitude = long

    def get_name(self) -> str:
        return self.__name
    
    def get_longitude(self) -> float:
        return self.__longitude
    
    def get_latitude(self) -> float:
        return self.__latitude
    
    def get_altitude(self) -> float:
        return self.__altitude
    
    def get_dev_model(self) -> str:
        return self.__dev_model
    
    def get_cam_model(self) -> str:
        return self.__cam_model
    
    def set_name(self, n:str) -> None:
        self.__name = n


class ReadingEntity(Entity):
    """
    Row of data in the Reading table.
    """
    __temperature:float
    __humidity:float
    __pressure:float
    __dewpoint:float
    __image_path:str

    def __init__(self, mac:str, temp:float, humidity:float, pressure:float,
                dewpoint:float, timestamp:str, path:str = None):
        Entity.__init__(self, mac, timestamp)
        self.__dewpoint = dewpoint
        self.__humidity = humidity
        self.__image_path = path
        self.__pressure = pressure
        self.__temperature = temp
    
    def get_dewpoint(self) -> float:
        return self.__dewpoint
    
    def get_humidity(self) -> float:
        return self.__humidity
    
    def get_pressure(self) -> float:
        return self.__pressure
    
    def get_temperature(self) -> float:
        return self.__temperature
    
    def get_image_path(self) -> str:
        return self.__image_path
    
    def set_image_path(self, path:str) -> None:
        self.__image_path = path


class SensorEntity(Entity):
    """
    Row of data in the senors table.
    """
    __sht:bool
    __bmp:bool
    __cam:bool
    __wifi:bool

    def __init__(self, mac:str, timestamp:str, sht_stat:bool, bmp_stat:bool, cam_stat:bool, wifi_stat:bool = None):
        Entity.__init__(self, mac, timestamp)
        self.__bmp = bmp_stat
        self.__cam = cam_stat
        self.__sht = sht_stat
        self.__wifi = wifi_stat
    
    def get_sht(self) -> bool:
        return self.__sht
    
    def get_bmp(self) -> bool:
        return self.__bmp
    
    def get_cam(self) -> bool:
        return self.__cam
    
    def get_wifi(self) -> bool:
        return self.__wifi
    
    def set_sht(self, x:bool) -> None:
        self.__sht = x
    
    def set_bmp(self, x:bool) -> None:
        self.__bmp = x

    def set_cam(self, x:bool) -> None:
        self.__cam = x

    def set_wifi(self, x:bool) -> None:
        self.__wifi = x
    
    def allUp(self) -> bool:
        return (self.__sht and self.__bmp and self.__cam)

class LocationEntity():
    """
    Row of data in the locations table.
    """
    __country:str
    __region:str
    __city:str
    __latitude:float
    __longitude:float

    def __init__(self, country:str, region:str, city:str, lat:float, lon:float):
        self.__country = country
        self.__region = region
        self.__city = city
        self.__latitude = lat
        self.__longitude = lon

    def get_country(self) -> str:
        return self.__country

    def get_region(self) -> str:
        return self.__region

    def get_city(self) -> str:
        return self.__city

    def get_latitude(self) -> float:
        return self.__latitude

    def get_longitude(self) -> float:
        return self.__longitude
