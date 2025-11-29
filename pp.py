import os
import time
import uuid
import random
import re
import cloudscraper
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import threading

# Add this section at the top of your script
os.system('cls' if os.name == 'nt' else 'clear')

# New ASCII Art and Text Design
ascii_art = """
______________  ________________   ________________________
__  ____/__  / / /__    |__  __/   __  ____/__  __ \__  __/
_  /    __  /_/ /__  /| |_  /      _  / __ __  /_/ /_  /   
/ /___  _  __  / _  ___ |  /       / /_/ / _  ____/_  /    
\____/  /_/ /_/  /_/  |_/_/        \____/  /_/     /_/     
                                                           
"""

# Print the ASCII Art when the script starts
print(ascii_art)

def generate_user_agent() -> str:
    """Return a randomized desktop Chrome user-agent per account"""
    chrome_major = random.randint(110, 141)
    build = random.randint(0, 5999)
    patch = random.randint(0, 199)
    os_tokens = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 10.0; WOW64",
        "Windows NT 6.3; Win64; x64",
        "Macintosh; Intel Mac OS X 10_15_7",
        "X11; Linux x86_64",
    ]
    os_token = random.choice(os_tokens)
    return (
        f"Mozilla/5.0 ({os_token}) AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{chrome_major}.0.{build}.{patch} Safari/537.36"
    )


class ChatGPTSignupTripleMethod:
    """
    ChatGPT Auto Signup - TRIPLE METHOD VERSION
    Choose between:
    1. 🆕 Jemuje Tmail API (jemuje.com, new 3-domain pool)
    2. 🏪 Alfashop Tmail API (legacy 12-domain pool)
    3. 📮 Cekmail Tmail API (cekmail.com)
    4. 🌐 Temp-Mail.io API (13 temp-mail domains)
    5. 📧 Gmail IMAP (custom domain + Gmail)
    6. 🔮 Generator.email (Random CapCut-style domains)
    7. 🎯 Generator.email (Custom domain)
    By: @itsmeaab
    """


    # Legacy Alfashop domains (unchanged)
    ALFASHOP_DOMAINS = [
        'tokoalfaya.my.id',
        'kakalfaa.my.id',
        'alfapremium.biz.id',
        'alfaganteng.biz.id',
        'alfaapril.web.id',
        'alfasatru.web.id',
        'alfajajanpremium.biz.id',
        'alfalagikeluar.biz.id',
        'alfasukadagang.my.id',
        'alfasukangopi.biz.id',
        'premiumwithalfa.my.id',
        'alfakalcer.biz.id'
    ]

    # Jemuje custom domains (new provider, separate from Alfashop)
    JEMUJE_DOMAINS = [
        'darosah.my.id',
        'gamaliya.my.id',
        'ramsis.my.id'
    ]
    
    # Temp-mail.io domains
    TEMP_MAIL_DOMAINS = [
        'jxpomup.com', 'ibolinva.com', 'wyoxafp.com', 'jkotypc.com',
        'cmhvzylmfc.com', 'daouse.com', 'illubd.com', 'mkzaso.com',
        'mrotzis.com', 'xkxkud.com', 'wnbaldwy.com', 'bwmyga.com', 'ozsaip.com'
    ]
    
    # Cekmail enforced domain
    CEKMAIL_DEFAULT_DOMAIN = "cekmail.com"

    def __init__(self, gmail_user: str, gmail_password: str, alfashop_api_key: str = None,
                 cekmail_api_key: str = None,
                 thread_id: int = 0, method: str = 'jemuje', user_agent: Optional[str] = None):
        self.auth_url = "https://auth.openai.com"
        self.chatgpt_url = "https://chatgpt.com"
        
        # Gmail credentials
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password.replace(' ', '').strip()
        
        # Jemuje Tmail API (new provider)
        self.alfashop_api_key = alfashop_api_key or "DZVBRbQ6SdeFXv7GUirx"
        self.alfashop_base_url = "https://jemuje.com/api"

        # Separate base for the legacy Alfashop domains (kept for compatibility)
        self.alfashop_legacy_base_url = self.alfashop_base_url

        # Cekmail Tmail API (dedicated key + single-domain service)
        self.cekmail_api_key = cekmail_api_key or "HuXcwajFG9PvtZoN6Tq7"
        self.cekmail_base_url = "https://cekmail.com/api"
        
        # Thread ID
        self.thread_id = thread_id
        
        # Method selection: 'jemuje', 'alfashop', 'cekmail', 'tempmail', 'imap', or generator modes
        self.method = method
        
        # Create session
        self.session = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        
        self.session.headers.update({
            'User-Agent': user_agent or generate_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        
        self.client_id = "app_X8zY6vW2pQ9tR3dE7nK1jL5gH"
        self.device_id = str(uuid.uuid4())
        self.auth_session_logging_id = str(uuid.uuid4())
        
        self.email = None
        self.password = None
        self.temp_mail_token = None
        
        # Lock
        self.lock = threading.Lock()
    
    def log(self, message: str):
        """Thread-safe logging"""
        timestamp = time.strftime("%H:%M:%S")
        method_icons = {
            'alfashop': '🏪',
            'jemuje': '🆕',
            'cekmail': '📮',
            'tempmail': '🌐',
            'imap': '📧',
            'generator_auto': '🔮',
            'generator_custom': '🎯'
        }
        icon = method_icons.get(self.method, '❓')
        print(f"[{timestamp}] [{icon} T-{self.thread_id:03d}] {message}", flush=True)
    
    def generate_clean_username(self) -> str:
        """Generate clean username"""
        try:
            from faker import Faker
            fake = Faker()
            first_name = re.sub(r'[^a-z]', '', fake.first_name().lower())
            last_name = re.sub(r'[^a-z]', '', fake.last_name().lower())
        except ImportError:
            first_names = ['james', 'mary', 'john', 'patricia', 'robert', 'jennifer']
            last_names = ['smith', 'johnson', 'williams', 'brown', 'jones']
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
        
        formats = [
            f"{first_name}{last_name}",
            f"{first_name}.{last_name}",
            f"{first_name}_{last_name}",
            first_name,
        ]
        return random.choice(formats)
    
    def generate_random_name(self) -> str:
        """Generate the fixed display name for accounts"""
        return "Jellal"
    
    # ==================== METHOD 1: ALFASHOP TMAIL ====================
    
    def _generate_tmail_email(self, base_url: str, api_key: str, domains: list, label: str) -> Optional[str]:
        """Generic email generator for Tmail-like providers"""
        if not domains:
            self.log(f"❌ No {label} domains available")
            return None

        try:
            domain = random.choice(domains)

            url = f'{base_url}/email/create/{api_key}'

            response = self.session.get(
                url,
                params={'domain': domain},
                timeout=10
            )

            if response.ok:
                email_address = response.text.strip()

                if '@' in email_address and '.' in email_address:
                    self.log(f"✅ {label} Email: {email_address}")
                    return email_address
                else:
                    self.log(f"⚠️  {label} invalid: {email_address}")
                    return None
            else:
                self.log(f"❌ {label} API failed: {response.status_code}")
                return None

        except Exception as e:
            self.log(f"❌ {label} error: {e}")
            return None

    def generate_alfashop_email(self) -> Optional[str]:
        """🏪 METHOD 1B: Generate email using the legacy Alfashop domain pool"""
        return self._generate_tmail_email(
            self.alfashop_legacy_base_url,
            self.alfashop_api_key,
            self.ALFASHOP_DOMAINS,
            "Alfashop"
        )

    def generate_jemuje_email(self) -> Optional[str]:
        """🆕 METHOD 1A: Generate email using the new Jemuje domain pool"""
        return self._generate_tmail_email(
            self.alfashop_base_url,
            self.alfashop_api_key,
            self.JEMUJE_DOMAINS,
            "Jemuje"
        )

    # ==================== METHOD 1B: CEKMAIL TMAIL ====================

    def fetch_cekmail_domains(self) -> list:
        """Return the single enforced cekmail.com domain."""
        return [self.CEKMAIL_DEFAULT_DOMAIN]

    def generate_cekmail_email(self) -> Optional[str]:
        """Generate email using cekmail.com domains."""
        domains = self.fetch_cekmail_domains()
        if not domains:
            self.log("❌ No Cekmail domains available")
            return None

        try:
            domain = domains[0]
            local_part = self.generate_clean_username()

            endpoints = [
                f"{self.cekmail_base_url}/email/create/{self.cekmail_api_key}",
                f"{self.cekmail_base_url}/email/create?apikey={self.cekmail_api_key}",
                f"{self.cekmail_base_url}/email/generate/{self.cekmail_api_key}",
            ]

            for url in endpoints:
                try:
                    response = self.session.get(
                        url,
                        params={'domain': domain, 'username': local_part},
                        timeout=15
                    )

                    if not response.ok:
                        continue

                    email_address = response.text.strip()
                    if '@' not in email_address:
                        email_address = f"{local_part}@{domain}"

                    if '@' in email_address and '.' in email_address:
                        self.log(f"✅ Email: {email_address}")
                        return email_address
                except Exception:
                    continue

            self.log("❌ Cekmail email generation failed")
            return None

        except Exception as e:
            self.log(f"❌ Cekmail error: {e}")
            return None
    
    def extract_otp_from_html(self, html_content: str) -> Optional[str]:
        """Extract OTP from HTML email"""
        if not html_content:
            return None
        
        # Method 1: Large font paragraph
        match = re.search(r'<p[^>]*font-size:\s*24px[^>]*>[\s\n]*(\d{6})[\s\n]*</p>', html_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Method 2: "Your ChatGPT code is XXXXXX"
        match = re.search(r'Your ChatGPT code is (\d{6})', html_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Method 3: Title tag
        match = re.search(r'<title>.*?(\d{6}).*?</title>', html_content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Method 4: Generic patterns
        text = re.sub(r'<[^>]+>', ' ', html_content)
        patterns = [
            r'verification code[:\s]*(\d{6})',
            r'code[:\s]*(\d{6})',
            r'\b(\d{6})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _get_otp_from_tmail(self, email_address: str, base_url: str, api_key: str, label: str,
                            max_wait: int = 120) -> Optional[str]:
        """Generic OTP poller for Tmail-like providers"""
        self.log(f"⏳ Checking {label} (max {max_wait}s)...")
        start_time = time.time()
        check_count = 0

        endpoint_patterns = [
            f'email/{email_address}/messages/{api_key}',
            f'messages/{email_address}/{api_key}',
            f'inbox/{email_address}/{api_key}',
            f'mail/{email_address}/{api_key}',
        ]

        while (time.time() - start_time) < max_wait:
            try:
                check_count += 1

                for endpoint in endpoint_patterns:
                    try:
                        url = f'{base_url}/{endpoint}'
                        response = self.session.get(url, timeout=10)

                        if response.ok:
                            content = response.text.strip()

                            if not content or len(content) < 20:
                                continue

                            try:
                                import json
                                data = json.loads(content)

                                messages = None
                                if isinstance(data, list) and len(data) > 0:
                                    messages = data
                                elif isinstance(data, dict):
                                    messages = data.get('messages') or data.get('data') or data.get('emails')

                                if messages:
                                    message = messages[0] if isinstance(messages, list) else messages

                                    html_body = ''
                                    if isinstance(message, dict):
                                        html_body = (
                                            message.get('html') or
                                            message.get('body_html') or
                                            message.get('html_body') or
                                            message.get('content') or
                                            message.get('body') or
                                            str(message)
                                        )
                                    else:
                                        html_body = str(message)

                                    otp = self.extract_otp_from_html(html_body)
                                    if otp:
                                        elapsed = time.time() - start_time
                                        self.log(f"🔑 {label} OTP: {otp} ({elapsed:.1f}s)")
                                        return otp

                            except json.JSONDecodeError:
                                otp = self.extract_otp_from_html(content)
                                if otp:
                                    elapsed = time.time() - start_time
                                    self.log(f"🔑 {label} OTP: {otp} ({elapsed:.1f}s)")
                                    return otp

                    except:
                        continue

                if check_count % 10 == 0:
                    elapsed = time.time() - start_time
                    self.log(f"⏳ Waiting... ({elapsed:.0f}s)")

            except:
                pass

            time.sleep(3)

        self.log(f"❌ Timeout ({max_wait}s)")
        return None

    def get_otp_from_alfashop(self, email_address: str, max_wait: int = 120) -> Optional[str]:
        """🏪 METHOD 1B: Get OTP from the legacy Alfashop domain pool"""
        return self._get_otp_from_tmail(
            email_address,
            self.alfashop_legacy_base_url,
            self.alfashop_api_key,
            "Alfashop",
            max_wait,
        )

    def get_otp_from_jemuje(self, email_address: str, max_wait: int = 120) -> Optional[str]:
        """🆕 METHOD 1A: Get OTP from the new Jemuje domain pool"""
        return self._get_otp_from_tmail(
            email_address,
            self.alfashop_base_url,
            self.alfashop_api_key,
            "Jemuje",
            max_wait,
        )

    def get_otp_from_cekmail(self, email_address: str, max_wait: int = 120) -> Optional[str]:
        """📮 METHOD 1B: Get OTP from Cekmail Tmail API"""
        self.log(f"⏳ Checking Cekmail (max {max_wait}s)...")
        start_time = time.time()
        check_count = 0

        endpoint_patterns = [
            f"messages/{email_address}/{self.cekmail_api_key}",
            f"email/{email_address}/messages/{self.cekmail_api_key}",
            f"inbox/{email_address}/{self.cekmail_api_key}",
            f"mail/{email_address}/{self.cekmail_api_key}",
        ]

        while (time.time() - start_time) < max_wait:
            try:
                check_count += 1

                for endpoint in endpoint_patterns:
                    try:
                        url = f"{self.cekmail_base_url}/{endpoint}"
                        response = self.session.get(url, timeout=10)

                        if response.ok:
                            content = response.text.strip()
                            if not content or len(content) < 20:
                                continue

                            try:
                                import json
                                data = json.loads(content)

                                messages = None
                                if isinstance(data, list) and len(data) > 0:
                                    messages = data
                                elif isinstance(data, dict):
                                    messages = data.get('messages') or data.get('data') or data.get('emails')

                                if messages:
                                    message = messages[0] if isinstance(messages, list) else messages
                                    html_body = ''
                                    if isinstance(message, dict):
                                        html_body = (
                                            message.get('html') or
                                            message.get('body_html') or
                                            message.get('html_body') or
                                            message.get('content') or
                                            message.get('body') or
                                            str(message)
                                        )
                                    else:
                                        html_body = str(message)

                                    otp = self.extract_otp_from_html(html_body)
                                    if otp:
                                        elapsed = time.time() - start_time
                                        self.log(f"🔑 OTP: {otp} ({elapsed:.1f}s)")
                                        return otp

                            except json.JSONDecodeError:
                                otp = self.extract_otp_from_html(content)
                                if otp:
                                    elapsed = time.time() - start_time
                                    self.log(f"🔑 OTP: {otp} ({elapsed:.1f}s)")
                                    return otp

                    except:
                        continue

                if check_count % 10 == 0:
                    elapsed = time.time() - start_time
                    self.log(f"⏳ Waiting... ({elapsed:.0f}s)")

            except:
                pass

            time.sleep(3)

        self.log(f"❌ Timeout ({max_wait}s)")
        return None
    
    # ==================== METHOD 2: TEMP-MAIL.IO ====================
    
    def generate_tempmail_email(self) -> Tuple[str, Optional[str]]:
        """🌐 METHOD 2: Generate email using Temp-Mail.io API"""
        try:
            domain = random.choice(self.TEMP_MAIL_DOMAINS)
            username = self.generate_clean_username()
            
            response = self.session.post(
                'https://api.internal.temp-mail.io/api/v3/email/new',
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                json={'name': username, 'domain': domain},
                timeout=10
            )
            
            if response.ok:
                data = response.json()
                if data.get('email') and data.get('token'):
                    self.log(f"✅ Temp-Mail: {data['email']}")
                    return data['email'], data['token']
            
            email_address = f"{username}{random.randint(100,999)}@{domain}"
            self.log(f"⚠️  Temp-Mail (no token): {email_address}")
            return email_address, None
            
        except Exception as e:
            domain = random.choice(self.TEMP_MAIL_DOMAINS)
            username = self.generate_clean_username()
            email_address = f"{username}{random.randint(100,999)}@{domain}"
            self.log(f"⚠️  Error: {email_address}")
            return email_address, None
    
    def get_otp_from_tempmail(self, email_address: str, token: Optional[str], max_wait: int = 120) -> Optional[str]:
        """🌐 METHOD 2: Get OTP from Temp-Mail.io API"""
        if not token:
            self.log("❌ No token")
            return None
        
        self.log(f"⏳ Checking Temp-Mail (max {max_wait}s)...")
        start_time = time.time()
        check_count = 0
        
        while (time.time() - start_time) < max_wait:
            try:
                check_count += 1
                
                response = self.session.get(
                    f'https://api.internal.temp-mail.io/api/v3/email/{email_address}/messages',
                    headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    messages = response.json()
                    
                    if messages and len(messages) > 0:
                        message = messages[0]
                        message_body = message.get('body_text', '') + message.get('body_html', '')
                        
                        patterns = [
                            r'verification code[:\s]*(\d{4,8})',
                            r'code[:\s]*(\d{4,8})',
                            r'(\d{6})',
                            r'(\d{4,8})'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, message_body, re.IGNORECASE)
                            if match:
                                otp = match.group(1)
                                elapsed = time.time() - start_time
                                self.log(f"🔑 OTP: {otp} ({elapsed:.1f}s)")
                                return otp
                
            except:
                pass
            
            time.sleep(3)
        
        self.log(f"❌ Timeout ({max_wait}s)")
        return None
    
    # ==================== METHOD 3: GMAIL IMAP ====================
    
    def generate_imap_email(self, domain: str) -> str:
        """📧 METHOD 3: Generate email with custom domain"""
        try:
            from faker import Faker
            fake = Faker()
            name = fake.first_name()
        except:
            names = ['james', 'mary', 'john', 'patricia', 'robert']
            name = random.choice(names)
        
        suffix = random.randint(1000, 9999)
        email_address = f"{name}{suffix}@{domain}"
        self.log(f"✅ Gmail: {email_address}")
        return email_address.lower()
    
    def get_otp_from_imap(self, target_email: str, max_wait: int = 120) -> Optional[str]:
        """📧 METHOD 3: Get OTP from Gmail IMAP"""
        self.log(f"⏳ Checking IMAP (max {max_wait}s)...")
        start_time = time.time()
        check_count = 0
        
        while (time.time() - start_time) < max_wait:
            try:
                if check_count > 0:
                    time.sleep(3)
                
                check_count += 1
                
                mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
                mail.login(self.gmail_user, self.gmail_password)
                
                folders = ['INBOX', '[Gmail]/Spam', '[Gmail]/All Mail']
                
                for folder in folders:
                    try:
                        mail.select(f'"{folder}"', readonly=True)
                        _, message_numbers = mail.search(None, '(FROM "noreply@tm.openai.com")')
                        
                        if message_numbers[0]:
                            email_ids = message_numbers[0].split()
                            
                            for email_id in reversed(email_ids[-15:]):
                                try:
                                    _, msg_data = mail.fetch(email_id, "(RFC822)")
                                    email_body = msg_data[0][1]
                                    email_message = email.message_from_bytes(email_body)
                                    
                                    to_address = email_message.get('To', '').lower()
                                    
                                    if target_email.lower() in to_address:
                                        body = ""
                                        if email_message.is_multipart():
                                            for part in email_message.walk():
                                                if part.get_content_type() in ["text/plain", "text/html"]:
                                                    try:
                                                        body += part.get_payload(decode=True).decode(errors='ignore')
                                                    except:
                                                        pass
                                        else:
                                            try:
                                                body = email_message.get_payload(decode=True).decode(errors='ignore')
                                            except:
                                                pass
                                        
                                        match = re.search(r'\b(\d{6})\b', body)
                                        if match:
                                            otp = match.group(1)
                                            elapsed = time.time() - start_time
                                            self.log(f"🔑 OTP: {otp} ({elapsed:.1f}s)")
                                            mail.logout()
                                            return otp
                                
                                except:
                                    continue
                    except:
                        continue
                
                mail.logout()
                
            except:
                pass
        
        self.log(f"❌ Timeout ({max_wait}s)")
        return None
    # ==================== METHOD 4 & 5: GENERATOR.EMAIL ====================

    def fetch_capcut_domains(self) -> list:
        """Scrape CapCut-style domain list from generator.email"""
        try:
            r = self.session.get("https://generator.email/", timeout=10)
            html = r.text
            block = re.search(r'class="e7m tt-suggestions".*?</div>', html, re.DOTALL)
            if not block:
                return []
            doms = re.findall(r"<p[^>]*>([^<]+)</p>", block.group(0))
            return list(set([d.strip() for d in doms if "." in d]))
        except:
            return []

    def generate_generator_auto_email(self) -> str:
        """Random username + random generator.email domain"""
        domains = self.fetch_capcut_domains()
        if not domains:
            raise Exception("No generator.email domains")
        user = self.generate_clean_username()
        domain = random.choice(domains)
        email_addr = f"{user}@{domain}"
        self.log(f"🔮 Generator Auto: {email_addr}")
        return email_addr

    def generate_generator_custom_email(self, custom_domain: str) -> str:
        user = self.generate_clean_username()
        email_addr = f"{user}@{custom_domain}"
        self.log(f"🎯 Generator Custom: {email_addr}")
        return email_addr

    def get_otp_from_generator(self, email_address: str, max_wait:int=120):
        """Fetch OTP from generator.email inbox"""
        local, domain = email_address.split("@")
        inbox = f"https://generator.email/{domain}/{local}/"
        self.log(f"⏳ Checking generator.email inbox…")

        start = time.time()
        while time.time()-start < max_wait:
            try:
                r = self.session.get(inbox, timeout=10)
                otp = self.extract_otp_from_html(r.text)
                if otp:
                    self.log(f"🔑 OTP: {otp}")
                    return otp
            except:
                pass
            time.sleep(3)
        self.log("❌ Timeout generator.email")
        return None

    # ==================== COMMON CHATGPT METHODS ====================
    
    def start_oauth_flow(self, email: str) -> bool:
        """Start OAuth flow"""
        try:
            self.session.get(self.chatgpt_url, timeout=30)
            time.sleep(0.5)
            
            state = str(uuid.uuid4())
            
            params = {
                'client_id': self.client_id,
                'scope': 'openid email profile offline_access model.request model.read organization.read organization.write',
                'response_type': 'code',
                'redirect_uri': f'{self.chatgpt_url}/api/auth/callback/openai',
                'audience': 'https://api.openai.com/v1',
                'device_id': self.device_id,
                'prompt': 'login',
                'ext-oai-did': self.device_id,
                'auth_session_logging_id': self.auth_session_logging_id,
                'screen_hint': 'login_or_signup',
                'login_hint': email,
                'state': state
            }
            
            url = f"{self.auth_url}/api/accounts/authorize"
            
            headers = self.session.headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://chatgpt.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
            })
            
            response = self.session.get(url, params=params, headers=headers, allow_redirects=True, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ OAuth started")
                return True
            
            self.log(f"❌ OAuth failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ OAuth error: {e}")
            return False
    
    def register_user(self, email: str, password: str) -> bool:
        """Register user"""
        url = f"{self.auth_url}/api/accounts/user/register"
        
        headers = self.session.headers.copy()
        headers.update({
            'accept': 'application/json',
            'content-type': 'application/json',
            'Origin': 'https://auth.openai.com',
            'Referer': 'https://auth.openai.com/create-account/password',
            'openai-sentinel-token': '{}',
        })
        
        payload = {"username": email, "password": password}
        
        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ Registered")
                return True
            
            self.log(f"❌ Registration failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ Register error: {e}")
            return False
    
    def send_otp(self) -> bool:
        """Send OTP"""
        url = f"{self.auth_url}/api/accounts/email-otp/send"
        
        headers = self.session.headers.copy()
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://auth.openai.com/create-account/password',
        })
        
        try:
            response = self.session.get(url, headers=headers, allow_redirects=True, timeout=30)
            
            if response.status_code in [200, 302]:
                self.log("✅ OTP sent")
                return True
            
            self.log(f"❌ OTP send failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ OTP error: {e}")
            return False
    
    def validate_otp(self, code: str) -> bool:
        """Validate OTP"""
        url = f"{self.auth_url}/api/accounts/email-otp/validate"
        
        headers = self.session.headers.copy()
        headers.update({
            'accept': 'application/json',
            'content-type': 'application/json',
            'Origin': 'https://auth.openai.com',
            'Referer': 'https://auth.openai.com/email-verification',
        })
        
        payload = {"code": code}
        
        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ OTP validated")
                return True
            
            self.log(f"❌ Validation failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ Validate error: {e}")
            return False
    
    def create_account(self, name: str, birthdate: str) -> bool:
        """Complete account creation"""
        url = f"{self.auth_url}/api/accounts/create_account"
        
        headers = self.session.headers.copy()
        headers.update({
            'accept': 'application/json',
            'content-type': 'application/json',
            'Origin': 'https://auth.openai.com',
            'Referer': 'https://auth.openai.com/about-you',
            'openai-sentinel-token': '{}'
        })
        
        payload = {"name": name, "birthdate": birthdate}
        
        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.log("✅ Account created!")
                return True
            
            self.log(f"❌ Creation failed: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ Create error: {e}")
            return False
    
    def save_account(self, filename='chatgpt_accounts.txt'):
        """Save account (thread-safe)"""
        with self.lock:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"{self.email}:{self.password}\n")
        self.log(f"💾 Saved")
    
    def create_account_auto(self, email: str, password: str, name: str, birthdate: str = "2002-05-30") -> bool:
        """Automated account creation"""
        self.email = email
        self.password = password
        
        try:
            # OAuth
            self.log(f"🚀 {name} | {email}")
            if not self.start_oauth_flow(email):
                return False
            time.sleep(0.5)
            
            # Register
            if not self.register_user(email, password):
                return False
            time.sleep(0.5)
            
            # Send OTP
            if not self.send_otp():
                return False
            
            if self.method == 'jemuje':
                code = self.get_otp_from_jemuje(email, max_wait=120)

            elif self.method == 'alfashop':
                code = self.get_otp_from_alfashop(email, max_wait=120)

            elif self.method == 'cekmail':
                code = self.get_otp_from_cekmail(email, max_wait=120)

            elif self.method == 'tempmail':
                code = self.get_otp_from_tempmail(email, self.temp_mail_token, max_wait=120)

            elif self.method == 'imap':
                code = self.get_otp_from_imap(email, max_wait=120)

            elif self.method in ['generator_auto', 'generator_custom']:
                code = self.get_otp_from_generator(email, max_wait=120)

            else:
                self.log("❌ Unknown email method")
                return False

            
            # Validate OTP
            if not self.validate_otp(code):
                return False
            time.sleep(0.5)
            
            # Complete
            if not self.create_account(name, birthdate):
                return False
            
            self.log(f"🎉 SUCCESS: {name} | {email}:{password}")
            self.save_account()
            
            return True
            
        except Exception as e:
            self.log(f"❌ Exception: {e}")
            return False


def create_single_account(args):
    """Worker function"""
    thread_id, gmail_user, gmail_password, alfashop_api_key, cekmail_api_key, method, domain, password = args
    
    try:
        bot = ChatGPTSignupTripleMethod(
            gmail_user=gmail_user,
            gmail_password=gmail_password,
            alfashop_api_key=alfashop_api_key,
            cekmail_api_key=cekmail_api_key,
            thread_id=thread_id,
            method=method,
            user_agent=generate_user_agent()
        )
        
        # Generate unique name for each account
        name = bot.generate_random_name()
        
        if method == 'jemuje':
            email_address = bot.generate_jemuje_email()

        elif method == 'alfashop':
            email_address = bot.generate_alfashop_email()

        elif method == 'cekmail':
            email_address = bot.generate_cekmail_email()

        elif method == 'tempmail':
            email_address, token = bot.generate_tempmail_email()
            bot.temp_mail_token = token

        elif method == 'imap':
            email_address = bot.generate_imap_email(domain)

        elif method == 'generator_auto':
            email_address = bot.generate_generator_auto_email()

        elif method == 'generator_custom':
            email_address = bot.generate_generator_custom_email(domain)

        
        # Create account
        success = bot.create_account_auto(
            email=email_address,
            password=password,
            name=name,
            birthdate="2002-05-30"
        )
        
        return {
            'success': success,
            'email': email_address,
            'password': password,
            'method': method,
            'name': name
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_user_input():
    """Get configuration"""
    print("="*80)
    print("🚀 ChatGPT Auto Signup - TRIPLE METHOD VERSION")
    print("   1. 🆕 Jemuje Tmail (jemuje.com, new domains, default: freepalestine)")
    print("   2. 🏪 Alfashop Tmail (legacy domains, default: freepalestine)")
    print("   3. 📮 Cekmail Tmail (cekmail.com, default key provided, pass Premium12121)")
    print("   4. 🌐 Temp-Mail.io (13 domains, default: Meow@1234567)")
    print("   5. 📧 Gmail IMAP (needs setup, default: Meow@1234567)")
    print("   6. 🔮 Generator.email (Random CapCut domains)")
    print("   7. 🎯 Generator.email (Custom domain)")
    print("   By: @itsmeaab")
    print("="*80)
    
    # Method selection
    print("\n📊 SELECT METHOD:")
    method_choice = input("Enter method [1=Jemuje, 2=Alfashop, 3=Cekmail, 4=Temp-Mail, 5=IMAP, 6=GenAuto, 7=GenCustom] (default 1): ").strip()

    # ---------------- METHOD 2 ----------------
    if method_choice == '2':
        method = 'alfashop'
        domain = None
        print("🏪 Selected: Alfashop Tmail (legacy pool)")

    # ---------------- METHOD 3 ----------------
    elif method_choice == '3':
        method = 'cekmail'
        domain = None
        print("✅ Selected: Cekmail Tmail")

    # ---------------- METHOD 4 ----------------
    elif method_choice == '4':
        method = 'tempmail'
        domain = None
        print("✅ Selected: Temp-Mail.io")

    # ---------------- METHOD 5 ----------------
    elif method_choice == '5':
        method = 'imap'
        print("\n🌐 Available IMAP domains:")
        domains = ['dressrosa.me', 'puella.shop', 'wemel.top']
        for i, d in enumerate(domains, 1):
            print(f"   [{i}] {d}")

        domain_choice = int(input("\nSelect domain (1–3, default 1): ").strip() or "1")
        domain = domains[domain_choice - 1]
        print(f"✅ Selected: Gmail IMAP → {domain}")

    # ---------------- METHOD 6 ----------------
    elif method_choice == '6':
        method = 'generator_auto'
        domain = None
        print("🔮 Selected: Generator.email (Random CapCut-style domain)")

    # ---------------- METHOD 7 ----------------
    elif method_choice == '7':
        method = 'generator_custom'
        domain = input("🌐 Enter custom domain (example: mailpro.org): ").strip()
        print(f"🎯 Selected: Generator.email Custom → {domain}")

    # ---------------- METHOD 1 (Default) ----------------
    else:
        method = 'jemuje'
        domain = None
        print("🆕 Selected: Jemuje Tmail (new pool)")

    # ---------------- Number of accounts ----------------
    while True:
        try:
            num_accounts = int(input("\n📊 How many accounts (default 10): ").strip() or "10")
            if num_accounts > 0:
                break
            print("❌ Enter positive number")
        except ValueError:
            print("❌ Enter valid number")

    # ---------------- Threads ----------------
    while True:
        try:
            default_threads = num_accounts
            max_threads_allowed = max(1, num_accounts)
            prompt = f"How many to run in parallel at once [1-{max_threads_allowed}] (default {default_threads}): "
            user_threads = input(f"\n⚡ {prompt}").strip()
            max_workers = default_threads if user_threads == "" else int(user_threads)

            if 1 <= max_workers <= max_threads_allowed:
                break
            print(f"❌ Enter number between 1 and {max_threads_allowed}")
        except ValueError:
            print("❌ Enter valid number")

    # ---------------- Default password logic ----------------
    if method == 'cekmail':
        default_pass = "Premium12121"
    elif method in ['jemuje', 'alfashop']:
        default_pass = "freepalestine"
    else:
        default_pass = "Meow@1234567"

    password = input(f"\n🔒 Password (default '{default_pass}'): ").strip()
    if not password:
        password = default_pass

    return num_accounts, max_workers, method, domain, password


def main():
    """Main function"""
    # Credentials
    GMAIL_USER = 'aabkhan402@gmail.com'
    GMAIL_APP_PASSWORD = 'ftljxjidduzsqxob'
    ALFASHOP_API_KEY = 'DZVBRbQ6SdeFXv7GUirx'
    CEKMAIL_API_KEY = 'HuXcwajFG9PvtZoN6Tq7'
    
    # Get config
    num_accounts, max_workers, method, domain, password = get_user_input()
    
    print(f"\n🎯 Configuration:")
    print(f"   Method: {method.upper()}")
    print(f"   Accounts: {num_accounts}")
    print(f"   Threads: {max_workers}")
    if method == 'imap':
        print(f"   Domain: {domain}")
    elif method == 'jemuje':
        print(f"   Domains: {len(ChatGPTSignupTripleMethod.JEMUJE_DOMAINS)} Jemuje domains")
    elif method == 'alfashop':
        print(f"   Domains: {len(ChatGPTSignupTripleMethod.ALFASHOP_DOMAINS)} Alfashop domains")
    elif method == 'cekmail':
        print(f"   Domain: {ChatGPTSignupTripleMethod.CEKMAIL_DEFAULT_DOMAIN} (Cekmail)")
    else:
        print(f"   Domains: {len(ChatGPTSignupTripleMethod.TEMP_MAIL_DOMAINS)} Temp-mail domains")
    print(f"   Password: {password}")
    print(f"   Names: Auto-generated (different for each)")
    print("="*80)
    
    input("\nPress Enter to start...")
    
    # Start processing
    print(f"\n🚀 Starting creation...")
    print(f"⏰ Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    start_time = time.time()
    successful = 0
    failed = 0
    results = []
    
    attempt_counter = 0
    active_futures = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while successful < num_accounts:
            while len(active_futures) < max_workers and successful < num_accounts:
                attempt_counter += 1
                task = (
                    attempt_counter,
                    GMAIL_USER,
                    GMAIL_APP_PASSWORD,
                    ALFASHOP_API_KEY,
                    CEKMAIL_API_KEY,
                    method,
                    domain,
                    password
                )
                future = executor.submit(create_single_account, task)
                active_futures[future] = task

            if not active_futures:
                break

            done, _ = wait(active_futures.keys(), return_when=FIRST_COMPLETED)

            for future in done:
                active_futures.pop(future, None)
                try:
                    result = future.result()
                    results.append(result)

                    if result.get('success'):
                        successful += 1
                    else:
                        failed += 1

                    total_done = successful + failed
                    print(f"\n{'='*80}")
                    print(f"📊 Progress: {successful}/{num_accounts} | ✅ {successful} | ❌ {failed} | Attempts: {total_done}")
                    print(f"{'='*80}\n")

                except Exception as e:
                    failed += 1
                    print(f"\n❌ Task error: {e}\n")

            if successful >= num_accounts:
                for future in active_futures:
                    future.cancel()
                break
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*80)
    print("🎉 FINAL SUMMARY")
    print("="*80)
    print(f"✅ Successful: {successful}/{num_accounts} ({successful/num_accounts*100:.1f}%)")
    print(f"❌ Failed: {failed}/{num_accounts}")
    print(f"⏱️  Total Time: {elapsed:.1f}s ({elapsed/60:.1f}min)")
    print(f"⚡ Avg: {elapsed/num_accounts:.1f}s per account")
    print(f"📁 Saved to: chatgpt_accounts_triple.txt")
    print("="*80)
    
    # Show accounts
    if successful > 0:
        print("\n✅ Successfully Created:")
        print("-" * 80)
        for result in results:
            if result['success']:
                method_icons = {
                    'alfashop': '🏪',
                    'cekmail': '📮',
                    'tempmail': '🌐',
                    'imap': '📧',
                    'generator_auto': '🔮',
                    'generator_custom': '🎯'
                }
                icon = method_icons.get(result['method'], '❓')
                name = result.get('name', 'User')
                print(f"   {icon} {name:12} | {result['email']}:{result['password']}")
        print("-" * 80)
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
