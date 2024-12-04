from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

def get_main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🔍 Buscar Produto", callback_data="menu_buscar"),
            InlineKeyboardButton("⭐ Favoritos", callback_data="menu_favoritos")
        ],
        [
            InlineKeyboardButton("⏰ Agendamentos", callback_data="menu_agendamentos"),
            InlineKeyboardButton("⚙️ Configurações", callback_data="menu_config")
        ],
        [
            InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Olá! Sou o bot Divulgador.\n\n"
        "Escolha uma opção abaixo:"
    )
    
    if update.callback_query:
        await update.callback_query.message.edit_text(
            text=text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=get_main_menu_keyboard()
        )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_buscar":
        await query.edit_message_text(
            "🔍 *Como buscar produtos:*\n\n"
            "1. Copie o link do produto da Shopee\n"
            "2. Use o comando:\n"
            "`/buscar link-do-produto`\n\n"
            "Exemplo:\n"
            "`/buscar https://shopee.com.br/produto...`\n\n"
            "Vou te retornar todas as informações do produto! 😊",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
            ]]),
            parse_mode='Markdown'
        )
    
    elif query.data == "menu_favoritos":
        keyboard = [
            [
                InlineKeyboardButton("❤️ Ver Favoritos", callback_data="favoritos_ver"),
                InlineKeyboardButton("🔔 Alertas", callback_data="favoritos_alertas")
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⭐ *Seus Favoritos*\n\n"
            "Gerencie seus produtos favoritos:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "menu_agendamentos":
        keyboard = [
            [
                InlineKeyboardButton("📅 Ver Agendados", callback_data="agenda_ver"),
                InlineKeyboardButton("➕ Novo", callback_data="agenda_novo")
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⏰ *Agendamentos*\n\n"
            "Gerencie suas mensagens agendadas:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "menu_config":
        keyboard = [
            [
                InlineKeyboardButton("🔔 Notificações", callback_data="config_notif"),
                InlineKeyboardButton("👥 Grupos", callback_data="config_grupos")
            ],
            [
                InlineKeyboardButton("🎨 Voltar", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚙️ *Configurações*\n\n"
            "Personalize seu bot:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "menu_principal":
        await start(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📖 Guia Completo", callback_data="help_guia"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
        ],
        [
            InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "❓ *Central de Ajuda*\n\n"
        "Como posso te ajudar?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    ) 