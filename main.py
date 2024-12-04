from telegram.ext import Updater, CommandHandler, MessageHandler, filters
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
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Adiciona handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("buscar", search_products))
    dp.add_handler(CommandHandler("agendar", schedule_message))

    # Inicia o bot
    print("Iniciando o bot...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() 