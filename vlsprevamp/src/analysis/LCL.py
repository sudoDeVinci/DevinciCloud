"""
Version 1.0 released by David Romps on September 12, 2017.
Version 1.1 vectorized lcl.R, released on May 24, 2021.

Code from: https://romps.berkeley.edu/papers/pubs-2016-lcl.html

@article{16lcl,
   Title   = {Exact expression for the lifting condensation level},
   Author  = {David M. Romps},
   Journal = {Journal of the Atmospheric Sciences},
   Year    = {2017},
   Month   = dec,
   Number  = {12},
   Pages   = {3891--3900},
   Volume  = {74}
}
"""

from math import exp
from scipy.special import lambertw
from src.config import debug, dispatch
from src.db.Entities import ReadingEntity

class Measurement:
    """
    A Singular timestamped set of Environmental Measurements.
    """
    # Environmental Reading Values
    HUMIDITY: float     # Rel Humidity percentagee, 0-1
    TEMPERATURE: float  # Temperature in Celsius
    DEWPOINT: float     # Dewpoint in Celsius
    PRESSURE: float     # Pressure in Pa
    ALTITUDE: float     # Altitude from Seal level in Metres
    QNH: float          # Pressure at Sea Level in Pa
    TIMESTAMP: str      # Formaatted UTC ISO Timestamp

    # Universal Natural Constants
    Ttrip = 273.16          # K -------> Triple point temp of water
    ptrip = 611.65          # Pa ------> Triple point pressure of water vapour
    E0v   = 2.3740e6        # J/kg ----> Latent heat of vaporization of water
    E0s   = 0.3337e6        # J/kg ----> Latent heat of sublimation of ice
    ggr   = 9.80665         # m/s^2 ---> Acceleration due to gravity
    rgasa = 287.04          # J/kg/K --> Specific gas constant for dry air
    rgasv = 461             # J/kg/K --> Specific gas constant for water vapor
    cva   = 719             # J/kg/K --> Specific heat capacity of dry air at constant volume
    cvv   = 1418            # J/kg/K --> Specific heat capacity of water vapor at constant volume
    cvl   = 4119            # J/kg/K --> Specific heat capacity of liquid water at constant volume
    cvs   = 1861            # J/kg/K --> Specific heat capacity of solid ice at constant volume
    cpa   = cva + rgasa     # J/kg/K --> Specific heat capacity of dry air at constant pressure 
    cpv   = cvv + rgasv     # J/kg/K --> Specific heat capacity of water vapor at constant pressure

    @dispatch(float, float, float)
    def __init__(self, temp: float, hum: float, pressure: float) -> None:
        self.TEMPERATURE = temp
        self.HUMIDITY = hum
        self.PRESSURE = pressure


    @dispatch(float, float, float, float, float, float)
    def __init__(self, temp: float, hum: float, pressure: float,
                dewpoint: float, timestamp: str, altitude: float = None,
                qnh:float = None) -> None:
        self.ALTITUDE = altitude
        self.DEWPOINT = dewpoint
        self.TEMPERATURE = temp
        self.HUMIDITY = hum
        self.QNH = qnh
        self.PRESSURE = pressure
        self.TIMESTAMP = timestamp

    @dispatch(ReadingEntity)
    def __init__(self, reading: ReadingEntity) -> None:
        self.HUMIDITY = reading.get_humidity()
        self.PRESSURE = reading.get_pressure()
        self.DEWPOINT = reading.get_dewpoint()
        self.TEMPERATURE = reading.get_temperature()
        self.TIMESTAMP = reading.get_timestamp()


    @dispatch(ReadingEntity, float)
    def __init__(self, reading: ReadingEntity, altitude: float) -> None: 
        self.ALTITUDE = altitude
        self.__init__(reading)


    # The saturation vapor pressure over liquid water
    def __pvstarl(self, T: float) -> float:
        return self.ptrip * (T/self.Ttrip)**((self.cpv-self.cvl)/self.rgasv) * \
            exp( (self.E0v - (self.cvv-self.cvl)*self.Ttrip) / self.rgasv * (1/self.Ttrip - 1/T) )

    # The saturation vapor pressure over solid ice
    def __pvstars(self, T: float) -> float:
        return self.ptrip * (T/self.Ttrip)**((self.cpv-self.cvs)/self.rgasv) * \
            exp( (self.E0v + self.E0s - (self.cvv-self.cvs)*self.Ttrip) / self.rgasv * (1/self.Ttrip - 1/T) )


    def __lcl(self, p:float, T:float, rh:float = None, rhl:float=None,
              rhs: float = None, return_ldl: bool = False, return_min_lcl_ldl: bool = False) -> float:
        """
        This lcl function returns the height of the lifting condensation level
        (LCL) in meters.  The inputs are:
        - p in Pascals
        - T in Kelvins
        - Exactly one of rh, rhl, and rhs (dimensionless, from 0 to 1):
            * The value of rh is interpreted to be the relative humidity with respect to liquid water if T >= 273.15 K and with respect to ice if T < 273.15 K. 
            * The value of rhl is interpreted to be the relative humidity with respect to liquid water
            * The value of rhs is interpreted to be the relative humidity with respect to ice
        - return_ldl is an optional logical flag.  If true, the lifting deposition level (LDL) is returned instead of the LCL. 
        - return_min_lcl_ldl is an optional logical flag.  If true, the minimum of the LCL and LDL is returned.
        """

        if return_ldl and return_min_lcl_ldl:
            debug('return_ldl and return_min_lcl_ldl cannot both be true')

        if (rh is None) and (rhl is None) and (rhs is None):
            debug('Error in lcl: Exactly one of rh, rhl, and rhs must be specified')
            return -1

        if rh is not None:
            pv = rh * self.__pvstarl(T) if T > self.Ttrip else rh * self.__pvstars(T)
            rhl = pv / self.__pvstarl(T)
            rhs = pv / self.__pvstars(T)
        elif rhl is not None:
            pv = rhl * self.__pvstarl(T)
            rhs = pv / self.__pvstars(T)
            rh = rhl if T > self.Ttrip else rhs
        elif rhs is not None:
            pv = rhs * self.__pvstars(T)
            rhl = pv / self.__pvstarl(T)
            rh = rhl if T > self.Ttrip else rhs

        if pv > p:
            debug('Error in lcl: pv greater than p')
            return -2

        qv = self.rgasa * pv / (self.rgasv * p + (self.rgasa - self.rgasv) * pv)
        rgasm = (1 - qv) * self.rgasa + qv * self.rgasv
        cpm = (1 - qv) * self.cpa + qv * self.cpv
        if rh == 0:
            return cpm * T / self.ggr

        aL = -(self.cpv - self.cvl) / self.rgasv + cpm / rgasm
        bL = -(self.E0v - (self.cvv - self.cvl) * self.Ttrip) / (self.rgasv * T)
        cL = pv / self.__pvstarl(T) * exp(-(self.E0v - (self.cvv - self.cvl) * self.Ttrip) / (self.rgasv * T))
        aS = -(self.cpv - self.cvs) / self.rgasv + cpm / rgasm
        bS = -(self.E0v + self.E0s - (self.cvv - self.cvs) * self.Ttrip) / (self.rgasv * T)
        cS = pv / self.__pvstars(T) * exp(-(self.E0v + self.E0s - (self.cvv - self.cvs) * self.Ttrip) / (self.rgasv * T))
        
        lcl = cpm * T / self.ggr * (1 - bL / (aL * lambertw(bL / aL * cL ** (1 / aL), -1).real))
        ldl = cpm * T / self.ggr * (1 - bS / (aS * lambertw(bS / aS * cS ** (1 / aS), -1).real))

        if return_ldl:
            return ldl
        elif return_min_lcl_ldl:
            return min(lcl, ldl)
        
        return lcl
    
    def lcl_feet(self):
        temp = self.TEMPERATURE + 273.15
        return self.__lcl(self.PRESSURE, temp, self.HUMIDITY) * 3.28084


    """
    def __within_bound() -> bool:
        
        Test that the results of calulations are within expected range for known readings.
        
        out = abs(lcl(1e5,300,rhl=.5,return_ldl=False)/( 1433.844139279)-1) < 1e-10 and \
        abs(lcl(1e5,300,rhs=.5,return_ldl=False)/( 923.2222457185)-1) < 1e-10 and \
        abs(lcl(1e5,200,rhl=.5,return_ldl=False)/( 542.8017712435)-1) < 1e-10 and \
        abs(lcl(1e5,200,rhs=.5,return_ldl=False)/( 1061.585301941)-1) < 1e-10 and \
        abs(lcl(1e5,300,rhl=.5,return_ldl=True )/( 1639.249726127)-1) < 1e-10 and \
        abs(lcl(1e5,300,rhs=.5,return_ldl=True )/( 1217.336637217)-1) < 1e-10 and \
        abs(lcl(1e5,200,rhl=.5,return_ldl=True )/(-8.609834216556)-1) < 1e-10 and \
        abs(lcl(1e5,200,rhs=.5,return_ldl=True )/( 508.6366558898)-1) < 1e-10
            
        if out: debug('Success') 
        else: debug("Failure")
        return out


    def __error_ranges() -> None:
        
        Test the error ranges for known measurements.
        
        debug("Error range differences: ")
        debug(f"{abs(lcl(1e5,300,rhl=.5,return_ldl=False) - 1433.844139279):0,.13f}")
        debug(f"{abs(lcl(1e5,300,rhs=.5,return_ldl=False) - 923.2222457185):0,.13f}")
        debug(f"{abs(lcl(1e5,200,rhl=.5,return_ldl=False) - 542.8017712435):0,.13f}")
        debug(f"{abs(lcl(1e5,200,rhs=.5,return_ldl=False) - 1061.585301941):0,.13f}")
        debug(f"{abs(lcl(1e5,300,rhl=.5,return_ldl=True ) - 1639.249726127):0,.13f}")
        debug(f"{abs(lcl(1e5,300,rhs=.5,return_ldl=True ) - 1217.336637217):0,.13f}")
        debug(f"{abs(lcl(1e5,200,rhl=.5,return_ldl=True ) - -8.609834216556):0,.13f}")
        debug(f"{abs(lcl(1e5,200,rhs=.5,return_ldl=True ) - 508.6366558898):0,.13f}")
    """


if __name__ == "__main__":
    """from matplotlib import pyplot as plt
    MEASUREMENTS = (
        (Measurement(3.0, 1.00, 99400.00), 500),
        (Measurement(3.0, 1.00, 99400.00), 400),
        (Measurement(3.0, 1.00, 99400.00), 500),
        (Measurement(3.0, 1.00, 99400.00), 500),
        (Measurement(3.0, 1.00, 99400.00), 500),
        (Measurement(4.0, 1.00, 99400.00), 600),
        (Measurement(4.0, 1.00, 99400.00), 600),
        (Measurement(4.0, 1.00, 99400.00), 700),
        (Measurement(5.0, 1.00, 99400.00), 600),
        (Measurement(4.0, 1.00, 99400.00), 700),
        (Measurement(5.0, 1.00, 99400.00), 700),
        (Measurement(6.0, 0.81, 100100.0), 2400),
        (Measurement(4.0, 0.93, 100100.0), 800),
        (Measurement(5.0, 0.87, 100100.0), 800),
        (Measurement(5.0, 0.93, 100100.0), 1300),
        (Measurement(5.0, 0.87, 100100.0), 2100),
        (Measurement(6.0, 0.81, 100100.0), 2300),
        (Measurement(5.0, 0.93, 100100.0), 2200),
        (Measurement(2.0, 1.00, 100300.0), 3300),   # 400
        (Measurement(4.0, 0.93, 100400.0), 5700),   # 500
        (Measurement(5.0, 0.93, 100300.0), 4400),   # 1200
        (Measurement(6.0, 0.87, 100300.0), 3700),   # 4900
        (Measurement(5.0, 0.87, 100400.0), 3300),   # 1500
        (Measurement(5.0, 0.87, 100400.0), 2300),   # 4800 and 600
        (Measurement(4.0, 0.93, 100300.0), 3300),   # 1100
        (Measurement(4.0, 0.93, 99500.0), 9800),    # None
        (Measurement(4.0, 0.93, 99500.0), 9800),    # None
        (Measurement(4.0, 0.87, 100000.0), 12_000), # 4300
        (Measurement(7.0, 0.71, 100100.0), 4100),   # 2600
        (Measurement(7.0, 0.76, 100200.0), 5900),   # 2100
        (Measurement(7.0, 0.76, 100200.0), 6200),   # 2400
        (Measurement(8.0, 0.71, 100200.0), 4500),    # 2400
        (Measurement(9.0, 0.66, 99400.0), 32808),
    )

    measures, actual = zip(*MEASUREMENTS)
    hum = tuple(m.HUMIDITY for m in measures)
    lcl = tuple(m.lcl_feet() for m in measures)
    fig, axes = plt.subplots(nrows=1, ncols=1)
    plt.scatter(hum, lcl, color = 'blue', label = 'LCL Calculated from METAR data')
    plt.scatter(hum, actual, color = 'red', label = 'Actual measurement from METAR data.')
    axes.set_xlabel("Actual observed height from METAR data.")
    axes.set_ylabel("LCL height from METAR readings")
    axes.legend(loc="upper left")
    plt.show()
"""

