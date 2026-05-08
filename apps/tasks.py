from os import getenv
from django.db.models.signals import post_save
from django.dispatch import receiver
from pytils.translit import slugify
from django.contrib.auth import get_user_model
import requests

from apps.models import *

User = get_user_model()


def generate_unique_login(first_name, last_name):
    last_t = slugify(last_name)[:5]
    first_t = slugify(first_name)[0] if first_name else 'u'

    base_login = f"{last_t}_{first_t}"
    login = base_login
    counter = 1

    while User.objects.filter(username=login).exists():
        login = f"{base_login}{counter}"
        counter += 1

    return login


def create_student_with_parent(student_fn, student_ln, parent_fn, parent_ln):
    s_login = generate_unique_login(student_fn, student_ln)
    student_user = User.objects.create_user(
        username=s_login,
        password=User.objects.make_random_password(),
        first_name=student_fn,
        last_name=student_ln,
        role='student'
    )

    p_login = generate_unique_login(parent_fn, parent_ln)

    parent_user = User.objects.create_user(
        username=p_login,
        first_name=parent_fn,
        last_name=parent_ln,
        role='parent',
        is_active=False
    )
    return s_login, p_login


@receiver(post_save, sender=JournalEntry)
def notify_parent(sender, instance, created, **kwargs):
    if created:
        try:
            parent = instance.student.parent_profile
            if parent and parent.telegram_id:
                text = (
                    f"📊 <b>Новая оценка!</b>\n"
                    f"Ученик: {instance.student.get_full_name()}\n"
                    f"Балл: {instance.grade_class}\n"
                    f"Заметка: {instance.note}\n"
                    f"Присутствие: {'✅' if instance.is_present else '❌'}"
                )
                send_telegram_notification(parent.telegram_id, text)
        except Exception as e:
            print(f"Ошибка уведомления: {e}")


def send_telegram_notification(chat_id, text):
    token = getenv("BOT_TOKEN")
    url = f"https://telegram.org{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Ошибка отправки в ТГ: {e}")





