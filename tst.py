#!/usr/bin/env python3
"""
PROFESSIONAL TUITION RECEIPT GENERATOR WITH INSTANT APPROVAL - PERFECT FOR SHEERID
✅ TUITION RECEIPT: Professional receipt with all required fields
✅ CLASS SCHEDULE: Complete schedule with enrollment proof
✅ INSTANT APPROVAL: Super-fast verification system
✅ INSTITUTION NAME: Full school name from JSON only  
✅ STUDENT INFO: Name, ID, Program, Semester, Payment Proof
✅ HARDCODED DATES: Current/upcoming term dates
✅ PDF OUTPUT: Professional formatting
✅ ALL 24 COUNTRIES: Complete global support
✅ VERIFICATION READY: Perfect for SheerID verification
"""

import sys
import os
import re
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
from faker import Faker
import qrcode
import random
import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
import time
import concurrent.futures
import threading
from functools import lru_cache
import gc
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- Logging & Helpers ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def clean_name(name: str) -> str:
    """Cleans up names from titles and unwanted characters."""
    name = re.sub(r"[.,]", "", name)
    name = re.sub(r"\b(Drs?|Ir|H|Prof|S|M|Bapak|Ibu)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+", " ", name).strip()
    return name

# ==================== COMPLETE 24 COUNTRY CONFIGURATION ====================
COUNTRY_CONFIG = {
    'US': {
        'name': 'United States',
        'code': 'us',
        'locale': 'en_US',
        'collegeFile': 'sheerid_us.json',
        'currency': 'USD',
        'currency_symbol': '$',
        'academic_terms': ['Fall 2024', 'Spring 2025', 'Summer 2024'],
        'flag': '🇺🇸',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'tuition_range': (1500, 5000),
        'fees_range': (200, 800)
    },
    'CA': {
        'name': 'Canada',
        'code': 'ca',
        'locale': 'en_CA',
        'collegeFile': 'sheerid_ca.json',
        'currency': 'CAD',
        'currency_symbol': '$',
        'academic_terms': ['Fall 2024', 'Winter 2025', 'Summer 2024'],
        'flag': '🇨🇦',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'tuition_range': (2000, 6000),
        'fees_range': (250, 900)
    },
    'GB': {
        'name': 'United Kingdom',
        'code': 'gb',
        'locale': 'en_GB',
        'collegeFile': 'sheerid_gb.json',
        'currency': 'GBP',
        'currency_symbol': '£',
        'academic_terms': ['Autumn 2024', 'Spring 2025', 'Summer 2024'],
        'flag': '🇬🇧',
        'time_format': '24-hour',
        'date_format': '%d %B %Y',
        'tuition_range': (3000, 8000),
        'fees_range': (300, 1000)
    },
    'IN': {
        'name': 'India',
        'code': 'in',
        'locale': 'en_IN',
        'collegeFile': 'sheerid_in.json',
        'currency': 'INR',
        'currency_symbol': '₹',
        'academic_terms': ['Monsoon 2024', 'Winter 2025', 'Summer 2024'],
        'flag': '🇮🇳',
        'time_format': 'AM/PM',
        'date_format': '%d %B %Y',
        'tuition_range': (50000, 200000),
        'fees_range': (5000, 20000)
    },
    'ID': {
        'name': 'Indonesia',
        'code': 'id',
        'locale': 'id_ID',
        'collegeFile': 'sheerid_id.json',
        'currency': 'IDR',
        'currency_symbol': 'Rp',
        'academic_terms': ['First Semester 2024', 'Second Semester 2025', 'Summer 2024'],
        'flag': '🇮🇩',
        'time_format': '24-hour',
        'date_format': '%d %B %Y',
        'tuition_range': (10000000, 30000000),
        'fees_range': (500000, 2000000)
    },
    'AU': {
        'name': 'Australia',
        'code': 'au',
        'locale': 'en_AU',
        'collegeFile': 'sheerid_au.json',
        'currency': 'AUD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025', 'Summer 2024'],
        'flag': '🇦🇺',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'tuition_range': (4000, 10000),
        'fees_range': (400, 1200)
    },
    'DE': {
        'name': 'Germany',
        'code': 'de',
        'locale': 'de_DE',
        'collegeFile': 'sheerid_de.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Wintersemester 2024', 'Sommersemester 2025'],
        'flag': '🇩🇪',
        'time_format': '24-hour',
        'date_format': '%d.%m.%Y',
        'tuition_range': (1000, 3000),
        'fees_range': (200, 600)
    },
    'FR': {
        'name': 'France',
        'code': 'fr',
        'locale': 'fr_FR',
        'collegeFile': 'sheerid_fr.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇫🇷',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'tuition_range': (1000, 4000),
        'fees_range': (200, 700)
    },
    'ES': {
        'name': 'Spain',
        'code': 'es',
        'locale': 'es_ES',
        'collegeFile': 'sheerid_es.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Primer Semestre 2024', 'Segundo Semestre 2025'],
        'flag': '🇪🇸',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'tuition_range': (1500, 4500),
        'fees_range': (250, 800)
    },
    'IT': {
        'name': 'Italy',
        'code': 'it',
        'locale': 'it_IT',
        'collegeFile': 'sheerid_it.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Primo Semestre 2024', 'Secondo Semestre 2025'],
        'flag': '🇮🇹',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'tuition_range': (1200, 4000),
        'fees_range': (200, 700)
    },
    'BR': {
        'name': 'Brazil',
        'code': 'br',
        'locale': 'pt_BR',
        'collegeFile': 'sheerid_br.json',
        'currency': 'BRL',
        'currency_symbol': 'R$',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇧🇷',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'tuition_range': (3000, 8000),
        'fees_range': (400, 1200)
    },
    'MX': {
        'name': 'Mexico',
        'code': 'mx',
        'locale': 'es_MX',
        'collegeFile': 'sheerid_mx.json',
        'currency': 'MXN',
        'currency_symbol': '$',
        'academic_terms': ['Semestre 1 2024', 'Semestre 2 2025'],
        'flag': '🇲🇽',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'tuition_range': (20000, 60000),
        'fees_range': (2000, 8000)
    },
    'NL': {
        'name': 'Netherlands',
        'code': 'nl',
        'locale': 'nl_NL',
        'collegeFile': 'sheerid_nl.json',
        'currency': 'EUR',
        'currency_symbol': '€',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇳🇱',
        'time_format': '24-hour',
        'date_format': '%d-%m-%Y',
        'tuition_range': (2000, 6000),
        'fees_range': (300, 900)
    },
    'SE': {
        'name': 'Sweden',
        'code': 'se',
        'locale': 'sv_SE',
        'collegeFile': 'sheerid_se.json',
        'currency': 'SEK',
        'currency_symbol': 'kr',
        'academic_terms': ['Hösttermin 2024', 'Vårtermin 2025'],
        'flag': '🇸🇪',
        'time_format': '24-hour',
        'date_format': '%Y-%m-%d',
        'tuition_range': (25000, 70000),
        'fees_range': (2000, 6000)
    },
    'NO': {
        'name': 'Norway',
        'code': 'no',
        'locale': 'no_NO',
        'collegeFile': 'sheerid_no.json',
        'currency': 'NOK',
        'currency_symbol': 'kr',
        'academic_terms': ['Høstsemester 2024', 'Vårsemester 2025'],
        'flag': '🇳🇴',
        'time_format': '24-hour',
        'date_format': '%d.%m.%Y',
        'tuition_range': (30000, 80000),
        'fees_range': (2500, 7000)
    },
    'DK': {
        'name': 'Denmark',
        'code': 'dk',
        'locale': 'da_DK',
        'collegeFile': 'sheerid_dk.json',
        'currency': 'DKK',
        'currency_symbol': 'kr',
        'academic_terms': ['Efterårssemester 2024', 'Forårssemester 2025'],
        'flag': '🇩🇰',
        'time_format': '24-hour',
        'date_format': '%d/%m/%Y',
        'tuition_range': (28000, 75000),
        'fees_range': (2200, 6500)
    },
    'JP': {
        'name': 'Japan',
        'code': 'jp',
        'locale': 'ja_JP',
        'collegeFile': 'sheerid_jp.json',
        'currency': 'JPY',
        'currency_symbol': '¥',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇯🇵',
        'time_format': '24-hour',
        'date_format': '%Y年%m月%d日',
        'tuition_range': (300000, 800000),
        'fees_range': (30000, 80000)
    },
    'KR': {
        'name': 'South Korea',
        'code': 'kr',
        'locale': 'ko_KR',
        'collegeFile': 'sheerid_kr.json',
        'currency': 'KRW',
        'currency_symbol': '₩',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇰🇷',
        'time_format': '24-hour',
        'date_format': '%Y년 %m월 %d일',
        'tuition_range': (3000000, 7000000),
        'fees_range': (300000, 700000)
    },
    'SG': {
        'name': 'Singapore',
        'code': 'sg',
        'locale': 'en_SG',
        'collegeFile': 'sheerid_sg.json',
        'currency': 'SGD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇸🇬',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'tuition_range': (5000, 12000),
        'fees_range': (500, 1500)
    },
    'NZ': {
        'name': 'New Zealand',
        'code': 'nz',
        'locale': 'en_NZ',
        'collegeFile': 'sheerid_nz.json',
        'currency': 'NZD',
        'currency_symbol': '$',
        'academic_terms': ['Semester 1 2024', 'Semester 2 2025'],
        'flag': '🇳🇿',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'tuition_range': (4000, 10000),
        'fees_range': (400, 1200)
    },
    'ZA': {
        'name': 'South Africa',
        'code': 'za',
        'locale': 'en_ZA',
        'collegeFile': 'sheerid_za.json',
        'currency': 'ZAR',
        'currency_symbol': 'R',
        'academic_terms': ['First Semester 2024', 'Second Semester 2025'],
        'flag': '🇿🇦',
        'time_format': 'AM/PM',
        'date_format': '%Y/%m/%d',
        'tuition_range': (25000, 60000),
        'fees_range': (2500, 6000)
    },
    'CN': {
        'name': 'China',
        'code': 'cn',
        'locale': 'zh_CN',
        'collegeFile': 'sheerid_cn.json',
        'currency': 'CNY',
        'currency_symbol': '¥',
        'academic_terms': ['Spring 2024', 'Fall 2024'],
        'flag': '🇨🇳',
        'time_format': '24-hour',
        'date_format': '%Y年%m月%d日',
        'tuition_range': (15000, 40000),
        'fees_range': (1500, 4000)
    },
    'AE': {
        'name': 'UAE',
        'code': 'ae',
        'locale': 'en_AE',
        'collegeFile': 'sheerid_ae.json',
        'currency': 'AED',
        'currency_symbol': 'د.إ',
        'academic_terms': ['Fall 2024', 'Spring 2025'],
        'flag': '🇦🇪',
        'time_format': 'AM/PM',
        'date_format': '%d/%m/%Y',
        'tuition_range': (10000, 30000),
        'fees_range': (1000, 3000)
    },
    'PH': {
        'name': 'Philippines',
        'code': 'ph',
        'locale': 'en_PH',
        'collegeFile': 'sheerid_ph.json',
        'currency': 'PHP',
        'currency_symbol': '₱',
        'academic_terms': ['First Semester 2025-2026', 'Second Semester 2026-2027', 'Summer 2026'],
        'flag': '🇵🇭',
        'time_format': 'AM/PM',
        'date_format': '%B %d, %Y',
        'tuition_range': (40000, 100000),
        'fees_range': (4000, 10000)
    }
}

class ProfessionalReceiptGenerator:
    def __init__(self):
        self.receipts_dir = "receipts"
        self.students_file = "students.txt"
        self.selected_country = None
        self.all_colleges = []
        
        self.faker_instances = []
        self.faker_lock = threading.Lock()
        self.faker_index = 0
        
        # Performance settings
        self.max_workers = 10
        self.memory_cleanup_interval = 100
        
        self.stats = {
            "receipts_generated": 0,
            "students_saved": 0,
            "start_time": None
        }
        
        # Professional color scheme for receipts
        self.colors = {
            "primary": colors.HexColor("#1e3a8a"),
            "secondary": colors.HexColor("#2563eb"),
            "accent": colors.HexColor("#059669"),
            "success": colors.HexColor("#10b981"),
            "warning": colors.HexColor("#f59e0b"),
            "background": colors.HexColor("#f8fafc"),
            "header_bg": colors.HexColor("#1e40af"),
            "text_dark": colors.HexColor("#1f2937"),
            "text_light": colors.HexColor("#6b7280"),
            "white": colors.white,
            "border": colors.HexColor("#d1d5db"),
            "row_even": colors.white,
            "row_odd": colors.HexColor("#f3f4f6")
        }

        self.create_directories()
        self.clear_all_data()

    def create_directories(self):
        os.makedirs(self.receipts_dir, exist_ok=True)

    def clear_all_data(self):
        try:
            if os.path.exists(self.receipts_dir):
                for f in os.listdir(self.receipts_dir):
                    if f.endswith(('.pdf', '.txt')):
                        try:
                            os.remove(os.path.join(self.receipts_dir, f))
                        except Exception:
                            pass
            if os.path.exists(self.students_file):
                try:
                    os.remove(self.students_file)
                except Exception:
                    pass
            
            print("🗑️  All previous data cleared!")
            print("✅ PERFECT FORMAT: Professional receipt layout")
            print("✅ INSTANT APPROVAL: Super-fast verification system") 
            print("✅ INSTITUTION: Full school name from JSON only")
            print("✅ STUDENT INFO: Name, ID, Program, Semester")
            print("✅ HARDCODED DATES: Current/upcoming term dates")
            print("✅ ALL 24 COUNTRIES: Complete global support")
            print("="*70)
        except Exception as e:
            print(f"⚠️  Warning: {e}")

    def load_colleges(self):
        """Load colleges ONLY from JSON file - no hardcoded data."""
        try:
            if not self.selected_country:
                return []
            
            config = COUNTRY_CONFIG[self.selected_country]
            college_file = config['collegeFile']
            
            print(f"📚 Loading {college_file}...")
            
            if not os.path.exists(college_file):
                print(f"❌ College file {college_file} not found!")
                return []
            
            with open(college_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            colleges = []
            for c in data:
                if c.get('name') and c.get('id'):
                    colleges.append({
                        'name': c['name'],
                        'id': c['id'],
                        'type': c.get('type', 'UNIVERSITY')
                    })
            
            print(f"✅ Loaded {len(colleges)} colleges from {college_file}")
            return colleges
            
        except Exception as e:
            print(f"❌ ERROR loading colleges from {college_file}: {e}")
            return []

    def get_country_colleges(self, country_code):
        """ONLY used as fallback if JSON file is completely missing."""
        print(f"⚠️  No colleges loaded from JSON, using minimal fallback")
        return [
            {'name': f'University of {COUNTRY_CONFIG[country_code]["name"]}', 'id': f'UNI001', 'type': 'UNIVERSITY'}
        ]

    def select_country_and_load(self):
        """Country selection interface with all 24 countries."""
        print("\n🌍 COUNTRY SELECTION - 24 COUNTRIES AVAILABLE")
        print("=" * 70)
        countries = list(COUNTRY_CONFIG.keys())
        
        for i in range(0, len(countries), 4):
            row = countries[i:i+4]
            line = ""
            for country in row:
                config = COUNTRY_CONFIG[country]
                idx = list(COUNTRY_CONFIG.keys()).index(country) + 1
                line += f"{idx:2d}. {config['flag']} {config['name']:18} "
            print(line)
        print("=" * 70)
        
        country_list = list(COUNTRY_CONFIG.keys())
        
        while True:
            try:
                choice = input("\nSelect country (1-24): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= 24:
                    self.selected_country = country_list[int(choice) - 1]
                    break
                else:
                    print("❌ Please enter a number between 1 and 24")
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")
        
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"\n✅ Selected: {config['flag']} {config['name']} ({self.selected_country})")
        
        self.all_colleges = self.load_colleges()
        
        if not self.all_colleges:
            print("❌ No colleges loaded from JSON! Using minimal fallback.")
            self.all_colleges = self.get_country_colleges(self.selected_country)
        
        # Initialize Faker instances with English names
        try:
            self.faker_instances = [Faker('en_US') for _ in range(20)]
        except:
            self.faker_instances = [Faker() for _ in range(20)]
            
        print("✅ Generator ready!")
        
        return True

    def get_faker(self):
        """Thread-safe Faker instance rotation."""
        with self.faker_lock:
            faker = self.faker_instances[self.faker_index]
            self.faker_index = (self.faker_index + 1) % len(self.faker_instances)
            return faker

    def select_random_college(self):
        """Select a random college from JSON data only."""
        if not self.all_colleges:
            config = COUNTRY_CONFIG.get(self.selected_country, COUNTRY_CONFIG['US'])
            return {'name': f'University of {config["name"]}', 'id': 'UNI001', 'type': 'UNIVERSITY'}
        return random.choice(self.all_colleges)

    def generate_payment_data(self, country_config):
        """Generate realistic payment data for tuition receipt."""
        tuition_min, tuition_max = country_config['tuition_range']
        fees_min, fees_max = country_config['fees_range']
        
        tuition_amount = random.randint(tuition_min, tuition_max)
        fees_amount = random.randint(fees_min, fees_max)
        total_amount = tuition_amount + fees_amount
        
        payment_methods = ["Credit Card", "Bank Transfer", "Online Payment", "Scholarship", "Financial Aid"]
        transaction_id = f"TX{random.randint(100000, 999999)}"
        
        return {
            "tuition_amount": tuition_amount,
            "fees_amount": fees_amount,
            "total_amount": total_amount,
            "payment_method": random.choice(payment_methods),
            "transaction_id": transaction_id,
            "payment_date": datetime.now() - timedelta(days=random.randint(1, 30))
        }

    def generate_student_data(self, college):
        """Generate student data with CURRENT/UPCOMING term dates."""
        fake = self.get_faker()
        config = COUNTRY_CONFIG[self.selected_country]
        
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = clean_name(f"{first_name} {last_name}")
        student_id = f"{fake.random_number(digits=8, fix_len=True)}"
        
        # CURRENT/UPCOMING TERM DATES for SheerID verification
        current_date = datetime.now()
        
        # Generate dates for current or upcoming semester
        if current_date.month in [1, 2, 3, 4, 5]:  # Spring semester
            date_issued = current_date
            first_day = datetime(current_date.year, 1, 15)
            last_day = datetime(current_date.year, 5, 15)
            exam_week = datetime(current_date.year, 5, 20)
            academic_term = "Spring 2025"
        else:  # Fall semester  
            date_issued = current_date
            first_day = datetime(current_date.year, 8, 25)
            last_day = datetime(current_date.year, 12, 15)
            exam_week = datetime(current_date.year, 12, 20)
            academic_term = "Fall 2025"
        
        # Country-specific programs
        programs_by_country = {
            'US': ["Computer Science", "Business Administration", "Engineering", "Psychology", "Biology"],
            'GB': ["Computer Science", "Business Studies", "Engineering", "Medicine", "Law"],
            'IN': ["Computer Science", "Business Administration", "Engineering", "Medicine", "Commerce"],
            'ID': ["Computer Science", "Business", "Engineering", "Medicine"],
            'AU': ["Computer Science", "Business", "Engineering", "Health Sciences"],
            'DE': ["Informatik", "BWL", "Ingenieurwesen", "Medizin"],
            'FR': ["Informatique", "Commerce", "Ingénierie", "Médecine"],
            'ES': ["Informática", "Negocios", "Ingeniería", "Medicina"],
            'IT': ["Informatica", "Economia", "Ingegneria", "Medicina"],
            'BR': ["Ciência da Computação", "Administração", "Engenharia", "Medicina"],
            'MX': ["Ciencias de la Computación", "Negocios", "Ingeniería", "Medicina"],
            'NL': ["Informatica", "Bedrijfskunde", "Techniek", "Geneeskunde"],
            'SE': ["Datateknik", "Företagsekonomi", "Teknik", "Medicin"],
            'NO': ["Informatikk", "Bedriftsøkonomi", "Ingeniørvitenskap", "Medisin"],
            'DK': ["Datalogi", "Erhvervsøkonomi", "Ingeniørvidenskab", "Medicin"],
            'JP': ["Computer Science", "Business", "Engineering", "Medicine"],
            'KR': ["Computer Science", "Business", "Engineering", "Medicine"],
            'SG': ["Computer Science", "Business", "Engineering", "Medicine"],
            'NZ': ["Computer Science", "Business", "Engineering", "Health Sciences"],
            'ZA': ["Computer Science", "Business", "Engineering", "Medicine"],
            'CN': ["Computer Science", "Business", "Engineering", "Medicine"],
            'AE': ["Computer Science", "Business", "Engineering", "Medicine"],
            'PH': ["Computer Science", "Business Administration", "Engineering", "Nursing", "Education"],
            'CA': ["Computer Science", "Business", "Engineering", "Health Sciences"]
        }
        
        programs = programs_by_country.get(self.selected_country, ["Computer Science", "Business", "Engineering"])
        
        # Generate payment data
        payment_data = self.generate_payment_data(config)
        
        return {
            "full_name": full_name,
            "student_id": student_id,
            "college": college,
            "program": random.choice(programs),
            "academic_term": academic_term,
            "date_issued": date_issued,
            "first_day": first_day,
            "last_day": last_day,
            "exam_week": exam_week,
            "country_config": config,
            "payment_data": payment_data
        }

    def format_currency(self, amount, country_config):
        """Format currency according to country preferences."""
        symbol = country_config['currency_symbol']
        if country_config['currency'] in ['USD', 'CAD', 'AUD', 'SGD', 'NZD']:
            return f"{symbol}{amount:,.2f}"
        elif country_config['currency'] in ['EUR', 'GBP']:
            return f"{symbol}{amount:,.2f}"
        elif country_config['currency'] in ['JPY', 'CNY']:
            return f"{symbol}{amount:,}"
        else:
            return f"{symbol} {amount:,.2f}"

    def create_tuition_receipt_pdf(self, student_data):
        """Create a professional tuition receipt PDF perfect for SheerID verification."""
        college = student_data['college']
        student_id = student_data['student_id']
        college_id = college['id']
        config = student_data['country_config']
        payment_data = student_data['payment_data']

        filename = f"TUITION_{student_id}_{college_id}.pdf"
        filepath = os.path.join(self.receipts_dir, filename)

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            # Container for the 'Flowable' objects
            elements = []
            styles = getSampleStyleSheet()
            
            # Header with institution name
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=10
            )
            
            header = Paragraph("OFFICIAL TUITION RECEIPT", header_style)
            elements.append(header)
            
            # Institution Name (from JSON only)
            uni_style = ParagraphStyle(
                'UniversityStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceAfter=20
            )
            
            university = Paragraph(college['name'], uni_style)
            elements.append(university)
            
            elements.append(Spacer(1, 15))
            
            # Receipt Information
            receipt_style = ParagraphStyle(
                'ReceiptStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=15
            )
            
            receipt_info = Paragraph(f"Receipt Date: {self.format_date(student_data['date_issued'], config)} | Transaction ID: {payment_data['transaction_id']}", receipt_style)
            elements.append(receipt_info)
            
            # Student Information Section
            student_info_style = ParagraphStyle(
                'StudentInfoTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['primary'],
                spaceAfter=8
            )
            
            student_info_title = Paragraph("Student Information", student_info_style)
            elements.append(student_info_title)
            
            # Student Info Table
            student_data_table = [
                ["Full Name:", student_data["full_name"]],
                ["Student ID:", student_data["student_id"]],
                ["Academic Program:", student_data["program"]],
                ["Current Semester:", student_data["academic_term"]],
                ["Enrollment Status:", "Full-Time Active"]
            ]
            
            student_table = Table(student_data_table, colWidths=[2*inch, 4*inch])
            student_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, -1), 1, self.colors['border']),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(student_table)
            elements.append(Spacer(1, 15))
            
            # Payment Details Section
            payment_title = Paragraph("Payment Details", student_info_style)
            elements.append(payment_title)
            
            payment_details = [
                ["Description", "Amount"],
                ["Tuition Fee", self.format_currency(payment_data['tuition_amount'], config)],
                ["University Fees", self.format_currency(payment_data['fees_amount'], config)],
                ["", ""],
                ["TOTAL PAID", self.format_currency(payment_data['total_amount'], config)]
            ]
            
            payment_table = Table(payment_details, colWidths=[4*inch, 2*inch])
            payment_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONT', (0, 1), (-1, -2), 'Helvetica', 11),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid and styling
                ('LINEABOVE', (0, -1), (-1, -1), 2, self.colors['accent']),
                ('BACKGROUND', (0, -1), (-1, -1), self.colors['success']),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.colors['border']),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 10),
            ]))
            
            elements.append(payment_table)
            elements.append(Spacer(1, 10))
            
            # Payment Method
            payment_method_style = ParagraphStyle(
                'PaymentMethod',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=0
            )
            
            payment_method = Paragraph(f"Payment Method: {payment_data['payment_method']} | Paid on: {self.format_date(payment_data['payment_date'], config)}", payment_method_style)
            elements.append(payment_method)
            
            elements.append(Spacer(1, 15))
            
            # Semester Dates
            dates_title = Paragraph("Semester Information", student_info_style)
            elements.append(dates_title)
            
            dates_data = [
                ["First Day of Classes:", self.format_date(student_data["first_day"], config)],
                ["Last Day of Classes:", self.format_date(student_data["last_day"], config)],
                ["Final Exams:", self.format_date(student_data["exam_week"], config)]
            ]
            
            dates_table = Table(dates_data, colWidths=[2.5*inch, 3.5*inch])
            dates_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, -1), 1, self.colors['border']),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(dates_table)
            elements.append(Spacer(1, 20))
            
            # Verification QR Code (placeholder text)
            verification_style = ParagraphStyle(
                'VerificationStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=10
            )
            
            verification = Paragraph(
                f"VERIFIED | {college['name']} | Student Status: ACTIVE | This receipt is valid for student verification purposes.",
                verification_style
            )
            elements.append(verification)
            
            # Official Stamp
            stamp_style = ParagraphStyle(
                'StampStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['accent'],
                alignment=1,
                spaceBefore=5
            )
            
            stamp = Paragraph("OFFICIAL UNIVERSITY RECEIPT • VALID FOR VERIFICATION", stamp_style)
            elements.append(stamp)
            
            # Build PDF
            doc.build(elements)
            return filename, student_data

        except Exception as e:
            logger.error(f"Failed to create PDF receipt {filename}: {e}")
            return None, student_data

    def create_class_schedule_pdf(self, student_data):
        """Create a professional class schedule PDF perfect for SheerID verification."""
        college = student_data['college']
        student_id = student_data['student_id']
        college_id = college['id']
        config = student_data['country_config']

        filename = f"SCHEDULE_{student_id}_{college_id}.pdf"
        filepath = os.path.join(self.receipts_dir, filename)

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=20
            )
            
            # Container for the 'Flowable' objects
            elements = []
            styles = getSampleStyleSheet()
            
            # Header
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=10
            )
            
            header = Paragraph("OFFICIAL CLASS SCHEDULE", header_style)
            elements.append(header)
            
            # Institution Name
            uni_style = ParagraphStyle(
                'UniversityStyle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceAfter=15
            )
            
            university = Paragraph(college['name'], uni_style)
            elements.append(university)
            
            elements.append(Spacer(1, 10))
            
            # Student Information
            student_info_style = ParagraphStyle(
                'StudentInfoTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['primary'],
                spaceAfter=8
            )
            
            # Student Info Table
            student_data_table = [
                ["Student Name:", student_data["full_name"]],
                ["Student ID:", student_data["student_id"]],
                ["Program:", student_data["program"]],
                ["Semester:", student_data["academic_term"]],
                ["Status:", "Full-Time Active"]
            ]
            
            student_table = Table(student_data_table, colWidths=[1.5*inch, 4.5*inch])
            student_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(student_table)
            elements.append(Spacer(1, 15))
            
            # Class Schedule
            schedule_title = Paragraph("Class Schedule", student_info_style)
            elements.append(schedule_title)
            
            # Generate realistic courses
            courses = self.generate_courses(student_data['program'])
            
            course_headers = ["Course Code", "Course Name", "Days", "Time", "Room", "Instructor"]
            course_data = [course_headers]
            
            for course in courses:
                course_data.append([
                    course["code"],
                    course["name"],
                    course["days"],
                    course["time"],
                    course["room"],
                    course["instructor"]
                ])
            
            course_table = Table(course_data, colWidths=[1*inch, 1.8*inch, 0.6*inch, 1.2*inch, 1*inch, 1.2*inch])
            course_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.colors['row_even'], self.colors['row_odd']]),
                ('GRID', (0, 0), (-1, -1), 0.5, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(course_table)
            elements.append(Spacer(1, 15))
            
            # Semester Dates
            dates_title = Paragraph("Important Dates", student_info_style)
            elements.append(dates_title)
            
            dates_data = [
                ["Semester Start:", self.format_date(student_data["first_day"], config)],
                ["Semester End:", self.format_date(student_data["last_day"], config)],
                ["Final Exams:", self.format_date(student_data["exam_week"], config)]
            ]
            
            dates_table = Table(dates_data, colWidths=[1.5*inch, 4.5*inch])
            dates_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
                ('BACKGROUND', (0, 0), (0, -1), self.colors['row_odd']),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text_dark']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 1, self.colors['border']),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(dates_table)
            
            # Verification Footer
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=20
            )
            
            footer = Paragraph(
                f"UNOFFICIAL STUDENT SCHEDULE • {college['name']} • Valid for verification purposes • Generated on: {self.format_date(student_data['date_issued'], config)}",
                footer_style
            )
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            return filename

        except Exception as e:
            logger.error(f"Failed to create schedule PDF {filename}: {e}")
            return None

    def generate_courses(self, program):
        """Generate realistic courses based on program."""
        base_courses = {
            "Computer Science": [
                {"code": "CS101", "name": "Introduction to Programming", "days": "MWF", "time": "09:00-09:50", "room": "CSB-201", "instructor": "Dr. Smith"},
                {"code": "CS201", "name": "Data Structures", "days": "TTH", "time": "10:30-11:45", "room": "CSB-305", "instructor": "Prof. Johnson"},
                {"code": "MATH151", "name": "Calculus I", "days": "MWF", "time": "11:00-11:50", "room": "MATH-102", "instructor": "Dr. Lee"},
                {"code": "CS301", "name": "Algorithms", "days": "TTH", "time": "13:00-14:15", "room": "CSB-410", "instructor": "Prof. Garcia"},
                {"code": "PHYS101", "name": "Physics I", "days": "MWF", "time": "14:00-14:50", "room": "SCI-205", "instructor": "Dr. Brown"}
            ],
            "Business Administration": [
                {"code": "BUS101", "name": "Introduction to Business", "days": "MWF", "time": "09:00-09:50", "room": "BUS-101", "instructor": "Prof. Wilson"},
                {"code": "ACC201", "name": "Financial Accounting", "days": "TTH", "time": "10:30-11:45", "room": "BUS-205", "instructor": "Dr. Martinez"},
                {"code": "MKT301", "name": "Marketing Principles", "days": "MWF", "time": "11:00-11:50", "room": "BUS-310", "instructor": "Prof. Davis"},
                {"code": "FIN401", "name": "Corporate Finance", "days": "TTH", "time": "13:00-14:15", "room": "BUS-415", "instructor": "Dr. Thompson"},
                {"code": "MGT351", "name": "Organizational Behavior", "days": "MWF", "time": "14:00-14:50", "room": "BUS-320", "instructor": "Prof. Anderson"}
            ],
            "Engineering": [
                {"code": "ENG101", "name": "Introduction to Engineering", "days": "MWF", "time": "09:00-09:50", "room": "ENG-101", "instructor": "Dr. Clark"},
                {"code": "MATH251", "name": "Calculus II", "days": "TTH", "time": "10:30-11:45", "room": "MATH-105", "instructor": "Prof. White"},
                {"code": "PHYS201", "name": "Physics II", "days": "MWF", "time": "11:00-11:50", "room": "SCI-210", "instructor": "Dr. Harris"},
                {"code": "ENG301", "name": "Thermodynamics", "days": "TTH", "time": "13:00-14:15", "room": "ENG-305", "instructor": "Prof. Martin"},
                {"code": "CSE211", "name": "Circuit Analysis", "days": "MWF", "time": "14:00-14:50", "room": "ENG-410", "instructor": "Dr. Young"}
            ]
        }
        
        return base_courses.get(program, base_courses["Computer Science"])

    def format_date(self, date_obj, country_config):
        """Format date according to country preferences."""
        return date_obj.strftime(country_config['date_format'])

    def save_student(self, student_data):
        """Save student data to file."""
        try:
            with open(self.students_file, 'a', encoding='utf-8', buffering=32768) as f:
                line = f"{student_data['full_name']}|{student_data['student_id']}|{student_data['college']['id']}|{student_data['college']['name']}|{self.selected_country}|{student_data['academic_term']}|{student_data['date_issued'].strftime('%Y-%m-%d')}|{student_data['first_day'].strftime('%Y-%m-%d')}|{student_data['last_day'].strftime('%Y-%m-%d')}\n"
                f.write(line)
                f.flush()

            self.stats["students_saved"] += 1
            return True
        except Exception as e:
            logger.error(f"⚠️ Save error: {e}")
            return False

    def process_one(self, num):
        try:
            college = self.select_random_college()
            if college is None:
                return False
            
            student_data = self.generate_student_data(college)
                
            # Generate both tuition receipt and class schedule
            receipt_filename, _ = self.create_tuition_receipt_pdf(student_data)
            schedule_filename = self.create_class_schedule_pdf(student_data)
            
            if receipt_filename and schedule_filename:
                self.save_student(student_data)
                self.stats["receipts_generated"] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing student {num}: {e}")
            return False

    def generate_bulk(self, quantity):
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"⚡ Generating {quantity} TUITION RECEIPTS + SCHEDULES for {config['flag']} {config['name']}")
        print(f"✅ {len(self.all_colleges)} colleges loaded from JSON")
        print("✅ INSTITUTION: Full school names from JSON only")
        print("✅ STUDENT INFO: Name, ID, Program, Semester, Payment Proof")
        print("✅ CURRENT DATES: Current/upcoming semester dates")
        print("✅ TUITION RECEIPT: Professional receipt with payment details")
        print("✅ CLASS SCHEDULE: Complete schedule with enrollment proof")
        print("✅ SHEERID READY: Perfect for instant verification")
        print("=" * 70)

        start = time.time()
        success = 0
        
        # Process in chunks for better memory management
        chunk_size = 50
        
        for chunk_start in range(0, quantity, chunk_size):
            chunk_end = min(chunk_start + chunk_size, quantity)
            chunk_qty = chunk_end - chunk_start
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self.process_one, i+1) for i in range(chunk_start, chunk_end)]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures), chunk_start + 1):
                    if future.result():
                        success += 1
                    
                    if i % 10 == 0 or i == quantity:
                        elapsed = time.time() - start
                        rate = i / elapsed if elapsed > 0 else 0
                        rate_per_min = rate * 60
                        print(f"Progress: {i}/{quantity} ({(i/quantity*100):.1f}%) | Rate: {rate_per_min:.0f} sets/min")
        
        duration = time.time() - start
        rate_per_min = (success / duration) * 60 if duration > 0 else 0
        
        print("\n" + "="*70)
        print(f"✅ COMPLETE - {config['flag']} {config['name']}")
        print("="*70)
        print(f"⏱️  Time: {duration:.1f}s")
        print(f"⚡ Speed: {rate_per_min:.0f} receipt+schedule sets/minute")
        print(f"✅ Success: {success}/{quantity}")
        print(f"📁 Folder: {self.receipts_dir}/")
        print(f"📄 Students: {self.students_file}")
        print(f"✅ FORMAT: Professional PDF receipts + schedules")
        print(f"✅ INSTITUTION: Names from JSON files only")
        print(f"✅ DATES: Current/upcoming semester dates")
        print(f"✅ SHEERID: Perfect for instant verification")
        print("="*70)

    def interactive(self):
        total = 0
        config = COUNTRY_CONFIG[self.selected_country]
        
        while True:
            print(f"\n{'='*60}")
            print(f"Country: {config['flag']} {config['name']}")
            print(f"Total Generated: {total}")
            print(f"Colleges from JSON: {len(self.all_colleges)}")
            print(f"Mode: Professional receipts + schedules")
            print(f"Institution: JSON names only")
            print(f"Dates: Current/upcoming semester")
            print(f"Verification: SheerID ready")
            print(f"{'='*60}")
            
            user_input = input(f"\nQuantity (0 to exit): ").strip()
            
            if user_input == "0":
                break
            
            try:
                quantity = int(user_input)
            except:
                print("❌ Enter a valid number")
                continue
            
            if quantity < 1:
                print("❌ Enter a number greater than 0")
                continue
            
            self.generate_bulk(quantity)
            total = self.stats["receipts_generated"]

def main():
    print("\n" + "="*70)
    print("PROFESSIONAL TUITION RECEIPT GENERATOR - SHEERID VERIFICATION READY")
    print("="*70)
    print("✅ TUITION RECEIPT: Professional receipt with payment proof")
    print("✅ CLASS SCHEDULE: Complete schedule with enrollment proof") 
    print("✅ INSTITUTION: Full school names from JSON only")
    print("✅ STUDENT INFO: Name, ID, Program, Semester, Payment")
    print("✅ CURRENT DATES: Current/upcoming semester dates")
    print("✅ INSTANT APPROVAL: Super-fast verification system")
    print("✅ PERFECT FORMAT: Professional PDF layout")
    print("✅ ALL 24 COUNTRIES: Complete global support")
    print("="*70)
    
    gen = ProfessionalReceiptGenerator()
    
    if not gen.select_country_and_load():
        return
    
    gen.interactive()
    
    print("\n✅ FINISHED! All documents are SheerID verification ready!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")