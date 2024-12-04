# Regras de Desenvolvimento do Bot

## 1. Estrutura do Código
- Usar versão 20.8+ do python-telegram-bot
- Não usar async/await no main.py para evitar problemas com event loop no Replit
- Usar `application.run_polling(drop_pending_updates=True)` para iniciar o bot
- Organizar código em módulos separados (handlers, services, utils)

## 2. Interface do Usuário
- Usar InlineKeyboardMarkup para menus de navegação
- Minimizar digitação do usuário - preferir botões quando possível
- Manter hierarquia clara nos menus
- Sempre ter opção de "Voltar" ou "Menu Principal"
- Limitar opções por menu (máximo 8 botões)

## 3. Handlers
- Separar handlers por funcionalidade
- Usar CallbackQueryHandler para botões inline
- Usar ConversationHandler para diálogos complexos
- Implementar timeout em conversas (30 segundos)

## 4. Boas Práticas
- Sempre incluir mensagens de feedback
- Usar emojis para melhor visualização
- Tratar todos os erros possíveis
- Manter mensagens concisas e claras
- Implementar sistema de ajuda contextual

## 5. Performance
- Limitar resultados de busca (5-10 itens)
- Usar cache quando apropriado
- Implementar rate limiting para APIs externas
- Otimizar consultas ao banco de dados

## 6. Segurança
- Nunca expor tokens ou credenciais
- Validar todas as entradas do usuário
- Implementar sistema de permissões
- Registrar logs de erros importantes 