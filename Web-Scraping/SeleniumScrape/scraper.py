import os
import time
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

load_dotenv()

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in ("1","true","t","yes","y")

def create_driver(
    browser: str | None = None,
    headless: bool | None = None,
    window_size: str | None = None,
    user_agent: str | None = None,
    implicit_wait_sec: float = 0
) -> webdriver.Remote:
    """Create a Chrome or Firefox driver using webdriver-manager."""
    browser = (browser or os.getenv("BROWSER") or "chrome").lower().strip()
    headless = _bool_env("HEADLESS", True) if headless is None else headless
    window_size = window_size or os.getenv("WINDOW_SIZE") or "1280,800"
    user_agent = user_agent or os.getenv("USER_AGENT") or None

    width, height = (int(x) for x in window_size.split(",", 1))

    if browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        if user_agent:
            options.set_preference("general.useragent.override", user_agent)
        service = FirefoxService(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
    else:
        # default: chrome
        options = ChromeOptions()
        if headless:
            # modern headless mode
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if user_agent:
            options.add_argument(f"--user-agent={user_agent}")
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    if implicit_wait_sec:
        driver.implicitly_wait(implicit_wait_sec)
    return driver

@contextmanager
def driver_context(**kwargs):
    driver = create_driver(**kwargs)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:
            pass

def safe_wait_css(driver, selector: str, timeout: float = 10.0):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )

def click_if_present(driver, selector: str, timeout: float = 3.0) -> bool:
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        el.click()
        return True
    except Exception:
        return False

# ---------------------- Demo scrape: quotes.toscrape.com ----------------------
def scrape_quotes(start_url: str = "https://quotes.toscrape.com/", max_pages: int = 5):
    """Yield quote dicts from quotes.toscrape.com, navigating pagination with Selenium."""
    with driver_context() as d:
        d.get(start_url)
        page = 0
        while page < max_pages:
            page += 1
            try:
                # Wait for quote cards
                safe_wait_css(d, ".quote", timeout=10)
            except Exception as e:
                log.error("Timeout waiting for quotes on page %s: %s", page, e)
                yield from ()
                break

            cards = d.find_elements(By.CSS_SELECTOR, ".quote")
            for c in cards:
                text = c.find_element(By.CSS_SELECTOR, ".text").text
                author = c.find_element(By.CSS_SELECTOR, ".author").text
                tags = [t.text for t in c.find_elements(By.CSS_SELECTOR, ".tags .tag")]
                yield {"text": text, "author": author, "tags": tags, "url": d.current_url}

            # Next page?
            if not click_if_present(d, "li.next a", timeout=2):
                break
            # wait for navigation
            time.sleep(0.5)