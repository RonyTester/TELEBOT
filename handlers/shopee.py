from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.shopee_api import get_product_details

def format_price(price: float, original_price: float = 0, discount: int = 0) -> str:
    """Formata o preço com desconto se houver"""
    if original_price > price and discount > 0:
        return f"💰 De R$ {original_price:.2f} por R$ {price:.2f} (-{discount}%)"
    return f"💰 R$ {price:.2f}"

def format_rating(rating: float, count: int) -> str:
    """Formata a avaliação do produto"""
    stars = "⭐" * int(rating)
    return f"{stars} ({count} avaliações)"

async def format_product_message(product: dict) -> str:
    """Formata a mensagem do produto no estilo do Divulgador Inteligente"""
    message = [
        f"📦 *{product['name']}*\n",
        format_price(product['price'], product['original_price'], product['discount']),
        f"📊 Vendidos: {product['sales']}",
        format_rating(product['rating'], product['rating_count']),
        f"\n🏪 Loja: {product['shop_name']}",
        f"⭐ Avaliação da Loja: {product['shop_rating']:.1f}",
        f"\n📝 Descrição: {product['description'][:200]}..." if len(product['description']) > 200 else f"\n📝 Descrição: {product['description']}",
        f"\n🔗 [Ver na Shopee]({product['link']})"
    ]
    return "\n".join(message)

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal para busca de produtos"""
    if not context.args:
        await update.message.reply_text(
            "🔍 Por favor, envie o link do produto da Shopee.\n"
            "Exemplo: /buscar https://shopee.com.br/produto..."
        )
        return

    url = context.args[0]
    if not "shopee.com.br" in url:
        await update.message.reply_text(
            "❌ Link inválido! Por favor, envie um link válido da Shopee Brasil."
        )
        return

    try:
        # Envia mensagem de carregamento
        loading_message = await update.message.reply_text(
            "🔄 Buscando informações do produto..."
        )

        # Busca detalhes do produto
        product = await get_product_details(url)
        
        if product:
            # Formata e envia a mensagem com os detalhes
            message = await format_product_message(product)
            keyboard = [
                [
                    InlineKeyboardButton("⭐ Favoritar", callback_data=f"fav_{product['id']}"),
                    InlineKeyboardButton("🔔 Alertar Preço", callback_data=f"alert_{product['id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await loading_message.edit_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            await loading_message.edit_text(
                "❌ Não foi possível encontrar o produto. Verifique se o link está correto."
            )
    except Exception as e:
        print(f"Erro ao processar produto: {e}")
        await update.message.reply_text(
            "😅 Ops! Ocorreu um erro ao buscar o produto.\n"
            "Por favor, verifique se o link está correto e tente novamente."
        ) 