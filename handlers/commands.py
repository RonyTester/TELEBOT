from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔍 Buscar Produtos", callback_data="menu_buscar"),
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
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 Olá! Sou o bot Divulgador.\n\n"
        "Escolha uma opção abaixo:",
        reply_markup=reply_markup
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_buscar":
        keyboard = [
            [
                InlineKeyboardButton("🛍️ Produtos Shopee", callback_data="buscar_shopee"),
                InlineKeyboardButton("🔥 Promoções", callback_data="buscar_promos")
            ],
            [
                InlineKeyboardButton("📊 Relatórios", callback_data="buscar_relatorios"),
                InlineKeyboardButton("🔄 Últimas Buscas", callback_data="buscar_historico")
            ],
            [
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔍 *Menu de Busca*\n\n"
            "O que você deseja buscar?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "menu_favoritos":
        keyboard = [
            [
                InlineKeyboardButton("❤️ Ver Favoritos", callback_data="favoritos_ver"),
                InlineKeyboardButton("➕ Adicionar", callback_data="favoritos_add")
            ],
            [
                InlineKeyboardButton("🔔 Alertas de Preço", callback_data="favoritos_alertas"),
                InlineKeyboardButton("🗑️ Gerenciar", callback_data="favoritos_gerenciar")
            ],
            [
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")
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
                InlineKeyboardButton("📊 Relatórios", callback_data="agenda_relatorios"),
                InlineKeyboardButton("🗑️ Gerenciar", callback_data="agenda_gerenciar")
            ],
            [
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")
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
                InlineKeyboardButton("🎨 Aparência", callback_data="config_aparencia"),
                InlineKeyboardButton("⚙️ Geral", callback_data="config_geral")
            ],
            [
                InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")
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
        # Volta para o menu principal
        await start(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📖 Guia Completo", callback_data="help_guia"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
        ],
        [
            InlineKeyboardButton("📱 Comandos", callback_data="help_comandos"),
            InlineKeyboardButton("🆘 Suporte", callback_data="help_suporte")
        ],
        [
            InlineKeyboardButton("🔙 Voltar ao Menu", callback_data="menu_principal")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "❓ *Central de Ajuda*\n\n"
        "Como posso te ajudar?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    ) 