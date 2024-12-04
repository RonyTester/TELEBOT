from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Olá! Sou o bot Divulgador. Posso ajudar você a:\n\n"
        "🔍 Buscar produtos na Shopee\n"
        "⏰ Agendar mensagens para grupos\n"
        "📊 Gerar relatórios personalizados\n\n"
        "Use /help para ver todos os comandos disponíveis!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 Comandos disponíveis:\n\n"
        "/buscar [termo] - Busca produtos na Shopee\n"
        "/agendar - Agenda uma mensagem para envio\n"
        "/relatorio - Gera relatório de produtos\n"
        "/config - Configura preferências do bot"
    ) 