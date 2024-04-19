import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config import FONT_STYLE, LINE_SPACING


pdfmetrics.registerFont(TTFont(FONT_STYLE, FONT_STYLE+'.ttf'))


def generate_pdf(data, single_user=False):
    pdf_bytes = io.BytesIO()
    styles = ParagraphStyle(FONT_STYLE)
    doc = SimpleDocTemplate(pdf_bytes, pagesize=A4)
    elements = []
    styles.fontName = FONT_STYLE
    if single_user:
        generate_user_pdf(elements, data, styles)
    else:
        for user in data:
            generate_user_pdf(elements, user, styles)
            elements.append(Spacer(5, LINE_SPACING))
    doc.build(elements)
    pdf_bytes.seek(0)
    return pdf_bytes


def generate_user_pdf(elements, user, styles):
    pdf_data = {
        'Номер телефона': user['phone_number'],
        'Имя': user['first_name'],
        'Отчество': user['second_name'],
        'Фамилия': user['last_name'],
        'Дата рождения': user['birth_date'],
        'Бонусы': user['loyality_balance']
    }

    for key, value in pdf_data.items():
        elements.append(Paragraph(f"<strong>{key}:</strong> {value}", styles))

    for car in user['cars']:
        cars_data = (
            f"Модель: {car['brand']},\n"
            f"Марка: {car['model']},\n"
            f"Гос.номер: {car['number_plate']}"
        )
        elements.append(Paragraph(cars_data, styles))
