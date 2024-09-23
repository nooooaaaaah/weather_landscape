import os
import logging
from weather_landscape import WeatherLandscape

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    w = WeatherLandscape()
    fn = w.SaveImage()
    print("Saved", fn)
except ValueError as e:
    logger.error(f"An error occurred: {str(e)}")
    print(f"Error: {str(e)}")
except Exception as e:
    logger.exception("An unexpected error occurred")
    print(f"Unexpected error: {str(e)}")
