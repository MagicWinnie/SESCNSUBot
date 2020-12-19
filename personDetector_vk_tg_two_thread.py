import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import skimage.metrics
import telebot
import datetime
import cv2
import time
from threading import Thread
import requests
import fileinput

with open('vk_token.txt', 'r') as token:
    vk_token = token.readline()
with open('tg_token.txt', 'r') as token:
    tg_token = token.readline()
# vk_token = ''
# tg_token = ''

vk_session = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

bot = telebot.TeleBot(tg_token)


with open('databasevk.txt', 'r') as fi:
    idsvk = fi.readlines()

with open('database.txt', 'r') as data:
    ids = data.readlines()

class Detection():
    def __init__(self):
        f = open('time.txt', 'r')
        self.list_of_time = f.readlines()

        thread = Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        global idsvk

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.text:
                if event.text == 'time':
                    if event.from_user:
                        f = open('time.txt', 'r')
                        self.list_of_time = f.readlines()
                        vk.messages.send(
                            random_id=random.randint(-2147483648, 2147483647),
                            user_id=event.user_id,
                            message='\n'.join(self.list_of_time)
                        )
                    if event.from_chat:
                        f = open('time.txt', 'r')
                        self.list_of_time = f.readlines()
                        vk.messages.send(
                            random_id=random.randint(-2147483648, 2147483647),
                            chat_id=event.chat_id,
                            message='\n'.join(self.list_of_time)
                        )
        
                if event.text == 'start':
                    if event.from_user:
                        fi = open('databasevk.txt', 'a')
                        vk.messages.send(
                            random_id=random.randint(-2147483648, 2147483647),
                            user_id=event.user_id,
                            message='Вы будете получать сообщение, когда ночной появится в зоне действия камеры'
                        )
                        fi.write(f'{event.user_id}\n')
                        fi.close()
        
                        fi = open('databasevk.txt', 'r')
                        idsvk = fi.readlines()
                        fi.close()
        
                if event.text == 'end':
                    if event.from_user:
                        for line in fileinput.input('databasevk.txt', inplace=True):
                            if int(line) == event.user_id:
                                continue
                            else:
                                print(line.rstrip('\n'))
                        vk.messages.send(
                            random_id=random.randint(-2147483648, 2147483647),
                            user_id=event.user_id,
                            message='Вы больше не будете получать сообщение, когда ночной появится в зоне действия камеры.\nЧтобы снова получать сообщения, напиши мне "start"'
                        )
                        with open('databasevk.txt', 'r') as fi:
                            idsvk = fi.readlines()


def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    if width: width = int(width)
    if height: height = int(height)

    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=inter)
    return resized

cap = cv2.VideoCapture(0)

_, before = cap.read()
_, after = cap.read()
start = time.time()
i = 0

thr = Detection()

later = 0
now = 0
cnt = 0

while True:
    timer = datetime.datetime.now()
    if later != 0:
        k = later.timestamp() - timer.timestamp()
        print(k)
        if k <= 5:
            lam = lam.replace(microsecond=0)
            lam = str(lam.time())
            if later.second - 5 < 0:
                later = later.replace(second=(later.second - 5 + 60))
                if later.minute - 1 < 0:
                    later = now.replace(minute=(later.minute - 1 + 60))
                    if later.hour - 1 < 0:
                        later = later.replace(hour=(later.hour - 1 + 24), microsecond=0)
                    else:
                        later = later.replace(hour=(later.hour - 1), microsecond=0)
                else:
                    later = later.replace(minute=(later.minute - 1), microsecond=0)
            else:
                later = later.replace(second=(later.second - 5), microsecond=0)
            later = str(later.time())
            print(lam, later)
            final = " - ".join([lam, later])
            timee = open('time.txt', 'a')
            timee.write(f'{final}\n')
            timee.close()
            later = 0
            now = 0
            cnt += 1
    _, before = cap.read()
    before = image_resize(before, height=200)
    # before = cv2.medianBlur(before, 15)
    before = cv2.fastNlMeansDenoisingColored(before, None, 10, 10, 7, 21)
    # time.sleep(0.3)
    _, after = cap.read()
    after = image_resize(after, height=200)
    # after = cv2.medianBlur(after, 15)
    after = cv2.fastNlMeansDenoisingColored(after, None, 10, 10, 7, 21)

    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    score, diff = skimage.metrics.structural_similarity(before_gray, after_gray, full=True)
    diff = (diff * 255).astype("uint8")

    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]

    if len(contour_sizes) > 0:
        largest_contour = max(contour_sizes, key=lambda x: x[0])[1]
        area = cv2.contourArea(largest_contour)
        if area > 2000:
            i += 1
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(before, (x, y), (x + w, y + h), (36, 255, 12), 2)
            cv2.rectangle(after, (x, y), (x + w, y + h), (36, 255, 12), 2)

    if i >= 3: #and datetime.datetime.now().hour in [22] + list(range(0, 7)):
        if later == 0:
            # print(2)
            now = datetime.datetime.now()
            lam = datetime.datetime.now()
            # print(now, lam)
            # print(2)
            if now.second + 7 > 59:
                later = now.replace(second=(now.second + 7 - 60))
                if now.minute + 1 > 59:
                    later = now.replace(minute=(now.minute + 1 - 60))
                    if now.hour + 1 > 23:
                        later = now.replace(hour=(now.hour + 1 - 24))
                    else:
                        later = now.replace(hour=(now.hour + 1))
                else:
                    later = now.replace(minute=(now.minute + 1))
                '''else:
                    if now.minute + 5 > 59:
                        later = now.replace(minute=(now.minute + 5 - 60))
                        if now.hour + 1 > 23:
                            later = now.replace(hour=(now.hour + 1 - 24))
                        else:
                            later = now.replace(hour=(now.hour + 1))
                    else:
                        later = now.replace(minute=(now.minute + 5))'''
            else:
                later = now.replace(second=(now.second + 7))
        else:
            # print(3)
            later = later + (later - datetime.datetime.now())
        for j in ids:
            bot.send_message(int(j), 'Ночной!!!')
        start = time.time()
        for j in idsvk:
            vk.messages.send(
                random_id=random.randint(-2147483648, 2147483647),
                user_id=int(j),
                message='Ночной!!!'
            )
        i = 0

    cv2.imshow('before', image_resize(before, width=1080 / 2))
    cv2.imshow('after', image_resize(after, width=1080 / 2))
    cv2.imshow('diff', image_resize(diff, width=1080 / 2))
    if cv2.waitKey(1) == 27: break

cap.release()
cv2.destroyAllWindows()
fi.close()
data.close()