import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =============================
# 🔐 CONFIGURAÇÕES
# =============================

BOT_TOKEN = "8472485329:AAGTwgm8KwU4tt-R69VmGijq6DiaSjCyv8I"
ADMIN_IDS = [8431121309]  # exemplo: [123456789]

# =============================
# 🎯 REGRAS
# =============================

REGRA_A = {3, 6, 9, 13, 16, 19, 23, 26, 29, 33, 36}
REGRA_B = {19, 32, 15, 0, 26, 3, 35, 12, 28, 8, 23, 10, 5}

historico = []
contador_a = 0
contador_b = 0
bancas = {}

# =============================
# 🎨 TECLADO 0-36
# =============================

def criar_teclado():
    teclado = []
    linha = []
    for i in range(37):
        linha.append(InlineKeyboardButton(str(i), callback_data=f"num_{i}"))
        if len(linha) == 6:
            teclado.append(linha)
            linha = []
    if linha:
        teclado.append(linha)
    return InlineKeyboardMarkup(teclado)

# =============================
# 📊 PLACAR AO VIVO
# =============================

def gerar_placar():
    texto = "📊 PLACAR AO VIVO (15 rodadas)\n\n"
    for i, numero in enumerate(historico[-15:], start=1):
        texto += f"{i}️⃣ {numero}\n"
    return texto

# =============================
# 🚨 VERIFICAÇÃO DE REGRAS
# =============================

def verificar_regras(numero):
    global contador_a, contador_b
    sinais = []

    if numero in REGRA_A:
        contador_a = 0
    else:
        contador_a += 1

    if numero in REGRA_B:
        contador_b = 0
    else:
        contador_b += 1

    if contador_a >= 10:
        sinais.append("🚨 SINAL REGRA A 🚨")
        contador_a = 0

    if contador_b >= 10:
        sinais.append("🚨 SINAL REGRA B 🚨")
        contador_b = 0

    return sinais

# =============================
# 💰 GESTÃO DE BANCA
# =============================

def calcular_fichas(banca, tipo="normal"):
    """
    Retorna uma lista com os valores das fichas dependendo do tipo de aposta
    tipo: normal, media, agressiva
    """
    if tipo == "normal":
        valor = banca / 4
        fichas = [valor / 12] * 12
    elif tipo == "media":
        valor = banca / 2
        fichas = [valor / 12] * 12
    elif tipo == "agressiva":
        valor = banca
        fichas = [valor / 12] * 12
    else:
        fichas = []
    return fichas

# =============================
# 🚀 COMANDO /start
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ BOT ONLINE\n\nDigite sua banca inicial (ex: 50) para começar."
    )

# =============================
# 💵 RECEBER BANCA
# =============================

async def registrar_banca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(update.message.text.replace(",", "."))
        bancas[update.effective_user.id] = valor
        await update.message.reply_text(
            f"✅ Banca registrada: R${valor}\n\n"
            "📊 Placar iniciado!",
            reply_markup=criar_teclado()
        )
    except:
        await update.message.reply_text("❌ Valor inválido. Digite apenas números.")

# =============================
# 🎯 CLIQUE NOS NÚMEROS (PAINEL ADMIN)
# =============================

async def clicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global historico

    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("Somente administrador pode registrar números.", show_alert=True)
        return

    numero = int(query.data.split("_")[1])
    historico.append(numero)

    if len(historico) > 15:
        historico = historico[-15:]

    sinais = verificar_regras(numero)
    texto = gerar_placar()

    if sinais:
        texto += "\n\n" + "\n".join(sinais)
        texto += f"\n🎯 Último número: {numero}"

    await query.edit_message_text(text=texto, reply_markup=criar_teclado())

# =============================
# ▶️ MAIN
# =============================

def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_banca))
    app.add_handler(CallbackQueryHandler(clicar))

    print("BOT INICIADO COM SUCESSO")
    app.run_polling()

if _name_ == "_main_":
    main()
