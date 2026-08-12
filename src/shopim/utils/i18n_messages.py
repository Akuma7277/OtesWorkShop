# Centrally managed translation module for Uzbek (uz) and Russian (ru)

MESSAGES = {
    "uz": {
        # Admin Main
        "admin_welcome": "Salom, <b>{name}</b>! Admin panelidasiz.\nRoli: <b>{role}</b>",
        "admin_keyboard_dashboard": "📊 Dashboard",
        "admin_keyboard_orders": "🛒 Buyurtmalar",
        "admin_keyboard_users": "👥 Foydalanuvchilar",
        "admin_keyboard_add_product": "➕ Tovar qo'shish",
        "admin_keyboard_edit_products": "✏️ Tovarlarni boshqarish",
        "admin_keyboard_topups": "💳 To'lovlar",
        "admin_keyboard_settings": "⚙️ Sozlamalar",
        
        # User Main
        "user_welcome": "<b>{bot_name}</b> 👥 Xush kelibsiz!\n\nAssalomu alaykum, <b>{full_name}</b>!\nMahsulotlarni tanlash va xarid qilish uchun pastdagi menyudan foydalaning.",
        "user_keyboard_buy": "🛒 Sotib olish",
        "user_keyboard_stock": "📦 Mavjud yuklar",
        "user_keyboard_profile": "👤 Profil",
        "user_keyboard_history": "📜 Xaridlar tarixi",
        "user_keyboard_jobs": "💼 Ish! YUQORI MAOSH!",
        "user_keyboard_lang": "🌐 Tilni o'zgartirish",
        "user_keyboard_reviews": "💬 Sharhlar",
        
        # Profile & Job
        "profile_text": "👤 <b>Sizning profilingiz</b>\n🧾 Xaridlar: <b>{total_orders}</b>\n💰 Xaridlar summasi: <b>{total_spent:.2f} USD</b>\n💳 Balans: <b>0.00 USD</b>\n🎁 Chegirma: <b>0%</b>",
        "job_text": "💼 <b>Ish! YUQORI MAOSH!</b>\n\nKuryerlar, qadoqlovchilar va omborchilar talab qilinadi!\nYuqori maosh, moslashuvchan grafik va to'liq maxfiylik.\n\nOperator bilan bog'lanish: {operator}",
        "lang_changed_uz": "Til muvaffaqiyatli O'zbekchaga o'zgartirildi!",
        "lang_changed_ru": "Язык успешно изменен на Русский!",
        
        # Shop & Location
        "select_location": "Joylash joyini (Toshkent tumanini) tanlang:",
        "select_product": "Mahsulotni tanlang:",
        "no_stock_in_location": "Ushbu tumanda hozircha tovarlar mavjud emas.",
        
        # Reviews
        "reviews_title": "💬 <b>Mijozlarimiz sharhlari:</b>\n",
        "no_reviews": "Hozircha sharhlar mavjud emas.",
        "write_review": "✍️ Sharh qoldirish",
        "review_thanks": "Rahmat! Sharhingiz adminga tekshirish uchun yuborildi.",
    },
    "ru": {
        # Admin Main
        "admin_welcome": "Здравствуйте, <b>{name}</b>! Вы в панели администратора.\nРоль: <b>{role}</b>",
        "admin_keyboard_dashboard": "📊 Dashboard",
        "admin_keyboard_orders": "🛒 Заказы",
        "admin_keyboard_users": "👥 Пользователи",
        "admin_keyboard_add_product": "➕ Добавить товар",
        "admin_keyboard_edit_products": "✏️ Управление товарами",
        "admin_keyboard_topups": "💳 Пополнения",
        "admin_keyboard_settings": "⚙️ Настройки",
        
        # User Main
        "user_welcome": "<b>{bot_name}</b> 👥 Добро пожаловать!\n\nЗдравствуйте, <b>{full_name}</b>!\nВоспользуйтесь меню ниже для выбора товаров и совершения покупок.",
        "user_keyboard_buy": "Купить",
        "user_keyboard_stock": "Наличие",
        "user_keyboard_profile": "Профиль",
        "user_keyboard_history": "История покупок",
        "user_keyboard_jobs": "Работа! ПЛАТИМ ДОХУЯ!",
        "user_keyboard_lang": "🌐 Сменить язык",
        "user_keyboard_reviews": "Отзывы",
        
        # Profile & Job
        "profile_text": "👤 <b>Ваш профиль</b>\n🧾 Покупок: <b>{total_orders}</b>\n💰 Сумма покупок: <b>{total_spent:.2f} USD</b>\n💳 Баланс: <b>0.00 USD</b>\n🎁 Скидка: <b>0%</b>",
        "job_text": "💼 <b>Работа! ПЛАТИМ ДОХУЯ!</b>\n\nТребуются курьеры, фасовщики и складские работники!\nВысокая оплата, гибкий график и полная анонимность.\n\nДля связи с оператором: {operator}",
        "lang_changed_uz": "Til muvaffaqiyatli O'zbekchaga o'zgartirildi!",
        "lang_changed_ru": "Язык успешно изменен на Русский!",
        
        # Shop & Location
        "select_location": "Выберите район:",
        "select_product": "Выберите товар:",
        "no_stock_in_location": "В этом районе пока нет товаров в наличии.",
        
        # Reviews
        "reviews_title": "💬 <b>Отзывы наших клиентов:</b>\n",
        "no_reviews": "Пока нет опубликованных отзывов.",
        "write_review": "✍️ Оставить отзыв",
        "review_thanks": "Спасибо! Ваш отзыв отправлен администратору на проверку.",
    }
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    lang_code = "uz" if lang == "uz" else "ru"
    template = MESSAGES.get(lang_code, {}).get(key, MESSAGES["ru"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template
