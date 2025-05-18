# Vision AI 3D Model API

**Vision AI API** — сервер, который позволяет на основе изображений автоматически создавать 3D-модели. Поддерживаются функции ремеширования (`quads_remesh`), текстурирования (`textured`) и конвертации в форматы `glb`, `fbx`, `stl`.

---

## 🚀 Быстрый старт

Сервер запускается на:
http://193.107.103.44:39152


Для всех запросов требуется API-ключ через заголовок `Vision-API-KEY`.

---

## 📌 Эндпоинты

### `POST /api/v1/models/single`

Создание 3D-модели из одного изображения.

**Параметры:**

- `image`: `UploadFile` — обязательное изображение.
- `quads_remesh`: `bool` — выполнять ремеш (по умолчанию `false`). Ремаширование позволяет улучшить качество полигональной сетки модели, оптимизируя количество полигонов и значительно ускоряет текстурирование, из-за чего при выборе текстурирования модели ремешивание включено по умолчанию.
- `textured`: `bool` — выполнять текстурирование (по умолчанию `false`).

**Ответ:**

```json
{
  "status": "success",
  "request_id": "abc123xyz"
}
```

### 📁 Поддерживаемые форматы

- `original` — изначальный формат
- `fbx` — универсальный для 3D-софтов
- `glb` — бинарный GLTF
- `stl` — для 3D-печати

⚠️ `stl` не поддерживает текстурирование. `stl` и `glb` не поддерживают четырехугольные полигоны.


### `POST /api/v1/models/multi`

Создание 3D-модели из нескольких ракурсов.

**Параметры:**

- `front`, `back`, `left`, `right`: изображения (любое количество).
- `quads_remesh`, `textured`: как выше.

### `GET /api/v1/models/{request_id}/status`

Проверка статуса задачи.

**Ответ:**

```json
{
  "request_id": "abc123xyz",
  "status": "processing",
  "progress": 65
}
```

### `GET /api/v1/models/{request_id}/download?format=glb`

Скачивание готовой 3D-модели.

**Параметры:**

- `format`: `original`, `glb`, `fbx`, `stl`.

---

## 🔑 API-ключ

Передаётся в заголовке каждого запроса:

Vision-API-KEY: <ваш_ключ>


## 📂 Примеры использования

### cURL

1. Отправка одного изображения

```bash
curl -X POST http://193.107.103.44:39152:39152/api/v1/models/single \
  -H "Vision-API-KEY: YOUR_API_KEY" \
  -F "image=@chair.jpg" \
  -F "quads_remesh=true" \
  -F "textured=true"
```

2. Проверка статуса

```bash
curl -X GET "http://193.107.103.44:39152/api/v1/models/abc123xyz/status" \
  -H "Vision-API-KEY: YOUR_API_KEY"
```

3. Скачивание результата

```bash
curl -X GET "http://193.107.103.44:39152/api/v1/models/abc123xyz/download?format=glb" \
  -H "Vision-API-KEY: YOUR_API_KEY" \
  -o model.glb
```

---

### 🖥 Использование client.py

Убедитесь, что:

- Установлен requests

```bash Linux/MacOS
python3 -m venv venv
source venv/bin/activate
pip install requests
```

```bash Windows
python -m venv venv
venv\Scripts\activate
pip install requests
```

- Указаны BASE_URL и API_KEY внутри client.py

Примеры:

1. Одиночное изображение

```bash
python client.py single image.jpg --remesh --texture --wait --download glb --output result/model
```

2. Несколько изображений

```bash
python client.py multi --front front.jpg --back back.jpg --remesh --wait --download glb --output result/model
```

3. Проверка статуса

```bash
python client.py status abc123xyz --wait
```

4. Скачивание результата напрямую

```bash
python client.py download abc123xyz --format glb --output result/model
```

---

### 📄 Swagger UI

Документация доступна по адресу:

http://193.107.103.44:39152/docs

---

### 📞 Поддержка

telegram: @vision_ai_org