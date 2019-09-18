import pyowm
import geocoder

def get_weather(lat, lng):
   owm = pyowm.OWM('f8c43bbd601d39c177afabec2d050d04')
   observation = owm.weather_at_coords(lat, lng)
   w = observation.get_weather()
   temp = w.get_temperature('celsius')
   humidity = w.get_humidity()
   pressure = w.get_pressure()
   return humidity, temp['temp'], pressure['press']


def get_location():
    g = geocoder.ip('me')
    return g.lat, g.lng, g.address
    
if __name__ == "__main__":
    latitude, longitude, address = get_location()
    humidity, temperature, pressure = get_weather(latitude, longitude)
    print(latitude, longitude, address)
    print(humidity, temperature, pressure)
