from django.shortcuts import render,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse
from django.db.models import Q
from .models import Filter, Camera
import cv2
import time
import datetime
import pygame
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt
import smtplib
import imghdr
from email.message import EmailMessage
import os
from twilio.rest import Client
from photos.models import Category, Photo


def control(request):
    return render(request,'control.html')


def searchposts(request):
    if request.method == 'GET':
        query= request.GET.get('q')

        submitbutton= request.GET.get('submit')

        if query is not None:
            lookups= Q(title__icontains=query) | Q(content__icontains=query)

            results= Camera.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton}

            return render(request, 'search.html', context)

        else:
            return render(request, 'search.html')

    else:
        return render(request, 'search.html')


def setcookie(request):
    response = HttpResponse("Cookie Set")
    response.set_cookie('java-tutorial', 'http://127.0.0.1:8001/')
    return response

def getcookie(request):
    tutorial  = request.COOKIES['java-tutorial']
    return HttpResponse("java tutorials @: "+  tutorial);

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })





def destroy(request,id):
    camera = Camera.objects.get(id=id)
    camera.delete()
    return redirect('home')

def full(request,id):
    camera_data = Camera.objects.get(id=id)
    print(camera_data.id)
    camera = camera_data.ip
    camera_id = camera_data.id

    return render(request,'full.html',{'camera':camera,'camera_id':camera_data.id})


def add_camera(request):
    if request.method == "POST":
        camera = Camera()
        camera.ip = request.POST['ip']
        camera.name = request.POST['name']
        camera.authority_no = request.POST['authority_no']
        camera.authority_email = request.POST['authority_email']
        camera.save()
    else:
        return render(request,'add_camera.html')


    return render(request,'add_camera.html')

def settings(request):
    if request.method == "POST":
        if request.POST.get('filters'):
            savedata = Filter()
            savedata.filters = request.POST.get('filters')
            savedata.save()
            all_state = Filter.objects.all()

            last = Filter.objects.all().last()
            lastCam = Camera.objects.all().last()

            #for taking email and phone number
            camera_data = Camera.objects.all().last()
            print("this Camera data:",camera_data.ip)


            print(type(lastCam))
            print("This is last added object:", last)
            print("This is last added items:", last.filters)
            print("type of last items:", type(last.filters))


            cap = cv2.VideoCapture(camera_data.ip)

            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            body_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_fullbody.xml")

            detection = False
            detection_stopped_time = None
            timer_started = False
            SECONDS_TO_RECORD_AFTER_DETECTION = 5

            frame_size = (int(cap.get(3)), int(cap.get(4)))
            # fourcc = cv2.VideoWriter_fourcc(*"mp4v") *'X264'
            fourcc = cv2.VideoWriter_fourcc(*"X264") 

            while True:
                last = Filter.objects.all().last()
                a = last.filters
                if 'human' in a:
                    _, frame = cap.read()

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    bodies = face_cascade.detectMultiScale(gray, 1.3, 5)
                    print("finding human")

                    if len(faces) + len(bodies) > 0:
                        if detection:
                            timer_started = False
                        else:
                            detection = True
                            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                            out = cv2.VideoWriter(
                                f"project/static/human/{current_time}.mp4", fourcc, 20, frame_size)
                            print("Started Recording!")
                    elif detection:
                        if timer_started:
                            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                                detection = False
                                timer_started = False
                                out.release()
                                print('Stop Recording!')

                                account_sid = 'AC7ada844a2a5d01b3430de1f0946565f8'
                                auth_token = '5e8310bb7ef7d757ef2c0fd1327f74bd'
                                nopas = '!!!November24!!!'
                                client = Client(account_sid, auth_token)

                                client.api.account.messages.create(
                                    to= camera_data.authority_no,
                                    from_="+12674946490",
                                    body= f"Someone entered a protected area without proper permission. Location: {camera_data.name}")

                                Sender_Email = "sarwar.maruf9@gmail.com"
                                Reciever_Email = camera_data.authority_email
                                # Password = input('Enter your email account password: ')
                                Password = nopas

                                newMessage = EmailMessage()                         
                                newMessage['Subject'] = "Unauthorized Person found" 
                                newMessage['From'] = Sender_Email                   
                                newMessage['To'] = Reciever_Email                   
                                newMessage.set_content(f'Someone entered a protected area without proper permission. Location: {camera_data.name}') 

                                # files = [f"Emergency_Help/{current_time}.png"]

                                # for file in files:
                                #     with open(file, 'rb') as f:
                                #         image_data = f.read()
                                #         image_type = imghdr.what(f.name)
                                #         image_name = f.name
                                #     newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    
                                    smtp.login(Sender_Email, Password)              
                                    smtp.send_message(newMessage)

                        else:
                            timer_started = True
                            detection_stopped_time = time.time()

                    if detection:
                        out.write(frame)

                    # for (x, y, width, height) in faces:
                    #    cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)

                    # cv2.imshow("Camera", frame)

                    if 'human' not in a:
                        break
                
                
                elif "emergency" in a:
                    mp_hands = mp.solutions.hands

                    # Set up the Hands functions for images and videos.
                    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5)
                    hands_videos = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

                    # Initialize the mediapipe drawing class.
                    mp_drawing = mp.solutions.drawing_utils


                    def detectHandsLandmarks(image, hands, draw=False, display = True):
                        '''
                        This function performs hands landmarks detection on an image.
                        Args:
                            image:   The input image with prominent hand(s) whose landmarks needs to be detected.
                            hands:   The Hands function required to perform the hands landmarks detection.
                            draw:    A boolean value that is if set to true the function draws hands landmarks on the output image. 
                            display: A boolean value that is if set to true the function displays the original input image, and the output 
                                    image with hands landmarks drawn if it was specified and returns nothing.
                        Returns:
                            output_image: A copy of input image with the detected hands landmarks drawn if it was specified.
                            results:      The output of the hands landmarks detection on the input image.
                        '''
                        
                        # Create a copy of the input image to draw landmarks on.
                        output_image = image.copy()
                        
                        # Convert the image from BGR into RGB format.
                        imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        
                        # Perform the Hands Landmarks Detection.
                        results = hands.process(imgRGB)
                        
                        # Check if landmarks are found and are specified to be drawn.
                        if results.multi_hand_landmarks and draw:
                            
                            # Iterate over the found hands.
                            for hand_landmarks in results.multi_hand_landmarks:
                                
                                # Draw the hand landmarks on the copy of the input image.
                                mp_drawing.draw_landmarks(image = output_image, landmark_list = hand_landmarks,
                                                        connections = mp_hands.HAND_CONNECTIONS,
                                                        landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,255),
                                                                                                    thickness=2, circle_radius=2),
                                                        connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0),
                                                                                                        thickness=2, circle_radius=2))
                        
                        # Check if the original input image and the output image are specified to be displayed.
                        if display:
                            
                            # Display the original input image and the output image.
                            plt.figure(figsize=[15,15])
                            plt.subplot(121);plt.imshow(image[:,:,::-1]);plt.title("Original Image");plt.axis('off');
                            plt.subplot(122);plt.imshow(output_image[:,:,::-1]);plt.title("Output");plt.axis('off');
                            
                        # Otherwise
                        else:
                            
                            # Return the output image and results of hands landmarks detection.
                            return output_image, results      


                    # Read a sample image and perform hands landmarks detection on it.
                    # image = cv2.imread('media/sample.jpg')
                    # detectHandsLandmarks(image, hands, display=True)
                    
                    def countFingers(image, results, draw=True, display=True):
                        '''
                        This function will count the number of fingers up for each hand in the image.
                        Args:
                            image:   The image of the hands on which the fingers counting is required to be performed.
                            results: The output of the hands landmarks detection performed on the image of the hands.
                            draw:    A boolean value that is if set to true the function writes the total count of fingers of the hands on the
                                    output image.
                            display: A boolean value that is if set to true the function displays the resultant image and returns nothing.
                        Returns:
                            output_image:     A copy of the input image with the fingers count written, if it was specified.
                            fingers_statuses: A dictionary containing the status (i.e., open or close) of each finger of both hands.
                            count:            A dictionary containing the count of the fingers that are up, of both hands.
                        '''
                        
                        # Get the height and width of the input image.
                        height, width, _ = image.shape
                        
                        # Create a copy of the input image to write the count of fingers on.
                        output_image = image.copy()
                        
                        # Initialize a dictionary to store the count of fingers of both hands.
                        count = {'RIGHT': 0, 'LEFT': 0}
                        
                        # Store the indexes of the tips landmarks of each finger of a hand in a list.
                        fingers_tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                            mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.PINKY_TIP]
                        
                        # Initialize a dictionary to store the status (i.e., True for open and False for close) of each finger of both hands.
                        fingers_statuses = {'RIGHT_THUMB': False, 'RIGHT_INDEX': False, 'RIGHT_MIDDLE': False, 'RIGHT_RING': False,
                                            'RIGHT_PINKY': False, 'LEFT_THUMB': False, 'LEFT_INDEX': False, 'LEFT_MIDDLE': False,
                                            'LEFT_RING': False, 'LEFT_PINKY': False}
                       
                        # Iterate over the found hands in the image.
                        for hand_index, hand_info in enumerate(results.multi_handedness):
                            
                            # Retrieve the label of the found hand.
                            hand_label = hand_info.classification[0].label
                            
                            # Retrieve the landmarks of the found hand.
                            hand_landmarks =  results.multi_hand_landmarks[hand_index]
                            
                            # Iterate over the indexes of the tips landmarks of each finger of the hand.
                            for tip_index in fingers_tips_ids:
                                
                                # Retrieve the label (i.e., index, middle, etc.) of the finger on which we are iterating upon.
                                finger_name = tip_index.name.split("_")[0]
                                
                                # Check if the finger is up by comparing the y-coordinates of the tip and pip landmarks.
                                if (hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y):
                                    
                                    # Update the status of the finger in the dictionary to true.
                                    fingers_statuses[hand_label.upper()+"_"+finger_name] = True
                                    
                                    # Increment the count of the fingers up of the hand by 1.
                                    count[hand_label.upper()] += 1
                            
                            # Retrieve the y-coordinates of the tip and mcp landmarks of the thumb of the hand.
                            thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
                            thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 2].x
                            
                            # Check if the thumb is up by comparing the hand label and the x-coordinates of the retrieved landmarks.
                            if (hand_label=='Right' and (thumb_tip_x < thumb_mcp_x)) or (hand_label=='Left' and (thumb_tip_x > thumb_mcp_x)):
                                
                                # Update the status of the thumb in the dictionary to true.
                                fingers_statuses[hand_label.upper()+"_THUMB"] = True
                                
                                # Increment the count of the fingers up of the hand by 1.
                                count[hand_label.upper()] += 1
                        
                        # Check if the total count of the fingers of both hands are specified to be written on the output image.
                        if draw:

                            # Write the total count of the fingers of both hands on the output image.
                            # cv2.putText(output_image, " Count: ", (10, 25),cv2.FONT_HERSHEY_COMPLEX, 1, (20,255,155), 2)
                            # cv2.putText(output_image, str(sum(count.values())), (width//2-150,240), cv2.FONT_HERSHEY_SIMPLEX,
                            #             8.9, (20,255,155), 10, 10)
                            cv2.putText(output_image, f" Location:{camera_data.name}", (10, 25),cv2.FONT_HERSHEY_COMPLEX, 1, (20,255,155), 2)
                            # cv2.putText(output_image, str(sum(count.values())), (width//2-150,240), cv2.FONT_HERSHEY_SIMPLEX,
                            #             8.9, (20,255,155), 10, 10)


                        # Check if the output image is specified to be displayed.
                        if display:
                            
                            # Display the output image.
                            plt.figure(figsize=[10,10])
                            plt.imshow(output_image[:,:,::-1])
                        
                        # Otherwise
                        else:

                            # Return the output image, the status of each finger and the count of the fingers up of both hands.
                            return output_image, fingers_statuses, count


                    # Initialize the VideoCapture object to read from the webcam.
                    camera_video = cv2.VideoCapture(camera_data.ip)
                    camera_video.set(3,1280)
                    camera_video.set(4,960)
                    img_counter = 0

                    # Create named window for resizing purposes.
                    cv2.namedWindow('Fingers Counter', cv2.WINDOW_NORMAL)
                    time_flag = True
                    t = time.time()

                    # Iterate until the webcam is accessed successfully.
                    while camera_video.isOpened() and 'emergency' in a:
                        last = Filter.objects.all().last()
                        a = last.filters
                        count = {'x': 0, 'y':0}
                        
                        # Read a frame.
                        ok, frame = camera_video.read()
                        
                        # Check if frame is not read properly then continue to the next iteration to read the next frame.
                        if not ok:
                            continue
                        
                        # Flip the frame horizontally for natural (selfie-view) visualization.
                        frame = cv2.flip(frame, 1)
                        
                        # Perform Hands landmarks detection on the frame.
                        frame, results = detectHandsLandmarks(frame, hands_videos, display=False)
                        
                        # Check if the hands landmarks in the frame are detected.
                        if results.multi_hand_landmarks:
                                
                            # Count the number of fingers up of each hand in the frame.
                            frame, fingers_statuses, count = countFingers(frame, results, display=False)


                        count = sum(count.values())
                                    
                        # # Display the frame.
                        # cv2.imshow('Fingers Counter', frame)
                        print(count)
                        if count == 10 and ((time.time()-t)>=30 or time_flag ==True) :
                            time_flag= False
                            captured_image = cv2.copyMakeBorder(src=frame, top=5, bottom=5, left=5, right=5, borderType=cv2.BORDER_CONSTANT, value=(255,255,255))
                            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
                            # out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20, frame_size)
                            
                            cv2.imwrite(f"Emergency_Help/{current_time}.png", captured_image)
                            # category = Category.objects.get(id = '8' )

                            # category = Category.objects.get_or_create(
          
                                      #     name = data['Emergency Help']
                            # )
                            # description = f'someone needs emergecny help in {camera_data.name}'
                            # photo = Photo.objects.create(
                            #     category = category,
                            #     description = description,
                            #     image = captured_image,
                            # )

                            # print(a)
                            # account_sid = os.environ['AC7ada844a2a5d01b3430de1f0946565f8']
                            # auth_token = os.environ['5e8310bb7ef7d757ef2c0fd1327f74bd']
                            account_sid = 'AC7ada844a2a5d01b3430de1f0946565f8'
                            auth_token = '5e8310bb7ef7d757ef2c0fd1327f74bd'
                            nopas = '!!!November24!!!'
                            client = Client(account_sid, auth_token)

                            client.api.account.messages.create(
                                to= camera_data.authority_no,
                                from_="+12674946490",
                                body= f"Somebody needs help! Check you email. At this moment, He is in {camera_data.name}")
                                
                            Sender_Email = "sarwar.maruf9@gmail.com"
                            Reciever_Email = camera_data.authority_email
                            # Password = input('Enter your email account password: ')
                            Password = nopas

                            newMessage = EmailMessage()                         
                            newMessage['Subject'] = "Emergency help needed:" 
                            newMessage['From'] = Sender_Email                   
                            newMessage['To'] = Reciever_Email                   
                            newMessage.set_content(f'He/She needs emergency help. Image attached! Location: {camera_data.name}') 

                            files = [f"Emergency_Help/{current_time}.png"]

                            for file in files:
                                with open(file, 'rb') as f:
                                    image_data = f.read()
                                    image_type = imghdr.what(f.name)
                                    image_name = f.name
                                newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                
                                smtp.login(Sender_Email, Password)              
                                smtp.send_message(newMessage)  




                            t = time.time()
                            # Capture an image and store it in the disk.
                            # cv2.imwrite('Emergency_Help/Captured_Image.png', captured_image)
                        
                        # Wait for 1ms. If a key is pressed, retreive the ASCII code of the key.
                        else: pass
                        k = cv2.waitKey(1) & 0xFF
                    #     a = sum(count.values())
                    #     if a == 11:
                    #         img_name = "opencv_frame_{}.png".format(img_counter)
                    #         cv2.imwrite(img_name, frame)
                    #         print("{} written!".format(img_name))
                    #         img_counter += 1
                        
                        # Check if 'ESC' is pressed and break the loop.
                        if 'emergency' not in a:
                            break

                    # Release the VideoCapture Object and close the windows.
                    camera_video.release()
                    cv2.destroyAllWindows()
                    return render(request, 'home.html') 
                
                else: 
                    cv2.destroyAllWindows()
                    return render(request, 'home.html')   
            out.release()
            cap.release()
            cv2.destroyAllWindows()
                

            
            # for all_state in all_state.iterator():
            #     print((all_state.filters))
            # print("Type is: ",type(all_state))
            # print("last you created:",Filter.objects.latest('filters'), "which is: ", Filter.objects.latest('filters'))
            return render(request, 'settings.html')
        else:
            return render(request, 'settings.html')
    else:
        return render(request, 'settings.html')

   
    return render(request, 'settings.html')


@login_required(login_url='login')
def home(request):
    username = request.user.username
    user_id = request.user.id

    print(user_id)
    print(username)

    camera = Camera.objects.all()


    return render(request,'home.html',{"camera":camera})

def signup(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.get(username=request.POST['username'])
                return render(request, 'login.html', {'error':'Username is already taken'})
            except User.DoesNotExist:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'],
                                                email = request.POST['email'])
                auth.login(request, user)
                return redirect('home')
        else:
            return render(request, 'login.html', {'error':'Password doesn\'t matched'})

    else:
        return render(request, 'login.html')

def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error':'username or password is incorrect!'})

    else:
        return render(request, 'login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')