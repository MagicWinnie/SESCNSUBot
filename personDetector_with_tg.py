from skimage.measure import compare_ssim
import telebot
import datetime
import cv2
import time

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    if width != None: width = int(width)
    if height != None: height = int(height)
    
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
    resized = cv2.resize(image, dim, interpolation = inter)
    return resized

cap = cv2.VideoCapture(0)

_, before = cap.read()
_, after = cap.read()

i = 0

with open('tg_token.txt', 'r') as token:
    tg_token = token.readline()
# tg_token = ''

bot = telebot.TeleBot(tg_token)
start = time.time()

ids = []

with open('database.txt', 'r') as data:
    ids = data.readlines()

while True:
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

    score, diff = compare_ssim(before_gray, after_gray, full=True)
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
            x,y,w,h = cv2.boundingRect(largest_contour)
            cv2.rectangle(before, (x, y), (x + w, y + h), (36,255,12), 2)
            cv2.rectangle(after, (x, y), (x + w, y + h), (36,255,12), 2)
            
    if i >= 5 and time.time() - start > 300 and datetime.datetime.now().hour in [23] + list(range(0, 7)):
        for i in ids:
            bot.send_message(i, 'Ночной!!!')
        i = 0
        start = time.time()
        
    cv2.imshow('before', image_resize(before, width=1080/2))
    cv2.imshow('after', image_resize(after, width=1080/2))
    cv2.imshow('diff', image_resize(diff, width=1080/2))
    if cv2.waitKey(1) == 27: break

cap.release()
cv2.destroyAllWindows()