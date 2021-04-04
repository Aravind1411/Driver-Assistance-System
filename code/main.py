import cv2 
import sys
import RPi.GPIO as GPIO
import smtplib,ssl  
from time import sleep  
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from firebase import firebase

firebase = firebase.FirebaseApplication('https://proj-cf1ae-default-rtdb.firebaseio.com/')
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml') 
count =0;
cap = cv2.VideoCapture(0)
temp=1;
temp1=1;
pizo=37
gas=40
buzzer=29
Motor=38
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pizo, GPIO.IN)
GPIO.setup(gas, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(Motor, GPIO.OUT)


def send_an_email(message):  
    toaddr = ''      # To id 
    me = ''          # your id
    subject = "What's News"              # Subject

    msg = MIMEMultipart()  
    msg['Subject'] = subject  
    msg['From'] = me  
    msg['To'] = toaddr  
    msg.preamble = message   
    msg.attach(MIMEText(message))  

    '''part = MIMEBase('application', "octet-stream")  
    part.set_payload(open("/home/pi/Downloads/sdcard.jpg", "rb").read())  
    encoders.encode_base64(part)  
    part.add_header('Content-Disposition', 'attachment; filename="saved_img.jpg"')   # File name and format name
    msg.attach(part)'''  

    try:  
       s = smtplib.SMTP('smtp.gmail.com', 587)  # Protocol
       s.ehlo()  
       s.starttls()  
       s.ehlo()  
       s.login(user = ' ', password = ' ')  # User id & password of sending email id
       #s.send_message(message)  
       s.sendmail(me, toaddr, msg.as_string())
       print("Done")
       s.quit()  
    #except:  
    #   print ("Error: unable to send email")    
    except SMTPException as error:  
          print ("Error")                # Exception

while(1):
    input_state = str(GPIO.input(pizo))
    input_state1 = str(GPIO.input(gas))
    GPIO.output(Motor,1)
    print("Pizo:"+input_state)
    print("gas :"+input_state1)
    if(GPIO.input(pizo)==1):
        GPIO.output(Motor,0)
        send_an_email("Accident Occured")
        GPIO.output(buzzer,1)
        sleep(3)
        GPIO.output(buzzer,0)
        result = firebase.put('/driver/', 'status',str("Accident Occured"))
    if(GPIO.input(gas)==0):
        GPIO.output(Motor,0)
        send_an_email("Drunken")
        GPIO.output(buzzer,1)
        sleep(2)
        GPIO.output(buzzer,0)
        result = firebase.put('/driver/', 'status',str("Drunken"))
    ret, img = cap.read() 
    resize_img=cv2.resize(img,(640,480))
    gray = cv2.cvtColor(resize_img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    cv2.imshow('img',resize_img)
    for (x,y,w,h) in faces:
        cv2.rectangle(resize_img,(x,y),(x+w,y+h),(255,255,0),2) 
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = resize_img[y:y+h, x:x+w]
        temp=1;
        eyes = eye_cascade.detectMultiScale(roi_gray) 
        cv2.imshow('img',resize_img)

        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)
            cv2.imshow('img',resize_img)
            #print ('eye detected')
            count=0;
            temp=0;

        if (temp==1):
            count = count+1
            print (count)
            if count>5:
                print('Sleeping')
                GPIO.output(Motor,0)
                send_an_email("Sleeping")
                result = firebase.put('/driver/', 'status',str("Sleeping"))
                GPIO.output(buzzer,1)
                sleep(1)
                GPIO.output(buzzer,0)
                count=0;


    k = cv2.waitKey(30) & 0xff
    if k == 27:
       break
cap.release()
GPIO.output(Motor,0)
GPIO.cleanup()  
cv2.destroyAllWindows() 

