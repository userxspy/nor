import os
import qrcode
import asyncio
from datetime import datetime, timedelta
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from hydrogram.errors import ListenerTimeout
from info import (IS_PREMIUM, PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME, 
                  UPI_ID, UPI_NAME, ADMINS, temp)
from Script import script
from database.users_chats_db import db
from utils import is_premium

# --- USER COMMANDS ---

@Client.on_message(filters.command('plan') & filters.private)
async def plan_cmd(client, message):
    if not IS_PREMIUM:
        return await message.reply('Premium feature was disabled by admin')
    btn = [[
        InlineKeyboardButton('Activate Trial', callback_data='activate_trial')
    ],[
        InlineKeyboardButton('Activate Plan', callback_data='activate_plan')
    ]]
    await message.reply(script.PLAN_TXT.format(PRE_DAY_AMOUNT, RECEIPT_SEND_USERNAME), reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('myplan') & filters.private)
async def myplan_cmd(client, message):
    if not IS_PREMIUM:
        return await message.reply('Premium feature was disabled by admin')
    mp = db.get_plan(message.from_user.id)
    if not await is_premium(message.from_user.id, client):
        btn = [[
            InlineKeyboardButton('Activate Trial', callback_data='activate_trial'),
            InlineKeyboardButton('Activate Plan', callback_data='activate_plan')
        ]]
        return await message.reply('You dont have any premium plan, please use /plan to activate plan', reply_markup=InlineKeyboardMarkup(btn))
    await message.reply(f"You activated {mp['plan']} plan\nExpire: {mp['expire'].strftime('%Y.%m.%d %H:%M:%S')}")

# --- ADMIN COMMANDS (Premium Management) ---

@Client.on_message(filters.command('add_prm') & filters.user(ADMINS))
async def add_prm(bot, message):
    if not IS_PREMIUM:
        return await message.reply('Premium feature was disabled')
    try:
        _, user_id, d = message.text.split(' ')
        d = int(d[:-1]) # Extract days from '1d', '7d'
    except:
        return await message.reply('Usage: /add_prm user_id 1d')
    
    try:
        user = await bot.get_users(user_id)
        ex = datetime.now() + timedelta(days=d)
        mp = db.get_plan(user.id)
        mp.update({'expire': ex, 'plan': f'{d} days', 'premium': True})
        db.update_plan(user.id, mp)
        await message.reply(f"Given premium to {user.mention}\nExpire: {ex.strftime('%Y.%m.%d %H:%M:%S')}")
        await bot.send_message(user.id, f"Your now premium user\nExpire: {ex.strftime('%Y.%m.%d %H:%M:%S')}")
    except Exception as e:
        await message.reply(f'Error: {e}')

@Client.on_message(filters.command('rm_prm') & filters.user(ADMINS))
async def rm_prm(bot, message):
    try:
        _, user_id = message.text.split(' ')
        user = await bot.get_users(user_id)
        mp = db.get_plan(user.id)
        mp.update({'expire': '', 'plan': '', 'premium': False})
        db.update_plan(user.id, mp)
        await message.reply(f"{user.mention} is no longer premium user")
    except Exception as e:
        await message.reply(f'Error: {e}')

# --- CALLBACK HANDLERS (Trial & Payment) ---

@Client.on_callback_query(filters.regex(r"^(activate_trial|activate_plan)"))
async def premium_callback_handler(client, query):
    if query.data == 'activate_trial':
        mp = db.get_plan(query.from_user.id)
        if mp.get('trial'):
            return await query.message.edit('You already used trial, use /plan to activate plan')
        ex = datetime.now() + timedelta(hours=1)
        mp.update({'expire': ex, 'trial': True, 'plan': '1 hour', 'premium': True})
        db.update_plan(query.from_user.id, mp)
        await query.message.edit(f"Congratulations! Your activated trial for 1 hour\nExpire: {ex.strftime('%Y.%m.%d %H:%M:%S')}")

    elif query.data == 'activate_plan':
        q = await query.message.edit('How many days you need premium plan?\nSend days as number (e.g. 7)')
        try:
            msg = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=300)
            days = int(msg.text)
        except (ListenerTimeout, ValueError):
            return await q.edit('Invalid input or Timeout!')

        amount = days * PRE_DAY_AMOUNT
        note = f'{days} days premium for {query.from_user.id}'
        upi_uri = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amount}&cu=INR&tn={note}"
        
        qr = qrcode.make(upi_uri)
        path = f"qr_{query.from_user.id}.png"
        qr.save(path)
        
        await q.delete()
        await query.message.reply_photo(path, caption=f"Amount: {amount} INR\nScan & Pay, then send Receipt Photo here.")
        os.remove(path)

        try:
            receipt = await client.listen(chat_id=query.message.chat.id, user_id=query.from_user.id, timeout=600)
            if receipt.photo:
                await client.send_photo(RECEIPT_SEND_USERNAME, receipt.photo.file_id, note)
                await receipt.reply("Receipt sent! Please wait for admin approval.")
        except ListenerTimeout:
            await query.message.reply("Time out! If paid, send receipt to Support.")
