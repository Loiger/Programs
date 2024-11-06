import pgzrun
import pygame
from datetime import datetime
import json
import os
import math
import time
import random
import os.path
import vlc
import yt_dlp

# Константи
WIDTH = 1000
HEIGHT = 600
PROGRAM_HEIGHT = 40
VISIBLE_PROGRAMS = 8
DAYS_OF_WEEK = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
LOGOS_PATH = r'C:\Users\ugaev\Desktop\58548\logos'

# Кольорова схема
COLORS = {
    'background': (8, 8, 32),
    'menu_bg': (15, 15, 45),
    'title': (255, 255, 255),
    'channel': (255, 223, 0),  # Яскравіший жовтий
    'program': (200, 200, 255),
    'selected': (0, 255, 255),
    'current': (255, 69, 58),  # Яскравіший червоний
    'past': (100, 100, 150),
    'future': (255, 255, 255),
    'button': (63, 81, 181),
    'button_hover': (92, 107, 192),
    'button_border': (100, 100, 255),
    'time_bg': (30, 30, 80),
    'gradient_top': (15, 15, 45),
    'gradient_bottom': (8, 8, 32),
    'program_bg': (40, 40, 90),
    'time_block': (50, 50, 100),
    'glow': (100, 149, 237),  # Світло-синій для ефектів світіння
    'shadow': (0, 0, 0, 50)   # Тінь
}

CHANNELS_PATH = r'C:\Users\ugaev\Desktop\58548\channels'

def load_channel_schedule(channel_name):
    """Завантажує розклад для одного каналу з JSON-файлу."""
    filepath = os.path.join(CHANNELS_PATH, f'{channel_name}.json')
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не знайдено. Перевірте, чи файл існує і має правильну назву.")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Завантаження файлів каналів (перевірте, що файли існують і мають правильні назви)
    channels = {
        "1+1": "1plus1.json",  # Перевірте, чи файл має таку назву
        "ICTV": "ICTV.json",
        "STB": "STB.json",
        "Novy": "Novy.json"
    }

    global schedule_instance
    schedule_instance = TVSchedule(channels)

class SplashScreen:
    def __init__(self):
        self.start_time = pygame.time.get_ticks()
        self.duration = 2000  # 3 секунди
        self.finished = False
        self.particles = []
        self.logo_scale = 0
        self.logo_alpha = 0
        
        # Створюємо частинки для анімації
        for _ in range(100):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'speed_x': random.uniform(-1, 1),
                'speed_y': random.uniform(-1, 1),
                'size': random.uniform(1, 3),
                'color': random.choice([
                    COLORS['button'],
                    COLORS['glow'],
                    COLORS['channel']
                ]),
                'alpha': random.uniform(50, 200)
            })
        
        # Налаштування логотипу
        self.logo_text = "TV Program"
        self.subtext = "Інтерактивна телепрограма"
        self.loading_text = "Завантаження..."
        self.loading_dots = 0
        self.loading_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        progress = (current_time - self.start_time) / self.duration
        
        if progress >= 1:
            self.finished = True
            return
        
        # Оновлюємо частинки
        for particle in self.particles:
            # Рух частинок
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            
            # Відбиття від країв екрану
            if particle['x'] < 0 or particle['x'] > WIDTH:
                particle['speed_x'] *= -1
            if particle['y'] < 0 or particle['y'] > HEIGHT:
                particle['speed_y'] *= -1

            # Змінюємо розмір частинок
            particle['size'] += random.uniform(-0.1, 0.1)
            particle['size'] = max(1, min(3, particle['size']))

        # Оновлюємо анімацію завантаження
        self.loading_time += 1
        if self.loading_time > 20:  # Кожні 20 кадрів
            self.loading_dots = (self.loading_dots + 1) % 4
            self.loading_time = 0

    def draw(self, screen):
        screen.clear()
        screen.fill(COLORS['background'])
        
        # Малюємо частинки з ефектом світіння
        for particle in self.particles:
            size = int(particle['size'] * 2)
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Основна частинка
            pygame.draw.circle(s, (*particle['color'], particle['alpha']),
                            (size, size), size)
            
            # Світіння
            glow_size = size * 2
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            for i in range(3):
                alpha = int(particle['alpha'] * (1 - i/3))
                pygame.draw.circle(glow_surface, (*particle['color'], alpha),
                                (glow_size, glow_size), size * (1 + i*0.5))
                
            screen.surface.blit(glow_surface, 
                              (particle['x'] - glow_size, particle['y'] - glow_size))
            screen.surface.blit(s, 
                              (particle['x'] - size, particle['y'] - size))
        
        # Анімація появи логотипу
        progress = (pygame.time.get_ticks() - self.start_time) / self.duration
        
        # Логотип
        font_size = int(50 + 30 * min(1, progress * 2))
        alpha = int(255 * min(1, progress * 2))
        
        logo_surface = pygame.font.Font(None, font_size).render(
            self.logo_text, True, COLORS['title'])
        logo_surface.set_alpha(alpha)
        logo_rect = logo_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        
        # Тінь для логотипу
        shadow_surface = pygame.font.Font(None, font_size).render(
            self.logo_text, True, (0, 0, 0))
        shadow_surface.set_alpha(alpha // 2)
        shadow_rect = shadow_surface.get_rect(center=(WIDTH//2 + 2, HEIGHT//2 - 48))
        
        screen.surface.blit(shadow_surface, shadow_rect)
        screen.surface.blit(logo_surface, logo_rect)
        
        # Підтекст
        if progress > 0.3:
            subtext_alpha = int(255 * min(1, (progress - 0.3) * 2))
            subtext_surface = pygame.font.Font(None, font_size // 2).render(
                self.subtext, True, COLORS['channel'])
            subtext_surface.set_alpha(subtext_alpha)
            subtext_rect = subtext_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
            screen.surface.blit(subtext_surface, subtext_rect)
        
        # Прогрес-бар
        if progress < 0.8:
            bar_width = 300
            bar_height = 6
            filled_width = int(bar_width * (progress / 0.8))
            
            # Фон прогрес-бару
            pygame.draw.rect(screen.surface, (*COLORS['button_border'], 100),
                           (WIDTH//2 - bar_width//2, HEIGHT//2 + 80,
                            bar_width, bar_height), border_radius=3)
            
            # Заповнена частина
            if filled_width > 0:
                gradient_surface = pygame.Surface((filled_width, bar_height), pygame.SRCALPHA)
                for x in range(filled_width):
                    progress = x / filled_width
                    color = [int(COLORS['button'][i] * (1 - progress * 0.3)) for i in range(3)]
                    pygame.draw.line(gradient_surface, (*color, 255),
                                   (x, 0), (x, bar_height))
                screen.surface.blit(gradient_surface, 
                                  (WIDTH//2 - bar_width//2, HEIGHT//2 + 80))
            
            # Текст завантаження
            loading_text = self.loading_text + "." * self.loading_dots
            loading_surface = pygame.font.Font(None, 30).render(
                loading_text, True, COLORS['title'])
            loading_rect = loading_surface.get_rect(
                center=(WIDTH//2, HEIGHT//2 + 80 + bar_height + 20))
            screen.surface.blit(loading_surface, loading_rect)
            

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.animation_progress = 0
        self.press_animation = 0
        self.clicked = False

    def draw(self, screen):
        # Анімація наведення
        target_progress = 1.0 if self.hovered else 0.0
        self.animation_progress += (target_progress - self.animation_progress) * 0.2

        # Анімація натискання
        if self.clicked:
            self.press_animation = min(1.0, self.press_animation + 0.3)
        else:
            self.press_animation = max(0.0, self.press_animation - 0.3)

        # Кольори з анімацією
        base_color = tuple(int(COLORS['button'][i] + (COLORS['button_hover'][i] - COLORS['button'][i]) 
                * self.animation_progress) for i in range(3))

        # Тінь
        shadow_offset = int(2 * (1 - self.press_animation))
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 50),
                        (0, 0, self.rect.width, self.rect.height), border_radius=10)
        screen.surface.blit(shadow_surface, 
                          (self.rect.x + shadow_offset, self.rect.y + shadow_offset))

        # Основна кнопка
        button_rect = self.rect.copy()
        button_rect.y -= int(2 * self.press_animation)
        pygame.draw.rect(screen.surface, base_color, button_rect, border_radius=10)
        pygame.draw.rect(screen.surface, COLORS['button_border'], button_rect, 2, border_radius=10)

        # Градієнтне світіння при наведенні
        if self.animation_progress > 0:
            glow_color = tuple(list(COLORS['button_hover']) + [int(100 * self.animation_progress)])
            pygame.draw.rect(screen.surface,
                           glow_color,
                           (button_rect.x - 2, button_rect.y - 2,
                            button_rect.width + 4, button_rect.height + 4),
                           2, border_radius=10)

        # Текст з тінню
        text_y_offset = int(2 * (1 - self.press_animation))
        text_pos = (button_rect.centerx, button_rect.centery - text_y_offset)
        
        # Тінь тексту
        shadow_surface = pygame.font.Font(None, 20).render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(text_pos[0] + 1, text_pos[1] + 1))
        screen.surface.blit(shadow_surface, shadow_rect)
        
        # Основний текст
        screen.draw.text(self.text, center=text_pos, fontsize=20, color="white")

    def handle_mouse(self, pos):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pos)
        if not was_hovered and self.hovered:
            self.animation_progress = 0
        return self.hovered

    def click(self):
        if self.hovered:
            self.clicked = True
            self.action()
            return True
        self.clicked = False
        return False

    
def smooth_scroll(current, target, speed=0.2):
    return current + (target - current) * speed

class VideoPlayer:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.instance = vlc.Instance('--no-xlib')
        self.player = self.instance.media_player_new()
        self.surface = pygame.Surface((self.width, self.height))
        self.is_playing = False
        self.current_stream = None

    def draw(self, screen, x, y):
        """Відображення відео у межах визначеної області."""
        # Малюємо фон плеєра
        

    def set_stream(self, stream_url):
        """Встановлює URL потоку для відтворення"""
        try:
            self.current_stream = stream_url
            media = self.instance.media_new(stream_url)
            self.player.set_media(media)
            
            # Налаштування для відображення в pygame вікні
            #if pygame.display.get_init():
               # handle = pygame.display.get_wm_info()['window']
               # if handle:
                #    self.player.set_hwnd(handle)
            
            # Додаткові налаштування для YouTube
            self.player.video_set_scale(0.5)  # Масштабування відео
            
        except Exception as e:
            print(f"Помилка встановлення потоку: {e}")

    def play(self):
        """Початок відтворення"""
        if not self.is_playing and self.current_stream:
            self.player.play()
            self.is_playing = True

    def pause(self):
        """Пауза відтворення"""
        if self.is_playing:
            self.player.pause()
            self.is_playing = False

    def stop(self):
        """Зупинка відтворення"""
        self.player.stop()
        self.is_playing = False

def draw(self, screen, x, y):
    """Відображення плеєра у межах визначеної області"""
    self.player.video_set_callbacks(
        lambda *args: None,  # set the video lock callback
        lambda *args: None,  # set the video unlock callback
        lambda *args: self.surface.blit(screen.surface, (x, y))  # set the display callback
    )
    
    # Фон плеєра
    pygame.draw.rect(screen.surface, COLORS['menu_bg'],
                     (x, y, self.width, self.height + 50))
    
    # Рамка з світінням
    glow_alpha = abs(math.sin(time.time() * 2)) * 30 + 70
    for i in range(2):
        pygame.draw.rect(screen.surface,
                         (*COLORS['button_border'], glow_alpha - i * 30),
                         (x - i, y - i, self.width + i*2, self.height + 50 + i*2),
                         2, border_radius=5)

    # Відображення кнопок
    for button in self.buttons:
        button.draw(screen)


    def handle_click(self, pos):
        """Обробка кліків по кнопках"""
        for button in self.buttons:
            if button.handle_mouse(pos):
                return True
        return False

class TVSchedule:
    def __init__(self, channel_files):
        self.channel_files = channel_files
        self.channels = list(channel_files.keys())
        self.schedules = {channel: load_channel_schedule(channel) for channel in self.channels}
        self.current_day_index = datetime.today().weekday()
        self.current_channel = self.channels[0]
        self.selected_program_index = None
        self.expanded_program_index = None
        self.scroll_offset = 0
        self.hovered_program_index = None
        self.target_scroll_offset = 0
        self.current_scroll_offset = 0
        self.animation_offset = 0
        self.transition_time = 0
        
        # Створюємо відеоплеєр
        self.video_player = VideoPlayer(400, 300)
        self.show_player = False
        
        # Додаємо YouTube URLs для каналів
        self.stream_urls = {
            "1+1": "https://www.youtube.com/watch?v=ggsawW9rr2g&ab_channel=WarnerMusicPoland",
            "ICTV": "https://www.youtube.com/live/WY8sDvZdWEA?si=Pn5JRX_1DGIaq1M5",
            "STB": "https://ythls.armelin.one/channel/UCVEaAWKfv7fE1c-ZuBs7TKQ.m3u8",
            "Novy": "https://live.m2.tv/hls3/stream.m3u8"
        }
        
        # Завантаження логотипів каналів
        self.channel_logos = {}
        for channel in self.channels:
            logo_path = os.path.join(LOGOS_PATH, f"{channel.lower()}.png")
            try:
                logo = pygame.image.load(logo_path)
                # Масштабуємо логотип до розміру 150x150
                self.channel_logos[channel] = pygame.transform.scale(logo, (150, 150))
            except:
                print(f"Не вдалося завантажити логотип для каналу {channel}")
                self.channel_logos[channel] = None
        
        # Ініціалізуємо список кнопок
        button_y = HEIGHT - 50
        self.buttons = [
            Button(20, button_y, 120, 30, "< День", self.previous_day),
            Button(150, button_y, 120, 30, "День >", self.next_day),
            Button(280, button_y, 120, 30, "< Канал", self.previous_channel),
            Button(410, button_y, 120, 30, "Канал >", self.next_channel),
            Button(540, button_y, 120, 30, "📺 Плеєр", self.toggle_player)
        ]


    @staticmethod
    def get_youtube_stream_url(youtube_url):
        """Отримання прямого URL потоку з YouTube за допомогою yt-dlp"""
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=False)
                return info_dict['url']
        except Exception as e:
            print(f"Помилка отримання YouTube потоку: {e}")
            return None


    def toggle_player(self):
        """Перемикання відображення плеєра"""
        self.show_player = not self.show_player
        if self.show_player:
            youtube_url = self.stream_urls.get(self.current_channel)
            if youtube_url:
                stream_url = self.get_youtube_stream_url(youtube_url)
                if stream_url:
                    self.video_player.set_stream(stream_url)
                    self.video_player.play()
                else:
                    print("Не вдалося отримати URL потоку")
            else:
                print(f"Немає доступного потоку для каналу {self.current_channel}")
        else:
            self.video_player.stop()


    def toggle_player(self):
        """Перемикання відображення плеєра"""
        self.show_player = not self.show_player
        if self.show_player:
            youtube_url = self.stream_urls.get(self.current_channel)
            if youtube_url:
                stream_url = self.get_youtube_stream_url(youtube_url)
                if stream_url:
                    self.video_player.set_stream(stream_url)
                    self.video_player.play()
                else:
                    print("Не вдалося отримати URL потоку")
            else:
                print(f"Немає доступного потоку для каналу {self.current_channel}")
        else:
            self.video_player.stop()

    def handle_click(self, pos):
        for button in self.buttons:
            if button.click():
                return True

        x, y = pos
        if 40 <= x <= 580 and 160 <= y <= 160 + VISIBLE_PROGRAMS * PROGRAM_HEIGHT:
            index = (y - 160) // PROGRAM_HEIGHT + self.scroll_offset
            programs = self.get_programs()
            if 0 <= index < len(programs):
                # Якщо клікнули на вже вибрану програму
                if self.expanded_program_index == index:
                    self.expanded_program_index = None  # Згортаємо програму
                else:
                    self.expanded_program_index = index  # Розгортаємо нову програму
                self.selected_program_index = index
                return True
        return False

    def get_current_day(self):
        return DAYS_OF_WEEK[self.current_day_index]

    def get_programs(self):
        current_day = self.get_current_day()
        return self.schedules[self.current_channel][current_day]

    def next_channel(self):
        current_index = self.channels.index(self.current_channel)
        self.current_channel = self.channels[(current_index + 1) % len(self.channels)]
        self.reset_selection()

    def previous_channel(self):
        current_index = self.channels.index(self.current_channel)
        self.current_channel = self.channels[(current_index - 1) % len(self.channels)]
        self.reset_selection()

    def next_day(self):
        self.current_day_index = (self.current_day_index + 1) % len(DAYS_OF_WEEK)
        self.reset_selection()

    def previous_day(self):
        self.current_day_index = (self.current_day_index - 1) % len(DAYS_OF_WEEK)
        self.reset_selection()

    def reset_selection(self):
        self.selected_program_index = None
        self.scroll_offset = 0

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
            self.target_scroll_offset = self.scroll_offset
            self.transition_time = time.time()

    def scroll_down(self):
        programs = self.get_programs()
        if self.scroll_offset < len(programs) - VISIBLE_PROGRAMS:
            self.scroll_offset += 1
            self.target_scroll_offset = self.scroll_offset
            self.transition_time = time.time()

    def handle_click(self, pos):
        for button in self.buttons:
            if button.click():
                return True

        x, y = pos
        if 40 <= x <= 580 and 160 <= y <= 160 + VISIBLE_PROGRAMS * PROGRAM_HEIGHT:
            index = (y - 160) // PROGRAM_HEIGHT + self.scroll_offset
            programs = self.get_programs()
            if 0 <= index < len(programs):
                self.selected_program_index = index
                return True
        return False
    def update_animations(self):
        # Оновлення плавної прокрутки
        if self.current_scroll_offset != self.target_scroll_offset:
            self.current_scroll_offset = smooth_scroll(
                self.current_scroll_offset,
                self.target_scroll_offset
            )

        # Анімація переходу між днями/каналами
        if self.animation_offset != 0:
            self.animation_offset *= 0.9
            if abs(self.animation_offset) < 0.1:
                self.animation_offset = 0


    
def update():
    if schedule_instance:
        schedule_instance.update_animations()



# Покращуємо функцію draw_gradient_background
def draw_gradient_background(screen):
    # Основний градієнт
    for y in range(HEIGHT):
        progress = y / HEIGHT
        r = COLORS['gradient_top'][0] + (COLORS['gradient_bottom'][0] - COLORS['gradient_top'][0]) * progress
        g = COLORS['gradient_top'][1] + (COLORS['gradient_bottom'][1] - COLORS['gradient_top'][1]) * progress
        b = COLORS['gradient_top'][2] + (COLORS['gradient_bottom'][2] - COLORS['gradient_top'][2]) * progress
        pygame.draw.line(screen.surface, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

    # Додаємо ефект "зірок" на фоні
    current_time = time.time()
    for _ in range(50):
        x = (math.sin(current_time + _ * 0.5) * 0.5 + 0.5) * WIDTH
        y = (math.cos(current_time + _ * 0.7) * 0.5 + 0.5) * HEIGHT
        radius = abs(math.sin(current_time + _ * 0.3)) * 2 + 1
        alpha = int(abs(math.sin(current_time + _ * 0.4)) * 100 + 50)
        
        star_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (*COLORS['glow'], alpha),
                         (radius, radius), radius)
        screen.surface.blit(star_surface, (x - radius, y - radius))

def draw_program_block(screen, program, y, is_current, is_past, is_selected=False):
    program_time, program_name = program['time'], program['program']
    
    # Визначаємо висоту блоку в залежності від того, чи він вибраний
    block_height = PROGRAM_HEIGHT * 2 if is_selected else PROGRAM_HEIGHT

    # Тінь для блоку програми
    shadow_surface = pygame.Surface((544, block_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, COLORS['shadow'],
                    (0, 0, 544, block_height + 4), border_radius=10)
    screen.surface.blit(shadow_surface, (33, y - 3))

    # Визначення кольорів
    if is_current:
        bg_color = (*COLORS['current'][:3], 200)
        text_color = COLORS['title']
        glow_color = COLORS['current']
    elif is_past:
        bg_color = (*COLORS['past'][:3], 150)
        text_color = COLORS['past']
        glow_color = COLORS['past']
    else:
        bg_color = (*COLORS['program_bg'][:3], 180)
        text_color = COLORS['future']
        glow_color = COLORS['button']

    # Основний блок програми з градієнтом
    program_surface = pygame.Surface((540, block_height), pygame.SRCALPHA)
    for i in range(block_height):
        progress = i / block_height
        color = [int(bg_color[j] * (1 - progress * 0.2)) for j in range(3)]
        pygame.draw.line(program_surface, (*color, bg_color[3]),
                        (0, i), (540, i))
    
    pygame.draw.rect(program_surface, (*bg_color[:3], bg_color[3]),
                    (0, 0, 540, block_height), border_radius=10)
    screen.surface.blit(program_surface, (35, y - 5))

    # Блок часу з окремим градієнтом
    time_block = pygame.Surface((80, block_height), pygame.SRCALPHA)
    for i in range(block_height):
        progress = i / block_height
        color = [int(COLORS['time_block'][j] * (1 - progress * 0.3)) for j in range(3)]
        pygame.draw.line(time_block, (*color, 200), (0, i), (80, i))
    
    screen.surface.blit(time_block, (35, y - 5))
    pygame.draw.rect(screen.surface, (*COLORS['button_border'], 128),
                    (35, y - 5, 80, block_height), 1, border_radius=10)

    # Текст з тінню для часу
    shadow_offset = 1
    time_shadow = pygame.font.Font(None, 25).render(program_time, True, (0, 0, 0))
    screen.surface.blit(time_shadow, (46, y + 1))
    screen.draw.text(program_time, (45, y), color=text_color, fontsize=25)

    # Відображення тексту програми
    font = pygame.font.Font(None, 25)
    max_width = 430  # Максимальна ширина для тексту
    
    if is_selected:
        # Повний текст у дві лінії для вибраного блоку
        text_y = y
        words = program_name.split()
        line = ""
        lines = []
        
        for word in words:
            test_line = line + " " + word if line else word
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                if line:
                    lines.append(line)
                line = word
        lines.append(line)
        
        # Відображення всіх ліній
        for i, line in enumerate(lines):
            name_shadow = font.render(line, True, (0, 0, 0))
            screen.surface.blit(name_shadow, (126, text_y + 1 + i * 25))
            screen.draw.text(line, (125, text_y + i * 25), color=text_color, fontsize=25)
    else:
        # Скорочений текст для невибраного блоку
        text = program_name
        text_width = font.size(text)[0]
        
        if text_width > max_width:
            while text_width > max_width - font.size("...")[0]:
                text = text[:-1]
                text_width = font.size(text)[0]
            text += "..."

        name_shadow = font.render(text, True, (0, 0, 0))
        screen.surface.blit(name_shadow, (126, y + 1))
        screen.draw.text(text, (125, y), color=text_color, fontsize=25)

    # Ефекти для поточної програми
    if is_current:
        glow_alpha = abs(math.sin(time.time() * 2)) * 50 + 50
        for i in range(3):
            pygame.draw.rect(screen.surface,
                           (*glow_color, glow_alpha - i * 15),
                           (35 - i, y - 5 - i, 540 + i*2, block_height + i*2),
                           2, border_radius=10)

    # Ефект виділення
    if is_selected:
        for i in range(2):
            pygame.draw.rect(screen.surface,
                           (*COLORS['selected'], 150 - i * 50),
                           (35 - i, y - 5 - i, 540 + i*2, block_height + i*2),
                           2, border_radius=10)
    
    return block_height  # Повертаємо висоту блоку для правильного розміщення наступних програм


def is_current_program(program_time, next_program_time=None):
    current_time = datetime.now().strftime("%H:%M")
    return program_time <= current_time < (next_program_time if next_program_time else "24:00")



def draw():
    global schedule_instance
    if not hasattr(draw, 'splash'):
        draw.splash = SplashScreen()
    
    if not draw.splash.finished:
        draw.splash.update()
        draw.splash.draw(screen)
        return
    
    if schedule_instance is None:
        return

    screen.clear()
    draw_gradient_background(screen)

    # Заголовок з ефектом світіння
    current_day = schedule_instance.get_current_day()
    title_text = f"Розклад телепередач - {current_day}"
    
    # Градієнтне підсвічування заголовка
    title_surface = pygame.font.Font(None, 50).render(title_text, True, COLORS['title'])
    text_rect = title_surface.get_rect(topleft=(20, 20))
    
    # Тінь для заголовка
    shadow_surface = pygame.font.Font(None, 50).render(title_text, True, (0, 0, 0))
    screen.surface.blit(shadow_surface, (22, 22))
    screen.surface.blit(title_surface, (20, 20))

    # Градієнтна лінія
    for x in range(WIDTH - 40):
        progress = x / (WIDTH - 40)
        alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        pygame.draw.line(screen.surface, (*COLORS['button_border'], alpha),
                        (20 + x, 80), (21 + x, 80))

    channel_text = f"Канал: {schedule_instance.current_channel}"
    text_size = pygame.font.Font(None, 35).size(channel_text)
    
    # Фон для назви каналу з градієнтом
    channel_bg = pygame.Surface((text_size[0] + 10, 40), pygame.SRCALPHA)
    for i in range(40):
        progress = i / 40
        color = [int(COLORS['button'][j] * (1 - progress * 0.3)) for j in range(3)]
        pygame.draw.line(channel_bg, (*color, 200), (0, i), (text_size[0] + 10, i))
    screen.surface.blit(channel_bg, (15, 95))
    
    # Текст каналу з тінню
    shadow_text = pygame.font.Font(None, 35).render(channel_text, True, (0, 0, 0))
    screen.surface.blit(shadow_text, (21, 101))
    screen.draw.text(channel_text, (20, 100), fontsize=35, color=COLORS['channel'])

    # Відображення логотипу каналу
    current_logo = schedule_instance.channel_logos.get(schedule_instance.current_channel)
    if current_logo:
        # Створюємо поверхню для тіні
        shadow_surface = pygame.Surface((82, 82), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, COLORS['shadow'],
                        (0, 0, 82, 82), border_radius=10)
        

        # Відображаємо логотип
        screen.surface.blit(current_logo, (WIDTH - 200, 100))
        



    # Текст каналу з тінню
    shadow_text = pygame.font.Font(None, 35).render(channel_text, True, (0, 0, 0))
    screen.surface.blit(shadow_text, (21, 101))
    screen.draw.text(channel_text, (20, 100), fontsize=35, color=COLORS['channel'])

    # Поточний час зі світінням
    current_time = datetime.now().strftime("%H:%M")
    time_text = f"Поточний час: {current_time}"
    time_size = pygame.font.Font(None, 30).size(time_text)
    
    # Фон для часу з градієнтом
    time_bg = pygame.Surface((time_size[0] + 20, 40), pygame.SRCALPHA)
    for i in range(40):
        progress = i / 40
        color = [int(COLORS['time_bg'][j] * (1 - progress * 0.3)) for j in range(3)]
        pygame.draw.line(time_bg, (*color, 200), (0, i), (time_size[0] + 20, i))
    screen.surface.blit(time_bg, (WIDTH - time_size[0] - 30, 15))

    # Рамка часу зі світінням
    glow_alpha = abs(math.sin(time.time() * 2)) * 30 + 70
    for i in range(2):
        pygame.draw.rect(screen.surface, (*COLORS['button_border'], glow_alpha - i * 30),
                        (WIDTH - time_size[0] - 30 - i, 15 - i,
                         time_size[0] + 20 + i*2, 40 + i*2),
                        2, border_radius=5)

    screen.draw.text(time_text, (WIDTH - time_size[0] - 20, 20),
                    fontsize=30, color=COLORS['title'])

    # Програми
    programs = schedule_instance.get_programs()
    visible_programs = programs[schedule_instance.scroll_offset:
                              schedule_instance.scroll_offset + VISIBLE_PROGRAMS]

    base_y = 160
    max_y = HEIGHT - 70

    for i, program in enumerate(visible_programs):
        if base_y + PROGRAM_HEIGHT > max_y:
            break
            
        is_current = is_current_program(program['time'])
        is_past = program['time'] < current_time
        is_selected = (schedule_instance.scroll_offset + i) == schedule_instance.selected_program_index
        
        # Отримуємо висоту блоку після відображення
        block_height = draw_program_block(screen, program, base_y, is_current, is_past, is_selected)
        
        # Збільшуємо base_y на висоту щойно намальованого блоку
        base_y += block_height
    if schedule_instance.show_player:
        schedule_instance.video_player.draw(screen, WIDTH - 450, 160)
        
    # Додаємо скроллбар з анімацією
    if len(programs) > VISIBLE_PROGRAMS:
        total_height = VISIBLE_PROGRAMS * PROGRAM_HEIGHT
        scroll_height = (VISIBLE_PROGRAMS / len(programs)) * total_height
        scroll_pos = (schedule_instance.scroll_offset / (len(programs) - VISIBLE_PROGRAMS)) * (total_height - scroll_height)
        
        # Фон скроллбара
        pygame.draw.rect(screen.surface, 
                        (*COLORS['menu_bg'], 150),
                        (580, 160, 5, total_height),
                        border_radius=3)
        pygame.draw.rect(screen.surface,
                        COLORS['button'],
                        (580, 160 + scroll_pos, 5, scroll_height),
                        border_radius=3)
        
        # Активна частина скроллбара з градієнтом
        scroll_surface = pygame.Surface((5, scroll_height), pygame.SRCALPHA)
        for i in range(int(scroll_height)):
            progress = i / scroll_height
            color = [int(COLORS['button'][j] * (1 - progress * 0.3)) for j in range(3)]
            pygame.draw.line(scroll_surface, (*color, 200),
                           (0, i), (5, i))
        screen.surface.blit(scroll_surface, (575, 160 + scroll_pos))


        # Додаємо світіння для скроллбара
        glow_alpha = abs(math.sin(time.time() * 2)) * 30 + 40
        pygame.draw.rect(screen.surface,
                        (*COLORS['button_border'], glow_alpha),
                        (575, 160 + scroll_pos, 5, scroll_height),
                        border_radius=3)

    # Малюємо кнопки
    for button in schedule_instance.buttons:
        button.draw(screen)


def on_mouse_move(pos):
    global schedule_instance
    if schedule_instance:
        for button in schedule_instance.buttons:
            button.handle_mouse(pos)


def on_mouse_down(pos, button):
    global schedule_instance
    if schedule_instance and button == mouse.LEFT:
        schedule_instance.handle_click(pos)


def on_mouse_wheel(pos, wheel_y):
    if schedule_instance:
        if wheel_y > 0:
            schedule_instance.scroll_up()
        else:
            schedule_instance.scroll_down()
            
def scroll_up(self):
    if self.scroll_offset > 0:
        self.scroll_offset = max(0, self.scroll_offset - 3)  # Прокручуємо на 3 програми вгору
        
def scroll_down(self):
    programs = self.get_programs()
    max_offset = len(programs) - VISIBLE_PROGRAMS
    if self.scroll_offset < max_offset:
        self.scroll_offset = min(max_offset, self.scroll_offset + 3)  # Прокручуємо на 3 програми вниз

def on_key_down(key):
    global schedule_instance
    if not schedule_instance:
        return
        
    if key == keys.PAGEDOWN:
        schedule_instance.next_channel()
        schedule_instance.animation_offset = WIDTH
    elif key == keys.PAGEUP:
        schedule_instance.previous_channel()
        schedule_instance.animation_offset = -WIDTH
    elif key == keys.DOWN:
        schedule_instance.scroll_down()
    elif key == keys.UP:
        schedule_instance.scroll_up()
    elif key == keys.RIGHT:
        schedule_instance.next_day()
        schedule_instance.animation_offset = HEIGHT
    elif key == keys.LEFT:
        schedule_instance.previous_day()
        schedule_instance.animation_offset = -HEIGHT


# Викликаємо функцію main() перед запуском
main()

pgzrun.go()
