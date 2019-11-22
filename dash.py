#############################################
from __future__ import print_function
from tkinter import *
import re
import sys
import json
import requests
import intrinio_sdk
from intrinio_sdk.rest import ApiException
import pyowm
import geocoder
import random
from os import path, environ
from PIL import Image, ImageTk
from subprocess import run
import face_recognition
import cv2
import numpy as np
import serial
#############################################

state = "SLEEP" # SLEEP, RECOG, ACTIVE_NORMAL, ACTIVE_AF
temp, ldr, ir = 0, "L", 0
degree_sign = u'\N{DEGREE SIGN}'

def serial_temp_reader():
    temperature = 0
    while temperature < 5 or temperature > 50:
        try:
            with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser:
                temperature = float(ser.readline().decode("utf-8").split(',')[2])
        except (Warning, Exception) as e:
            pass
    return temperature

def get_weather(lat, lng):
   owm = pyowm.OWM(os.environ["PYOWM_API_KEY"])
   observation = owm.weather_at_coords(lat, lng)
   w = observation.get_weather()
   temp = w.get_temperature('celsius')
   humidity = w.get_humidity()
   return humidity, temp['temp']

def get_location():
    g = geocoder.ip('me')
    return g.lat, g.lng, g.address

def get_mails():
    filePath = "/home/team01/Mail/477grp1"
    if not path.isfile(filePath):
        return ["NO MAILS FOUND"]
    else:
        # Returns Sender, Date, Subject of last 5 emails
        regexstr_sender = r'From: .*<(.*)>'
        regexstr_subject = r'Subject: (.*)'
        with open(filePath, "r") as mail_file:
            text = mail_file.read()
        senders = re.findall(regexstr_sender, text)
        subjects = re.findall(regexstr_subject, text)
        sender_subject = list()
        for sender, subject in zip(senders, subjects):
            sender_subject.append(sender + " : " + subject)
        return sender_subject[-5:]

def NewsFromBBC():
    main_url = " https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=" + os.environ["NEWS_API_KEY"]
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

def get_stonks():
    intrinio_sdk.ApiClient().configuration.api_key['api_key'] = os.environ["INTRINIO_API_KEY"]
    security_api = intrinio_sdk.SecurityApi()
    identifiers = ['AAPL', 'MSFT', 'GS', 'NKE']
    price_list = list()
    try:
        for identifier in identifiers:
            api_response = security_api.get_security_realtime_price(identifier)
            price_list.append((identifier + " " + str(api_response.ask_price)))
    except ApiException as e:
        print("Exception when calling SecurityApi->get_security_realtime_price: %s\r\n" % e)
    finally:
        return price_list

def getQuote():
    try:
        r = requests.get('https://programming-quotes-api.herokuapp.com/quotes')
        a = json.loads(r.text)
        for i in range(10):
            i = random.randint(0, 250)
            quote = a[i]['en']
            author = a[i]['author']
            if len(quote) < 130:
                return quote, author

    except (Warning, Exception) as e:
        print(e)
        quote = "whomst'd've'ly'yaint'nt'ed'ies's'y'es"
        author = "Team 1"
        return quote, author

#############################################
class Stonks(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")

        self.stonks = ""
        self.label_stonks = Label(self, font="Times 13", bg="BLACK", fg="WHITE")
        self.label_stonks.pack(side=BOTTOM, anchor="n")

        self.stonksIconLbl = Label(self, font="Times 13", bg="BLACK", fg="WHITE")
        self.stonksIconLbl.pack(side=BOTTOM, anchor="n")
        self.stonks_icon_location = './icons/Stocks.png'

        self.update_stonks()

    def update_stonks(self):
        x = get_stonks()
        for i in range(len(x)):
            temp = x[i]
            temp1 = '* ' + temp
            x[i] = temp1
        string = '\n'.join(x)
        img = Image.open(self.stonks_icon_location)
        img = img.resize((45, 45), Image.ANTIALIAS)
        img = img.convert('RGB')
        pic = ImageTk.PhotoImage(img)
        self.stonksIconLbl.config(image=pic, bg="black")
        self.stonksIconLbl.image = pic
        self.label_stonks.config(text=string)
        self.after(600000, self.update_stonks)

class Mail(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")

        self.mail = ""
        self.label_mail = Label(self, font="Times 11", bg="BLACK", fg="WHITE")
        self.label_mail.pack(side=BOTTOM, anchor="n")

        self.mailIconLbl = Label(self, font="Times 11", bg="BLACK", fg="WHITE")
        self.mailIconLbl.pack(side=BOTTOM, anchor="n")
        self.mail_icon_location = './icons/email.png'

        self.update_mail()

    def update_mail(self):
        x = get_mails()
        for i in range(len(x)):
            temp = x[i]
            temp1 = '* ' + temp
            x[i] = temp1
        string = '\n'.join(x)
        img = Image.open(self.mail_icon_location)
        img = img.resize((45, 45), Image.ANTIALIAS)
        img = img.convert('RGB')
        pic = ImageTk.PhotoImage(img)
        self.mailIconLbl.config(image=pic, bg="black")
        self.mailIconLbl.image = pic
        self.label_mail.config(text=string)
        self.after(600000, self.update_mail)

class News(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")

        self.news = ""
        self.label_news = Label(self, font="Times 11", bg="BLACK", fg="WHITE")
        self.label_news.pack(side=BOTTOM, anchor="n")

        self.newsIconLbl = Label(self, font="Times 11", bg="BLACK", fg="WHITE")
        self.newsIconLbl.pack(side=BOTTOM, anchor="n")
        self.news_icon_location = './icons/news.png'

        self.update_news()

    def update_news(self):
        x = NewsFromBBC()
        for i in range(len(x)):
            temp = x[i]
            temp1 = '* ' + temp
            x[i] = temp1
        string = '\n'.join(x)
        img = Image.open(self.news_icon_location)
        img = img.resize((45, 45), Image.ANTIALIAS)
        img = img.convert('RGB')
        pic = ImageTk.PhotoImage(img)
        self.newsIconLbl.config(image=pic, bg="black")
        self.newsIconLbl.image = pic
        self.label_news.config(text=string)
        self.after(600000, self.update_news)

class Time_and_Day(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")
        self.time1 = ""
        self.label_time = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        self.label_time.pack(side=TOP, anchor="e")

        self.day1 = ""
        self.label_day = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        self.label_day.pack(side=TOP, anchor="e")

        self.day_of_the_week1 = ""
        self.label_day_of_the_week = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
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

        # self.weatherIconLbl = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        # self.weatherIconLbl.pack(side=TOP, anchor="w")
        # self.icon_location = './icons/weatherIcon.png'

        self.temperature = ""
        self.label_temperature = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        self.label_temperature.pack(side=TOP, anchor="w")

        self.roomtemp = ""
        self.label_roomtemp = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        self.label_roomtemp.pack(side=TOP, anchor="w")

        self.humidity= ""
        self.label_humidity = Label(self, font = "Times 20", bg="BLACK", fg="WHITE")
        self.label_humidity.pack(side=TOP, anchor="w")

        self.location = ""
        self.label_location = Label(self, font="Times 20", bg="BLACK", fg="WHITE")
        self.label_location.pack(side=TOP, anchor="w")

        self.update_weatherloc()

    def update_weatherloc(self):
        latitude, longitude, address = get_location()
        self.humidity, self.temperature = get_weather(latitude, longitude)
        self.roomtemp = serial_temp_reader()
        # img = Image.open(self.icon_location)
        # img = img.resize((45, 45), Image.ANTIALIAS)
        # img = img.convert('RGB')
        # pic = ImageTk.PhotoImage(img)
        # self.weatherIconLbl.config(image=pic, bg="black")
        # self.weatherIconLbl.image = pic
        self.label_temperature.config(text="Exterior: "str(self.temperature) + ' ' + degree_sign + 'C')
        self.label_roomtemp.config(text="Room: "str(self.roomtemp) + ' ' + degree_sign + 'C')
        self.label_humidity.config(text='Humidity: ' + str(self.humidity) + '%')
        self.label_location.config(text=address)
        self.after(60000, self.update_weatherloc)

class Final:
    def __init__(self, name="User"):
        self.root = Tk()
        self.root.configure(bg="BLACK")
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")
        self.top = Frame(self.root, bg="BLACK")
        self.top.pack(side=TOP, fill=BOTH)
        self.bottom = Frame(self.root, bg="BLACK")
        self.bottom.pack(side=BOTTOM, fill=BOTH)

        self.greeting = Label(self.root, text="Welcome, " + name, font="Times 43", bg="BLACK", fg="WHITE")
        self.greeting.pack(pady=200)

        self.time = Time_and_Day(self.top)
        self.time.pack(side=RIGHT, anchor=N)

        self.weather = WeatherLocation(self.top)
        self.weather.pack(side=LEFT)

        self.news = News(self.bottom)
        self.news.pack(side=LEFT)

        self.mail = Mail(self.bottom)
        self.mail.pack(side=RIGHT)

        self.stonks = Stonks(self.root)

        quote, author = getQuote()

        self.quote = Label(self.root, text=(30 * "\n" + quote), font="Times 14", bg="BLACK", fg="WHITE")
        self.author = Label(self.root, text=(author + "\n\n\n\n"), font="Times 14", bg="BLACK", fg="WHITE")
        self.quote.pack()
        self.author.pack()
        self.stonks.pack()

if __name__ == "__main__":
    start = Final()
    start.root.mainloop()
