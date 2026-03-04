"""Page Object Model helpers for the UI Portal."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


DEFAULT_TIMEOUT = 10


class BasePage:
    """Base class for all page objects."""

    def __init__(self, driver: WebDriver, base_url: str = "") -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = "") -> None:
        self.driver.get(f"{self.base_url}{path}")

    def find(self, by: str, value: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    @property
    def title(self) -> str:
        return self.driver.title

    @property
    def current_url(self) -> str:
        return self.driver.current_url


class LoginPage(BasePage):
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")

    def login(self, username: str, password: str) -> None:
        self.find(*self.USERNAME_FIELD).clear()
        self.find(*self.USERNAME_FIELD).send_keys(username)
        self.find(*self.PASSWORD_FIELD).clear()
        self.find(*self.PASSWORD_FIELD).send_keys(password)
        self.find(*self.LOGIN_BUTTON).click()

    def get_error(self) -> str:
        try:
            return self.find(*self.ERROR_MESSAGE, timeout=3).text
        except Exception:
            return ""


class DashboardPage(BasePage):
    WELCOME_HEADER = (By.CSS_SELECTOR, "h1.welcome")
    LOGOUT_LINK = (By.LINK_TEXT, "Logout")

    def is_loaded(self) -> bool:
        try:
            self.find(*self.WELCOME_HEADER, timeout=5)
            return True
        except Exception:
            return False

    def logout(self) -> None:
        self.find(*self.LOGOUT_LINK).click()
