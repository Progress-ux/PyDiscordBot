import discord
import asyncio
import re
import yt_dlp
from collections import deque
from discord.ext import commands

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'extract_flat': True,
    'quiet': True,
    'ignoreerrors': False,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def cleanURL(url):
    if 'playlist' not in url and 'list=' in url:
        cleaned_url = re.sub(r"(\?list=[^&]+)", "", url)
        return cleaned_url
    else:
        return url

async def create_bot():
    # Очередь треков
    track_queue = deque()
    track_history = deque()

    # Автовоспроизведение видео\трека
    isRepeat = False
    current_track = None
    should_play_next = True

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f'✅ Бот запущен как {bot.user}')

    @bot.event
    async def on_message(message):
        print(f"Получено сообщение: {message.content}")
        await bot.process_commands(message)

    @bot.command()
    async def join(ctx):
        """Подключает бота к голосовому каналу"""
        print("Команда !join вызвана")
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Подключился к каналу {channel}")
        else:
            await ctx.send("Вы должны быть в голосовом канале!")

    @bot.command()
    async def leave(ctx):
        """Отключает бота из голосового канала"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send("Бот не в голосовом канале!")

    @bot.command()
    async def play(ctx, url: str): 
        """Проигрывает следующий трек в очереди"""
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                cleanurl = cleanURL(url)

                info = ydl.extract_info(cleanurl, download=False, process=False)
                i = 0
                if 'entries' in info:
                    # Если это плейлист, добавляем все треки в очередь
                    for entry in info['entries']:
                        track_title = entry.get('title', 'Неизвестный трек')
                        track_url = entry.get('url')
                        if track_url:  
                            track_queue.append((track_title, track_url))
                            i += 1
                    await ctx.send(f"🎶 Добавлен плейлист из {i} треков!")
                else:
                    track_title = info.get('title', 'Неизвестный трек')
                    track_queue.append((track_title, cleanurl))
                    await ctx.send(f"🎵 Добавлен трек: {track_title}")

        except Exception as e:
            await ctx.send(f"❌ Ошибка загрузки: {e}")


        # Подключаемся к каналу, если бота нет в голосовом канале
        if not ctx.voice_client:
            await ctx.invoke(join)

        if not ctx.voice_client.is_playing():
            await play_next(ctx)

    async def play_next(ctx):
        nonlocal current_track, should_play_next

        if not should_play_next or not track_queue:
            should_play_next = True
            return
        
        if isRepeat and current_track:
            title, url = current_track
        elif track_queue:
            title, url = track_queue.popleft()
            track_history.append((title, url))
            current_track = (title, url)
        else:
            await ctx.send("❌ Очередь пуста.")
            return

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                await ctx.send(f"▶ Начинаю воспроизведение: {title}")
                source = discord.FFmpegPCMAudio(url2, executable="C:/ffmpeg/bin/ffmpeg.exe", **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)) 
        except Exception as e:
            await ctx.send(f"❌ Ошибка загрузки: {e}")
    
    @bot.command()
    async def back(ctx):
        """Возвращает на предыдущий трек"""
        nonlocal current_track, should_play_next, isRepeat

        if len(track_history) > 1:
            # Возвращаем текущий трек в очередь
            track_queue.appendleft(current_track)

            # Берем последний проигранный трек
            track_history.pop()
            title, url = track_history[-1]
            current_track = (title, url)

            try:
                if ctx.voice_client and ctx.voice_client.is_playing():
                    if isRepeat:
                        await repeat(ctx)
                    ctx.voice_client.stop()
                    should_play_next = False

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    url2 = info['url']
                    await ctx.send(f"⏮ Возвращаюсь к предыдущему треку: {title}")
                    source = discord.FFmpegPCMAudio(url2, executable="C:/ffmpeg/bin/ffmpeg.exe", **FFMPEG_OPTIONS)
                    ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
            except Exception as e:
                await ctx.send(f"❌ Ошибка загрузки: {e}")
        else:
            await ctx.send("❌ Нет предыдущих треков!")

    @bot.command()
    async def repeat(ctx):
        """Включение/выключение автоповтора"""
        nonlocal isRepeat
        isRepeat = not isRepeat
        status = "включен 🔁" if isRepeat else "выключен ❌"
        await ctx.send(f"🔁 Автоповтор {status}")

    @bot.command()
    async def playlist(ctx):
        """Показывает текущую очередь треков"""
        if not track_queue:
            await ctx.send("📭 Очередь пуста.")
            return
        
        track_list = ""
        for i, (title, url) in enumerate(track_queue, start=1):
            track_list += f"{i}. {title}\n"

        if len(track_list) > 1900:
            track_list = track_list[:1900] + "...\nСлишком много треков для показа!"
        
        await ctx.send(f"🎵 **Очередь треков:**\n{track_list}")

    @bot.command()
    async def skip(ctx):
        """Пропускает текущий трек и воспроизводит следующий"""
        nonlocal should_play_next, isRepeat
        if ctx.voice_client and ctx.voice_client.is_playing():
            if isRepeat:
                    await repeat(ctx)
            ctx.voice_client.stop()
            should_play_next = False  
            await ctx.send("⏭ Пропущен текущий трек.")
            await play_next(ctx)
        else:
            await ctx.send("Сейчас ничего не играет!")

    @bot.command()
    async def pause(ctx):
        """Ставит музыку на паузу"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸ Музыка на паузе")
        else:
            await ctx.send("Сейчас ничего не играет!")

    @bot.command()
    async def resume(ctx):
        """Возобновляет воспроизведение"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶ Музыка продолжается")
        else:
            await ctx.send("Музыка не на паузе!")

    @bot.command()
    async def clear(ctx):
        """Очищает очередь"""
        track_queue.clear()
        track_history.clear()
        global current_track
        current_track = None
        await ctx.send("🗑 Очередь очищена.")

    @bot.command()
    async def stop(ctx):
        """Останавливает музыку"""
        nonlocal should_play_next
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            should_play_next = False
            await ctx.send("⏹ Музыка остановлена")
        else:
            await ctx.send("Сейчас ничего не играет!")

    # Запуск бота
    await bot.start("YOUR_TOKEN")
    
# Запуск бота в асинхронном контексте
asyncio.run(create_bot())
