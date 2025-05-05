import argparse
import os
import sys
import io
import re
from urllib.parse import urlparse
import search_download_photo

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Лаунчер: запускает загрузчик с аргументами.")
    parser.add_argument("--url", required=True, help="Ссылка на скачивание.")
    parser.add_argument("--id", required=True, help="ID объекта (например, поста или группы).")

    def sanitize(name):
        return re.sub(r'[<>:"/\\|?*]', '_', name)
    
    args = parser.parse_args()
    parsed_url = urlparse(args.url)
    domain = sanitize(parsed_url.netloc)  # например: 'sreality.cz' → 'sreality.cz'
    folder_name = f"{args.id}_{domain}"  # например: '123_sreality.cz'
    
    media_dir = os.path.join("../static/media", folder_name)
    url = args.url

    # Создание папки media/<id>
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
        print(f"📁 Создана папка: {media_dir}")
    else:
        print(f"📁 Папка уже существует: {media_dir}")

    # Вызов функции загрузки
    if "bezrealitky.cz" in url:
        images = search_download_photo.find_images_bezrealitky(url)
            
    elif "reality.bazos.cz" in url:
        images = search_download_photo.find_images_bazos(url)
            
    elif "sreality.cz" in url:
        images = search_download_photo.find_images_sreality(url) 
            
    elif "byty.cz" in url:
        images = search_download_photo.find_images_bytycz(url)
            
    elif 'sbazar.cz' in url:
        images = search_download_photo.find_images_sbazar(url)
            
    elif 'realitymix.cz' in url:
        images = search_download_photo.find_images_realitymix(url)
            
    elif 'reality.idnes.cz' in url:
        images = search_download_photo.find_image_idnes(url)
            
    else:   
        print(f"Не поддерживаемый сайт для URL {url}")
        return
    

    
    

    for image_url in images:
        image_path = search_download_photo.download_image(image_url, media_dir)
        if image_path:
            print(f'Изображение скачано в {image_path}')

if __name__ == "__main__":
    main()
