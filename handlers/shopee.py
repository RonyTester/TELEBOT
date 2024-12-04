from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.shopee_api import search_shopee

# Mapeamento de categorias para IDs da Shopee
CATEGORIAS = {
    "eletronicos": {
        "id": 11036132,
        "keywords": "celular tablet notebook eletrônicos"
    },
    "moda": {
        "id": 11035567,
        "keywords": "roupa calçado acessórios moda"
    },
    "casa": {
        "id": 11036670,
        "keywords": "casa decoração móveis"
    },
    "games": {
        "id": 11035954,
        "keywords": "jogos games console"
    }
}

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
    """Formata a mensagem de um produto com todas as informações"""
    message = [
        f"📦 *{product['name']}*",
        format_price(product['price'], product['original_price'], product['discount']),
        format_rating(product['rating'], product['rating_count']),
        f"📊 Vendidos: {product['sales']}",
        f"📦 Estoque: {product['stock']}",
        f"🔗 [Ver na Shopee]({product['link']})\n"
    ]
    return "\n".join(message)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE, products: list):
    """Mostra os produtos com botões de navegação"""
    if not products:
        keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="buscar_shopee")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "😕 Nenhum produto encontrado nesta categoria.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    # Cria a mensagem com os produtos
    message = "🛍️ *Produtos Encontrados*\n\n"
    for product in products[:5]:  # Limita a 5 produtos
        message += await format_product_message(product)

    # Adiciona botões de navegação
    keyboard = [
        [
            InlineKeyboardButton("⭐ Favoritar", callback_data=f"fav_{products[0]['id']}"),
            InlineKeyboardButton("🔄 Mais Produtos", callback_data="mais_produtos")
        ],
        [InlineKeyboardButton("🔙 Voltar", callback_data="buscar_shopee")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        # Se a mensagem for muito longa, envia uma versão resumida
        message = "🛍️ *Produtos Encontrados*\n\n"
        for product in products[:3]:  # Reduz para 3 produtos
            message += f"📦 {product['name'][:50]}...\n{format_price(product['price'])}\n\n"
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def search_by_category(update: Update, context: ContextTypes.DEFAULT_TYPE, categoria: str):
    """Busca produtos por categoria"""
    try:
        cat_info = CATEGORIAS.get(categoria)
        if not cat_info:
            return []
        
        # Busca usando as palavras-chave da categoria e seu ID
        products = await search_shopee(
            query=cat_info['keywords'],
            category_id=cat_info['id']
        )
        
        return products
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        return []

async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler principal de busca"""
    if not context.args:
        await update.message.reply_text(
            "🔍 Por favor, use:\n"
            "/buscar [termo]\n"
            "Exemplo: /buscar celular samsung"
        )
        return

    query = ' '.join(context.args)
    try:
        products = await search_shopee(query)
        if products:
            message = "🛍️ *Produtos Encontrados*\n\n"
            for product in products[:5]:
                message += await format_product_message(product)
            
            keyboard = [
                [
                    InlineKeyboardButton("⭐ Favoritar", callback_data=f"fav_{products[0]['id']}"),
                    InlineKeyboardButton("🔄 Mais Produtos", callback_data="mais_produtos")
                ],
                [InlineKeyboardButton("🔙 Menu Principal", callback_data="menu_principal")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text("😕 Nenhum produto encontrado.")
    except Exception as e:
        await update.message.reply_text(
            "😅 Ops! Ocorreu um erro ao buscar produtos.\n"
            "Por favor, tente novamente mais tarde."
        ) 