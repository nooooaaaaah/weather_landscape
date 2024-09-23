from math import cos, sin, acos, asin, tan
from math import degrees as deg, radians as rad
from datetime import date, datetime, time, timedelta
import logging
from typing import Optional

class sun:
    """
    Calculate sunrise and sunset based on equations from NOAA
    http://www.srrb.noaa.gov/highlights/sunrise/calcdetails.html

    typical use, calculating the sunrise at the present day:

    import datetime
    import sunrise
    s = sun(lat=49,long=3)
    print('sunrise at ',s.sunrise(when=datetime.datetime.now())
    """
    def __init__(self, lat: float = 50.4546600, long: float = 30.5238000):  # default Kyiv
        self.lat: float = lat
        self.long: float = long
        self.tzoffset: float = (datetime.now() - datetime.utcnow()).total_seconds() / (60 * 60)

    def sunrise(self, when: Optional[datetime] = None) -> datetime:
        """
        return the time of sunrise as a datetime.time object
        when is a datetime.datetime object. If none is given
        a local time zone is assumed (including daylight saving
        if present)
        """
        if when is None: when = datetime.now()
        self.__preptime(when)
        self.__calc()
        result = sun.__timefromdecimalday(self.sunrise_t, when)
        logging.debug(f"Sunrise calculation - Input: {when}, Result: {result}")
        return result

    def sunset(self, when: Optional[datetime] = None) -> datetime:
        if when is None: when = datetime.now()
        self.__preptime(when)
        self.__calc()
        result = sun.__timefromdecimalday(self.sunset_t, when)
        logging.debug(f"Sunset calculation - Input: {when}, Result: {result}")
        return result

    def solarnoon(self, when: Optional[datetime] = None) -> datetime:
        if when is None: when = datetime.now()
        self.__preptime(when)
        self.__calc()
        result = sun.__timefromdecimalday(self.solarnoon_t, when)
        logging.debug(f"Solar noon calculation - Input: {when}, Result: {result}")
        return result

    @staticmethod
    def __timefromdecimalday(d: float, when: datetime) -> datetime:
        hours = 24.0 * d
        days, hours = divmod(hours, 24)
        h = int(hours)
        minutes = (hours - h) * 60
        m = int(minutes)
        seconds = (minutes - m) * 60
        s = int(seconds)

        # Add debugging output
        logging.debug(f"Original d: {d}, hours: {hours}, h: {h}, m: {m}, s: {s}")

        when += timedelta(days=int(days))

        # Ensure h is within 0-23 range
        h = h % 24

        logging.debug(f"Adjusted when: {when}, h: {h}, m: {m}, s: {s}")

        return datetime(when.year, when.month, when.day, h, m, s)

    def __preptime(self, when: datetime) -> None:
        """
        Extract information in a suitable format from when,
        a datetime.datetime object.
        """
        # datetime days are numbered in the Gregorian calendar
        # while the calculations from NOAA are distibuted as
        # OpenOffice spreadsheets with days numbered from
        # 1/1/1900. The difference are those numbers taken for
        # 18/12/2010
        self.day: int = when.toordinal() - (734124 - 40529)
        t = when.time()
        self.time: float = (t.hour + t.minute / 60.0 + t.second / 3600.0) / 24.0

        self.timezone: float = self.tzoffset

    def __calc(self) -> None:
        """
        Perform the actual calculations for sunrise, sunset and
        a number of related quantities.

        The results are stored in the instance variables
        sunrise_t, sunset_t and solarnoon_t
        """
        timezone: float = self.timezone  # in hours, east is positive
        longitude: float = self.long  # in decimal degrees, east is positive
        latitude: float = self.lat  # in decimal degrees, north is positive

        time: float = self.time  # percentage past midnight, i.e. noon  is 0.5
        day: int = self.day  # daynumber 1=1/1/1900

        Jday: float = day + 2415018.5 + time - timezone / 24  # Julian day
        Jcent: float = (Jday - 2451545) / 36525  # Julian century

        Manom: float = 357.52911 + Jcent * (35999.05029 - 0.0001537 * Jcent)
        Mlong: float = 280.46646 + Jcent * (36000.76983 + Jcent * 0.0003032) % 360
        Eccent: float = 0.016708634 - Jcent * (0.000042037 + 0.0001537 * Jcent)
        Mobliq: float = 23 + (26 + ((21.448 - Jcent * (46.815 + Jcent * (0.00059 - Jcent * 0.001813)))) / 60) / 60
        obliq: float = Mobliq + 0.00256 * cos(rad(125.04 - 1934.136 * Jcent))
        vary: float = tan(rad(obliq / 2)) * tan(rad(obliq / 2))
        Seqcent: float = sin(rad(Manom)) * (1.914602 - Jcent * (0.004817 + 0.000014 * Jcent)) + sin(rad(2 * Manom)) * (
                    0.019993 - 0.000101 * Jcent) + sin(rad(3 * Manom)) * 0.000289
        Struelong: float = Mlong + Seqcent
        Sapplong: float = Struelong - 0.00569 - 0.00478 * sin(rad(125.04 - 1934.136 * Jcent))
        declination: float = deg(asin(sin(rad(obliq)) * sin(rad(Sapplong))))

        eqtime: float = 4 * deg(vary * sin(2 * rad(Mlong)) - 2 * Eccent * sin(rad(Manom)) + 4 * Eccent * vary * sin(
            rad(Manom)) * cos(2 * rad(Mlong)) - 0.5 * vary * vary * sin(4 * rad(Mlong)) - 1.25 * Eccent * Eccent * sin(
            2 * rad(Manom)))

        hourangle: float = deg(acos(cos(rad(90.833)) / (cos(rad(latitude)) * cos(rad(declination))) - tan(rad(latitude)) * tan(
            rad(declination))))

        self.solarnoon_t: float = (720 - 4 * longitude - eqtime + timezone * 60) / 1440
        self.sunrise_t: float = self.solarnoon_t - hourangle * 4 / 1440
        self.sunset_t: float = self.solarnoon_t + hourangle * 4 / 1440
