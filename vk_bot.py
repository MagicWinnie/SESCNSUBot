import random
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import fileinput
import os

with open('vk_token.txt', 'r') as token:
    vk_token = token.readline()
# vk_token = ''

vk_session = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

if 'databasevk.txt' not in os.listdir('.'):
    with open('databasevk.txt', 'w') as fi:
        pass

if 'time.txt' not in os.listdir('.'):
    with open('time.txt', 'w') as fi:
        pass
    
with open('databasevk.txt', 'r') as fi:
    idsvk = fi.readlines()

f = open('time.txt', 'r')
list_of_time = f.readlines()

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.text:
        if event.text == 'time':
            if event.from_user:
                f = open('time.txt', 'r')
                list_of_time = f.readlines()
                vk.messages.send(
                    random_id=random.randint(-2147483648, 2147483647),
                    user_id=event.user_id,
                    message='Данных нет' if len(list_of_time)==0 else '\n'.join(list_of_time)
                )
            if event.from_chat:
                f = open('time.txt', 'r')
                list_of_time = f.readlines()
                vk.messages.send(
                    random_id=random.randint(-2147483648, 2147483647),
                    chat_id=event.chat_id,
                    message='Данных нет' if len(list_of_time)==0 else '\n'.join(list_of_time)
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

fi.close()
data.close()