with open('token_vk.txt', 'r') as file_object:
    token_vk = file_object.read().strip()

with open('token_ya.txt', 'r') as file_object:
    token_ya = file_object.read().strip()

import time
import requests
import json
from tqdm import tqdm
from pprint import pprint

class YaUploader:

    def __init__(self, token):
        assert isinstance(token, object)
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def newfolder(self, folder_name: str):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {"path": folder_name}
        response = requests.put(url, headers=headers, params=params)
        print(type(response))
        pprint(response.json())

    def upload_for_url(self, path_upload: str, url_upload: str):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": path_upload, "url": url_upload}
        requests.post(url,headers=headers, params=params)

class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def user_info(self, id):
        user_info_url = self.url + 'users.get'
        user_info_params = {
            'user_ids': id
        }

        res_user_info = requests.get(user_info_url, params={**self.params, **user_info_params})
        return res_user_info.json()

    def photo_info(self, id, album, photo_count='5', ex='1'):
        photo_info_url = self.url + 'photos.get'
        photo_info_params = {
            'owner_id': id,
            'album_id': album,
            'extended': ex,
            'count': photo_count,
        }

        res_photo_info = requests.get(photo_info_url, params={**self.params, **photo_info_params})
        return res_photo_info.json()

    def create_files_list(self, file_photo_info):
        files_list = []
        for key, value in file_photo_info.items():
            file_names = []
            for element in value['items']:
                new_element = {'file_name':'', 'size':'', 'url':''}
                if str(element['likes']['count']) in file_names:
                    data = time.localtime(element['date'])
                    data_str = time.strftime('%Y_%m_%d', data)
                    name = str(element['likes']['count']) + '_' + data_str
                else:
                    name = str(element['likes']['count'])
                new_element['file_name'] = name + '.jpg'
                file_names.append(name)
                new_element['size'] = element['sizes'][-1]['type']
                new_element['url'] = element['sizes'][-1]['url']
                files_list.append(new_element)
            print(file_names)
        print('==================')
        return files_list

if __name__ == '__main__':

    user_id = '1'

    vk_client = VkUser(token_vk, '5.131')
    user_info = vk_client.user_info(user_id)
    photo_info = vk_client.photo_info(user_id, 'profile')
    pprint(user_info)
    pprint(photo_info)
    list_for_download = vk_client.create_files_list(photo_info)

    ya_disk = YaUploader(token_ya)
    new_folder_name = user_info['response'][0]['first_name'] + ' ' + user_info['response'][0]['last_name']
    result = ya_disk.newfolder(new_folder_name)

    for photo_download in tqdm(list_for_download):
        file_name_download = photo_download['file_name']
        result_upload_url = ya_disk.upload_for_url(f'{new_folder_name}/{file_name_download}', photo_download['url'])
        del photo_download['url']

    with open('final_file_' + user_id + '.json', 'w') as write_file:
        json.dump(list_for_download, write_file)



