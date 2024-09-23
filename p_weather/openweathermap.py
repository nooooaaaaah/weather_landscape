import os
import time
import json
import datetime
from typing import List, Tuple, Optional
from urllib.request import urlopen




class WeatherInfo():

    KTOC: float = 273.15

    Thunderstorm: int = 2
    Drizzle: int = 3
    Rain: int = 5
    Snow: int = 6
    Atmosphere: int = 7
    Clouds: int = 8

    FORECAST_PERIOD_HOURS: int = 3


    def __init__(self, fdata: dict) -> None:
        self.t: datetime.datetime = datetime.datetime.fromtimestamp(int(fdata['dt']))
        self.id: int = int(fdata['weather'][0]['id'])

        if ('clouds' in fdata) and ('all' in fdata['clouds']):
            self.clouds: int = int(fdata['clouds']['all'])
        else:
            self.clouds: int = 0

        if ('rain' in fdata) and ('3h' in fdata['rain']):
            self.rain: float = float(fdata['rain']['3h'])
        else:
            self.rain: float = 0.0

        if ('snow' in fdata) and ('3h' in fdata['snow']):
            self.snow: float = float(fdata['snow']['3h'])
        else:
            self.snow: float = 0.0

        if ('wind' in fdata) and ('speed' in fdata['wind']):
            self.windspeed: float = float(fdata['wind']['speed'])
        else:
            self.windspeed: float = 0.0

        if ('wind' in fdata) and ('deg' in fdata['wind']):
            self.winddeg: float = float(fdata['wind']['deg'])
        else:
            self.winddeg: float = 0.0


        self.temp: float = float(fdata['main']['temp']) - WeatherInfo.KTOC


    def Print(self) -> None:
        print("%s %i %03i%%  %.2f %.2f  %+.2f (%5.1f,%03i)"  % (str(self.t),self.id,self.clouds,self.rain,self.snow,self.temp,self.windspeed,self.winddeg)  )

    @staticmethod
    def Check(fdata: dict) -> bool:
        if not ('dt' in fdata):
            return False
        if not ('weather' in fdata):
            return False
        if not ('main' in fdata):
            return False
        return True




class OpenWeatherMap():

    OWMURL: str = "http://api.openweathermap.org/data/2.5/"


    FILENAME_CURR: str = "openweathermap_curr_"
    FILENAME_FORECAST: str = "openweathermap_fcst_"
    FILENAME_EXT: str = ".json"

    FILETOOOLD_SEC: int = 15*60 # 15 mins
    TOOMUCHTIME_SEC: int = 4*60*60 # 4 hours

    def __init__(self,apikey:str,latitude:float,longitude:float,rootdir:str="") -> None:

        self.latitude: float = latitude
        self.longitude: float = longitude

        reqstr: str = "lat=%.4f&lon=%.4f&mode=json&APPID=%s" % (self.LAT,self.LON,apikey)
        self.URL_FOREAST: str = self.OWMURL+"forecast?"+reqstr
        self.URL_CURR: str =  self.OWMURL+"weather?"+reqstr
        self.f: List[WeatherInfo] = []
        self.rootdir: str = rootdir

        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir)

        self.filename_forecast: str = os.path.join(self.rootdir,self.FILENAME_FORECAST+self.PLACEKEY+self.FILENAME_EXT)
        self.filename_curr: str = os.path.join(self.rootdir,self.FILENAME_CURR+self.PLACEKEY+self.FILENAME_EXT)

    @property
    def LAT(self)->float:
        return self.latitude

    @property
    def LON(self)->float:
        return self.longitude

    @staticmethod
    def MakeCoordinateKey(p:float) -> str:
        n: int = int(p*10000)
        return ( "%08X"  % ( n if n>=0 else (n+(1 << 32)) ))[2:]

    @property
    def PLACEKEY(self)->str:
        return  OpenWeatherMap.MakePlaceKey(self.LAT,self.LON)

    @staticmethod
    def MakePlaceKey(latitude:float,longitude:float) -> str:
        return  OpenWeatherMap.MakeCoordinateKey(latitude) + OpenWeatherMap.MakeCoordinateKey(longitude)

    def FromWWW(self) -> bool:
        fjsontext: bytes = urlopen(self.URL_FOREAST).read()
        ff = open(self.filename_forecast,"wb")
        ff.write(fjsontext)
        ff.close()
        fdata: dict = json.loads(fjsontext)
        cjsontext: bytes = urlopen(self.URL_CURR).read()
        cf = open(self.filename_curr,"wb")
        cf.write(cjsontext)
        cf.close()
        cdata: dict = json.loads(cjsontext)
        return self.FromJSON(cdata,fdata)





    def GetTempRange(self,maxtime: datetime.datetime) -> Optional[Tuple[float, float]]:
        if len(self.f)==0:
            return None
        tmax: float = -999
        tmin: float = 999
        isfirst: bool = True
        for f in self.f:
            if (isfirst):
                isfirst = False
                continue
            if (f.t>maxtime):
                break
            if (f.temp>tmax):
                tmax = f.temp
            if (f.temp<tmin):
                tmin = f.temp
        return (tmin,tmax)


    def FromJSON(self,data_curr:dict,data_fcst:dict) -> bool:
        self.f = []
        cdata: dict = data_curr
        f: WeatherInfo = WeatherInfo(cdata)
        self.f.append(f)
        if not ('list' in data_fcst):
            return False
        for fdata in data_fcst['list']:
            if not WeatherInfo.Check(fdata):
                continue
            f = WeatherInfo(fdata)
            self.f.append(f)
        return True



    def FromFile(self) -> bool:
        ff = open(self.filename_forecast)
        fdata: dict = json.load(ff)
        ff.close()
        cf = open(self.filename_curr)
        cdata: dict = json.load(cf)
        cf.close()

        return self.FromJSON(cdata,fdata)

    def IsFileTooOld(self, filename: str) -> bool:
        return (not os.path.isfile(filename)) or ( (time.time() - os.stat(filename).st_mtime) > self.FILETOOOLD_SEC )

    def FromAuto(self) -> bool:
        if (self.IsFileTooOld(self.filename_forecast) or self.IsFileTooOld(self.filename_curr)):
            print("Using WWW")
            return self.FromWWW()

        print("Using Cache '%s','%s'" % (self.filename_curr,self.filename_forecast))
        return self.FromFile()

    def GetCurr(self) -> Optional[WeatherInfo]:
        if len(self.f)==0:
            return None
        return self.f[0]


    def Get(self,time: datetime.datetime) -> Optional[WeatherInfo]:
        for f in self.f:
            if (f.t>time):
                return f
        return None



    def PrintAll(self) -> None:
        for f in self.f:
            f.Print()
