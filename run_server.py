
import os
import time
import datetime
from PIL import Image

from http.server import HTTPServer, BaseHTTPRequestHandler

from weather_landscape import WeatherLandscape


SERV_IPADDR = "0.0.0.0"
SERV_PORT = 3355

EINKFILENAME = "test.bmp"
USERFILENAME = "test1.bmp"

FILETOOOLD_SEC = 60*10

WEATHER = WeatherLandscape()


class WeatherLandscapeServer(BaseHTTPRequestHandler):


    

    def do_GET(self):
        
        if self.path == '/':
           self.path = '/index.html'
           
           
        print("GET:",self.path)
           
        if (self.path.startswith('/index.html')):
           self.send_response(200)
           self.end_headers()
           self.wfile.write(bytes(self.IndexHtml(), 'utf-8'))
           
           
        if (self.path.startswith('/'+EINKFILENAME)) or (self.path.startswith('/'+USERFILENAME)):
        
            self.CreateWeatherImages() 
        
            databytes = bytearray()
            try:
            
               file_name = WEATHER.TmpFilePath(self.path[1:])
               f = open(file_name, "rb") 
               databytes = f.read()               
               f.close()
               self.send_response(200)
               s.send_header("Content-type", "image/bmp")
            except:
               file_to_open = "File not found"
               self.send_response(404)
            self.end_headers()
            self.wfile.write(databytes)


    def IsFileTooOld(self, filename):
        return (not os.path.isfile(filename)) or ( (time.time() - os.stat(filename).st_mtime) > FILETOOOLD_SEC )


    def CreateWeatherImages(self):
                    
        user_file_name = WEATHER.TmpFilePath(USERFILENAME)
        eink_file_name = WEATHER.TmpFilePath(EINKFILENAME)
       
        if not self.IsFileTooOld(user_file_name):
            return
       
        img = WEATHER.MakeImage() 
        img.save(user_file_name) 
        
        img = img.rotate(-90, expand=True)   
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  
        
        img.save(eink_file_name) 
        
        
        
        


    def IndexHtml(self):
    
        body = '<h1>Weather as Landscape</h1>'
        body+='<p>Place: '+("%.4f" % WEATHER.OWM_LAT) +' , '+("%.4f" % WEATHER.OWM_LON)+'</p>'
        body+='<p><img src="'+USERFILENAME+'" alt="Weather" "></p>'
        body+='<p>ESP32 URL: <span id="eink"></span></p>'
        body+='<script> document.getElementById("eink").innerHTML = window.location+"'+EINKFILENAME+'" ;</script>'
            
            
        return """
            <!DOCTYPE html>
            <html lang="en">
              <head>
                <meta charset="utf-8">
                <title>Weather as Landscape</title>
              </head>
              <body> """ + body + """
              </body>
            </html>"""

        
    





httpd = HTTPServer((SERV_IPADDR,SERV_PORT),WeatherLandscapeServer)
print(r"Serving at http://%s:%i/" % (SERV_IPADDR,SERV_PORT))
httpd.serve_forever() 


