# 🎵 Discord Music Bot 

Этот бот предназначен для воспроизведения музыки в голосовых каналах Discord. Он поддерживает работу с очередью, повтор треков, управление воспроизведением и обработку плейлистов.

## 🚀 Функции
- 🔊 Воспроизведение аудио из YouTube
- 📜 Очередь треков
- 🔁 Повтор текущего трека
- ⏮ Переключение на предыдущий трек
- ⏭ Пропуск текущего трека
- ⏸ Пауза и ▶️ возобновление
- 🗑 Очистка очереди
- 🎵 Управление плейлистами

## 📌 Установка
### 1. Установка зависимостей
Убедитесь, что у вас установлен Python 3.9+ и pip. Затем установите нужные библиотеки:
```sh
pip install discord.py yt-dlp asyncio
```

### 2. Установка FFmpeg
Для работы с аудио установите [FFmpeg](https://ffmpeg.org/download.html) и добавьте его в переменные окружения.

### 3. Клонирование репозитория
```sh
git clone https://github.com/Progress-ux/PyDiscordBot.git
cd PyDiscordBot
```

### 4. Запуск бота
```sh
python bot.py
```

## 📜 Команды
| Команда | Описание |
|---------|----------|
| `!join` | Подключает бота к голосовому каналу |
| `!leave` | Отключает бота из голосового канала |
| `!play [ссылка]` | Добавляет трек/плейлист в очередь и начинает воспроизведение |
| `!pause` | Ставит воспроизведение на паузу |
| `!resume` | Возобновляет воспроизведение |
| `!skip` | Пропускает текущий трек |
| `!back` | Возвращает предыдущий трек |
| `!repeat` | Включает/выключает повтор текущего трека |
| `!playlist` | Показывает очередь треков |
| `!clear` | Очищает очередь |
| `!stop` | Останавливает музыку |

## 🛠 Возможные ошибки и решения
- **Бот не подключается к голосовому каналу** – Убедитесь, что у бота есть права `Connect` и `Speak`.
- **Ошибка с FFmpeg** – Проверьте, установлен ли FFmpeg и добавлен ли в `PATH`.

## 📜 Лицензия
Этот проект распространяется под лицензией MIT.

