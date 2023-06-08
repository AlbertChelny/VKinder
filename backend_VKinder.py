from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError


class VkTools():
    def __init__(self, token_vu):
        self.vkapi = vk_api.VkApi(token=token_vu)

    def _bdate_to_year(self, bdate):
        now = datetime.now().year
        if len(bdate.split('.')) == 3:
            user_year = bdate.split('.')[2]
            return now - int(user_year)
        else:
            user_year = '0'
            return user_year

    def get_profile_info(self, user_id):
        try:
            info, = self.vkapi.method('users.get',
                                    {'user_id': user_id,
                                    'fields': 'bdate, city, sex, relation'
                                    }
                                    )
        except ApiError as ae:
            info = {}
            print(f'Error = {ae}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if 'first_name' in info and 'last_name' in info else None,
                     'id': info.get('id'),
                     'bdate': self._bdate_to_year(info.get('bdate')),
                     'city': info.get('city')['title'] if info.get('city') is not None else None,
                     'sex': info.get('sex')
                     }
        return result

    def search_users(self, params, offset, age_f, age_t, stat_f, online_us):
        try:
            found_users = self.vkapi.method('users.search',
                                      {'count': 45,
                                       'offset': offset,
                                       'hometown': params['city'],
                                       'sex': 1 if params['sex'] == 2 else 2,
                                       'has_photo': True,
                                       'age_from': params['bdate'] - int(age_f),
                                       'age_to': params['bdate'] + int(age_t),
                                       'status': stat_f,
                                       'online': online_us
                                       }
                                       )
        except ApiError as ae:
            found_users = []
            print(f'Error = {ae}')
        result = [{'name': item['first_name'] + ' ' + item['last_name'],
                   'id': item['id']} for item in found_users['items'] if item['is_closed'] is False]
        return result

    def get_photos(self, user_id):
        try:
            photos = self.vkapi.method('photos.get',
                                    {'owner_id': user_id,
                                    'album_id': 'profile',
                                    'extended': 1
                                    }
                                    )
        except ApiError as ae:
            photos = {}
            print(f'Error = {ae}')

        result = [{'owner_id': item['owner_id'],
                   'id': item['id'],
                   'likes': item['likes']['count'],
                   'comments': item['comments']['count'],
                   } for item in photos['items']]
        result.sort(key=lambda x: (x['likes'], x['comments']), reverse=True)
        return result[:3]


    def check_like(self, params, user_id, id):
        try:
            like_check = self.vkapi.method('likes.isLiked',
                                        {'user_id': params['id'],
                                        'type': 'photo',
                                        'owner_id': user_id,
                                        'item_id': id
                                        }
                                        )
        except ApiError as ae:
            like_check = {}
            print(f'Error = {ae}')
        return like_check

    def add_like(self, user_id, id):
        try:
            like_add = self.vkapi.method('likes.add',
                                        {'type': 'photo',
                                        'owner_id': user_id,
                                        'item_id': id
                                        }
                                        )
        except ApiError as ae:
            like_add = {}
            print(f'Error = {ae}')
        return like_add
