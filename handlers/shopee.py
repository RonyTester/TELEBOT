from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.shopee_api import get_product_details, extract_product_info
import re

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
        format_price(product['price'], product.get('original_price', 0), product.get('discount', 0)),
        f"📊 Vendidos: {product['sales']}",
        format_rating(product['rating'], product.get('rating_count', 0)),
        f"\n🏪 Loja: {product['shop_name']}",
        f"⭐ Avaliação da Loja: {product['shop_rating']:.1f}",
        f"\n📝 Descrição: {product['description'][:200]}..." if len(product['description']) > 200 else f"\n📝 Descrição: {product['description']}",
        f"\n🔗 [Ver na Shopee]({product['link']})"
    ]
    return "\n".join(message)

def extract_shopee_url(text: str) -> str:
    """Extrai URL da Shopee do texto"""
    # Padrões de URL da Shopee
    patterns = [
        r'https?://[^\s<>"]+?shopee\.com\.br[^\s<>"]+',
        r'https?://shope\.ee[^\s<>"]+',
        r'https?://s\.shopee[^\s<>"]+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            url = match.group(0)
            # Remove parâmetros desnecessários da URL
            clean_url = url.split('?')[0]
            return clean_url
    return None

async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens procurando por links da Shopee"""
    message_text = update.message.text
    
    # Extrai URL da Shopee
    url = extract_shopee_url(message_text)
    
    if not url:
        # Ignora mensagens sem links da Shopee
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

# Mantém a função search_products para compatibilidade, mas redireciona para process_message
async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /buscar (mantido para compatibilidade)"""
    await process_message(update, context) 