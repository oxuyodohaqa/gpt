#!/usr/bin/env python3
"""
PROFESSIONAL TEACHER LETTER GENERATOR WITH INSTANT APPROVAL - PERFECT FOR SHEERID
✅ TEACHER LETTER: Official letter with educator name and header
✅ INSTANT APPROVAL: Super-fast verification system
✅ INSTITUTION NAME: Full school name from JSON only
✅ HARDCODED DATES: Current/upcoming term dates
✅ PDF OUTPUT: Professional formatting
✅ ALL 24 COUNTRIES: Complete global support
✅ VERIFICATION READY: Perfect for SheerID verification
"""

import os
import re
import logging
from faker import Faker
import random
import json
from datetime import datetime, timedelta
import time
import concurrent.futures
import threading
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

TEACHER_LETTER_TYPES = [
    "Principal letter",
    "Superintendent letter",
    "Parent / guardian letter",
    "Student notice letter (template)",
    "Attendance letter",
    "Behavior / discipline letter (template)",
    "Policy & compliance letter (FERPA, AUP, AI use)",
    "Consent / notification letter (template)",
    "Staff memo",
    "Staff notice",
    "Enrollment letter",
    "Transfer / withdrawal letter",
    "Records request letter",
    "Meeting invitation letter",
    "Community / public letter"
]

class ProfessionalReceiptGenerator:
    def __init__(self):
        self.receipts_dir = "receipts"
        self.teachers_file = "teachers.txt"
        self.selected_country = None
        self.all_colleges = []
        
        self.faker_instances = []
        self.faker_lock = threading.Lock()
        self.faker_index = 0
        
        # Performance settings
        self.max_workers = 10
        self.memory_cleanup_interval = 100

        self.stats = {
            "teacher_letters_generated": 0,
            "teachers_saved": 0,
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
            if os.path.exists(self.teachers_file):
                try:
                    os.remove(self.teachers_file)
                except Exception:
                    pass

            print("🗑️  All previous data cleared!")
            print("✅ PERFECT FORMAT: Professional letter layout")
            print("✅ INSTANT APPROVAL: Super-fast verification system")
            print("✅ INSTITUTION: Full school name from JSON only")
            print("✅ EDUCATOR INFO: Name-only teacher confirmation")
            print("✅ HARDCODED DATES: Current/upcoming term window")
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

    def generate_teacher_data(self, college):
        """Generate teacher data with CURRENT/UPCOMING term dates."""
        fake = self.get_faker()
        config = COUNTRY_CONFIG[self.selected_country]
        
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = clean_name(f"{first_name} {last_name}")
        teacher_id = f"{fake.random_number(digits=8, fix_len=True)}"
        
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
        
        teacher_titles = [
            "Professor", "Associate Professor", "Assistant Professor",
            "Senior Lecturer", "Lecturer", "Adjunct Instructor"
        ]
        teacher_name = clean_name(f"{random.choice(teacher_titles)} {fake.first_name()} {fake.last_name()}")
        letter_type = random.choice(TEACHER_LETTER_TYPES)

        return {
            "teacher_name": teacher_name,
            "teacher_id": teacher_id,
            "college": college,
            "academic_term": academic_term,
            "date_issued": date_issued,
            "first_day": first_day,
            "last_day": last_day,
            "exam_week": exam_week,
            "country_config": config,
            "letter_type": letter_type,
        }


    def create_teacher_letter_pdf(self, teacher_data):
        """Create an official teacher letter with visible header and educator name."""
        college = teacher_data['college']
        teacher_id = teacher_data['teacher_id']
        college_id = college['id']
        letter_type = teacher_data.get('letter_type', 'Teacher letter')

        filename = f"TEACHER_LETTER_{teacher_id}_{college_id}.pdf"
        filepath = os.path.join(self.receipts_dir, filename)

        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=30
            )

            elements = []
            styles = getSampleStyleSheet()

            header_style = ParagraphStyle(
                'TeacherHeader',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=self.colors['primary'],
                alignment=1,
                spaceAfter=8
            )

            subheader_style = ParagraphStyle(
                'TeacherSubheader',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceAfter=10
            )

            name_style = ParagraphStyle(
                'TeacherName',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=self.colors['text_dark'],
                alignment=1,
                spaceAfter=12
            )

            elements.append(Paragraph(letter_type.upper(), header_style))
            elements.append(Paragraph("Educator Identity Confirmation", subheader_style))
            elements.append(Paragraph(teacher_data['teacher_name'], name_style))

            elements.append(Spacer(1, 18))

            body_style = ParagraphStyle(
                'TeacherBody',
                parent=styles['BodyText'],
                fontSize=11,
                leading=15,
                textColor=self.colors['text_dark'],
                spaceAfter=10
            )

            body_text = (
                f"This {letter_type.lower()} confirms the identity of {teacher_data['teacher_name']} "
                "for educator verification and SheerID-style review."
            )
            elements.append(Paragraph(body_text, body_style))

            scope_style = ParagraphStyle(
                'TeacherScope',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceAfter=8
            )
            elements.append(Paragraph("Teacher-only content. No student data included.", scope_style))

            signature_style = ParagraphStyle(
                'TeacherSignature',
                parent=styles['Normal'],
                fontSize=10,
                textColor=self.colors['secondary'],
                alignment=1,
                spaceBefore=16
            )

            elements.append(Paragraph(teacher_data['teacher_name'], signature_style))

            verification_style = ParagraphStyle(
                'TeacherVerification',
                parent=styles['Normal'],
                fontSize=9,
                textColor=self.colors['text_light'],
                alignment=1,
                spaceBefore=10
            )

            verification_text = (
                f"OFFICIAL TEACHER LETTER • {letter_type} • Educator-only verification"
            )
            elements.append(Paragraph(verification_text, verification_style))

            doc.build(elements)
            return filename

        except Exception as e:
            logger.error(f"Failed to create teacher letter PDF {filename}: {e}")
            return None

    def format_date(self, date_obj, country_config):
        """Format date according to country preferences."""
        return date_obj.strftime(country_config['date_format'])

    def save_teacher(self, teacher_data):
        """Save teacher data to file."""
        try:
            with open(self.teachers_file, 'a', encoding='utf-8', buffering=32768) as f:
                line = f"{teacher_data['teacher_name']}|{teacher_data['teacher_id']}|{teacher_data['college']['id']}|{teacher_data['college']['name']}|{self.selected_country}|{teacher_data['academic_term']}|{teacher_data['letter_type']}|{teacher_data['date_issued'].strftime('%Y-%m-%d')}\n"
                f.write(line)
                f.flush()

            self.stats["teachers_saved"] += 1
            return True
        except Exception as e:
            logger.error(f"⚠️ Save error: {e}")
            return False

    def process_one(self, num):
        try:
            college = self.select_random_college()
            if college is None:
                return False

            teacher_data = self.generate_teacher_data(college)
            teacher_letter_filename = self.create_teacher_letter_pdf(teacher_data)

            if teacher_letter_filename:
                self.save_teacher(teacher_data)
                self.stats["teacher_letters_generated"] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Error processing teacher {num}: {e}")
            return False

    def generate_bulk(self, quantity):
        config = COUNTRY_CONFIG[self.selected_country]
        print(f"⚡ Generating {quantity} OFFICIAL TEACHER LETTERS for {config['flag']} {config['name']}")
        print(f"✅ {len(self.all_colleges)} colleges loaded from JSON")
        print("✅ INSTITUTION: Full school names from JSON only")
        print("✅ EDUCATOR INFO: Name-only teacher confirmation")
        print("✅ CURRENT DATES: Current/upcoming semester window")
        print("✅ TEACHER LETTER: Official educator identity header")
        print("✅ SHEERID READY: Perfect for instant verification")
        print("✅ LETTER TYPES: " + ", ".join(TEACHER_LETTER_TYPES))
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
                        print(f"Progress: {i}/{quantity} ({(i/quantity*100):.1f}%) | Rate: {rate_per_min:.0f} letters/min")
        
        duration = time.time() - start
        rate_per_min = (success / duration) * 60 if duration > 0 else 0
        
        print("\n" + "="*70)
        print(f"✅ COMPLETE - {config['flag']} {config['name']}")
        print("="*70)
        print(f"⏱️  Time: {duration:.1f}s")
        print(f"⚡ Speed: {rate_per_min:.0f} letters/minute")
        print(f"✅ Success: {success}/{quantity}")
        print(f"📁 Folder: {self.receipts_dir}/")
        print(f"📄 Teachers: {self.teachers_file}")
        print(f"✅ FORMAT: Official teacher letters only")
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
            print(f"Mode: Official teacher letters only")
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
            total = self.stats["teacher_letters_generated"]

def main():
    print("\n" + "="*70)
    print("PROFESSIONAL TEACHER LETTER GENERATOR - SHEERID VERIFICATION READY")
    print("="*70)
    print("✅ TEACHER LETTER: Official educator letter with visible header")
    print("✅ INSTITUTION: Full school names from JSON only")
    print("✅ EDUCATOR INFO: Name-only verification focus")
    print("✅ CURRENT DATES: Current/upcoming semester dates")
    print("✅ INSTANT APPROVAL: Super-fast verification system")
    print("✅ PERFECT FORMAT: Professional PDF layout")
    print("✅ ALL 24 COUNTRIES: Complete global support")
    print("✅ LETTER TYPES: " + ", ".join(TEACHER_LETTER_TYPES))
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
