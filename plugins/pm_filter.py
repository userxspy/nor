import asyncio
import re
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import (IS_PREMIUM, FILMS_LINK, SUPPORT_GROUP, LOG_CHANNEL, 
                  ADMINS, DELETE_TIME, temp)
from database.users_chats_db import db
from database.ia_filterdb import get_search_results
from utils import (is_premium, get_size, is_check_admin, get_readable_time, 
                   get_settings, get_shortlink)

# इन फंक्शन्स को हमने दूसरी फाइल्स में बनाया है, यहाँ सिर्फ इम्पोर्ट कर रहे हैं
from plugins.imdb import get_imdb_cap
from plugins.navigation import BUTTONS, CAP

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_search(client, message):
    if message.text.startswith("/"):
        return
    stg = db.get_bot_sttgs()
    if not stg.get('PM_SEARCH'):
        return await message.reply_text('PM search was disabled!')
    
    # Auto Filter Trigger
    s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>", quote=True)
    await auto_filter(client, message, s)

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_search(client, message):
    user_id = message.from_user.id if message.from_user else 0
    if not user_id: return
    
    stg = db.get_bot_sttgs()
    if not stg.get('AUTO_FILTER'): return

    # Admin report and Links check logic (As it was before)
    if '@admin' in message.text.lower():
        # ... (Your existing admin report code)
        return
        
    if re.findall(r'https?://\S+|www\.\S+|t\.me/\S+|@\w+', message.text):
        if not await is_check_admin(client, message.chat.id, user_id):
            await message.delete()
            return await message.reply('Links not allowed!')

    # Search Trigger
    s = await message.reply(f"<b><i>⚠️ `{message.text}` searching...</i></b>")
    await auto_filter(client, message, s)

async def auto_filter(client, msg, s, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        search = re.sub(r"\s+", " ", re.sub(r"[-:\"';!]", " ", message.text)).strip()
        files, offset, total_results = await get_search_results(search)
        if not files:
            # Spell check logic call
            return await advantage_spell_chok(message, s)
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll

    req = message.from_user.id
    key = f"{message.chat.id}-{message.id}"
    
    # Global dictionaries update (from navigation.py)
    temp.FILES[key] = files
    BUTTONS[key] = search
    
    # --- Calling IMDb Logic from imdb.py ---
    cap, imdb = await get_imdb_cap(search, files[0]['file_name'], settings)
    CAP[key] = cap
    
    # --- Buttons Creation ---
    btn = []
    for file in files:
        btn.append([InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", 
                                         callback_data=f"file#{file['_id']}")])
    
    # Navigation Buttons (Next Page)
    if offset != "":
        btn.append([InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"),
                    InlineKeyboardButton(text="ɴᴇxᴛ »", callback_data=f"next_{req}_{key}_{offset}")])

    # Final Reply
    if imdb and imdb.get('poster'):
        await s.delete()
        await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
    else:
        await s.edit_text(cap, reply_markup=InlineKeyboardMarkup(btn))

async def advantage_spell_chok(message, s):
    # Your existing spell check logic remains here or can be moved to utils.py
    pass
