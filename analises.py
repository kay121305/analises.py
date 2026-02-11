import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ======================================
# 🔐 CONFIGURAÇÕES
# ======================================

BOT_TOKEN = "8472485329:AAF1IXgzm1AaRdKKXbT-pRmQa0VBhNz_2ow"
ADMIN_IDS = [8431121309] 

# ======================================
# 🎯 REGRA B
# ======================================

grupoB = {
    19, 32, 15, 0, 26, 3, 35, 12, 28,
    8, 23, 10, 5
}

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

# ======================================
# 📊 VARIÁVEIS
# ======================================

rodadas = []
contadorB = 0
usuarios = {}
chat_ids = set()

logging.basicConfig(level=logging.INFO)

# ======================================
# 🎨 FUNÇÕES
# ======================================

def info_numero(n):
    if n == 0:
        return "🟢 Zero"

    cor = "🔴" if n in vermelhos else "⚫"
    alto = "⬆ Alto" if n >= 19 else "⬇ Baixo"
    coluna = ((n - 1) % 3) + 1
    duzia = ((n - 1) // 12) + 1

    return f"{alto} {cor} | Coluna {coluna} | {duzia}ª Dúzia"

def teclado_admin():
    teclado = []
    linha = []
    for i in range(37):
        linha.append(InlineKeyboardButton(str(i), callback_data=str(i)))
        if len(linha) == 6:
            teclado.append(linha)
            linha = []
    if linha:
        teclado.append(linha)
    return InlineKeyboardMarkup(teclado)

def gerar_placar():
    texto = "🎯 <b>ANÁLISES - PLACAR AO VIVO</b>\n"
    texto += "━━━━━━━━━━━━━━━━━━\n\n"

    for i, n in enumerate(rodadas, start=1):
        texto += f"{i:02d}️⃣  {n} → {info_numero(n)}\n"

    texto += "\n━━━━━━━━━━━━━━━━━━"
    texto += f"\n📊 Regra B sem sair: {contadorB}"

    return texto

def calcular_gestao(banca):
    conservador = 12
    medio = banca / 2
    agressivo = banca

    def calc(valor):
        ficha = round(valor / 12, 2)
        retorno = round(ficha * 36, 2)
        lucro = round(retorno - valor, 2)
        return valor, ficha, lucro

    return calc(conservador), calc(medio), calc(agressivo)

# ======================================
# 🚀 START
# ======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_ids.add(chat_id)

    await update.message.reply_text(
        "💰 Informe sua banca inicial (ex: 50)"
    )

# ======================================
# 💰 RECEBER BANCA
# ======================================

async def receber_banca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if chat_id in usuarios:
        return

    try:
        banca = float(update.message.text)
        usuarios[chat_id] = banca

        await update.message.reply_text(
            f"✅ Banca registrada: R${banca:.2f}\nInicializando sistema ANÁLISES..."
        )

        await update.message.reply_text(
            gerar_placar(),
            parse_mode="HTML"
        )

        if update.effective_user.id in ADMIN_IDS:
            await update.message.reply_text(
                "🔐 PAINEL ADMIN - ANÁLISES",
                reply_markup=teclado_admin()
            )

    except:
        await update.message.reply_text("Digite apenas números.")

# ======================================
# 🎰 CLIQUE ADMIN
# ======================================

async def clique(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global contadorB, rodadas

    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        return

    numero = int(query.data)

    if len(rodadas) == 15:
        rodadas = []

    rodadas.append(numero)

    if numero in grupoB:
        contadorB = 0
    else:
        contadorB += 1

    for chat in chat_ids:
        try:
            await context.bot.send_message(chat, gerar_placar(), parse_mode="HTML")
        except:
            pass

    if contadorB >= 10:
        for chat in chat_ids:
            banca = usuarios.get(chat, 50)
            cons, med, agr = calcular_gestao(banca)

            mensagem = f"""
🚨 <b>SINAL ANÁLISES - REGRA B</b> 🚨

Se não saiu 10 vezes:
19, 32, 15, 0, 26, 3, 35, 12, 28, 8, 23, 10 e 5

🎯 Entrar agora!
🎲 Último número: <b>{numero}</b>

💰 Banca: R${banca:.2f}

🟢 Conservador
Apostar: R${cons[0]:.2f}
Ficha: R${cons[1]:.2f}
Lucro possível: R${cons[2]:.2f}

🟡 Médio
Apostar: R${med[0]:.2f}
Ficha: R${med[1]:.2f}
Lucro possível: R${med[2]:.2f}

🔴 Agressivo
Apostar: R${agr[0]:.2f}
Ficha: R${agr[1]:.2f}
Lucro possível: R${agr[2]:.2f}
"""
            try:
                await context.bot.send_message(chat, mensagem, parse_mode="HTML")
            except:
                pass

        contadorB = 0

# ======================================
# 🤖 INICIAR
# ======================================

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_banca))
app.add_handler(CallbackQueryHandler(clique))

app.run_polling()
