import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =============================
# 🔐 CONFIGURAÇÃO
# =============================

BOT_TOKEN = "8472485329:AAF1IXgzm1AaRdKKXbT-pRmQa0VBhNz_2ow"
ADMIN_IDS = [8431121309]

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
# 🎨 FUNÇÕES
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


def info_roleta(numero):
    cores_vermelhas = {
        1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
    }

    cor = "🔴 Vermelho" if numero in cores_vermelhas else "⚫ Preto"
    if numero == 0:
        cor = "🟢 Verde"

    coluna = (
        "1ª Coluna" if numero % 3 == 1 else
        "2ª Coluna" if numero % 3 == 2 else
        "3ª Coluna"
    ) if numero != 0 else "-"

    duzia = (
        "1ª Dúzia" if 1 <= numero <= 12 else
        "2ª Dúzia" if 13 <= numero <= 24 else
        "3ª Dúzia"
    ) if numero != 0 else "-"

    alto_baixo = "Alto" if numero >= 19 else "Baixo"
    if numero == 0:
        alto_baixo = "-"

    return f"{alto_baixo} | {cor} | {coluna} | {duzia}"


def gerar_placar():
    texto = "📊 PLACAR AO VIVO (15 rodadas)\n\n"

    for i, n in enumerate(historico[-15:], start=1):
        texto += f"{i}️⃣ {n}\n"

    return texto


def verificar_regras(context, ultimo):
    global contador_a, contador_b

    if ultimo in REGRA_A:
        contador_a = 0
    else:
        contador_a += 1

    if ultimo in REGRA_B:
        contador_b = 0
    else:
        contador_b += 1

    if contador_a >= 10:
        context.bot.send_message(
            chat_id=context._chat_id,
            text=f"🚨 SINAL REGRA A 🚨\nEntrar agora!\nÚltimo número: {ultimo}"
        )
        contador_a = 0

    if contador_b >= 10:
        context.bot.send_message(
            chat_id=context._chat_id,
            text=f"🚨 SINAL REGRA B 🚨\nEntrar agora!\nÚltimo número: {ultimo}"
        )
        contador_b = 0


# =============================
# 🚀 COMANDOS
# =============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 Qual sua banca inicial?"
    )


async def receber_banca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        valor = float(update.message.text.replace(",", "."))
        bancas[update.effective_user.id] = valor

        await update.message.reply_text(
            "✅ Banca registrada!\n\n📊 Placar iniciado.",
            reply_markup=criar_teclado()
        )
    except:
        pass


async def clicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global historico

    query = update.callback_query
    await query.answer()

    numero = int(query.data.split("_")[1])
    historico.append(numero)

    if len(historico) > 15:
        historico = historico[-15:]

    texto = (
        f"🎯 Número: {numero}\n"
        f"{info_roleta(numero)}\n\n"
        f"{gerar_placar()}"
    )

    await query.edit_message_text(
        texto=texto,
        reply_markup=criar_teclado()
    )

    verificar_regras(context, numero)


# =============================
# ▶️ MAIN
# =============================

def main():
    logging.basicConfig(level=logging.INFO)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(clicar))
    app.add_handler(
        CommandHandler(None, receber_banca)
    )

    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()
