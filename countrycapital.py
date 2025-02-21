import sys
import requests

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class Country_Capital_App(QWidget):
    def __init__(self):
        super().__init__()
        self.country_label = QLabel("Enter country name", self)
        self.country_input = QLineEdit(self)
        self.get_capital_button = QPushButton("Get Capital", self)
        self.capital_label = QLabel(self)
        self.country_flag_label = QLabel(self)
        self.country_flag = QPixmap()
        self.initUI()
        self.cache = {}


    def initUI(self):
        self.setWindowTitle("Get the capital of every country")

        vbox = QVBoxLayout()
        vbox.addWidget(self.country_label)
        vbox.addWidget(self.country_input)
        vbox.addWidget(self.get_capital_button)
        vbox.addWidget(self.capital_label)
        vbox.addWidget(self.country_flag_label)

        self.setLayout(vbox)

        self.country_label.setAlignment(Qt.AlignCenter)
        self.country_input.setAlignment(Qt.AlignCenter)
        self.capital_label.setAlignment(Qt.AlignCenter)
        self.country_flag_label.setAlignment(Qt.AlignCenter)

        self.country_label.setObjectName("country_label")
        self.country_input.setObjectName("country_input")
        self.get_capital_button.setObjectName("get_capital_button")
        self.capital_label.setObjectName("capital_label")
        self.country_flag_label.setObjectName("country_flag_label")

        self.setStyleSheet(""" 
            QLabel, QPushbutton{
                font-family: calibri;
            }
            QLabel#country_label{
                font-size: 40px;
                font-style: italic;
            }
            QLineEdit#country_input{
                font-size: 40px;
            }
            QPushButton#get_capital_button{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#capital_label{
                font-size: 75px;
            }
            QLabel#country_flag_label{
                font-size: 100px;
                font-family: Segoe UI emoji;
            }
        """)

        self.get_capital_button.clicked.connect(self.get_capital)

    def get_capital(self):
        country_name = self.country_input.text().strip().lower()

        if not country_name: 
            self.display_error("Please enter a country name")
            return
        
        if country_name in self.cache:
            self.display_capital(self.cache[country_name])  
            return
        
        self.capital_label.setStyleSheet("font-size: 30px; color: gray;")
        self.capital_label.setText("Loading...") 

        api_url = f"https://restcountries.com/v3.1/name/{country_name}"

        try:
            response = requests.get(api_url)
            response.raise_for_status() 

            if response.status_code == 200:
                data = response.json()
                self.cache[country_name] = data
                self.display_capital(data)
        
        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Bad request:\nPlease check your input")
                case 401:
                    self.display_error("Unathorized:\nInvalid API key")
                case 403:
                    self.display_error("Forbidden:\nAccess is denied")
                case 404:
                    self.display_error("Not found:\nCountry not found")
                case 500:
                    self.display_error("Internal Server Error:\nPlease try again later")
                case 502:
                    self.display_error("Bad gateway:\nInvalid response from the server")
                case 503:
                    self.display_error("Server is unavailable:\n Server is down")
                case 504:
                    self.display_error("Gateway Timeout:\n No response from the server")
                case _:
                    self.display_error(f"HTTP error occured:\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error: \nCheck your internet connection")

        except requests.exceptions.ConnectTimeout:
            self.display_error("Timeout Error: \nThe request timed out!")

        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects: \nCheck the URL")

        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error: \n{req_error}")

        
    def get_country_flag(self, data):
        flag_url = data[0]["flags"]["png"]  
    
        try:
            flag_response = requests.get(flag_url)
            flag_response.raise_for_status()
            self.country_flag.loadFromData(flag_response.content)
            self.country_flag_label.setPixmap(self.country_flag)
            self.country_flag_label.setAlignment(Qt.AlignCenter)
        except requests.exceptions.RequestException:
            self.country_flag_label.setText("Flag not found")
    
    def display_error(self, message):
        self.capital_label.setStyleSheet("font-size: 30px;")
        self.capital_label.setText(message)
        self.country_flag_label.clear()

    def display_capital(self, data):
        self.capital_label.setStyleSheet("font-size: 75px;")
        capital_name = data[0].get("capital", ["Capital not available"])[0]
        self.capital_label.setText(capital_name)

        self.get_country_flag(data)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    country_app = Country_Capital_App()
    country_app.show()
    sys.exit(app.exec_())


    


