from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from handlers.shopee import search_by_category, show_products

def get_main_menu_keyboard():
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
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔍 *Menu de Busca*\n\n"
            "O que você deseja buscar?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "buscar_shopee":
        keyboard = [
            [
                InlineKeyboardButton("📱 Eletrônicos", callback_data="shopee_eletronicos"),
                InlineKeyboardButton("👕 Moda", callback_data="shopee_moda")
            ],
            [
                InlineKeyboardButton("🏠 Casa", callback_data="shopee_casa"),
                InlineKeyboardButton("🎮 Games", callback_data="shopee_games")
            ],
            [
                InlineKeyboardButton("🔍 Busca Livre", callback_data="shopee_busca_livre")
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_buscar")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🛍️ *Produtos Shopee*\n\n"
            "Escolha uma categoria ou faça uma busca livre:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data.startswith("shopee_"):
        categoria = query.data.replace("shopee_", "")
        if categoria == "busca_livre":
            keyboard = [[InlineKeyboardButton("🔙 Voltar", callback_data="buscar_shopee")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔍 *Busca Livre*\n\n"
                "Digite o que você quer buscar:\n"
                "Exemplo: `/buscar celular samsung`",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Busca produtos da categoria
            produtos = await search_by_category(update, context, categoria)
            await show_products(update, context, produtos)
    
    elif query.data == "menu_principal":
        await start(update, context)
    
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
                InlineKeyboardButton("📊 Relatórios", callback_data="agenda_relatorios"),
                InlineKeyboardButton("🗑️ Gerenciar", callback_data="agenda_gerenciar")
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
                InlineKeyboardButton("🎨 Aparência", callback_data="config_aparencia"),
                InlineKeyboardButton("⚙️ Geral", callback_data="config_geral")
            ],
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="menu_principal")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⚙️ *Configurações*\n\n"
            "Personalize seu bot:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

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