import os
import random
import time
import threading
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display  # For headless on Linux
import mouse
from mouse import move
import pyautogui
import numpy as np
from faker import Faker

fake = Faker()

class AntiDetectBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Al-Khair Traffic Bot by Waqar-Hussnain")
        self.root.geometry("900x750")
        self.running = False
        self.threads = []
        self.profiles = []
        self.setup_ui()
        
    def get_user_agent(self):
        """Get a random user agent with fallback if browsers.json is missing"""
        try:
            return UserAgent().random
        except:
            # Fallback user agents if the main method fails
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
            ]
            return random.choice(user_agents)
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Website Settings Frame
        website_frame = ttk.LabelFrame(main_frame, text="Website Settings", padding="10")
        website_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Website URL
        ttk.Label(website_frame, text="Website URL:").grid(row=0, column=0, sticky="w")
        self.website_url = ttk.Entry(website_frame, width=50)
        self.website_url.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        # Referral Link
        ttk.Label(website_frame, text="Referral Link (optional):").grid(row=1, column=0, sticky="w")
        self.referral_link = ttk.Entry(website_frame, width=50)
        self.referral_link.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        # Official Site URL
        ttk.Label(website_frame, text="Official Site URL (optional):").grid(row=2, column=0, sticky="w")
        self.official_site_url = ttk.Entry(website_frame, width=50)
        self.official_site_url.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Keywords (optional)
        ttk.Label(website_frame, text="Keywords (optional, comma separated):").grid(row=3, column=0, sticky="w")
        self.keywords = ttk.Entry(website_frame, width=50)
        self.keywords.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Bot Settings Frame
        bot_frame = ttk.LabelFrame(main_frame, text="Bot Settings", padding="10")
        bot_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Use Proxies
        self.use_proxy = tk.BooleanVar()
        ttk.Checkbutton(bot_frame, text="Use Proxy File (proxies.txt)", variable=self.use_proxy).grid(row=0, column=0, sticky="w")
        
        # Proxy File Location
        ttk.Label(bot_frame, text="Proxy File Location:").grid(row=1, column=0, sticky="w")
        self.proxy_file = ttk.Entry(bot_frame, width=40)
        self.proxy_file.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Button(bot_frame, text="Browse", command=self.browse_proxy_file).grid(row=1, column=2, padx=5)
        
        # Current Profiles
        ttk.Label(bot_frame, text="Current Profiles (Max 100):").grid(row=2, column=0, sticky="w")
        self.current_profiles = ttk.Entry(bot_frame, width=10)
        self.current_profiles.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        self.current_profiles.insert(0, "1")
        
        # Total Profiles
        ttk.Label(bot_frame, text="Total Profiles:").grid(row=3, column=0, sticky="w")
        self.total_profiles = ttk.Entry(bot_frame, width=10)
        self.total_profiles.grid(row=3, column=1, padx=5, pady=2, sticky="w")
        self.total_profiles.insert(0, "10")
        
        # Completion Time
        ttk.Label(bot_frame, text="Completion Time (hrs/mins):").grid(row=4, column=0, sticky="w")
        self.completion_time = ttk.Entry(bot_frame, width=10)
        self.completion_time.grid(row=4, column=1, padx=5, pady=2, sticky="w")
        self.completion_time.insert(0, "1h")
        
        # Max Page Visits
        ttk.Label(bot_frame, text="Max Page Visits (0-10):").grid(row=5, column=0, sticky="w")
        self.max_page_visits = ttk.Spinbox(bot_frame, from_=0, to=10, width=5)
        self.max_page_visits.grid(row=5, column=1, padx=5, pady=2, sticky="w")
        self.max_page_visits.set("3")
        
        # Platforms
        ttk.Label(bot_frame, text="Platforms:").grid(row=6, column=0, sticky="w")
        self.platform_win = tk.BooleanVar(value=True)
        self.platform_android = tk.BooleanVar()
        ttk.Checkbutton(bot_frame, text="Windows", variable=self.platform_win).grid(row=6, column=1, sticky="w")
        ttk.Checkbutton(bot_frame, text="Android", variable=self.platform_android).grid(row=6, column=2, sticky="w")
        
        # Additional Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Additional Options", padding="10")
        options_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        # Checkboxes
        self.extra_pages = tk.BooleanVar()
        self.headless = tk.BooleanVar()
        self.direct_visit = tk.BooleanVar(value=True)
        self.referral = tk.BooleanVar()
        
        ttk.Checkbutton(options_frame, text="Visit Extra Pages", variable=self.extra_pages).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(options_frame, text="Headless Mode", variable=self.headless).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(options_frame, text="Direct Visit", variable=self.direct_visit).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(options_frame, text="Use Referral", variable=self.referral).grid(row=1, column=1, sticky="w")
        
        # Control Buttons Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        # Start/Stop Buttons
        self.start_button = ttk.Button(button_frame, text="Start Bot", command=self.start_bot)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=5)
        
        # Log Text
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
    def browse_proxy_file(self):
        filename = filedialog.askopenfilename(title="Select Proxy File", filetypes=[("Text files", "*.txt")])
        if filename:
            self.proxy_file.delete(0, tk.END)
            self.proxy_file.insert(0, filename)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def start_bot(self):
        if not self.website_url.get():
            messagebox.showerror("Error", "Please enter a website URL")
            return
            
        try:
            total_profiles = int(self.total_profiles.get())
            if total_profiles < 1 or total_profiles > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Total profiles must be between 1 and 100")
            return
            
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.log_message("Starting bot...")
        
        # Load proxies if enabled
        proxies = []
        if self.use_proxy.get():
            try:
                with open(self.proxy_file.get(), 'r') as f:
                    proxies = [line.strip() for line in f.readlines() if line.strip()]
                self.log_message(f"Loaded {len(proxies)} proxies")
            except Exception as e:
                self.log_message(f"Error loading proxies: {str(e)}")
                proxies = []
        
        # Start bot threads
        total_profiles = int(self.total_profiles.get())
        for i in range(total_profiles):
            if not self.running:
                break
                
            proxy = random.choice(proxies) if proxies else None
            thread = threading.Thread(target=self.run_bot_profile, args=(i+1, proxy))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            time.sleep(random.uniform(0.5, 2.0))  # Stagger profile starts
            
        self.log_message(f"Started {total_profiles} bot profiles")
    
    def stop_bot(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("Stopping bot... Please wait for all profiles to close.")
        
    def run_bot_profile(self, profile_num, proxy=None):
        try:
            self.log_message(f"Profile {profile_num}: Starting...")
            
            # Create human-like profile
            profile = self.create_human_profile(profile_num)
            
            # Configure browser options
            options = self.configure_browser_options(profile, proxy)
            
            # Initialize WebDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.profiles.append(driver)
            
            # Set window size randomly
            width = random.randint(1000, 1400)
            height = random.randint(700, 900)
            driver.set_window_size(width, height)
            
            # Random window position
            x_pos = random.randint(0, 500)
            y_pos = random.randint(0, 300)
            driver.set_window_position(x_pos, y_pos)
            
            # Visit website
            visit_type = self.determine_visit_type()
            self.visit_website(driver, profile_num, visit_type)
            
            # Human-like browsing
            max_visits = int(self.max_page_visits.get())
            if max_visits > 0:
                self.human_browsing(driver, profile_num, max_visits)
            
            # Random time on site
            time_on_site = random.uniform(30, 300)
            self.log_message(f"Profile {profile_num}: Staying on site for {time_on_site:.1f} seconds")
            start_time = time.time()
            
            while time.time() - start_time < time_on_site and self.running:
                time.sleep(1)
                # Occasionally scroll or interact
                if random.random() < 0.2:
                    self.human_interaction(driver)
            
            self.log_message(f"Profile {profile_num}: Session completed")
            
        except Exception as e:
            self.log_message(f"Profile {profile_num}: Error - {str(e)}")
        finally:
            try:
                if 'driver' in locals():
                    driver.quit()
                    self.log_message(f"Profile {profile_num}: Browser closed")
            except Exception as e:
                self.log_message(f"Profile {profile_num}: Error closing browser - {str(e)}")
    
    def create_human_profile(self, profile_num):
        """Create a human-like profile with randomized attributes"""
        profile = {
            'id': profile_num,
            'user_agent': self.get_user_agent(),
            'platform': random.choice(['win32', 'linux', 'mac']) if self.platform_win.get() else 'android',
            'timezone': random.choice(['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']),
            'language': random.choice(['en-US', 'en-GB', 'fr-FR', 'de-DE', 'es-ES']),
            'screen_width': random.randint(1280, 1920),
            'screen_height': random.randint(720, 1080),
            'color_depth': random.choice([24, 30, 32]),
            'cpu_cores': random.randint(2, 8),
            'memory': random.randint(4, 16),
            'name': fake.name(),
            'email': fake.email(),
            'address': fake.address(),
            'ip': fake.ipv4() if not self.use_proxy.get() else None
        }
        return profile
    
    def configure_browser_options(self, profile, proxy=None):
        """Configure Chrome options with human-like settings"""
        options = Options()
        
        # Basic settings
        if self.headless.get():
            options.add_argument('--headless')
        
        # Human-like settings
        options.add_argument(f'--user-agent={profile["user_agent"]}')
        options.add_argument(f'--lang={profile["language"]}')
        options.add_argument(f'--timezone={profile["timezone"]}')
        
        # Disable automation flags
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Proxy settings
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Randomize other settings
        if random.random() < 0.5:
            options.add_argument('--disable-extensions')
        if random.random() < 0.3:
            options.add_argument('--disable-gpu')
        
        return options
    
    def determine_visit_type(self):
        """Determine how the bot will visit the website"""
        if self.direct_visit.get() and not self.referral.get():
            return 'direct'
        elif self.referral.get() and not self.direct_visit.get():
            return 'referral'
        else:
            return random.choice(['direct', 'referral'])
    
    def visit_website(self, driver, profile_num, visit_type):
        """Visit the website with human-like behavior"""
        base_url = self.website_url.get()
        
        if visit_type == 'referral' and self.referral_link.get():
            url = self.referral_link.get()
            self.log_message(f"Profile {profile_num}: Visiting via referral: {url}")
        else:
            url = base_url
            self.log_message(f"Profile {profile_num}: Visiting directly: {url}")
        
        # Simulate human-like delay before visiting
        time.sleep(random.uniform(1.0, 3.0))
        
        # Open the URL
        driver.get(url)
        
        # Random mouse movement to the address bar before typing
        if random.random() < 0.7:  # 70% chance to simulate address bar interaction
            self.simulate_address_bar_interaction(driver)
        
        # Human-like typing of URL
        self.human_type(driver, url)
        
        # Random wait before pressing Enter
        time.sleep(random.uniform(0.5, 2.0))
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.RETURN)
        
        # Random wait after page load
        time.sleep(random.uniform(2.0, 5.0))
        
        # Random scroll
        if random.random() < 0.8:  # 80% chance to scroll initially
            self.human_scroll(driver)
    
    def human_browsing(self, driver, profile_num, max_visits):
        """Simulate human-like browsing behavior"""
        base_url = self.website_url.get()
        visited_pages = [base_url]
        visit_count = 1
        
        while visit_count < max_visits and self.running:
            # Find links on page
            try:
                links = driver.find_elements(By.TAG_NAME, 'a')
                if not links:
                    self.log_message(f"Profile {profile_num}: No links found on page")
                    break
                
                # Filter valid links
                valid_links = []
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        if href and base_url in href and href not in visited_pages:
                            valid_links.append(link)
                    except:
                        continue
                
                if not valid_links:
                    self.log_message(f"Profile {profile_num}: No new links found to visit")
                    break
                
                # Choose a random link
                link = random.choice(valid_links)
                href = link.get_attribute('href')
                
                # Human-like delay before clicking
                time.sleep(random.uniform(1.0, 3.0))
                
                # Human-like mouse movement to the link
                self.human_mouse_move_to_element(driver, link)
                
                # Random hover time
                time.sleep(random.uniform(0.5, 1.5))
                
                # Click the link
                link.click()
                visited_pages.append(href)
                visit_count += 1
                
                self.log_message(f"Profile {profile_num}: Visiting {href}")
                
                # Random wait after page load
                time.sleep(random.uniform(3.0, 8.0))
                
                # Human-like interaction with the page
                self.human_interaction(driver)
                
                # Random chance to go back
                if random.random() < 0.3 and len(visited_pages) > 1:
                    driver.back()
                    time.sleep(random.uniform(2.0, 5.0))
                    visit_count += 1
                
            except Exception as e:
                self.log_message(f"Profile {profile_num}: Error during browsing - {str(e)}")
                break
    
    def human_interaction(self, driver):
        """Simulate various human-like interactions with the page"""
        # Random scroll
        if random.random() < 0.7:  # 70% chance to scroll
            self.human_scroll(driver)
        
        # Random mouse movements
        if random.random() < 0.6:  # 60% chance for mouse movement
            self.random_mouse_movement(driver)
        
        # Random clicks on non-interactive elements
        if random.random() < 0.3:  # 30% chance for random click
            self.random_click(driver)
        
        # Random form interaction if available
        if random.random() < 0.4:  # 40% chance to interact with forms
            self.interact_with_forms(driver)
    
    def human_scroll(self, driver):
        """Simulate human-like scrolling behavior"""
        try:
            # Get page height
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            if scroll_height <= 0:
                return
                
            # Determine scroll amount and pattern
            scroll_amount = random.randint(300, 800)
            scroll_pattern = self.generate_scroll_pattern()
            
            # Execute scroll pattern
            current_pos = 0
            for segment in scroll_pattern:
                target_pos = min(current_pos + segment, scroll_height)
                if target_pos <= current_pos:
                    break
                
                # Smooth scroll to position
                driver.execute_script(f"window.scrollTo({{top: {current_pos}, behavior: 'smooth'}})")
                
                # Random wait during scroll
                time.sleep(random.uniform(0.1, 0.5))
                
                # Update current position
                current_pos = target_pos
                
                # Random chance to pause scrolling
                if random.random() < 0.2:
                    time.sleep(random.uniform(1.0, 3.0))
            
            # Random chance to scroll back up
            if random.random() < 0.4:
                time.sleep(random.uniform(1.0, 2.0))
                scroll_back = random.randint(200, 600)
                driver.execute_script(f"window.scrollBy({{top: -{scroll_back}, behavior: 'smooth'}})")
                time.sleep(random.uniform(0.5, 1.5))
        
        except Exception as e:
            pass
    
    def generate_scroll_pattern(self):
        """Generate a human-like scroll pattern"""
        pattern = []
        remaining = random.randint(500, 1500)  # Total scroll amount
        
        while remaining > 0:
            # Random segment size
            segment = random.randint(50, 200)
            if segment > remaining:
                segment = remaining
            
            pattern.append(segment)
            remaining -= segment
            
            # Random chance to add a pause (negative value)
            if random.random() < 0.3:
                pause = random.randint(-50, -20)  # Small "backscroll" to simulate hesitation
                pattern.append(pause)
                remaining += abs(pause)
        
        return pattern
    
    def human_mouse_move_to_element(self, driver, element):
        """Simulate human-like mouse movement to an element"""
        try:
            # Get element location
            location = element.location_once_scrolled_into_view
            x = location['x'] + random.randint(5, element.size['width'] - 5)
            y = location['y'] + random.randint(5, element.size['height'] - 5)
            
            # Get current mouse position
            current_x, current_y = pyautogui.position()
            
            # Generate human-like movement path
            self.smooth_mouse_move(current_x, current_y, x, y)
            
        except Exception as e:
            # Fallback to simple movement if something goes wrong
            ActionChains(driver).move_to_element(element).perform()
    
    def smooth_mouse_move(self, start_x, start_y, end_x, end_y):
        """Simulate human-like smooth mouse movement with slight randomness"""
        # Number of steps in the movement
        steps = random.randint(20, 40)
        
        # Generate a Bezier curve for natural movement
        control1_x = start_x + (end_x - start_x) * random.uniform(0.1, 0.3)
        control1_y = start_y + (end_y - start_y) * random.uniform(0.1, 0.3)
        control2_x = start_x + (end_x - start_x) * random.uniform(0.7, 0.9)
        control2_y = start_y + (end_y - start_y) * random.uniform(0.7, 0.9)
        
        for i in range(steps):
            t = i / float(steps - 1)
            # Cubic Bezier curve formula
            x = (1-t)**3 * start_x + 3*(1-t)**2*t*control1_x + 3*(1-t)*t**2*control2_x + t**3*end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2*t*control1_y + 3*(1-t)*t**2*control2_y + t**3*end_y
            
            # Add some randomness to the position
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            
            # Move the mouse
            move(int(x), int(y))
            
            # Random delay between movements
            time.sleep(random.uniform(0.01, 0.05))
    
    def random_mouse_movement(self, driver):
        """Simulate random mouse movements on the page"""
        try:
            # Get viewport size
            width = driver.execute_script("return window.innerWidth")
            height = driver.execute_script("return window.innerHeight")
            
            # Number of movements
            movements = random.randint(3, 8)
            
            # Start from current position
            current_x, current_y = pyautogui.position()
            
            for _ in range(movements):
                # Random target position within viewport
                target_x = random.randint(0, width - 1)
                target_y = random.randint(0, height - 1)
                
                # Smooth movement to target
                self.smooth_mouse_move(current_x, current_y, target_x, target_y)
                
                # Update current position
                current_x, current_y = target_x, target_y
                
                # Random pause between movements
                if random.random() < 0.5:
                    time.sleep(random.uniform(0.2, 1.5))
        
        except Exception as e:
            pass
    
    def random_click(self, driver):
        """Simulate random click on the page"""
        try:
            # Get viewport size
            width = driver.execute_script("return window.innerWidth")
            height = driver.execute_script("return window.innerHeight")
            
            # Random position within viewport
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            
            # Smooth movement to position
            current_x, current_y = pyautogui.position()
            self.smooth_mouse_move(current_x, current_y, x, y)
            
            # Random delay before click
            time.sleep(random.uniform(0.2, 1.0))
            
            # Click
            pyautogui.click()
            
            # Random delay after click
            time.sleep(random.uniform(0.5, 2.0))
        
        except Exception as e:
            pass
    
    def interact_with_forms(self, driver):
        """Simulate interaction with form elements if available"""
        try:
            # Find all input elements
            inputs = driver.find_elements(By.TAG_NAME, 'input')
            textareas = driver.find_elements(By.TAG_NAME, 'textarea')
            all_elements = inputs + textareas
            
            if not all_elements:
                return
                
            # Choose random elements to interact with
            elements_to_interact = random.sample(all_elements, min(len(all_elements), random.randint(1, 3)))
            
            for element in elements_to_interact:
                try:
                    # Skip hidden and non-interactive elements
                    if not element.is_displayed() or not element.is_enabled():
                        continue
                        
                    input_type = element.get_attribute('type')
                    
                    # Human-like mouse movement to element
                    self.human_mouse_move_to_element(driver, element)
                    
                    # Click on the element
                    element.click()
                    time.sleep(random.uniform(0.2, 0.5))
                    
                    # Generate appropriate input based on type
                    if input_type in ['text', 'email', 'search', 'textarea', None]:
                        # Text input
                        text = fake.sentence(nb_words=random.randint(2, 5))[:-1]  # Remove period
                        self.human_type(driver, text, element)
                    elif input_type == 'checkbox':
                        # Randomly check/uncheck
                        if random.random() < 0.5:
                            element.click()
                    elif input_type == 'radio':
                        # Just click, radio should stay selected
                        pass
                    elif input_type == 'number':
                        # Number input
                        number = str(random.randint(1, 100))
                        self.human_type(driver, number, element)
                    elif input_type == 'date':
                        # Date input
                        date = fake.date_between(start_date='-1y', end_date='today').strftime('%m/%d/%Y')
                        self.human_type(driver, date, element)
                    
                    # Random delay after input
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    # Random chance to clear the input
                    if random.random() < 0.3:
                        element.clear()
                        time.sleep(random.uniform(0.3, 0.8))
                
                except Exception as e:
                    continue
        
        except Exception as e:
            pass
    
    def human_type(self, driver, text, element=None):
        """Simulate human-like typing"""
        try:
            if element is None:
                # If no element provided, use the body to simulate typing in address bar
                element = driver.find_element(By.TAG_NAME, 'body')
            
            # Split text into parts for more realistic typing
            parts = []
            remaining = text
            while len(remaining) > 0:
                part_length = random.randint(1, 5)
                parts.append(remaining[:part_length])
                remaining = remaining[part_length:]
            
            # Type each part with random delays
            for part in parts:
                element.send_keys(part)
                time.sleep(random.uniform(0.05, 0.3))  # Random typing speed
            
            # Random chance to make a mistake and correct it
            if random.random() < 0.2:
                mistakes = random.randint(1, 3)
                for _ in range(mistakes):
                    element.send_keys(Keys.BACK_SPACE)
                    time.sleep(random.uniform(0.1, 0.5))
                corrections = text[-mistakes:] if mistakes <= len(text) else text
                element.send_keys(corrections)
                time.sleep(random.uniform(0.1, 0.3))
        
        except Exception as e:
            pass
    
    def simulate_address_bar_interaction(self, driver):
        """Simulate interaction with the browser address bar"""
        try:
            # Move mouse to top-left corner (where address bar would be)
            width = driver.execute_script("return window.innerWidth")
            self.smooth_mouse_move(
                pyautogui.position()[0], pyautogui.position()[1],
                random.randint(50, 200), random.randint(10, 30)
            )
            
            # Random clicks or drags
            if random.random() < 0.5:
                pyautogui.click()
                time.sleep(random.uniform(0.1, 0.5))
            else:
                pyautogui.mouseDown()
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.move(random.randint(10, 50), 0)
                pyautogui.mouseUp()
                time.sleep(random.uniform(0.2, 0.5))
        
        except Exception as e:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AntiDetectBot(root)
    root.mainloop()