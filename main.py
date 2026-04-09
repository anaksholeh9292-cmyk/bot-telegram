from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import uuid, asyncio, os
from datetime import datetime
from flask import Flask
from threading import Thread

# ================= CONFIG =================
TOKEN = os.environ.get("8681144173:AAHantRl8ko-7c2xgWIXCBqlLoY-5ijoTwk")
ADMIN_ID = 719777441
ADMIN_NAME = "CS Digital Shop"
QR_IMAGE = "qris.jpg"

orders = {}
history = {}
chat_mode = {}
users = set()
cs_status = "🔴 Offline"

# ================= WEB SERVER =================
web = Flask('')

@web.route('/')
def home():
    return "Bot Musa aktif di Render 🚀"

def run_web():
    web.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ================= UTIL =================
def rupiah(x):
    return "Rp{:,.0f}".format(int(x)).replace(",", ".")

def validasi_nomor(n):
    return n.isdigit() and n.startswith("08") and 10 <= len(n) <= 13

def detect_operator(n):
    prefix = n[:4]
    if prefix in ["0811","0812","0813","0821","0822","0823","0852","0853","0851"]:
        return "Telkomsel"
    elif prefix in ["0817","0818","0819","0859","0877","0878"]:
        return "XL"
    elif prefix in ["0831","0832","0833","0838"]:
        return "Axis"
    elif prefix in ["0814","0815","0816","0855","0856","0857","0858"]:
        return "Indosat"
    elif prefix in ["0895","0896","0897","0898","0899"]:
        return "Tri"
    elif prefix in ["0881","0882","0883","0884","0885","0886","0887","0888","0889"]:
        return "Smartfren"
    return None

def btn_back(to="menu"):
    return InlineKeyboardButton("🔙 Kembali", callback_data=to)

def btn_menu():
    return InlineKeyboardButton("🏠 Menu Utama", callback_data="menu")

# ================= DATA =================
paket_kuota = {
    "Telkomsel":[("1GB / 30 Hari",10000),("3GB / 30 Hari",18000),("5GB / 30 Hari",25000),("10GB / 30 Hari",35000),("20GB / 30 Hari",70000),("50GB / 30 Hari",120000),("Unlimited Apps / 30 Hari",90000)],
    "XL":[("1GB / 30 Hari",8000),("2GB / 30 Hari",12000),("5GB / 30 Hari",25000),("10GB / 30 Hari",30000),("20GB / 30 Hari",50000),("30GB / 30 Hari",75000),("Unlimited Turbo / 30 Hari",120000),("Unlimited Full Speed / 30 Hari",150000)],
    "Axis":[("1GB / 30 Hari",7000),("2GB / 30 Hari",10000),("5GB / 30 Hari",20000),("10GB / 30 Hari",30000),("20GB / 30 Hari",45000),("Unlimited Bronet / 30 Hari",80000),("Unlimited Game / 30 Hari",60000)],
    "Indosat":[("1GB / 30 Hari",8000),("3GB / 30 Hari",15000),("5GB / 30 Hari",22000),("10GB / 30 Hari",25000),("20GB / 30 Hari",45000),("50GB / 30 Hari",90000),("Unlimited / 30 Hari",140000)],
    "Tri":[("1GB / 30 Hari",6000),("3GB / 30 Hari",12000),("5GB / 30 Hari",18000),("10GB / 30 Hari",20000),("20GB / 30 Hari",40000),("Unlimited / 30 Hari",130000)],
    "Smartfren":[("1GB / 30 Hari",7000),("5GB / 30 Hari",20000),("10GB / 30 Hari",25000),("20GB / 30 Hari",40000),("30GB / 30 Hari",50000),("Unlimited Nonstop / 30 Hari",50000),("Unlimited Malam / 30 Hari",30000),("Unlimited Full 24 Jam / 30 Hari",75000)]
}

pulsa_data = {
    "Telkomsel": {5000:6000,10000:9000,20000:19000,50000:46000,100000:93000},
    "XL": {5000:6000,10000:8500,20000:18500,50000:45000,100000:92000},
    "Axis": {5000:6000,10000:8500,20000:18500,50000:45000,100000:92000},
    "Indosat": {5000:6000,10000:8000,20000:18000,50000:44000,100000:90000},
    "Tri": {5000:6000,10000:7500,20000:17500,50000:43000,100000:89000},
    "Smartfren": {5000:6000,10000:7000,20000:17000,50000:42000,100000:88000}
}

imei_data = {
    "1 Bulan":150000,
    "3 Bulan":250000,
    "6 Bulan":350000,
    "1 Tahun":750000
}

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📶 Paket Data", callback_data="kuota"),
         InlineKeyboardButton("📞 Pulsa", callback_data="pulsa")],
        [InlineKeyboardButton("📱 Unblock IMEI iPhone", callback_data="imei")],
        [InlineKeyboardButton("🧾 Riwayat", callback_data="history")],
        [InlineKeyboardButton(f"💬 Chat Admin ({cs_status})", callback_data="chat")]
    ])

# ================= STATUS =================
async def online(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cs_status
    if update.effective_user.id == ADMIN_ID:
        cs_status = "🟢 Online"
        await update.message.reply_text("CS Online")

async def offline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global cs_status
    if update.effective_user.id == ADMIN_ID:
        cs_status = "🔴 Offline"
        await update.message.reply_text("CS Offline")

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text("✨ DIGITAL SHOP PREMIUM", reply_markup=menu())

# ================= BUTTON =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    u = context.user_data
    data = q.data

    if data == "menu":
        chat_mode.pop(uid, None)
        return await q.edit_message_text("🛒 MENU UTAMA", reply_markup=menu())

    elif data == "chat":
        chat_mode[uid] = True
        return await q.edit_message_text(
            f"💬 Chat dengan CS ({cs_status})",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Akhiri Chat", callback_data="end_chat")],
                [btn_menu()]
            ])
        )

    elif data == "end_chat":
        chat_mode.pop(uid, None)
        context.user_data.clear()
        history.pop(uid, None)
        await q.message.delete()
        return await context.bot.send_message(uid, "❌ Chat diakhiri\n🧹 Riwayat dihapus", reply_markup=menu())

    elif data.startswith("reply_"):
        context.user_data["reply_to"] = int(data.split("_")[1])
        return await q.message.reply_text("Ketik balasan...")

    # ===== KUOTA =====
    elif data == "kuota":
        kb = [[InlineKeyboardButton(op, callback_data=f"op_{op}")] for op in paket_kuota]
        kb.append([btn_back()])
        return await q.edit_message_text("Pilih Operator", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("op_"):
        op = data.split("_")[1]
        u["operator"] = op
        kb = [[InlineKeyboardButton(f"{p[0]} - {rupiah(p[1])}", callback_data=f"pkt_{i}")]
              for i,p in enumerate(paket_kuota[op])]
        kb.append([btn_back("kuota")])
        return await q.edit_message_text("Pilih Paket", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("pkt_"):
        i = int(data.split("_")[1])
        u["produk"] = f"{paket_kuota[u['operator']][i][0]} ({u['operator']})"
        u["harga"] = paket_kuota[u["operator"]][i][1]
        u["menu"] = "kuota"
        return await q.edit_message_text("Masukkan nomor HP")

    # ===== PULSA =====
    elif data == "pulsa":
        kb = [[InlineKeyboardButton(f"{rupiah(n)} + Masa Aktif 30 Hari", callback_data=f"pulsa_{n}")]
              for n in [5000,10000,20000,50000,100000]]
        kb.append([btn_back()])
        return await q.edit_message_text("Pilih nominal", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("pulsa_"):
        u["nominal"] = int(data.split("_")[1])
        u["menu"] = "pulsa"
        return await q.edit_message_text("Masukkan nomor HP")

    # ===== IMEI =====
    elif data == "imei":
        kb = [[InlineKeyboardButton(f"{k} - {rupiah(v)}", callback_data=f"imei_{k}")]
              for k,v in imei_data.items()]
        kb.append([InlineKeyboardButton("🏛 Bea Cukai", callback_data="imei_bc")])
        kb.append([btn_back()])
        return await q.edit_message_text("Pilih layanan IMEI", reply_markup=InlineKeyboardMarkup(kb))

    elif data.startswith("imei_") and data != "imei_bc":
        paket = data.split("_")[1]
        u["produk"] = f"Unblock IMEI ({paket})"
        u["harga"] = imei_data[paket]
        u["menu"] = "imei"
        return await q.edit_message_text("Masukkan IMEI")

    elif data == "imei_bc":
        chat_mode[uid] = True
        return await q.edit_message_text("💬 Konsultasi IMEI", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Akhiri Chat", callback_data="end_chat")],
            [btn_menu()]
        ]))

    elif data == "history":
        text = "\n".join(history.get(uid,[])) or "Belum ada transaksi"
        return await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[btn_back()]]))

    elif data.startswith("upload_"):
        u["upload"] = data.split("_")[1]
        return await q.message.reply_text("📤 Kirim bukti transfer")

# ================= HANDLE =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uname = update.effective_user.username or "User"
    text = update.message.text if update.message.text else ""
    u = context.user_data

    # ADMIN BALAS
    if uid == ADMIN_ID:
        target = u.get("reply_to")

        if not target and update.message.reply_to_message:
            try:
                msg = update.message.reply_to_message.text
                if "🆔" in msg:
                    target = int(msg.split("🆔")[1].split("\n")[0])
            except:
                pass

        if target:
            await context.bot.send_message(target, "⌨️ CS sedang mengetik...")
            await asyncio.sleep(1.5)

            await context.bot.send_message(
                target,
                f"╔══ 💬 {ADMIN_NAME}\n{text}\n╚══════════════\n✓✓"
            )

            u.pop("reply_to", None)
            return await update.message.reply_text("Terkirim ✓✓")

    # USER CHAT
    if uid in chat_mode:
        await context.bot.send_message(
            ADMIN_ID,
            f"╔══ 📩 CHAT MASUK\n🆔 {uid}\n👤 @{uname}\n────────────\n{text}\n────────────",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Balas", callback_data=f"reply_{uid}")]
            ])
        )

        return await update.message.reply_text(
            "Terkirim ✓",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Akhiri Chat", callback_data="end_chat")],
                [btn_menu()]
            ])
        )

    # ORDER
    if "menu" in u and "upload" not in u:
        oid = str(uuid.uuid4())[:6]
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        tujuan = f"IMEI: {text}" if u["menu"]=="imei" else text

        orders[oid] = {"user":uid,"produk":u["produk"],"tujuan":tujuan,"harga":u["harga"],"status":"PENDING"}
        history.setdefault(uid,[]).append(f"{oid} | {rupiah(u['harga'])} | ⏳ PENDING | {now}")

        with open(QR_IMAGE,"rb") as qr:
            await update.message.reply_photo(qr, caption=f"{oid}\n{u['produk']}\n{tujuan}\n{rupiah(u['harga'])}")

        await update.message.reply_text("Klik setelah bayar", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Upload Bukti", callback_data=f"upload_{oid}")],
            [btn_menu()]
        ]))

    elif "upload" in u and update.message.photo:
        oid = u["upload"]
        data = orders[oid]

        await context.bot.send_photo(
            ADMIN_ID,
            update.message.photo[-1].file_id,
            caption=f"{oid}\n{data['produk']}\n{data['tujuan']}\n{rupiah(data['harga'])}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Selesai", callback_data=f"done_{oid}"),
                 InlineKeyboardButton("❌ Gagal", callback_data=f"fail_{oid}")]
            ])
        )

        await update.message.reply_text("⏳ Diproses", reply_markup=InlineKeyboardMarkup([[btn_menu()]]))
        u.clear()

# ================= ADMIN =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    oid = q.data.split("_")[1]
    if oid not in orders:
        return

    data = orders[oid]
    user_id = data["user"]

    status = "SELESAI" if q.data.startswith("done_") else "GAGAL"
    icon = "✅" if status=="SELESAI" else "❌"

    orders[oid]["status"] = status

    now = datetime.now().strftime("%d-%m-%Y %H:%M")

    history[user_id] = [
        f"{oid} | {rupiah(data['harga'])} | {icon} {status} | {now}"
        if h.startswith(oid) else h
        for h in history.get(user_id, [])
    ]

    await context.bot.send_message(user_id, f"{icon} Order {status}\n🆔 {oid}",
        reply_markup=InlineKeyboardMarkup([[btn_menu()]])
    )

    await q.edit_message_caption(f"{oid}\n{status}")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("online", online))
app.add_handler(CommandHandler("offline", offline))
app.add_handler(CallbackQueryHandler(admin, pattern="^(done_|fail_)"))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle))

print("BOT FINAL PERFECT 🔥")
keep_alive()
app.run_polling()
