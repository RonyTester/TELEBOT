from telegram import Update
from telegram.ext import ContextTypes
from services.shopee_api import search_shopee

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Por favor, forneça um termo para busca!")
        return
    
    search_term = ' '.join(context.args)
    try:
        products = await search_shopee(search_term)
        if products:
            response = "🔍 Resultados encontrados:\n\n"
            for product in products[:5]:  # Limita a 5 produtos
                response += f"📦 {product['name']}\n"
                response += f"💰 R$ {product['price']}\n"
                response += f"🔗 {product['link']}\n\n"
        else:
            response = "Nenhum produto encontrado!"
            
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text("Erro ao buscar produtos. Tente novamente!") 