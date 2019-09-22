#############################################
from __future__ import print_function
from tkinter import *
from time import *
import re
import json
import threading
import locale
import time
import requests
import time
import intrinio_sdk
from intrinio_sdk.rest import ApiException
import pyowm
import geocoder
import random
#############################################

degree_sign = u'\N{DEGREE SIGN}'

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

def get_mails():
    # Returns Sender, Date, Subject of last 5 emails
    regexstr = r'From: (.*) <.*?>\nDate:(.*)\nMessage.*\nSubject: (.*)\n'
    with open("/var/mail/477grp1", "r") as mail_file:
        text = mail_file.read()
    mail_list = re.findall(regexstr, text)
    return mail_list[-5:]

def NewsFromBBC():
    main_url = " https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=4dbc17e007ab436fb66416009dfb59a8"
    open_bbc_page = requests.get(main_url).json()
    if 'articles' in open_bbc_page:
        articles = open_bbc_page["articles"]
    else:
        articles = []
    result = []
    for article in articles:
        if article is not None:
            result.append(article["title"])
    if len(result) > 5:
        return result[0:5]
    else:
        return result

def get_stocks():
    intrinio_sdk.ApiClient().configuration.api_key['api_key'] = 'API-KEY'
    security_api = intrinio_sdk.SecurityApi()
    identifiers = ['AAPL', 'MSFT', 'GS', 'NKE']
    price_list = list()
    try:
        for identifier in identifiers:
            api_response = security_api.get_security_realtime_price(identifier)
            price_list.append((identifier, api_response.ask_price))
    except ApiException as e:
        print("Exception when calling SecurityApi->get_security_realtime_price: %s\r\n" % e)
    finally:
        return price_list

def getQuote():
    r = requests.get('https://programming-quotes-api.herokuapp.com/quotes')
    quoteObj = json.loads(r.text)
    return quoteObj
#############################################

class News(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")
        self.news = ""
        self.label_news = Label(self, font="dreams 15", bg="BLACK", fg="WHITE")
        self.label_news.pack(side=BOTTOM, anchor="n")
        self.update_news()

    def update_news(self):
        x = NewsFromBBC()
        for i in range(len(x)):
            temp = x[i]
            temp1 = '* ' + temp
            x[i] = temp1
        string = '\n'.join(x)
        self.label_news.config(text="--News--\n" + string)
        self.after(600000, self.update_news)

class Time_and_Day(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")
        self.time1 = ""
        self.label_time = Label(self, font="dreams 30", bg="BLACK", fg="WHITE")
        self.label_time.pack(side=TOP, anchor="e")

        self.day1 = ""
        self.label_day = Label(self, font="dreams 30", bg="BLACK", fg="WHITE")
        self.label_day.pack(side=TOP, anchor="e")

        self.day_of_the_week1 = ""
        self.label_day_of_the_week = Label(self, font="dreams 30", bg="BLACK", fg="WHITE")
        self.label_day_of_the_week.pack(side=TOP, anchor="e")

        self.update_time()

    def update_time(self):
        time2 = strftime("%I:%M:%S %p")
        day2 =  strftime("%B %d, %Y")
        day_of_the_week2 = strftime("%A")
        if self.time1 != time2:
            self.time1 = time2
            self.label_time.config(text=time2)
        if self.day1 != day2:
            self.day1 = day2
            self.label_day.config(text=day2)
        if self.day_of_the_week1 != day_of_the_week2:
            self.day_of_the_week1 = day_of_the_week2
            self.label_day_of_the_week.config(text=day_of_the_week2)
        self.after(200, self.update_time)

class WeatherLocation(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")
        self.temperature = ""
        self.label_temperature = Label(self, font="dreams 30", bg="BLACK", fg="WHITE")
        self.label_temperature.pack(side=TOP, anchor="w")

        self.humidity= ""
        self.label_humidity = Label(self, font = "dreams 30", bg="BLACK", fg="WHITE")
        self.label_humidity.pack(side=TOP, anchor="w")

        self.location = ""
        self.label_location = Label(self, font="dreams 30", bg="BLACK", fg="WHITE")
        self.label_location.pack(side=TOP, anchor="w")

        self.update_weatherloc()

    def update_weatherloc(self):
        latitude, longitude, address = get_location()
        humidity, temperature, pressure = get_weather(latitude, longitude)
        self.label_temperature.config(text=str(temperature) + ' ' + degree_sign + 'C')
        self.label_humidity.config(text='Humidity: ' + str(humidity) + '%')
        self.label_location.config(text=address)
        self.after(600000, self.update_weatherloc)

class Final:
    def __init__(self):
        self.root = Tk()
        self.root.configure(bg="BLACK")
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")
        self.top = Frame(self.root, bg="BLACK")
        self.top.pack(side=TOP, fill=BOTH)
        self.bottom = Frame(self.root, bg="BLACK")
        self.bottom.pack(side=BOTTOM, fill=BOTH)

        self.greeting = Label(self.root, text="Welcome to IntelliFace :)", font="Helvetica 45", bg="BLACK", fg="WHITE")
        self.greeting.pack(pady=210)

        self.time = Time_and_Day(self.top)
        self.time.pack(side=RIGHT, anchor=N)

        self.weather = WeatherLocation(self.top)
        self.weather.pack(side=LEFT)

        self.news = News(self.bottom)
        self.news.pack(side=LEFT)

        quote = ""
        author = ""
        a = getQuote()
        if len(a) == 0:
            quote = "It was what it was. It is what it is. It will be what it will be."
            author = "Team1"
        else:
            i = random.randint(0, 10)
            if i < len(a) or len(a[i]['en']) < 160:
                quote = a[i]['en']
                author = a[i]['author']
            else:
                quote = a[0]['en']
                author = a[0]['author']
        self.quote = Label(self.root, text=quote, font="Helvetica 14", bg="BLACK", fg="WHITE")
        self.author = Label(self.root, text=author, font="Helvetica 14", bg="BLACK", fg="WHITE")
        self.quote.pack()
        self.author.pack()

if __name__ == "__main__":
    start = Final()
    start.root.mainloop()
