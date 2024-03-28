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
from config import debug


# Parameters
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


# The saturation vapor pressure over liquid water
def __pvstarl(T):
    return ptrip * (T/Ttrip)**((cpv-cvl)/rgasv) * \
        exp( (E0v - (cvv-cvl)*Ttrip) / rgasv * (1/Ttrip - 1/T) )

# The saturation vapor pressure over solid ice
def __pvstars(T):
    return ptrip * (T/Ttrip)**((cpv-cvs)/rgasv) * \
        exp( (E0v + E0s - (cvv-cvs)*Ttrip) / rgasv * (1/Ttrip - 1/T) )


def lcl(p,T,rh=None,rhl=None,rhs=None,return_ldl=False,return_min_lcl_ldl=False) -> float:
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
        pv = rh * __pvstarl(T) if T > Ttrip else rh * __pvstars(T)
        rhl = pv / __pvstarl(T)
        rhs = pv / __pvstars(T)
    elif rhl is not None:
        pv = rhl * __pvstarl(T)
        rhs = pv / __pvstars(T)
        rh = rhl if T > Ttrip else rhs
    elif rhs is not None:
        pv = rhs * __pvstars(T)
        rhl = pv / __pvstarl(T)
        rh = rhl if T > Ttrip else rhs

    if pv > p:
        debug('Error in lcl: pv greater than p')
        return -2

    qv = rgasa * pv / (rgasv * p + (rgasa - rgasv) * pv)
    rgasm = (1 - qv) * rgasa + qv * rgasv
    cpm = (1 - qv) * cpa + qv * cpv
    if rh == 0:
        return cpm * T / ggr

    aL = -(cpv - cvl) / rgasv + cpm / rgasm
    bL = -(E0v - (cvv - cvl) * Ttrip) / (rgasv * T)
    cL = pv / __pvstarl(T) * exp(-(E0v - (cvv - cvl) * Ttrip) / (rgasv * T))
    aS = -(cpv - cvs) / rgasv + cpm / rgasm
    bS = -(E0v + E0s - (cvv - cvs) * Ttrip) / (rgasv * T)
    cS = pv / __pvstars(T) * exp(-(E0v + E0s - (cvv - cvs) * Ttrip) / (rgasv * T))
    
    lcl = cpm * T / ggr * (1 - bL / (aL * lambertw(bL / aL * cL ** (1 / aL), -1).real))
    ldl = cpm * T / ggr * (1 - bS / (aS * lambertw(bS / aS * cS ** (1 / aS), -1).real))

    if return_ldl:
        return ldl
    elif return_min_lcl_ldl:
        return min(lcl, ldl)
    
    return lcl


def __within_bound() -> bool:
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
    debug("Error range differences: ")
    debug(f"{abs(lcl(1e5,300,rhl=.5,return_ldl=False) - 1433.844139279):0,.13f}")
    debug(f"{abs(lcl(1e5,300,rhs=.5,return_ldl=False) - 923.2222457185):0,.13f}")
    debug(f"{abs(lcl(1e5,200,rhl=.5,return_ldl=False) - 542.8017712435):0,.13f}")
    debug(f"{abs(lcl(1e5,200,rhs=.5,return_ldl=False) - 1061.585301941):0,.13f}")
    debug(f"{abs(lcl(1e5,300,rhl=.5,return_ldl=True ) - 1639.249726127):0,.13f}")
    debug(f"{abs(lcl(1e5,300,rhs=.5,return_ldl=True ) - 1217.336637217):0,.13f}")
    debug(f"{abs(lcl(1e5,200,rhl=.5,return_ldl=True ) - -8.609834216556):0,.13f}")
    debug(f"{abs(lcl(1e5,200,rhs=.5,return_ldl=True ) - 508.6366558898):0,.13f}")



if __name__ == "__main__":
    __within_bound()
    # __error_ranges()
    # height = lcl(p=99800, T=280.15, rh=0.71)
    # print("LCL Height:", height, "meters")