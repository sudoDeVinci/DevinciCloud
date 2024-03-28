import requests
from src.config import *
from datetime import datetime, UTC
import json

class Airport(Enum):
    """
    Airport names and equivalent METAR callsign.
    """
    VAXJO = "ESMX"
    UNKNOWN = "UNKNOWN"

    @classmethod
    @functools.lru_cache(maxsize=None)
    def match(cls, airport:str):
        """
        Match input string to airport callsign.
        """
        airport = airport.upper()
        for _, port_sign in cls.__members__.items():
            if airport == port_sign.value.upper(): return port_sign
        return cls.UNKNOWN

class Locale(Enum):
    """
    Lanuguage Locales for requesting data.
    """
    Deutsch = "de-DE"
    English = "en-US"
    Español = "es-ES"
    Français = "fr-FR"
    Italiano = "it-IT"
    Nederlands = "nl-NL"
    Polski = "pl-PL"
    Português = "pt-PT"
    中文 = "zh-CN"
    

API_KEY = ""
AIRPORT = Airport.VAXJO
LOCALE = Locale.English
TIME = ""  # UTC ISO8661


def __utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0, tzinfo=None).isoformat()


def __query(archive:bool = False, api_key:str = API_KEY, version:float = 2.3,
                    language:Locale = Locale.English, airport:Airport = Airport.VAXJO,
                    timestamp:str=None, human_readable:bool = False) -> str:
   
    """
    Query constructor for METAR api.
    """

    URL = "https://api.metar-taf.com/metar-archive?" if archive else "https://api.metar-taf.com/metar?"
    key = f"api_key={api_key}"
    v = f"v={version}"
    locale = f"locale={language.value}"
    id = f"id={airport.value}"
    test = f"test={int(human_readable)}"
    time = f"date={timestamp}" if archive else f"time={timestamp}"

    URL += f"{key}&{v}&{locale}&{id}"
    if timestamp: URL += f"&{time}"    
    if human_readable: URL += f"&{test}"
    return URL


def get(query: str) -> Dict[str, Any] | None:
    """
    Send a query to METAR api and receive json reply.
    Return either json reply or None.
    """
    reply = requests.get(query)
    debug(reply.content)
    outjson = None

    try:
        outjson = json.loads(reply.content)
    except requests.exceptions.JSONDecodeError as e:
        debug(e)
        outjson = None
    except json.decoder.JSONDecodeError as e:
        debug(e)
        outjson = None
    
    return outjson


def write(data: str | Dict, path: str) -> None:
    try:
        out = json.dumps(data)
        with open(path, "w") as f:
            f.write(out)
    except Exception as e:
        debug(f"Error writing to JSON file: {e}")

if __name__ == "__main__":
    query = __query(archive=True, api_key='', timestamp='2023-08-10')
    debug(query)
    data = get(query)
    write(data, "test.json")