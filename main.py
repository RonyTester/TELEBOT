from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update
import os
from dotenv import load_dotenv
import logging
import sys
from handlers.commands import start, help_command, menu_handler
from handlers.shopee import search_products
from handlers.scheduler import schedule_message

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Verifica se o token existe
if not TOKEN:
    logger.error("Token do Telegram não encontrado! Verifique o arquivo .env")
    sys.exit(1)

async def error_handler(update: Update, context):
    """Trata erros do bot de forma global"""
    logger.error(f"Erro durante o processamento: {context.error}")
    if update:
        await update.message.reply_text(
            "😅 Ops! Ocorreu um erro ao processar sua solicitação.\n"
            "Por favor, tente novamente mais tarde."
        )

def main():
    try:
        # Inicializa o bot
        application = Application.builder().token(TOKEN).build()

        # Adiciona handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("buscar", search_products))
        application.add_handler(CommandHandler("agendar", schedule_message))
        
        # Adiciona handler para os menus
        application.add_handler(CallbackQueryHandler(menu_handler))

        # Adiciona handler de erro global
        application.add_error_handler(error_handler)

        # Inicia o bot
        logger.info("Iniciando o bot...")
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        logger.error(f"Erro fatal ao iniciar o bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 