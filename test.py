#############################################
from __future__ import print_function
from tkinter import *
from time import *
import re
import sys
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
from os import path, environ
from PIL import Image, ImageTk
from subprocess import run
import face_recognition
import os
import cv2
import numpy as np
import time
import serial
#############################################

state = "SLEEP" # SLEEP, RECOG, ACTIVE_NORMAL, ACTIVE_AF
temp, ldr, ir = 0, "L", 0
degree_sign = u'\N{DEGREE SIGN}'



def detect_face():
    try:
        state = "RECOG"
        start_time = time.time()
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        while True:
            if (time.time() - start_time) < 2:
                continue
            if (time.time() - start_time) > 15:
                return "Unknown"
            # Grab a single frame of video
            ret, frame = video_capture.read()
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        return (name)
                        face_names.append(name)
            process_this_frame = not process_this_frame
    except (Warning, Exception) as e:
        return str(e)
    finally:
        video_capture.release()

def serial_read():
    while True:
        with serial.Serial('/dev/ttyS0', 115200, timeout=1) as ser:
            # temp, ldr, ir = (ser.readline().decode("utf-8")).split(',')
            print(ser.readline().decode("utf-8"))

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

def get_stonks():
    intrinio_sdk.ApiClient().configuration.api_key['api_key'] = "OmM0NjI0Y2IyMjEyOGYxNjgyMjJmY2U2YWZhZmIyNTk2"
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
    r = requests.get('https://programming-quotes-api.herokuapp.com/quotes')
    quoteObj = json.loads(r.text)
    return quoteObj
#############################################
class Stonks(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, background="BLACK")

        self.stonks = ""
        self.label_stonks = Label(self, font="dreams 13", bg="BLACK", fg="WHITE")
        self.label_stonks.pack(side=BOTTOM, anchor="n")

        self.stonksIconLbl = Label(self, font="dreams 13", bg="BLACK", fg="WHITE")
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
        self.label_mail = Label(self, font="dreams 11", bg="BLACK", fg="WHITE")
        self.label_mail.pack(side=BOTTOM, anchor="n")

        self.mailIconLbl = Label(self, font="dreams 11", bg="BLACK", fg="WHITE")
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
        self.label_news = Label(self, font="dreams 11", bg="BLACK", fg="WHITE")
        self.label_news.pack(side=BOTTOM, anchor="n")

        self.newsIconLbl = Label(self, font="dreams 11", bg="BLACK", fg="WHITE")
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
        self.label_time = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
        self.label_time.pack(side=TOP, anchor="e")

        self.day1 = ""
        self.label_day = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
        self.label_day.pack(side=TOP, anchor="e")

        self.day_of_the_week1 = ""
        self.label_day_of_the_week = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
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

        self.weatherIconLbl = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
        self.weatherIconLbl.pack(side=TOP, anchor="w")
        self.icon_location = './icons/weatherIcon.png'

        self.temperature = ""
        self.label_temperature = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
        self.label_temperature.pack(side=TOP, anchor="w")

        self.humidity= ""
        self.label_humidity = Label(self, font = "dreams 20", bg="BLACK", fg="WHITE")
        self.label_humidity.pack(side=TOP, anchor="w")

        self.location = ""
        self.label_location = Label(self, font="dreams 20", bg="BLACK", fg="WHITE")
        self.label_location.pack(side=TOP, anchor="w")

        self.update_weatherloc()
        
    def update_weatherloc(self):
        latitude, longitude, address = get_location()
        humidity, temperature, pressure = get_weather(latitude, longitude)
        img = Image.open(self.icon_location)
        img = img.resize((45, 45), Image.ANTIALIAS)
        img = img.convert('RGB')
        pic = ImageTk.PhotoImage(img)
        self.weatherIconLbl.config(image=pic, bg="black")
        self.weatherIconLbl.image = pic
        self.label_temperature.config(text=str(temperature) + ' ' + degree_sign + 'C')
        self.label_humidity.config(text='Humidity: ' + str(humidity) + '%')
        self.label_location.config(text=address)
        self.after(600000, self.update_weatherloc)

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

        self.greeting = Label(self.root, text="Welcome, " + name, font="Helvetica 43", bg="BLACK", fg="WHITE")
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
        a = getQuote()
        if len(a) == 0:
            quote = "It was what it was. It is what it is. It will be what it will be."
            author = "Team1"
        else:
            i = random.randint(0, 10)
            if i < len(a) and len(a[i]['en']) < 160:
                quote = a[i]['en']
                author = a[i]['author']
            elif len(a[0]['en']) < 160:
                quote = a[0]['en']
                author = a[0]['author']
            else:
                quote = "It was what it was. It is what it is. It will be what it will be."
                author = "Team1"
        self.quote = Label(self.root, text=(30 * "\n" + quote), font="Helvetica 14", bg="BLACK", fg="WHITE")
        self.author = Label(self.root, text=(author + "\n\n\n\n"), font="Helvetica 14", bg="BLACK", fg="WHITE")
        self.quote.pack()
        self.author.pack()
        self.stonks.pack()
        # self.serial_parser()
        
def main():
    print("started")
    while True:
        state = "SLEEP"
        time.sleep(0.1)
        try:
            with serial.Serial('/dev/ttyS0', 115200, timeout=15) as ser:
                temp, ir, ldr = (ser.readline().decode("utf-8")).split(',')
                if float(ir) < 0.5:
                    print("Detected wake request")
                    name = detect_face()
                    print(name)
                    if name in known_face_names:
                        state = "ACTIVE_NORMAL"
                        print("Starting dashboard", name)
                        start = Final(name)
                        start.root.mainloop()
        except (Exception, Warning) as e:
            pass
      
            
start = Final()
start.root.mainloop()
