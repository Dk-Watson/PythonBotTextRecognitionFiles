import telebot
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import os
from dotenv import load_dotenv

# Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Для Windows
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'  # Для Windows

# Poppler
os.environ['PATH'] += r';C:\Users\Admin_PC\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin'

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def split_text(text, max_length=4096):
    """
    Делим текст на части (ограниченние ТГ).
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@bot.message_handler(content_types=['document', 'photo'])
def handle_document(message):
    try:
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file = bot.download_file(file_info.file_path)
            file_extension = message.document.file_name.split('.')[-1].lower()

            if file_extension == 'pdf':
                text = extract_text_from_pdf(file)
            elif file_extension in ['jpg', 'jpeg', 'png']:
                text = extract_text_from_image(file)
            else:
                bot.reply_to(message, "Формат файла не поддерживается. Пожалуйста, отправьте PDF или JPEG файл.")
                return

        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            file = bot.download_file(file_info.file_path)
            text = extract_text_from_image(file)

        # Разбиваем текст на части и отправляем
        text_parts = split_text(text)
        for part in text_parts:
            bot.reply_to(message, part)

    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

def extract_text_from_pdf(file):
    """
    Конвертирует PDF в изображение и распознаёт текст.
    """
    images = convert_from_bytes(file)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image, lang='rus')
    return text

def extract_text_from_image(file):
    """
    Распознаёт текст из изображения.
    """
    image = Image.open(io.BytesIO(file))
    text = pytesseract.image_to_string(image, lang='rus')
    return text

if __name__ == "__main__":
    bot.polling(none_stop=True)