#############################################
import face_recognition
import cv2
import numpy as np
import serial
from time import time, sleep
import slack_send
import sys, os
#############################################

stime = time()
degree_sign = u'\N{DEGREE SIGN}'
rtvik_image_1 = face_recognition.load_image_file("known_users/Rtvik.jpg")
rtvik_face_encoding_1 = face_recognition.face_encodings(rtvik_image_1)[0]
abhay_image_1 = face_recognition.load_image_file("known_users/Abhay.jpg")
abhay_face_encoding_1 = face_recognition.face_encodings(abhay_image_1)[0]
prat_image_1 = face_recognition.load_image_file("known_users/Prat.jpg")
prat_face_encoding_1 = face_recognition.face_encodings(prat_image_1)[0]
ishaan_image_1 = face_recognition.load_image_file("known_users/Ishaan.jpg")
ishaan_face_encoding_1 = face_recognition.face_encodings(ishaan_image_1)[0]
staff1_image_1 = face_recognition.load_image_file("known_users/staff1.jpg")
staff1_face_encoding_1 = face_recognition.face_encodings(staff1_image_1)[0]
staff2_image_1 = face_recognition.load_image_file("known_users/staff2.jpg")
staff2_face_encoding_1 = face_recognition.face_encodings(ishaan_image_1)[0]
staff3_image_1 = face_recognition.load_image_file("known_users/staff3.jpg")
staff3_face_encoding_1 = face_recognition.face_encodings(staff3_image_1)[0]
staff4_image_1 = face_recognition.load_image_file("known_users/staff4.jpg")
staff4_face_encoding_1 = face_recognition.face_encodings(staff4_image_1)[0]

known_face_encodings = [
   rtvik_face_encoding_1,
   abhay_face_encoding_1,
   prat_face_encoding_1,
   ishaan_face_encoding_1,
   staff1_face_encoding_1,
   staff2_face_encoding_1,
   staff3_face_encoding_1,
   staff4_face_encoding_1
]

known_face_names = [
   "Rtvik",
   "Abhay",
   "Prat",
   "Ishaan",
   "Unknown",
   "Unknown",
   "Unknown",
   "Unknown"
]
face_locations = []
face_encodings = []
face_names = []
print("Done in ", time() - stime)

def detect_face():
    video_capture = cv2.VideoCapture(0)
    try:
        start_time = time()
        process_this_frame = True

        while True:
            run_time = time() - start_time
            if run_time < 2:
                continue
            elif run_time > 15:
                return None
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

                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        return name
                        
            process_this_frame = not process_this_frame

    except (Warning, Exception) as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(e, exc_type, fname, exc_tb.tb_lineno)
    
    finally:
        video_capture.release()


if __name__ == "__main__":
    print("ere")
    longPress, press = False, False
    mode = "OFF" # OFF, ON
    while True:
        try:
            wait = 0
            with serial.Serial('/dev/ttyUSB0', 115200, timeout=15) as ser:
                temperature, ldr, ir = (ser.readline().decode("utf-8")).split(',')

                if mode is "ON":
                    os.system("xrandr --output HDMI-0 --brightness " + str(0.8 + float(ldr) * 0.16))

                if float(temperature) > 35 and float(temperature) < 50:
                    slack_send.send_message("Temperature exceeding normal levels: " + temperature + ' ' + degree_sign + 'C')

                if (float(ir) < 4.7) and (press is False):
                    press = True
                    longPress = False
                    start_time = time()

                elif (press is True) and (longPress is False):
                    if time() - start_time > 3:
                        longPress = True
                        print("Long Press", time() - start_time)
                        if mode is "ON":
                            mode = "OFF"
                            os.system("xrandr --output HDMI-0 --brightness 0.3")
                        elif mode is "OFF":
                            name = detect_face()
                            if (name in known_face_names) and (name is not "Unknown"):
                                mode = "ON"
                            else:
                                pass
                                # slack_send.send_message("Unauthorized access attempt")

                elif (float(ir) < 4.7) and (press is True):
                    press = False
                    if (time() - start_time <= 3):
                        print("Short Press", time() - start_time)
                        if mode is "ON":
                            slack_send.send_message(message="")
                            pass

        except (serial.SerialException, serial.SerialTimeoutException):
            wait = 0.1
        except (ValueError):
            wait = 0.1
        except (Warning, Exception) as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(e, exc_type, fname, exc_tb.tb_lineno)
        finally:
            sleep(wait)
