#############################################
import face_recognition
import cv2
import numpy as np
from serial import Serial
from time import time
#############################################

abhay_image_1 = face_recognition.load_image_file("known_users/Abhay.jpg")
abhay_face_encoding_1 = face_recognition.face_encodings(abhay_image_1)[0]
prat_image_1 = face_recognition.load_image_file("known_users/Prat.jpg")
prat_face_encoding_1 = face_recognition.face_encodings(prat_image_1)[0]
rtvik_image_1 = face_recognition.load_image_file("known_users/Rtvik.jpg")
rtvik_face_encoding_1 = face_recognition.face_encodings(rtvik_image_1)[0]
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
   abhay_face_encoding_1,
   prat_face_encoding_1,
   rtvik_face_encoding_1,
   ishaan_face_encoding_1,
   staff1_face_encoding_1,
   staff2_face_encoding_1,
   staff3_face_encoding_1,
   staff4_face_encoding_1
]

known_face_names = [
   "Abhay",
   "Prat",
   "Rtvik",
   "Ishaan",
   "Unknown",
   "Unknown",
   "Unknown",
   "Unknown"
]
face_locations = []
face_encodings = []
face_names = []

def detect_face():
    try:
        state = "RECOG"
        start_time = time.time()
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        while True:
            if (time.time() - start_time) < 2:
                continue
            elif (time.time() - start_time) > 15:
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
        print(e)
        return "Unknown"

    finally:
        video_capture.release()

if __name__ == "__main__":
    longPress, press = False, False
    mode = "OFF" # OFF, ON
    while True:
        try:
            with Serial('/dev/ttyUSB0', 115200, timeout=15) as ser:
                _, ir, ldr = (ser.readline().decode("utf-8")).split(',')

                if mode is "ON":
                    os.system("xrandr --output HDMI-0 --brightness " + str(0.8 + float(ldr) * 0.16))

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
                            os.system("xrandr --output HDMI-0 --brightness 0.0")
                        elif mode is "OFF"
                            name = detect_face()
                            if name in known_face_names:
                                mode = "ON"

                elif (float(ir) < 4.7) and (press is True):
                    press = False
                    if (time() - start_time <= 3):
                        print("Short Press", time() - start_time)
                        if mode is "ON":
                            # Run slack thing
                            pass

        except (Warning, Exception):
            pass
