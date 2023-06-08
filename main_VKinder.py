import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from backend_VKinder import VkTools
from database_VKinder import create_engine, Base, add_user, check_user
from datetime import datetime
from settings import token_vg, token_vu, DSN


class VKinder():

    def __init__(self, token_vg, token_vu):
        self.vk_interface = vk_api.VkApi(token=token_vg)
        self.longpoll = VkLongPoll(self.vk_interface)
        self.vk_tools = VkTools(token_vu)
        self.offset = 0
        self.age_f = 0
        self.age_t = 0
        self.city = ''
        self.stat_f = None
        self.online_us = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk_interface.method('messages.send',
                              {'user_id': user_id,
                               'message': message,
                               'attachment': attachment,
                               'random_id': get_random_id()
                               }
                              )

    def event_message(self, user_id, text):
        self.message_send(user_id, text)
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                value = event.text.lower()
                return value

    def check_add_database(self, user_id, found_users):
        found_user = self.found_users.pop()
        while check_user(engine, user_id, found_user['id']) == True:
            if len(self.found_users) == 0:
                while len(self.found_users) == 0:
                    self.offset += 45
                    self.found_users = self.vk_tools.search_users(self.params, self.offset, self.age_f, self.age_t, self.stat_f, self.online_us)
            found_user = self.found_users.pop()
        photos_user = self.vk_tools.get_photos(found_user['id'])

        count = 0
        for photo in photos_user:
            count += 1
            photo_string = f'photo{photo["owner_id"]}_{photo["id"]}'
            check_like = self.vk_tools.check_like(self.params, photo["owner_id"], photo["id"])

            if check_like['liked'] == 0:
                self.message_send(user_id,
                              f'имя: {found_user["name"]} ссылка: vk.com/id{found_user["id"]}\n'
                              f'Если хотите поставить "like", нажмите "+", нет "-".',
                              attachment=photo_string)
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        answer = event.text.lower()
                        if answer == '+':
                            self.vk_tools.add_like(photo["owner_id"], photo["id"])
                        else:
                            break
                if count == len(photos_user):
                    self.message_send(user_id, f'Для продолжения поиска напишите "искать".')

            elif check_like['liked'] == 1:
                self.message_send(user_id,
                              f'имя: {found_user["name"]} ссылка: vk.com/id{found_user["id"]}\n'
                              f'Эта фотография Вами уже отмечена ("like").',
                              attachment=photo_string)
                if count == len(photos_user):
                    self.message_send(user_id, f'Для продолжения поиска напишите "искать".')

        add_user(engine, user_id, found_user['id'])

    def event_handler(self):

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                self.params = self.vk_tools.get_profile_info(event.user_id)

                if command == 'привет':
                    self.message_send(event.user_id, f'Приятно познакомиться,  {self.params["name"]}!')

                    if self.params['bdate'] == '0':
                        text = f'{self.params["name"]} напишите сколько Вам лет.\n'
                        year = self.event_message(event.user_id, text)
                        self.params['bdate'] = int(year)

                    if self.age_f == 0 and self.age_t == 0:
                        text = f'{self.params["name"]} напишите диапазон поиска (пример написания: 5%2, т.е. на 5 лет ' \
                               f'младше, и на 2 года старше).\n'
                        range_year = self.event_message(event.user_id, text)
                        self.age_f = range_year.split('%')[0]
                        self.age_t = range_year.split('%')[1]

                    if self.city == '':
                        text = f'{self.params["name"]} напишите в каком городе искать.\n'
                        ev_city = self.event_message(event.user_id, text)
                        self.params['city'] = ev_city

                    if self.params['sex'] == '':
                        text = f'{self.params["name"]} укажите Ваш пол цифрой (1 - женский, 2 - мужской).\n'
                        ev_sex = self.event_message(event.user_id, text)
                        self.params['sex'] = int(ev_sex)

                    if self.stat_f == None:
                        text = f'{self.params["name"]} Выберите семейное положение для поиска. Возможные значения:\n ' \
                               f'1 - не женат (не замужем),\n 2 - встречается,\n 3 - помолвлен(-а),\n 4 - женат (' \
                               f'замужем),\n 5 - всё сложно,\n 6 - в активном поиске,\n 7 - влюблен(-а),' \
                               f'\n 8 - в гражданском браке,\n 0 - не указано.\n'
                        status = self.event_message(event.user_id, text)
                        self.stat_f = int(status)

                    if self.online_us == 0:
                        text =  f'{self.params["name"]} Учитывать ли статус «онлайн». Возможные значения:\n 1 - ' \
                                f'искать только пользователей онлайн,\n 0 - искать по всем пользователям.\n'
                        online = self.event_message(event.user_id, text)
                        self.online_us = int(online)


                    if self.params['bdate'] != datetime.now().year or self.params['city'] != '' or self.params['sex'] != '':
                        self.message_send(event.user_id, f'Чтобы начать поиск, напишите "искать".\n'
                                                         f'Чтобы остановить поиск, напишите "закончить".')

                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                command = event.text.lower()

                                if command == 'искать':
                                    self.found_users = self.vk_tools.search_users(self.params, self.offset, self.age_f, self.age_t, self.stat_f, self.online_us)
                                    self.check_add_database(event.user_id, self.found_users)

                                elif command == 'закончить':
                                    self.message_send(event.user_id, f'До свидания, {self.params["name"]}!')
                                    break

                                else:
                                    self.message_send(event.user_id, 'Команда не найдена!')

                else:
                    self.message_send(event.user_id, 'Команда не найдена!')


if __name__ == '__main__':
    engine = create_engine(DSN)
    Base.metadata.create_all(engine)
    bot = VKinder(token_vg, token_vu)
    bot.event_handler()