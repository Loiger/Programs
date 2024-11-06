from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import os
from time import sleep
import random

DAYS_OF_WEEK = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]

def setup_driver():
    """Налаштування драйвера Chrome з українською локалізацією"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--lang=uk-UA')  # Українська локалізація
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def parse_tv_program(url, driver, retries=2):
    """Парсинг телепрограми з використанням Selenium для кожного дня."""
    try:
        print(f"Відкриваємо сторінку: {url}")
        driver.get(url)
        sleep(random.uniform(3, 5))

        # Видаляємо клас hidden у прихованих елементів
        driver.execute_script("document.querySelectorAll('.hidden').forEach(el => el.classList.remove('hidden'));")

        # Чекаємо на завантаження елементів
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "channel-block__day"))
        )

        days_programs = {}

        # Знаходимо всі секції з програмами для кожного дня
        day_sections = driver.find_elements(By.CLASS_NAME, "channel-block__day")

        for i, section in enumerate(day_sections):
            try:
                # Отримуємо назву дня (приклад: "Понеділок", "Вівторок" тощо)
                day_name = DAYS_OF_WEEK[i % 7]

                # Ініціалізуємо пустий список для програм кожного дня
                days_programs[day_name] = []

                # Збираємо програми для цього дня
                program_elements = section.find_elements(By.CSS_SELECTOR, ".channel-block__channels td")

                for element in program_elements:
                    try:
                        # Знаходимо час і назву програми
                        span_elements = element.find_elements(By.TAG_NAME, "span")

                        if len(span_elements) >= 2:
                            time = span_elements[0].text.strip()  # Перший span - час
                            name = span_elements[1].text.strip()  # Другий span - назва програми

                            if time and name:
                                days_programs[day_name].append({
                                    "time": time,
                                    "program": name
                                })
                                print(f"Знайдено програму для {day_name}: {time} - {name}")
                    except Exception as e:
                        print(f"Помилка при парсингу елемента: {e}")
                        continue

            except Exception as e:
                print(f"Помилка при парсингу дня: {e}")
                continue

        return days_programs

    except Exception as e:
        if retries > 0:
            print(f"Помилка при парсингу сторінки, повторна спроба: {e}")
            sleep(5)
            return parse_tv_program(url, driver, retries - 1)
        else:
            print(f"Помилка при парсингу сторінки: {e}")
            driver.save_screenshot("error_screenshot.png")
            return {}

def save_to_json(channel_name, days_programs):
    """Зберігає програми у JSON файл у форматі для кожного дня"""
    os.makedirs('channels', exist_ok=True)
    filename = f'channels/{channel_name}.json'

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(days_programs, f, ensure_ascii=False, indent=4)

    print(f"Програму збережено у файл {filename}")

def main():
    channels = {
        "ictv": "https://tv.meta.ua/uk/ictv/",
        "1plus1": "https://tv.meta.ua/uk/1plus1/",
        "stb": "https://tv.meta.ua/uk/stb/",
        "novy": "https://tv.meta.ua/uk/novy/"
    }

    for channel_name, url in channels.items():
        driver = setup_driver()  # Створюємо новий екземпляр драйвера для кожного каналу
        try:
            print(f"\nПарсимо канал {channel_name}...")

            # Очищаємо файли cookie перед переходом на нову сторінку
            driver.delete_all_cookies()

            days_programs = parse_tv_program(url, driver)

            if days_programs:
                save_to_json(channel_name, days_programs)
                print(f"Програми успішно збережено для каналу {channel_name}")
            else:
                print(f"Не вдалося отримати програми для каналу {channel_name}")

            sleep(random.uniform(2, 4))  # Затримка між каналами

        finally:
            driver.quit()  # Закриваємо драйвер після кожного каналу

if __name__ == "__main__":
    main()
