import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import os
import asyncio
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN', '8355962334:AAF2YC4G4wsASItcyQR8G0oWTsEo9m8r7YI')
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID', '2009580445')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        keyboard = [
            [InlineKeyboardButton("🚀 Оформить заказ", web_app=WebAppInfo(url="https://ghostdoxbin.github.io"))]
        ]
        
        await update.message.reply_text(
            "👋 Добро пожаловать в сервис заказа проектов!\n\n"
            "Для оформления заказа нажмите кнопку ниже:\n"
            "• Заполните детальную форму\n" 
            "• Скопируйте готовую заявку\n"
            "• Отправьте боту\n\n"
            "Я свяжусь с вами для обсуждения деталей в течение 24 часов! 🚀",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info(f"Команда /start от пользователя {update.effective_user.first_name}")
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {e}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

async def handle_order_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений с заказами"""
    try:
        message_text = update.message.text
        
        # Проверяем, это заказ из формы
        if "🎯 ДЕТАЛЬНЫЙ ЗАКАЗ ПРОЕКТА" in message_text:
            logger.info(f"Получен детальный заказ от {update.effective_user.first_name}")
            
            # Парсим данные из сообщения
            order_data = parse_detailed_order(message_text)
            
            # Подтверждение пользователю
            await update.message.reply_text(
                f"✅ <b>Детальная заявка принята!</b>\n\n"
                f"Спасибо, <b>{order_data.get('name', '')}</b>!\n"
                f"Ваш заказ на <b>{order_data.get('direction', '')}</b> принят в работу.\n\n"
                f"📞 Я изучу ваше ТЗ и свяжусь с вами в Telegram для обсуждения:\n"
                f"• Детальной оценки\n• Сроков реализации\n• Технических вопросов\n\n"
                f"<i>Время получения: {datetime.now().strftime('%d.%m.%Y в %H:%M')}</i>",
                parse_mode='HTML'
            )
            
            # Сообщение разработчику
            developer_message = f"""
🎯 <b>ДЕТАЛЬНЫЙ ЗАКАЗ ПРОЕКТА</b>

👤 <b>Клиент:</b> {order_data.get('name', 'N/A')}
📱 <b>Telegram:</b> {order_data.get('telegram', 'N/A')}
🆔 <b>User ID:</b> {update.effective_user.id}
👤 <b>Username:</b> @{update.effective_user.username or 'N/A'}

📋 <b>Основная информация:</b>
<b>Направление:</b> {order_data.get('direction', 'N/A')}
<b>Цель:</b> {order_data.get('purpose', 'N/A')}
<b>Бюджет:</b> {order_data.get('budget', 'N/A')}

🎯 <b>Техническое задание:</b>
{order_data.get('tech_task', 'N/A')}

⚙️ <b>Функционал:</b>
<b>Обязательные функции:</b>
{order_data.get('required_features', 'N/A')}

{f"<b>Необязательные функции:</b>\n{order_data.get('optional_features', '')}" if order_data.get('optional_features') else ""}

{f"<b>Материалы:</b>\n{order_data.get('references', '')}" if order_data.get('references') else ""}

📖 <b>Полное описание:</b>
{order_data.get('full_description', 'N/A')}

⏰ <b>Время заявки:</b> {order_data.get('time', 'N/A')}
            """
            
            # Отправляем разработчику
            try:
                await context.bot.send_message(
                    chat_id=DEVELOPER_CHAT_ID,
                    text=developer_message,
                    parse_mode='HTML'
                )
                logger.info(f"Детальный заказ отправлен разработчику от {update.effective_user.first_name}")
            except Exception as e:
                logger.error(f"Ошибка отправки разработчику: {e}")
                
        else:
            # Обычное сообщение - предлагаем оформить заказ
            keyboard = [
                [InlineKeyboardButton("🚀 Оформить заказ", web_app=WebAppInfo(url="https://ghostdoxbin.github.io"))]
            ]
            
            await update.message.reply_text(
                "Для оформления детального заказа нажмите кнопку ниже:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
    except Exception as e:
        logger.error(f"Ошибка в обработчике handle_order_message: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке заказа. Попробуйте еще раз.")

def parse_detailed_order(message):
    """Парсит детальные данные заказа из текстового сообщения"""
    data = {}
    
    try:
        # Имя и Telegram
        name_match = re.search(r'• Имя: (.+)', message)
        telegram_match = re.search(r'• Telegram: (.+)', message)
        
        if name_match:
            data['name'] = name_match.group(1).strip()
        if telegram_match:
            data['telegram'] = telegram_match.group(1).strip()
        
        # Основная информация
        direction_match = re.search(r'• Направление: (.+)', message)
        purpose_match = re.search(r'• Цель проекта: (.+)', message) 
        budget_match = re.search(r'• Бюджет: (.+)', message)
        
        if direction_match:
            data['direction'] = direction_match.group(1).strip()
        if purpose_match:
            data['purpose'] = purpose_match.group(1).strip()
        if budget_match:
            data['budget'] = budget_match.group(1).strip()
        
        # Разделы с многострочным содержанием
        sections = {
            'tech_task': r'🎯 ТЕХНИЧЕСКОЕ ЗАДАНИЕ:\n(.+?)(?=⚙️|📎|📖|⏰|$)',
            'required_features': r'• Обязательные функции:\n(.+?)(?=• Необязательные|📎|📖|⏰|$)',
            'optional_features': r'• Необязательные функции:\n(.+?)(?=📎|📖|⏰|$)',
            'references': r'📎 МАТЕРИАЛЫ:\n(.+?)(?=📖|⏰|$)',
            'full_description': r'📖 ПОЛНОЕ ОПИСАНИЕ:\n(.+?)(?=⏰|$)'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, message, re.DOTALL)
            if match:
                data[key] = match.group(1).strip()
        
        # Время
        time_match = re.search(r'⏰ ВРЕМЯ ЗАЯВКИ: (.+)', message)
        if time_match:
            data['time'] = time_match.group(1).strip()
            
    except Exception as e:
        logger.error(f"Ошибка парсинга детального заказа: {e}")
    
    return data

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    try:
        logger.error(f'Ошибка при обработке update {update}: {context.error}')
        
        # Можно отправить сообщение пользователю об ошибке
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Произошла непредвиденная ошибка. Попробуйте еще раз позже."
                )
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
                
    except Exception as e:
        logger.error(f"Ошибка в обработчике ошибок: {e}")

def main():
    """Основная функция запуска бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order_message))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        # Запускаем бота
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {e}")
        raise

if __name__ == '__main__':
    main()