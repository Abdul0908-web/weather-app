import sys
import requests
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QAction,
                             QLineEdit, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QIcon, QPixmap, QPainter


class weatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image = None
        self.city_label = QLabel('Enter city name:', self)
        self.city_input = QLineEdit(self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.weather_description_label = QLabel(self)
        self.initUI()

    def resource_path(self, relative_path):
        """Get absolute path to resource, works for PyInstaller"""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def initUI(self):
        self.setWindowTitle('Weather App')
        self.setWindowIcon(QIcon(self.resource_path('cloudy.ico')))
        self.setMinimumSize(450, 550)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Glass Container
        self.glass_frame = QWidget()
        self.glass_frame.setFixedWidth(400)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.black)
        self.glass_frame.setGraphicsEffect(shadow)

        glass_layout = QVBoxLayout(self.glass_frame)
        glass_layout.setSpacing(15)
        glass_layout.setContentsMargins(30, 40, 30, 40)

        glass_layout.addWidget(self.city_label)
        glass_layout.addWidget(self.city_input)
        glass_layout.addWidget(self.temperature_label)
        glass_layout.addWidget(self.emoji_label)
        glass_layout.addWidget(self.weather_description_label)

        layout.addWidget(self.glass_frame)
        self.setLayout(layout)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.weather_description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName('city_label')
        self.city_input.setObjectName('city_input')
        self.glass_frame.setObjectName('glass_frame')
        self.temperature_label.setObjectName('temperature_label')
        self.emoji_label.setObjectName('emoji_label')
        self.weather_description_label.setObjectName(
            'weather_description_label')

        search_icon = QIcon(self.resource_path(('search.png')))
        search_button = QAction(search_icon, "", self)
        self.city_input.addAction(search_button, QLineEdit.TrailingPosition)

        search_button.triggered.connect(self.get_weather)
        self.city_input.returnPressed.connect(self.get_weather)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4facfe,
                    stop:1 #00f2fe       
                );
                font-family: 'Segoe UI';
            }}
            QWidget#glass_frame{{
                background-color: rgba(255, 255, 255, 0.15);         
                border-radius: 25px;
                border: 1px solid rgba(255, 255, 255, 0.3)
            }}
            QLabel#city_label,
            QLabel#temperature_label,
            QLabel#weather_description_label{{
                background-color: transparent;
                color: white;
            }}
            QLabel#city_label {{
                font-size: 40px;  font-weight: 600
            }}
            QLineEdit#city_input {{
                font-size: 35px; padding-right: 25px;
                border: none; border-radius: 15px; 
                background-color: rgba(255,255,255,0.25);
                color: white;
            }}
            QLineEdit#city_input:hover {{
                background-color: rgba(255,255,255,0.35);
            }}
            QLabel#temperature_label {{
                font-size: 75px;  font-weight: bold;
            }}
            QLabel#emoji_label {{
                font-size: 75px; background: transparent;
                font-family: 'Segoe Ui Emoji';
            }}
            QLabel#weather_description_label {{
                font-size: 45px;
            }}
        """)

    def set_background(self, weather_description, is_night):
        desc = weather_description.lower()

        if is_night:
            image = 'night.jpg'
        elif "clear" in desc:
            image = "sunny.jpg"
        elif "cloud" in desc:
            image = "clouds.jpg"
        elif "rain" in desc or "drizzle" in desc:
            image = "rain.jpg"
        elif "thunderstorm" in desc:
            image = "thunderstorm.jpg"
        elif "snow" in desc:
            image = "snow.jpg"
        elif "fog" in desc or "mist" in desc or "haze" in desc:
            image = "fog.jpg"
        elif "smoke" in desc:
            image = "smoke.jpg"
        else:
            image = None  # default background

        if image:
            picture = QPixmap(self.resource_path(image))
            if not picture.isNull():
                self.background_image = picture
            else:
                self.background_image = None

        else:
            self.background_image = None

        self.update()

    def fade_in_animation(self):
        if not hasattr(self, 'content_opacity'):
            self.glass_frame.setGraphicsEffect(None)

            self.content_opacity = QGraphicsOpacityEffect()
            self.glass_frame.setGraphicsEffect(self.content_opacity)

            self.animation = QPropertyAnimation(
                self.content_opacity, b'opacity')
            self.animation.setDuration(600)
            self.animation.setStartValue(0)
            self.animation.setEndValue(1)
            self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.background_image:
            scaled = self.background_image.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        super().paintEvent(event)

    def get_weather(self):
        api_key = 'ENTER YOUR API KEY'
        city_name = self.city_input.text()
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric'
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('cod') == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError:
            match response.status_code:
                case 400:
                    self.display_errors("Bad Request:\nCheck your input")
                case 401:
                    self.display_errors("Unauthorized:\nInvalid API key")
                case 403:
                    self.display_errors("Forbidden:\nAccess is denied")
                case 404:
                    self.display_errors("Not Found:\nCity not found")
                case 500:
                    self.display_errors(
                        "Internal Server Error:\nTry again later")
                case 502:
                    self.display_errors("Bad Gateway:\nTry again later")
                case 503:
                    self.display_errors(
                        "Service Unavailable:\nTry again later")
                case 504:
                    self.display_errors("Gateway Timeout:\nTry again later")

        except requests.exceptions.ConnectionError:
            self.display_errors(
                "Connection Error:\nCheck your internet connection")

        except requests.exceptions.Timeout:
            self.display_errors("Timeout Error:\nThe request timed out")

        except requests.exceptions.TooManyRedirects:
            self.display_errors("Too Many Redirects:\nCheck the URL")

        except requests.exceptions.RequestException as req_error:
            self.display_errors(f"Request Error:\n{req_error}")

    def display_errors(self, error_message):
        self.temperature_label.setStyleSheet('font-size: 20px;')
        self.temperature_label.setText(error_message)
        self.emoji_label.setText('⚠️')
        self.weather_description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet('font-size: 75px;')
        self.temperature_label.setText(
            f"{data['main']['temp']:.1f}°C")

        weather_description = data['weather'][0]['description']
        self.weather_description_label.setText(weather_description)

        # Night detection:
        current_time = data['dt']
        sunrise = data['sys']['sunrise']
        sunset = data['sys']['sunset']

        is_night = current_time < sunrise or current_time > sunset

        self.set_background(weather_description, is_night)
        self.emoji(weather_description, is_night)

        self.fade_in_animation()

    def emoji(self, weather_description, is_night):
        desc = weather_description.lower()
        if is_night:
            if 'broken' in desc or 'partly' in desc:
                self.emoji_label.setText('☁🌙')
            elif 'rian' in desc:
                self.emoji_label.setText('🌧🌙')
            elif 'cloud' in desc:
                self.emoji_label.setText('☁')
            else:
                self.emoji_label.setText('🌙')
        else:
            if 'rain' in desc:
                self.emoji_label.setText('🌧️')
            elif 'broken clouds' in desc:
                self.emoji_label.setText('⛅')
            elif 'clear' in desc:
                self.emoji_label.setText('☀️')
            elif 'thunderstorm' in desc:
                self.emoji_label.setText('⛈️')
            elif 'drizzle' in desc:
                self.emoji_label.setText('🌦️')
            elif 'cloud' in desc:
                self.emoji_label.setText('☁️')
            elif 'fog' in desc or 'mist' in desc:
                self.emoji_label.setText('🌫️')
            elif 'snow' in desc:
                self.emoji_label.setText('❄️')
            elif 'haze' in desc:
                self.emoji_label.setText('🌁')
            elif 'smoke' in desc:
                self.emoji_label.setText('🚬')


def main():
    app = QApplication(sys.argv)
    weatherapp = weatherApp()
    weatherapp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
