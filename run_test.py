import os
import logging
from weather_landscape import WeatherLandscape
from datetime import datetime
from PIL import Image
from unittest.mock import Mock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWeatherLandscape:
    def __init__(self):
        self.weather_landscape = WeatherLandscape()
        self.weather_landscape.TMP_DIR = "tmp"
        os.makedirs(self.weather_landscape.TMP_DIR, exist_ok=True)

    def create_mock_weather_info(self):
        mock_weather = Mock()
        mock_weather.temp = 20
        mock_weather.clouds = 40
        mock_weather.rain = 1
        mock_weather.snow = 0
        mock_weather.windspeed = 2
        mock_weather.winddeg = 180
        mock_weather.t = datetime.now()
        mock_weather.weather = [{'main': 'Rain', 'description': 'light rain'}]
        return mock_weather

    def run_test(self):
        try:
            mock_owm = Mock()
            mock_owm.GetCurr.return_value = self.create_mock_weather_info()
            mock_owm.Get.return_value = self.create_mock_weather_info()
            mock_owm.GetTempRange.return_value = (15, 25)
            mock_owm.LAT, mock_owm.LON = 52.196136, 21.007963

            img = self.weather_landscape.MakeImage()
            fn = f"test_landscape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            outfilepath = os.path.join(self.weather_landscape.TMP_DIR, fn)
            img.save(outfilepath)
            logger.info(f"Saved {outfilepath}")
            self.verify_landscape(outfilepath)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")

    def verify_landscape(self, outfilepath):
        if not os.path.exists(outfilepath):
            raise ValueError(f"File {outfilepath} was not created")

        with Image.open(outfilepath) as img:
            extrema = img.convert("L").getextrema()
            if extrema in ((0, 0), (255, 255)):
                raise ValueError("Image is completely black or white")
            if len(img.getcolors(maxcolors=1000)) <= 1:
                raise ValueError("Image has only one color")

        logger.info("Landscape verification passed")

if __name__ == '__main__':
    test = TestWeatherLandscape()
    test.run_test()
