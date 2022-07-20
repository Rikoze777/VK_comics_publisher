import requests
import os
import random
from dotenv import load_dotenv


def get_last_comic_number():
    url = f'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comix_discription = response.json()
    last_number = comix_discription["num"]
    return last_number


def get_img_url_and_comment(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comic_discription = response.json()
    img_url = comic_discription["img"]
    author_comment = comic_discription["alt"]
    comic_num = comic_discription["num"]
    return img_url, author_comment, comic_num


def save_comic(img_url, comics_path, comic_num):
    os.makedirs(comics_path, exist_ok=True)
    split_url = os.path.splitext(img_url)
    head_url, extension = split_url
    img_response = requests.get(img_url)
    img_response.raise_for_status()
    comic_name = "comic_{}{}".format(comic_num, extension)
    file_path = os.path.join(comics_path, comic_name)
    with open(file_path, 'wb') as img_file:
        img_file.write(img_response.content)
    return comic_name


def get_load_discription(group_id, access_token, version):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {
        "group_id": group_id,
        "access_token": access_token,
        "v": version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    load_discription = response.json()
    return load_discription


def load_to_server(upload_url, comic_name, comics_path):
    for root, dirs, files in os.walk(comics_path):
        for file in files:
            if file == comic_name:
                img_root = os.path.join(root, file)
    with open(img_root, 'rb') as comic:
        url = upload_url
        files = {
            'photo': comic,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
        load_response = response.json()
        vk_server = load_response['server']
        vk_photo = load_response['photo']
        vk_hash = load_response['hash']
        return vk_server, vk_photo, vk_hash


def save_to_album(access_token, user_id, group_id, server,
                  photo, hash, version):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        "access_token": access_token,
        "user_id": user_id,
        "group_id": group_id,
        "server": server,
        "photo": photo,
        "hash": hash,
        "v": version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    load_discription = response.json()
    for item in load_discription['response']:
        owner_id = item['owner_id']
        media_id = item['id']
    return owner_id, media_id


def post_to_group(access_token, group_id, auth_comment,
                  owner, media_id, version):
    url = "https://api.vk.com/method/wall.post"
    attachments = f"photo{owner}_{media_id}"
    params = {
        "access_token": access_token,
        "owner_id": f"-{group_id}",
        "from_group": 1,
        "message": auth_comment,
        "attachments": attachments,
        "v": version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    response_discription = response.json()
    return response_discription


def main():
    load_dotenv()
    comics_path = os.environ.get("COMICS_PATH")
    client_id = os.environ.get("CLIENT_ID")
    secure_key = os.environ.get("SECURE_KEY")
    service_key = os.environ.get("SERVICE_KEY")
    access_token = os.environ.get("ACCESS_TOKEN")
    group_id = os.environ.get("GROUP_ID")
    api_version = os.environ.get("API_VERSION")
    user_id = os.environ.get("USER_ID")
    last_comic_number = get_last_comic_number()
    random_comic_number = random.randint(1, last_comic_number)
    img_url, auth_comment, comic_num = get_img_url_and_comment(
                                                random_comic_number)
    comic_name = save_comic(img_url, comics_path, comic_num)
    load_discription = get_load_discription(group_id, access_token,
                                            api_version)
    upload_url = load_discription['response']['upload_url']
    vk_server, vk_photo, vk_hash = load_to_server(upload_url, comic_name,
                                                  comics_path)
    owner_id, media_id = save_to_album(access_token, user_id, group_id,
                                       vk_server, vk_photo, vk_hash,
                                       api_version)
    post_to_group(access_token, group_id, auth_comment,
                  owner_id, media_id, api_version)


if __name__ == '__main__':
    main()
