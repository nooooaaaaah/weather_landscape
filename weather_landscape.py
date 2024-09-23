import os
import logging
from PIL import Image as PILImage
from typing import Any

from p_weather.openweathermap import OpenWeatherMap
from p_weather.sprites import Sprites
from p_weather.draw_weather import DrawWeather

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WeatherLandscape:
    OWM_KEY: str = "7d4c9a66d83ea191504f10e3e96afb23"  # Replace with your actual API key
    OWM_LAT: float = 52.196136
    OWM_LON: float = 21.007963

    TMP_DIR: str = "tmp"
    OUT_FILENAME: str = "test_"
    OUT_FILEEXT: str = ".png"  # Make sure this is set to ".png"
    TEMPLATE_FILENAME: str = "p_weather/template.bmp"
    SPRITES_DIR: str = "p_weather/sprite"
    DRAWOFFSET: int = 65

    def __init__(self) -> None:
        assert self.OWM_KEY!=None, "Set OWM_KEY variable to your OpenWeather API key"
        pass

    def MakeImage(self) -> PILImage.Image:
        try:
            logger.debug("Starting MakeImage method")
            owm: OpenWeatherMap = OpenWeatherMap(self.OWM_KEY, self.OWM_LAT, self.OWM_LON, self.TMP_DIR)
            owm.FromAuto()
            logger.debug("OpenWeatherMap data fetched")

            img: PILImage.Image = PILImage.open(self.TEMPLATE_FILENAME)
            logger.debug(f"Template image opened: {self.TEMPLATE_FILENAME}")
            logger.debug(f"Image type: {type(img)}, size: {img.size}, mode: {img.mode}")

            spr: Sprites = Sprites(self.SPRITES_DIR, img)
            logger.debug("Sprites initialized")

            art: DrawWeather = DrawWeather(img, spr)
            logger.debug("DrawWeather initialized")

            art.Draw(self.DRAWOFFSET, owm)
            logger.debug("Drawing completed")

            logger.debug(f"Final image type: {type(img)}, size: {img.size}, mode: {img.mode}")
            return img
        except Exception as e:
            logger.error(f"Error in MakeImage: {str(e)}", exc_info=True)
            raise

    def SaveImage(self) -> str:
        try:
            logger.debug("Starting SaveImage method")
            img: PILImage.Image = self.MakeImage()
            placekey: str = OpenWeatherMap.MakePlaceKey(self.OWM_LAT, self.OWM_LON)
            filename: str = f"{self.OUT_FILENAME}{placekey}{self.OUT_FILEEXT}"
            outfilepath: str = self.TmpFilePath(filename)

            logger.debug(f"Saving image to: {outfilepath}")
            if isinstance(img, PILImage.Image):
                img.save(outfilepath)
                logger.debug("Image saved successfully")
            else:
                raise TypeError("img is not a PIL.Image object")

            return outfilepath
        except Exception as e:
            logger.error(f"Error in SaveImage: {str(e)}", exc_info=True)
            raise

    def TmpFilePath(self, filename: str) -> str:
        return os.path.join(self.TMP_DIR, filename)
