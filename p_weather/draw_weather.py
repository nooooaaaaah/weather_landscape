from p_weather.sprites import Sprites
from p_weather.openweathermap import OpenWeatherMap, WeatherInfo
from p_weather.sunrise import sun

import datetime
from PIL import Image
import random
from typing import Tuple, List


class DrawWeather():

    XSTART: int = 32
    XSTEP: int = 44
    XFLAT: int = 10

    YSTEP: int = 50  #64

    DEFAULT_DEGREE_PER_PIXEL: float = 0.5

    @staticmethod
    def mybeizelfnc(t: float, d0: float, d1: float, d2: float, d3: float) -> float:
        return  (1-t)*( (1-t)*((1-t)*d0+t*d1 ) + t*( (1-t)*d1 + t*d2)) + t*( (1-t)*( (1-t)*d1 + t*d2)+t*((1-t)*d2 +t*d3))


    def mybezier(self, x: int, xa: int, ya: int, xb: int, yb: int) -> int:
        xc: float = (xb+xa)/2.0
        d: float = xb-xa
        t: float = float(x-xa)/float(d)
        y: float = DrawWeather.mybeizelfnc(t,ya,ya,yb,yb)
        return int(y)
        #print(t,x,y)




    def __init__(self, canvas: Image.Image, sprites: Sprites):
        self.img: Image.Image = canvas
        self.sprite: Sprites = sprites
        (self.IMGEWIDTH, self.IMGHEIGHT) = self.img.size


    def TimeDiffToPixels(self, dt: datetime.timedelta) -> int:
       ds: float = dt.total_seconds()
       secondsperpixel: float = (WeatherInfo.FORECAST_PERIOD_HOURS*60*60) / DrawWeather.XSTEP
       return int ( ds / secondsperpixel )


    def DegToPix(self, t: float) -> int:
        n: float = (t - self.tmin)/self.degreeperpixel
        y: int = self.ypos+self.YSTEP - int(n)
        return y

    #todo: add thunderstorm
    #todo: add fog
    #todo: add snow

    def Draw(self, ypos: int, owm: OpenWeatherMap) -> None:

        self.picheight: int = self.IMGHEIGHT
        self.picwidth: int = self.IMGEWIDTH
        self.ypos: int = ypos

        nforecasrt: float = ( (self.picwidth-self.XSTART)/self.XSTEP )
        maxtime: datetime.datetime = datetime.datetime.now() + datetime.timedelta(hours=WeatherInfo.FORECAST_PERIOD_HOURS*nforecasrt)

        # Manually iterate through temperatures to find min and max
        self.tmin = float('inf')
        self.tmax = float('-inf')
        current_time = datetime.datetime.now()
        while current_time <= maxtime:
            weather_info = owm.Get(current_time)
            if weather_info is not None:
                self.tmin = min(self.tmin, weather_info.temp)
                self.tmax = max(self.tmax, weather_info.temp)
            current_time += datetime.timedelta(hours=WeatherInfo.FORECAST_PERIOD_HOURS)
        self.temprange: float = self.tmax-self.tmin
        if ( self.temprange < self.YSTEP ):
            self.degreeperpixel: float = self.DEFAULT_DEGREE_PER_PIXEL
        else:
            self.degreeperpixel: float = self.temprange/float(self.YSTEP)

        #print("tmin = %f , tmax = %f, range=%f" % (self.tmin,self.tmax,self.temprange))

        xpos: int = 0
        tline: List[int] = [0]*(self.picwidth+self.XSTEP+1)
        f: WeatherInfo | None = owm.GetCurr()
        if f is None:
            raise ValueError("Could not get current weather information")
        oldtemp: float = f.temp
        oldy: int = self.DegToPix(oldtemp)
        for i in range(self.XSTART):
            tline[i] = oldy
        yclouds: int = int(ypos-self.YSTEP/2)
        f.Print()

        self.sprite.Draw("house",xpos,0,oldy)
        self.sprite.DrawInt(int(oldtemp),xpos+8,oldy+10)
        self.sprite.DrawCloud(f.clouds,xpos,yclouds,self.XSTART,int(self.YSTEP/2))
        self.sprite.DrawRain(f.rain,xpos,yclouds,self.XSTART,tline)
        self.sprite.DrawSnow(f.snow,xpos,yclouds,self.XSTART,tline)


        t: datetime.datetime = datetime.datetime.now()
        dt: datetime.timedelta = datetime.timedelta(hours=WeatherInfo.FORECAST_PERIOD_HOURS)
        tf: datetime.datetime = t

        xpos = int(self.XSTART)
        nforecasrt = int(nforecasrt)

        n: int = int( (self.XSTEP-self.XFLAT)/2 )
        for i in range(nforecasrt+1):
            f = owm.Get(tf)
            if (f==None):
                continue
            f.Print()
            newtemp: float = f.temp
            newy: int = self.DegToPix(newtemp)
            for i in range(n):
                tline[xpos+i] = self.mybezier(xpos+i,xpos,oldy,xpos+n,newy)


            for i in range(self.XFLAT):
                tline[int(xpos+i+n)] = newy


            xpos+=n+self.XFLAT

            n = (self.XSTEP-self.XFLAT)
            oldtemp = newtemp
            oldy = newy
            tf += dt

        s: sun = sun(owm.LAT,owm.LON)
        tf = t
        xpos = self.XSTART
        objcounter: int = 0
        for i in range(nforecasrt+1):
            f = owm.Get(tf)
            if (f==None):
                continue

            t_sunrise: datetime.datetime = s.sunrise(tf)
            t_sunset: datetime.datetime = s.sunset(tf)

            ymoon: int = ypos-self.YSTEP*5//8

            if (tf<=t_sunrise) and (tf+dt>t_sunrise):
                dx: int = self.TimeDiffToPixels(t_sunrise-tf)  - self.XSTEP//2
                self.sprite.Draw("sun",0,xpos+dx,ymoon)
                objcounter+=1
                if (objcounter==2):
                    break

            if (tf<=t_sunset) and (tf+dt>t_sunset):
                dx = self.TimeDiffToPixels(t_sunset-tf)  - self.XSTEP//2
                self.sprite.Draw("moon",0,xpos+dx,ymoon)
                objcounter+=1
                if (objcounter==2):
                    break

            xpos+=self.XSTEP
            tf += dt



        istminprinted: bool = False
        istmaxprinted: bool = False
        tf = t
        xpos = self.XSTART
        n = int( (self.XSTEP-self.XFLAT)/2 )
        for i in range(nforecasrt+1):
            f = owm.Get(tf)
            if (f==None):
                continue

            #f.Print()

            yclouds = int( ypos-self.YSTEP/2 )


            if (f.temp==self.tmin) and (not istminprinted):
                self.sprite.DrawInt(int(f.temp), xpos+n, tline[xpos+n]+10)
                istminprinted = True

            if (f.temp==self.tmax) and (not istmaxprinted):
                self.sprite.DrawInt(int(f.temp), xpos+n, tline[xpos+n]+10)
                istmaxprinted = True

            t0: datetime.datetime = f.t - dt/2
            t1: datetime.datetime = f.t + dt/2





            # FLOWERS: black - midnight ,  red - midday
            dt_onehour: datetime.timedelta = datetime.timedelta(hours=1)
            dx_onehour: float = self.XSTEP/WeatherInfo.FORECAST_PERIOD_HOURS
            tt: datetime.datetime = t0
            xx: float = xpos
            while(tt<=t1):
                ix: int = int(xx)
                if(tt.hour==12):
                    self.sprite.Draw("flower",1,ix,tline[ix])
                if(tt.hour==0):
                    self.sprite.Draw("flower",0,ix,tline[ix])
                if(tt.hour==6) or (tt.hour==18) or (tt.hour==3) or (tt.hour==15) or (tt.hour==9) or (tt.hour==21):
                    self.sprite.DrawWind(f.windspeed,f.winddeg,ix,tline)


                tt+=dt_onehour
                xx+=dx_onehour






            self.sprite.DrawCloud(f.clouds,xpos,yclouds,self.XSTEP,int(self.YSTEP/2))

            self.sprite.DrawRain(f.rain,xpos,yclouds,self.XSTEP,tline)
            self.sprite.DrawSnow(f.snow,xpos,yclouds,self.XSTEP,tline)

            # Draw rainbow if it's raining and there's sunlight (assuming daytime)
            # if f.rain > 0 and 6 <= tf.hour <= 18 and random.random() < 0.7:  # 70% chance
            if True:
                rainbow_width: int = self.XSTEP * 2
                rainbow_height: int = self.YSTEP
                self.sprite.DrawRainbow(xpos, yclouds - rainbow_height)

            xpos+=self.XSTEP
            tf += dt




        BLACK: int = 0

        for x in range(self.picwidth):
            if (tline[x]<self.picheight):
                self.sprite.Dot(x,tline[x],Sprites.BLACK)
            else:
                print("out of range: %i - %i(max %i)" % (x,tline[x],self.picheight))

    def __iter__(self):
        # This is a placeholder implementation. Adjust according to your needs.
        return iter([])
