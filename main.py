from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import os
from dotenv import load_dotenv
import logging
from handlers.commands import start, help_command
from handlers.shopee import search_products
from handlers.scheduler import schedule_message

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

def main():
    # Inicializa o bot
    application = Application.builder().token(TOKEN).build()

    # Adiciona handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("buscar", search_products))
    application.add_handler(CommandHandler("agendar", schedule_message))

    # Inicia o bot
    print("Iniciando o bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 