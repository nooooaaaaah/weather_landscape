from PIL import Image
from typing import List, Tuple, Optional
import random
import os

class Sprites:

    Black: int = 0
    White: int = 1

    BLACK: int = 0
    WHITE: int = 1
    RED: int = 2
    TRANS: int = 3

    PLASSPRITE: int = 10
    MINUSSPRITE: int = 11

    EXT: str = ".png"


    def __init__(self, spritesdir: str, canvas: Image.Image):
        self.img: Image.Image = canvas
        self.pix= self.img.load()
        self.dir: str = spritesdir
        self.ext: str = self.EXT
        self.w: int
        self.h: int
        self.w, self.h = self.img.size



    def Dot(self, x: int, y: int, color: int) -> None:

        #y = self.h - y

        if (y>=self.h) or (x>=self.w) or (y<0) or (x<0):
            return

        self.pix[x,y] = color


    def Draw(self, name: str, index: int, xpos: int, ypos: int) -> int:

        #print("DRAW '%s' #%i at %i,%i" % (name,index,xpos,ypos))

        imagefilename: str = "%s_%02i%s" % (name, index, self.ext)
        imagepath: str = os.path.join(self.dir,imagefilename)
        img: Image.Image = Image.open(imagepath)
        w: int
        h: int
        w, h = img.size
        pix= img.load()
        ypos -= h
        for x in range(w):
            for y in range(h):
                if (xpos+x>=self.w) or (xpos+x<0):
                    continue
                if (ypos+y>=self.h) or (ypos+y<0):
                    continue
                if (pix[x,y]==self.BLACK):
                    self.Dot(xpos+x,ypos+y,self.Black)
                elif (pix[x,y]==self.WHITE):
                    self.Dot(xpos+x,ypos+y,self.White)
                elif (pix[x,y]==self.RED):
                    self.Dot(xpos+x,ypos+y,self.Black)

        return w


    DIGITPLAS: int = 10
    DIGITMINUS: int = 11
    DIGITSEMICOLON: int = 12

    def DrawInt(self, n: int, xpos: int, ypos: int, issign: bool = True, isleadzero: bool = False) -> int:
        if (n<0):
            sign: int = self.DIGITMINUS
        else:
            sign: int = self.DIGITPLAS
        n = round(n)
        n = abs(n)
        n1: int = n // 10
        n2: int = n % 10
        dx: int = 0
        if (issign):
            w: int = self.Draw("digit",sign,xpos+dx,ypos)
            dx+=w+1
        if (n1!=0) or (isleadzero):
            w = self.Draw("digit",n1,xpos+dx,ypos)
            dx+=w+1
        w = self.Draw("digit",n2,xpos+dx,ypos)
        dx+=w+1
        return dx

    def DrawClock(self, xpos: int, ypos: int, h: int, m: int) -> int:
        dx: int = 0
        w: int = self.DrawInt(h,xpos+dx,ypos,False,True)
        dx+=w
        w = self.Draw("digit",self.DIGITSEMICOLON,xpos+dx,ypos)
        dx+=w
        dx = self.DrawInt(m,xpos+dx,ypos,False,True)
        dx+=w+1
        return dx




    CLOUDWMAX: int = 32
    CLOUDS: List[int] = [2,3,5,10,30,50]
    CLOUDK: float = 0.5

    def DrawCloud(self, persent: float, xpos: int, ypos: int, width: int, height: int) -> None:
        if (persent<2):
            return
        elif (persent<5):
            cloudset: List[int] = [2]
        elif (persent<10):
            cloudset = [3,2]
        elif (persent<20):
            cloudset = [5,3,2]
        elif (persent<30):
            cloudset = [10,5]
        elif (persent<40):
            cloudset = [10,10]
        elif (persent<50):
            cloudset = [10,10,5]
        elif (persent<60):
            cloudset = [30,5]
        elif (persent<70):
            cloudset = [30,10]
        elif (persent<80):
            cloudset = [30,10,5,5]
        elif (persent<90):
            cloudset = [30,10,10]
        else:
            cloudset = [50,30,10,10,5]

        dx: int = width
        dy: int = 16
        for c in cloudset:
            self.Draw("cloud",c,xpos+random.randrange(dx),ypos)

    HEAVYRAIN: float = 5.0
    RAINFACTOR: int = 20

    def DrawRain(self, value: float, xpos: int, ypos: int, width: int, tline: List[int]) -> None:
        ypos+=1
        r: float = 1.0 - ( value / self.HEAVYRAIN ) / self.RAINFACTOR

        for x in range(xpos,xpos+width):
            for y in range(ypos,tline[x],2):
                if (x>=self.w):
                    continue
                if (y>=self.h):
                    continue
                if (random.random()>r):
                    self.pix[x,y] = self.Black
                    self.pix[x,y-1] = self.Black

    HEAVYSNOW: float = 5.0
    SNOWFACTOR: int = 10

    def DrawSnow(self, value: float, xpos: int, ypos: int, width: int, tline: List[int]) -> None:
        ypos+=1
        r: float = 1.0 - ( value / self.HEAVYSNOW ) / self.SNOWFACTOR

        for x in range(xpos,xpos+width):
            for y in range(ypos,tline[x],2):
                if (x>=self.w):
                    continue
                if (y>=self.h):
                    continue
                if (random.random()>r):
                    self.pix[x,y] = self.Black




    def  DrawWind_degdist(self, deg1: float, deg2: float) -> float:
        h: float = max(deg1,deg2)
        l: float = min(deg1,deg2)
        d: float = h-l
        if (d>180):
            d = 360-d
        return d



    def DrawWind_dirsprite(self, dir: float, dir0: float, name: str, list: List[str]) -> None:
        count: List[int] = [4,3,3,2,2,1,1]
        step: float = 11.25 #degrees
        dist: float = self. DrawWind_degdist(dir,dir0)
        n: int = int(dist/step)
        if (n<len(count)):
            for i in range(0,count[n]):
                list.append(name)





    def DrawWind(self, speed: float, direction: float, xpos: int, tline: List[int]) -> None:

            list: List[str] = []

            self.DrawWind_dirsprite(direction,0,  "pine",list)
            self.DrawWind_dirsprite(direction,90, "east",list)
            self.DrawWind_dirsprite(direction,180,"palm",list)
            self.DrawWind_dirsprite(direction,270,"tree",list)

            random.shuffle(list)

            windindex: Optional[List[int]] = None
            if   (speed<=0.4):
                windindex = []
            elif (speed<=0.7):
                windindex = [0]
            elif (speed<=1.7):
                windindex = [1,0,0]
            elif (speed<=3.3):
                windindex = [1,1,0,0]
            elif (speed<=5.2):
                windindex = [1,2,0,0]
            elif (speed<=7.4):
                windindex = [1,2,2,0]
            elif (speed<=9.8):
                windindex = [1,2,3,0]
            elif (speed<=12.4):
                windindex = [2,2,3,0]
            else:
                windindex = [3,3,3,3]


            if (windindex!=None):
                ix: int = int(xpos)
                random.shuffle(windindex)
                j: int = 0
                #print("wind>>>",direction,speed,list,windindex);
                for i in windindex:
                    offset: int = ix+5
                    if (offset>=len(tline)):
                        break
                    self.Draw(list[j],i,ix,tline[offset]+1)
                    ix+=9
                    j+=1

    def DrawRainbow(self, xpos: int, ypos: int) -> None:
        rainbow_file: str = f"rainbow_00{self.ext}"
        rainbow_path: str = os.path.join(self.dir, rainbow_file)

        if os.path.exists(rainbow_path):
            self.Draw("rainbow", 0, xpos, ypos)
        else:
            print(f"Warning: Rainbow sprite not found at {rainbow_path}")
            # Fallback: Draw a simple rainbow arc if sprite is missing
            colors: List[Tuple[int, int, int]] = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (143,0,255)]
            radius: int = 50
            for i, color in enumerate(colors):
                for x in range(-radius, radius):
                    y: int = int((radius - i*5)**2 - x**2)**0.5
                    if 0 <= xpos+x < self.w and 0 <= ypos-y < self.h:
                        self.pix[xpos+x, ypos-y] = color

if __name__ == "__main__":


    img: Image.Image = Image.open('../test.bmp')


    s: Sprites = Sprites('../sprite',img)


    s.Draw("house",0,100,100)
    s.DrawRainbow(50,150)

    img.save("../tmp/sprites_test.bmp")
