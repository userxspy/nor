import re
import math
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import temp, PICS, script, TUTORIAL
from utils import get_poster, get_settings, save_group_settings, is_check_admin

# --- IMDB CAPTION GENERATOR ---
async def get_imdb_cap(search, file_name, settings):
    imdb = await get_poster(search, file=file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url']
        )
    else:
        cap = f"<b>💭 ʜᴇʏ,\n♻️ ʜᴇʀᴇ ɪ ꜰᴏᴜɴᴅ ꜰᴏʀ ʏᴏᴜʀ sᴇᴀʀᴄʜ {search}...</b>"
    return cap, imdb

# --- IMDB SETTINGS CALLBACK HANDLERS ---
@Client.on_callback_query(filters.regex(r"^(imdb_setgs|set_imdb|default_imdb|tutorial_setgs|set_tutorial|default_tutorial)"))
async def imdb_settings_manager(client, query):
    data = query.data
    userid = query.from_user.id
    
    # Extract Group ID
    try:
        grp_id = int(data.split("#")[1])
    except:
        return await query.answer("Invalid Group ID!")

    # Check Admin Permission
    if not await is_check_admin(client, grp_id, userid):
        return await query.answer("You are not admin in this group.", show_alert=True)

    # 1. IMDb Template Settings
    if data.startswith("imdb_setgs"):
        settings = await get_settings(grp_id)
        btn = [[
            InlineKeyboardButton('Set IMDb template', callback_data=f'set_imdb#{grp_id}')
        ],[
            InlineKeyboardButton('Default IMDb template', callback_data=f'default_imdb#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Select IMDb option\n\nCurrent template:\n{settings["template"]}', reply_markup=InlineKeyboardMarkup(btn))

    elif data.startswith("set_imdb"):
        m = await query.message.edit('Send IMDb template with formats...')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=userid)
        await save_group_settings(grp_id, 'template', msg.text)
        await m.delete()
        btn = [[InlineKeyboardButton('Back', callback_data=f'imdb_setgs#{grp_id}')]]
        await query.message.reply('Successfully changed template', reply_markup=InlineKeyboardMarkup(btn))

    elif data.startswith("default_imdb"):
        await save_group_settings(grp_id, 'template', script.IMDB_TEMPLATE)
        btn = [[InlineKeyboardButton('Back', callback_data=f'imdb_setgs#{grp_id}')]]
        await query.message.edit('Successfully changed template to default', reply_markup=InlineKeyboardMarkup(btn))

    # 2. Tutorial Settings
    elif data.startswith("tutorial_setgs"):
        settings = await get_settings(grp_id)
        btn = [[
            InlineKeyboardButton('Set tutorial link', callback_data=f'set_tutorial#{grp_id}')
        ],[
            InlineKeyboardButton('Default tutorial link', callback_data=f'default_tutorial#{grp_id}')
        ],[
            InlineKeyboardButton('Back', callback_data=f'back_setgs#{grp_id}')
        ]]
        await query.message.edit(f'Current tutorial link:\n{settings["tutorial"]}', reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    elif data.startswith("set_tutorial"):
        m = await query.message.edit('Send new tutorial link...')
        msg = await client.listen(chat_id=query.message.chat.id, user_id=userid)
        await save_group_settings(grp_id, 'tutorial', msg.text)
        await m.delete()
        btn = [[InlineKeyboardButton('Back', callback_data=f'tutorial_setgs#{grp_id}')]]
        await query.message.reply('Successfully changed tutorial link', reply_markup=InlineKeyboardMarkup(btn))

    elif data.startswith("default_tutorial"):
        await save_group_settings(grp_id, 'tutorial', TUTORIAL)
        btn = [[InlineKeyboardButton('Back', callback_data=f'tutorial_setgs#{grp_id}')]]
        await query.message.edit('Successfully changed tutorial link to default', reply_markup=InlineKeyboardMarkup(btn))
