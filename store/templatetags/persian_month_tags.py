import jdatetime
from django import template

register = template.Library()

PERSIAN_MONTHS = {
    "Farvardin": "فروردین",
    "Ordibehesht": "اردیبهشت",
    "Khordad": "خرداد",
    "Tir": "تیر",
    "Mordad": "مرداد",
    "Shahrivar": "شهریور",
    "Mehr": "مهر",
    "Aban": "آبان",
    "Azar": "آذر",
    "Dey": "دی",
    "Bahman": "بهمن",
    "Esfand": "اسفند",
}

PERSIAN_DIGITS = {
    "0": "۰",
    "1": "۱",
    "2": "۲",
    "3": "۳",
    "4": "۴",
    "5": "۵",
    "6": "۶",
    "7": "۷",
    "8": "۸",
    "9": "۹",
}


def convert_to_persian_digits(s):
    return "".join(PERSIAN_DIGITS.get(ch, ch) for ch in str(s))


@register.filter
def to_full_persian_date(value):
    if not value:
        return ""

    jdate = jdatetime.date.fromgregorian(date=value)
    year = convert_to_persian_digits(jdate.year)
    month = PERSIAN_MONTHS.get(jdate.strftime("%B"), jdate.strftime("%B"))
    day = convert_to_persian_digits(jdate.day)

    return f"{day} {month} {year}"
