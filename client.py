import requests
import time
import os
import argparse
from typing import List, Dict, Optional, Union
import sys

# Базовый URL сервера
BASE_URL = "http://193.107.103.44:39152"
API_KEY = "your_api_key_here"  # Замените на ваш API-ключ

def process_single_image(image_path: str, quads_remesh: bool = False, textured: bool = False) -> str:
    """
    Отправляет одно изображение на обработку и возвращает ID запроса

    Args:
        image_path: Путь к изображению
        quads_remesh: Применить remesh
        textured: Применить текстурирование

    Returns:
        ID запроса
    """
    global BASE_URL, API_KEY

    print(f"Отправка изображения {image_path} на обработку...")

    # Проверяем, существует ли файл
    if not os.path.exists(image_path):
        print(f"Ошибка: Файл {image_path} не найден")
        return None

    # Подготавливаем файл для отправки
    files = {'image': open(image_path, 'rb')}

    # Подготавливаем параметры
    params = {
        'quads_remesh': 'true' if quads_remesh else 'false',
        'textured': 'true' if textured else 'false'
    }

    # Отправляем запрос
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/models/single",
            files=files,
            params=params,
            headers={"Vision-API-KEY": API_KEY}
        )

        # Закрываем файл
        files['image'].close()

        # Проверяем ответ
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            print(f"Запрос успешно отправлен. ID запроса: {request_id}")
            return request_id
        else:
            print(f"Ошибка при отправке запроса: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return None


def process_multiple_images(
    front_path: Optional[str] = None,
    back_path: Optional[str] = None,
    left_path: Optional[str] = None,
    right_path: Optional[str] = None,
    quads_remesh: bool = False,
    textured: bool = False
) -> str:
    """
    Отправляет несколько изображений на обработку и возвращает ID запроса

    Args:
        front_path: Путь к фронтальному изображению
        back_path: Путь к заднему изображению
        left_path: Путь к левому изображению
        right_path: Путь к правому изображению
        quads_remesh: Применить remesh
        textured: Применить текстурирование

    Returns:
        ID запроса
    """
    global BASE_URL, API_KEY

    print("Отправка изображений на обработку...")

    # Проверяем, что хотя бы одно изображение предоставлено
    if not any([front_path, back_path, left_path, right_path]):
        print("Ошибка: Необходимо предоставить хотя бы одно изображение")
        return None

    # Подготавливаем файлы для отправки
    files = {}

    # Добавляем только существующие файлы
    if front_path and os.path.exists(front_path):
        files['front'] = open(front_path, 'rb')

    if back_path and os.path.exists(back_path):
        files['back'] = open(back_path, 'rb')

    if left_path and os.path.exists(left_path):
        files['left'] = open(left_path, 'rb')

    if right_path and os.path.exists(right_path):
        files['right'] = open(right_path, 'rb')

    # Проверяем, что хотя бы один файл существует
    if not files:
        print("Ошибка: Ни один из указанных файлов не найден")
        return None

    # Подготавливаем параметры
    params = {
        'quads_remesh': 'true' if quads_remesh else 'false',
        'textured': 'true' if textured else 'false'
    }

    # Отправляем запрос
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/models/multi",
            files=files,
            params=params,
            headers={"Vision-API-KEY": API_KEY}
        )

        # Закрываем все файлы
        for f in files.values():
            f.close()

        # Проверяем ответ
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            print(f"Запрос успешно отправлен. ID запроса: {request_id}")
            return request_id
        else:
            print(f"Ошибка при отправке запроса: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return None


def download_result(request_id: str, format: str = "original", output: str = None) -> bool:
    """
    Скачивает результат обработки

    Args:
        request_id: ID запроса
        format: Формат для скачивания (original, fbx, glb, stl)
        output: Полный путь для сохранения файла с именем (по умолчанию - model_{request_id}.{format})

    Returns:
        True если скачивание успешно, иначе False
    """
    global BASE_URL, API_KEY

    if not request_id:
        print("Ошибка: ID запроса не указан")
        return False

    if format not in ["original", "fbx", "glb", "stl"]:
        print(f"Ошибка: Неподдерживаемый формат {format}")
        return False

    try:
        print(f"Скачивание результата в формате {format}...")

        response = requests.get(
            f"{BASE_URL}/api/v1/models/{request_id}/download",
            params={'format': format},
            headers={"Vision-API-KEY": API_KEY},
            stream=True
        )

        if response.status_code != 200:
            print(f"Ошибка при скачивании: {response.status_code} - {response.text}")
            return False

        # Определяем путь для сохранения файла
        if output:
            # Если указан полный путь с именем файла
            output_path = output

            # Добавляем расширение, если его нет
            if not output_path.endswith(f".{format}"):
                output_path = f"{output_path}.{format}"

            # Создаем директорию, если она не существует
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        else:
            # Получаем имя файла из заголовка Content-Disposition или используем ID запроса
            filename = f"model_{request_id}.{format}"
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                import re
                filename_match = re.search(r'filename="(.+)"', content_disposition)
                if filename_match:
                    filename = filename_match.group(1)

            output_path = filename

        # Сохраняем файл
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Результат успешно скачан и сохранен как {output_path}")
        return True

    except Exception as e:
        print(f"Произошла ошибка при скачивании: {str(e)}")
        return False


def check_status(request_id: str, wait_for_completion: bool = False, download_format: str = None,
                output: str = None) -> Dict:
    """
    Проверяет статус запроса и при необходимости ожидает его завершения

    Args:
        request_id: ID запроса
        wait_for_completion: Ожидать завершения запроса
        download_format: Формат для скачивания результата (original, fbx, glb, stl)
        output: Полный путь для сохранения файла с именем

    Returns:
        Словарь с информацией о статусе
    """
    global BASE_URL, API_KEY

    if not request_id:
        print("Ошибка: ID запроса не указан")
        return None

    try:
        # Если нужно ожидать завершения
        if wait_for_completion:
            print(f"Ожидание завершения запроса {request_id}...")

            # Для хранения предыдущей длины строки статуса
            prev_status_length = 0

            while True:
                response = requests.get(
                    f"{BASE_URL}/api/v1/models/{request_id}/status",
                    headers={"Vision-API-KEY": API_KEY}
                )

                if response.status_code != 200:
                    print(f"Ошибка при проверке статуса: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)

                # Формируем строку статуса
                status_str = f"Статус: {status}, Прогресс: {progress}%"

                # Очищаем предыдущую строку и выводим новую
                sys.stdout.write('\r' + ' ' * prev_status_length + '\r')
                sys.stdout.write(status_str)
                sys.stdout.flush()

                # Запоминаем длину текущей строки
                prev_status_length = len(status_str)

                # Если задача завершена или произошла ошибка
                if status == "completed":
                    print("\nЗадача успешно завершена!")

                    # Если нужно скачать результат
                    if download_format:
                        download_result(request_id, download_format, output)

                    return data
                elif status == "error":
                    error = data.get('error', 'Неизвестная ошибка')
                    print(f"\nПроизошла ошибка: {error}")
                    return data

                # Ждем перед следующей проверкой
                time.sleep(5)
        else:
            # Просто проверяем текущий статус
            response = requests.get(
                f"{BASE_URL}/api/v1/models/{request_id}/status",
                headers={"Vision-API-KEY": API_KEY}
            )

            if response.status_code != 200:
                print(f"Ошибка при проверке статуса: {response.status_code} - {response.text}")
                return None

            data = response.json()
            status = data.get('status')
            progress = data.get('progress', 0)

            print(f"Статус: {status}, Прогресс: {progress}%")
            return data

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return None
    

def main():
    parser = argparse.ArgumentParser(description='Клиент для API обработки изображений в 3D модели')

    # Подкоманды
    subparsers = parser.add_subparsers(dest='command', help='Команда')

    # Команда для обработки одного изображения
    single_parser = subparsers.add_parser('single', help='Обработка одного изображения')
    single_parser.add_argument('image', type=str, help='Путь к изображению')
    single_parser.add_argument('--remesh', action='store_true', help='Применить remesh')
    single_parser.add_argument('--texture', action='store_true', help='Применить текстурирование')
    single_parser.add_argument('--wait', action='store_true', help='Ожидать завершения обработки')
    single_parser.add_argument('--download', type=str, choices=['original', 'fbx', 'glb', 'stl'],
                              help='Скачать результат в указанном формате')
    single_parser.add_argument('--output', type=str, help='Путь для сохранения результата с именем файла')

    # Команда для обработки нескольких изображений
    multi_parser = subparsers.add_parser('multi', help='Обработка нескольких изображений')
    multi_parser.add_argument('--front', type=str, help='Путь к фронтальному изображению')
    multi_parser.add_argument('--back', type=str, help='Путь к заднему изображению')
    multi_parser.add_argument('--left', type=str, help='Путь к левому изображению')
    multi_parser.add_argument('--right', type=str, help='Путь к правому изображению')
    multi_parser.add_argument('--remesh', action='store_true', help='Применить remesh')
    multi_parser.add_argument('--texture', action='store_true', help='Применить текстурирование')
    multi_parser.add_argument('--wait', action='store_true', help='Ожидать завершения обработки')
    multi_parser.add_argument('--download', type=str, choices=['original', 'fbx', 'glb', 'stl'],
                             help='Скачать результат в указанном формате')
    multi_parser.add_argument('--output', type=str, help='Путь для сохранения результата с именем файла')

    # Команда для проверки статуса
    status_parser = subparsers.add_parser('status', help='Проверка статуса запроса')
    status_parser.add_argument('request_id', type=str, help='ID запроса')
    status_parser.add_argument('--wait', action='store_true', help='Ожидать завершения обработки')
    status_parser.add_argument('--download', type=str, choices=['original', 'fbx', 'glb', 'stl'],
                              help='Скачать результат в указанном формате')
    status_parser.add_argument('--output', type=str, help='Путь для сохранения результата с именем файла')

    # Команда для скачивания результата
    download_parser = subparsers.add_parser('download', help='Скачивание результата')
    download_parser.add_argument('request_id', type=str, help='ID запроса')
    download_parser.add_argument('--format', type=str, default='original',
                                choices=['original', 'fbx', 'glb', 'stl'],
                                help='Формат для скачивания')
    download_parser.add_argument('--output', type=str, help='Путь для сохранения результата с именем файла')

    args = parser.parse_args()

    # Проверяем, что API ключ указан
    if API_KEY == "your_api_key_here":
        print("Ошибка: Необходимо указать API ключ через --api-key или изменить значение API_KEY в скрипте")
        return

    # Обрабатываем команды
    if args.command == 'single':
        request_id = process_single_image(args.image, args.remesh, args.texture)
        if request_id and args.wait:
            check_status(request_id, True, args.download, args.output)

    elif args.command == 'multi':
        request_id = process_multiple_images(args.front, args.back, args.left, args.right, args.remesh, args.texture)
        if request_id and args.wait:
            check_status(request_id, True, args.download, args.output)

    elif args.command == 'status':
        check_status(args.request_id, args.wait, args.download, args.output)

    elif args.command == 'download':
        download_result(args.request_id, args.format, args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
