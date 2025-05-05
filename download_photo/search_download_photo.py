import requests
import random
import re
import os
import hashlib
import cv2
import numpy as np
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright




# Функция для скачивания изображения
def download_image(url: str, folder: str, index: int = 0):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Проверяем, есть ли в URL 'bazos.cz'
            if "bazos.cz" in url:
                # Извлекаем имя файла и добавляем индекс к имени
                base_name = os.path.basename(url.split('?')[0])
                name, ext = os.path.splitext(base_name)  # Разделяем имя файла и расширение
                image_name = f"{name}_{random.randint(0, 1000)}{ext}"  # Формируем новое имя файла

            elif "sreality" in url or "sbazar" in url or 'sta-reality' in url:
                # Удаляем всё после `?`, чтобы убрать параметры
                clean_url = url.split('?')[0]

                # Получаем имя файла
                base_name = os.path.basename(clean_url)
                name, _ = os.path.splitext(base_name)  # отбросим "ложное" расширение

                # Добавим правильное расширение .jpg, так как sreality отдаёт JPEG
                image_name = f"{name}.jpg"

                # Удаляем запрещённые символы
                image_name = re.sub(r'[<>:"/\\|?*]', '_', image_name)
            else:
                base_name = os.path.basename(url.split('?')[0])  # Удаляем параметры из URL
                image_name = os.path.basename(url)

            # Дополнительная обработка для 'sreality'
            

            # Формируем полный путь для изображения
            image_path = os.path.join(folder, image_name)

            # Проверяем, превышает ли длина пути ограничение в 260 символов
            max_path_length = 260
            if len(image_path) > max_path_length:
                # Если превышает, создаём сокращённое имя с помощью хеширования
                short_name = hashlib.md5(image_name.encode()).hexdigest() + ext
                image_path = os.path.join(folder, short_name)

            # Сохраняем изображение
            with open(image_path, 'wb') as file:
                file.write(response.content)
            return image_path
        else:
            print(f"Error: Received status code {response.status_code} for {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None




# Скачивание изображений с bezrealitky.cz
def find_images_bezrealitky(url: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.find_all('div', class_='PropertyCarousel_propertyCarouselSlide__BPboJ')
        image_urls = []
        
        for container in containers:
            anchors = container.find_all('a')
            for anchor in anchors:
                if 'href' in anchor.attrs:
                    image_urls.append(anchor['href'])
        return image_urls
    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []
    


# Скачивание изображений с reality.bazos.cz
def find_images_bazos(url: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        image_urls = []

        # Находим все изображения с классом carousel-cell-image
        image_tags = soup.find_all('img', class_='carousel-cell-image')

        # Проверяем наличие хотя бы одного изображения
        if not image_tags:
            return []

        # Извлекаем первый доступный src
        first_image_src = image_tags[0]['src']

        # Извлекаем ID из первого src
        image_id = first_image_src.split('/')[-1]  # ID, например '193408447.jpg'
        image_id2 = first_image_src.split('/')[-2]  # ID, например '447'

        # Определяем базовый URL
        base_url_match = re.match(r'(https?://[^/]+)', first_image_src)
        if base_url_match:
            base_url = base_url_match.group(0)
        else:
            print("Error: Could not extract base URL")
            return []

        # Считаем количество изображений
        images_count = len(image_tags)

        # Формируем список URL с правильными номерами
        for i in range(1, images_count + 1):
            image_urls.append(f"{base_url}/img/{i}/{image_id2}/{image_id}")

        return image_urls  # Добавлен возврат списка изображений

    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []
    

headers_sreality = {
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
    "Viewport-Width": "820"
    
}


#Скачивание изображений sreality.cz
"""def find_images_sreality(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        pattern = r'\b(?:watermark|sreality)\b'
        urls = []
        divs = soup.find_all('div', class_='MuiBox-root css-suw43e')
        
        for div in divs:
            results = div.find_all('img', class_='lazyload')    
            #print(f'{results}\n')
            
            for result in results:
                img_url = result.get('data-src')  # Получаем URL изображения
                if img_url and re.search(pattern, img_url, re.IGNORECASE):  # Если URL содержит 'watermark' или 'sreality'
                    urls.append(f'https:{img_url}')
                    #print(f'Found URL: {img_url}')
 
        return urls
                   
    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []"""



def find_images_sreality(url: str):

    urls = []
    
    try:
        # Сложный селектор для кнопки внутри li
        POPUP_BUTTON_SELECTOR = "li.lg-min\\:d-grid.g-md.gtr-subgrid.gr-span-5.md-max\\:o-1 button.cw-btn.cw-btn--lg.cw-btn--green.color-white.is-wider.lg-max\\:mt-sm"
        DIV_SELECTOR = "div.ContentLabel.css-k1yxg"
        DIV_SELECTOR_IMG = "div.css-1c5glad"  
        TARGET_SELECTOR = "div.css-nsjzxx"  

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            #context = browser.new_context()
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            
            page.goto(url)
            
            # Ожидаем появления кнопки и прокручиваем страницу, чтобы она стала видимой
            page.wait_for_selector(POPUP_BUTTON_SELECTOR, timeout=5000)  # Ждём до 10 секунд, чтобы элемент стал видимым
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')  # Прокручиваем страницу вниз, если кнопка ниже
            
            # Теперь кликаем по кнопке
            page.click(POPUP_BUTTON_SELECTOR)
            page.wait_for_timeout(5000)  # Ждём, пока исчезнет попап или появится нужный элемент

            page.wait_for_timeout(5000)

            # Ждём появления необходимого div после клика
            page.wait_for_selector(DIV_SELECTOR_IMG)
            page.click(DIV_SELECTOR_IMG)

            page.wait_for_timeout(5000)
            
            page.wait_for_selector(TARGET_SELECTOR)
            element = page.query_selector(TARGET_SELECTOR)

            #print(element)

            if element:
                # Извлекаем все изображения внутри найденного элемента
                images = element.query_selector_all("img")  # Находим все теги img
                if images:
                    print(f"Найдено {len(images)} изображений:")
                    for img in images:
                        srcset = img.get_attribute("srcset")  # Получаем значение атрибута src
                        urls.append(f'https:{srcset}')
                else:
                    print("Изображений не найдено.")
            else:
                print("Элемент не найден.")

            browser.close()

            return urls

    except Exception as e:
        print(f'Ошибка: {e}')
    



#Скачивание изображения для byty.cz
def find_images_bytycz(url: str):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
    try:
        response = requests.get(url, headers=headers,timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        containers = soup.find('ul', class_='sliderxs', id='xs_fotoslider')
        image_urls = []
        items = containers.find_all('li', class_='item')
        for item in items:
            if 'data-src' in item.attrs:
                image_urls.append(item['data-src'])
        
        return image_urls
        
    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []
    


#Скачивание изображения для sbazar.cz
def find_images_sbazar(url: str):
    image_urls = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            page.goto(url, timeout=20000)

            # Шаг 1 — принять cookies
            try:
                page.wait_for_selector('button[data-testid="cw-button-agree-with-ads"]', timeout=8000)
                page.click('button[data-testid="cw-button-agree-with-ads"]')
                #print("✅ Клик по кнопке 'Souhlasím'")
            except Exception as e:
                print("⚠️ Кнопка 'Souhlasím' не найдена или неактивна:", e)

            page.wait_for_timeout(5000)

            # Шаг 2 — клик по кнопке галереи (без привязки к тексту)
            try:
                gallery_btn_selector = 'button[class*="detailGalleryCountButton"]'
                page.wait_for_selector(gallery_btn_selector, timeout=8000)
                page.click(gallery_btn_selector)
                #print("✅ Клик по кнопке открытия галереи")
            except Exception as e:
                print("⚠️ Кнопка галереи не найдена:", e)

            page.wait_for_timeout(5000)

            # Шаг 3 — ждём появления галереи
            page.wait_for_selector('div[data-gallery-item]', timeout=8000)
            gallery_blocks = page.query_selector_all('div[data-gallery-item]')

            #print(f"🔍 Найдено блоков с изображениями: {len(gallery_blocks)}")

            for block in gallery_blocks:
                img = block.query_selector("img")
                if img:
                    src = img.get_attribute("src")
                    if src and src.startswith("//"):
                        src = "https:" + src
                    if src:
                        image_urls.append(src)

            browser.close()
            return image_urls

    except Exception as e:
        print(f"💥 Ошибка при загрузке изображений с {url}: {e}")
        return []




    
#Скачивание изображения для realitymix
def find_images_realitymix(url:str):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
    try:
        response = requests.get(url, headers=headers,timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_urls = []
        
        a_gallery_main = soup.find('a', class_='gallery__main-img-inner')
        image_urls.append(a_gallery_main['data-src'])

        collection_gallery_smal = soup.find_all('div', class_='gallery__item')
        for item in collection_gallery_smal:
            image_urls.append(item.find('a')['data-src'])

        collection_all_gallery = soup.find_all('div', class_='gallery__hidden-items')[0].find_all('a')

        for item in collection_all_gallery:
            image_urls.append(item['href'])

        


        
        return image_urls
            
    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []
    




#Скачинвание изображенгий https://reality.idnes.cz/
def find_image_idnes(url:str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers,timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        image_urls = []

        div = soup.find_all('a', class_='carousel__item')

        for item in div:
            image_urls.append(item['href'])

    
        return image_urls
        

    except Exception as e:
        print(f"Error fetching images from {url}: {e}")
        return []

    



# Функция для создания масок безреалитка
def create_masks_bezrealitky(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            width, height = image.size

            #Новый улучшенный скрипт
            if width > height:
                # Горизонтальная ориентация
                logo_size = (0.10, None)  # Высота будет вычисляться динамически
                logo_position = (0.25, 0.3897)
                title_size = (0.40, None)  # Высота будет вычисляться динамически
                title_position = (0.3556, 0.4245)

                # Формулы для вычисления высоты
                logo_height_percent = -0.0124 * height + 30.62  # Процент высоты логотипа 
                title_height_percent = -0.00735 * height + 20.4   # Процент высоты текста 

                # Преобразуем проценты в абсолютные пиксели
                logo_height = int((logo_height_percent / 100) * height + 10) #ДОбавил по 10 пикселей
                title_height = int((title_height_percent / 100) * height + 10) #ДОбавил по 10 пикселей

                # Вычисляем размеры и положение логотипа в пикселях
                logo_x = int(logo_position[0] * width)
                logo_y = int(logo_position[1] * height)
                logo_width = int(logo_size[0] * width)
                # Высота логотипа заменяется динамическим значением из формулы
                # Вычисляем размеры и положение текста в пикселях
                title_x = int(title_position[0] * width)
                title_y = int(title_position[1] * height)
                title_width = int(title_size[0] * width)
            else:
                # Вертикальная ориентация
                logo_size = (0.1211, 0.09)
                logo_position = (0.2333, 0.45)
                title_size = (0.4033, 0.0692)
                title_position = (0.3556, 0.4667)
                
                # Вычисляем размеры и положение логотипа в пикселях
                logo_x = int(logo_position[0] * width)
                logo_y = int(logo_position[1] * height)
                logo_width = int(logo_size[0] * width)
                logo_height = int(logo_size[1] * height)

                # Вычисляем размеры и положение текста в пикселях
                title_x = int(title_position[0] * width)
                title_y = int(title_position[1] * height)
                title_width = int(title_size[0] * width)
                title_height = int(title_size[1] * height)

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черное изображение (фон маски)
            draw = ImageDraw.Draw(mask)

            # Добавляем логотип на маску
            draw.rectangle([logo_x, logo_y, logo_x + logo_width, logo_y + logo_height], fill=255)

            # Добавляем текст на маску
            draw.rectangle([title_x, title_y, title_x + title_width, title_y + title_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)

            # 👉 Преобразуем PIL маску в NumPy массив
            mask_np = np.array(mask)

            # 👉 Размытие краёв маски
            blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

            # 👉 Нормализуем — можно оставить как есть (плавная маска)
            blurred_mask = Image.fromarray(blurred_mask_np)

            # 👉 Сохраняем размытую маску
            blurred_mask.save(mask_path)
            #mask.save(mask_path)
            print(f"Маска для {filename} сохранена как {mask_path}")


# Создание масок для изображений с bazos.cz
def create_masks_bazos(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            width, height = image.size

            # Вычисляем размеры белого поля в зависимости от размера изображения
            mask_width = int(width * 0.3)  # 30% от ширины
            mask_height = int(height * 0.06875)  # 6.875% от высоты

            # Координаты правого нижнего угла
            mask_x = width - mask_width
            mask_y = height - mask_height

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черное изображение (фон маски)
            draw = ImageDraw.Draw(mask)

            # Добавляем белое поле для маски в правый нижний угол
            draw.rectangle([mask_x, mask_y, mask_x + mask_width, mask_y + mask_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)
            # 👉 Преобразуем PIL маску в NumPy массив
            mask_np = np.array(mask)

            # 👉 Размытие краёв маски
            blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

            # 👉 Нормализуем — можно оставить как есть (плавная маска)
            blurred_mask = Image.fromarray(blurred_mask_np)

            # 👉 Сохраняем размытую маску
            blurred_mask.save(mask_path)
            #mask.save(mask_path)
            print(f"Маска для {filename} сохранена как {mask_path}")



#Создание масок для sreality.cz
def create_masks_sreality(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            width, height = image.size

            # Проверка ориентации изображения и установка параметров маски
            if width > height:
                # Параметры для горизонтальных фотографий
                mask_width = int(width * 0.3)  # 30% от ширины
                mask_height = int(height * 0.15)  # 15% от высоты
            else:
                # Параметры для вертикальных фотографий
                mask_width = int(width * 0.31)  # 31% от ширины
                mask_height = int(height * 0.1)  # 10% от высоты

            # Координаты левого верхнего угла
            mask_x, mask_y = 0, 0

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черное изображение (фон маски)
            draw = ImageDraw.Draw(mask)

            # Добавляем белое поле для маски в левом верхнем углу
            draw.rectangle([mask_x, mask_y, mask_x + mask_width, mask_y + mask_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)
            # 👉 Преобразуем PIL маску в NumPy массив
            mask_np = np.array(mask)

            # 👉 Размытие краёв маски
            blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

            # 👉 Нормализуем — можно оставить как есть (плавная маска)
            blurred_mask = Image.fromarray(blurred_mask_np)

            # 👉 Сохраняем размытую маску
            blurred_mask.save(mask_path)
            #mask.save(mask_path)
            print(f"Маска для {filename} сохранена как {mask_path}")




#Создание масок для byty.cz
def create_masks_bytycz(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            width, height = image.size

            # Проверка ориентации изображения и установка параметров маски
            if width > height:
                # Параметры для горизонтальных фотографий
                mask_width = int(width * 0.16)  # 16% от ширины
                mask_height = int(height * 0.09)  # 9% от высоты
            else:
                # Параметры для вертикальных фотографий
                mask_width = int(width * 0.16)  # 16% от ширины
                mask_height = int(height * 0.05)  # 5% от высоты

            
            # Координаты правого нижнего угла
            mask_x = width - mask_width
            mask_y = height - mask_height

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черное изображение (фон маски)
            draw = ImageDraw.Draw(mask)

            # Добавляем белое поле для маски в левом верхнем углу
            draw.rectangle([mask_x, mask_y, mask_x + mask_width, mask_y + mask_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)
            # 👉 Преобразуем PIL маску в NumPy массив
            mask_np = np.array(mask)

            # 👉 Размытие краёв маски
            blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

            # 👉 Нормализуем — можно оставить как есть (плавная маска)
            blurred_mask = Image.fromarray(blurred_mask_np)

            # 👉 Сохраняем размытую маску
            blurred_mask.save(mask_path)
            #mask.save(mask_path)
            print(f"Маска для {filename} сохранена как {mask_path}")







#Создание масок для sbazar.cz
def create_masks_sbazar(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = Image.open(image_path)
            width, height = image.size

            # Проверка ориентации изображения и установка параметров маски
            if width > height:
                # Параметры для горизонтальных фотографий
                mask_width = int(width * 0.35)  # 35% от ширины
                mask_height = int(height * 0.06)  # 6% от высоты
            else:
                # Параметры для вертикальных фотографий
                mask_width = int(width * 0.5)  # 50% от ширины
                mask_height = int(height * 0.06)  # 6% от высоты

            # Координаты левого верхнего угла
            mask_x, mask_y = 0, 0

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черное изображение (фон маски)
            draw = ImageDraw.Draw(mask)

            # Добавляем белое поле для маски в левом верхнем углу
            draw.rectangle([mask_x, mask_y, mask_x + mask_width, mask_y + mask_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)
            # 👉 Преобразуем PIL маску в NumPy массив
            mask_np = np.array(mask)

            # 👉 Размытие краёв маски
            blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

            # 👉 Нормализуем — можно оставить как есть (плавная маска)
            blurred_mask = Image.fromarray(blurred_mask_np)

            # 👉 Сохраняем размытую маску
            blurred_mask.save(mask_path)
            #mask.save(mask_path)
            print(f"Маска для {filename} сохранена как {mask_path}")




#Создаение маски для realitymix.cz
def create_masks_realitymix(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(input_folder):
        print(f"Ошибка: Входная папка '{input_folder}' не найдена.")
        return

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        
        if not os.path.isfile(file_path):
            continue  # Пропускаем директории и невалидные файлы
        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                image = Image.open(file_path)
                width, height = image.size
            except Exception as e:
                print(f"Ошибка при обработке {filename}: {e}")
                continue

            # Определение размеров и координат масок относительно изображения
            mask_width = int(width * 0.25)  # Маска занимает 25% ширины изображения
            mask_height = int(height * 0.1)  # Маска занимает 10% высоты изображения

            # Координаты правого водяного знака
            right_mask_x = width - mask_width - int(width * 0.02)  # Отступ 2% от правого края
            right_mask_y = height - mask_height - int(height * 0.02)  # Отступ 2% от нижнего края
            
            # Координаты левого водяного знака
            left_mask_x = int(width * 0.0208)  # Отступ 2.08% от левого края
            left_mask_y = height - mask_height - int(height * 0.0576)  # Отступ 5.76% от нижнего края

            # Создаем черно-белую маску
            mask = Image.new("L", (width, height), 0)  # Черный фон маски
            draw = ImageDraw.Draw(mask)

            # Добавляем белые области масок
            draw.rectangle([right_mask_x, right_mask_y, right_mask_x + mask_width, right_mask_y + mask_height], fill=255)
            draw.rectangle([left_mask_x, left_mask_y, left_mask_x + mask_width, left_mask_y + mask_height], fill=255)

            # Сохраняем маску с тем же именем файла, но в формате PNG
            mask_filename = os.path.splitext(filename)[0] + ".png"
            mask_path = os.path.join(output_folder, mask_filename)
            
            try:
                # 👉 Преобразуем PIL маску в NumPy массив
                mask_np = np.array(mask)

                # 👉 Размытие краёв маски
                blurred_mask_np = cv2.GaussianBlur(mask_np, (51, 51), 0)

                # 👉 Нормализуем — можно оставить как есть (плавная маска)
                blurred_mask = Image.fromarray(blurred_mask_np)

                # 👉 Сохраняем размытую маску
                blurred_mask.save(mask_path)
                #mask.save(mask_path)
                print(f"Маска для {filename} сохранена как {mask_path}")
            except Exception as e:
                print(f"Ошибка при сохранении маски для {filename}: {e}")




