# def jobA(num, q):
#     q.put(num * 2)

# def jobB(num, q):
#     q.put(num ^ 3)



# import multiprocessing as mp
# q = mp.Queue()
# jobs = (jobA, jobB)
# args = ((10, q), (2, q))
# for job, arg in zip(jobs, args):
#     mp.Process(target=job, args=arg).start()

# for i in range(len(jobs)):
#     print('Result of job {} is: {}'.format(i, q.get()))



import smtplib
import imghdr
from email.message import EmailMessage

Sender_Email = "sarwar.maruf9@gmail.com"
Reciever_Email = "sarwar15-8988@diu.edu.bd"
# Password = input('Enter your email account password: ')
Password = '!!!November24!!!'

newMessage = EmailMessage()                         
newMessage['Subject'] = "Emergency help needed:" 
newMessage['From'] = Sender_Email                   
newMessage['To'] = Reciever_Email                   
newMessage.set_content('Let me know what you think. Image attached!') 

files = ['Emergency_help/02-12-2021-13-40-39.png', 'Emergency_Help/02-12-2021-13-47-48.png']

for file in files:
    with open(file, 'rb') as f:
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.name
    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    
    smtp.login(Sender_Email, Password)              
    smtp.send_message(newMessage)      