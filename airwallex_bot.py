#!/usr/bin/env python3
import logging
import os
import re
import imaplib
from datetime import timezone
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8292127678:AAGDhFHjZpEld0nyzJKKa2HkG7zZ-ch_t0g")
GMAIL_USER = os.getenv("GMAIL_USER", "aabkhan402@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "ftljxjidduzsqxob")
AIRWALLEX_SENDER = os.getenv("AIRWALLEX_SENDER", "support@info.airwallex.com")


def extract_body_text(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition") or "").lower()
            if content_type == "text/plain" and "attachment" not in disposition:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(charset, errors="ignore")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(charset, errors="ignore")
    return ""


def fetch_airwallex_otp():
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise RuntimeError("Gmail credentials are not configured")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        status, _ = mail.select("INBOX")
        if status != "OK":
            raise RuntimeError("Could not open INBOX")

        status, data = mail.search(None, f'(FROM "{AIRWALLEX_SENDER}")')
        if status != "OK":
            raise RuntimeError("Search failed")

        ids = data[0].split()
        if not ids:
            raise RuntimeError("No Airwallex emails found")

        latest_id = ids[-1]
        status, msg_data = mail.fetch(latest_id, "(RFC822)")
        if status != "OK" or not msg_data:
            raise RuntimeError("Failed to fetch latest Airwallex email")

        raw_email = msg_data[0][1]
        msg = message_from_bytes(raw_email)
        subject = msg.get("Subject", "")
        body_text = extract_body_text(msg)

        otp_match = re.search(r"\b(\d{6})\b", subject) or re.search(r"\b(\d{6})\b", body_text)
        if not otp_match:
            raise RuntimeError("OTP code not found in latest email")

        sent_at = parsedate_to_datetime(msg.get("Date")) if msg.get("Date") else None
        return otp_match.group(1), subject, sent_at
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Send /otp to fetch the latest Airwallex passcode.")


def otp(update: Update, context: CallbackContext):
    try:
        otp_code, subject, sent_at = fetch_airwallex_otp()
        timestamp = sent_at.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z') if sent_at else "Unknown"
        update.message.reply_text(
            "🔐 Latest Airwallex OTP\n\n"
            f"From: {AIRWALLEX_SENDER}\n"
            f"Subject: {subject}\n"
            f"Date: {timestamp}\n\n"
            f"OTP: `{otp_code}`",
            parse_mode='Markdown'
        )
    except Exception as exc:
        logger.error(f"❌ OTP fetch failed: {exc}")
        update.message.reply_text(f"❌ Failed to fetch Airwallex OTP: {exc}")


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("otp", otp))

    logger.info("✅ Airwallex OTP bot started")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
