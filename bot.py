import aiohttp
import asyncio
import discord
import logging
import os
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde el archivo .env

TOKEN = os.getenv("DISCORD-TOKEN")

logger = logging.getLogger('discord') # Logeo de errores
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# === MODIFICACIÓN ===

import sys
from discord.gateway import DiscordWebSocket, _log
from discord.ext.commands import Bot


async def identify(self):
    payload = {
        'op': self.IDENTIFY,
        'd': {
            'token': self.token,
            'properties': {
                '$os': sys.platform,
                '$browser': 'Discord Android',
                '$device': 'Discord Android',
                '$referrer': '',
                '$referring_domain': ''
            },
            'compress': True,
            'large_threshold': 250,
            'v': 3
        }
    }

    if self.shard_id is not None and self.shard_count is not None:
        payload['d']['shard'] = [self.shard_id, self.shard_count]

    state = self._connection
    if state._activity is not None or state._status is not None:
        payload['d']['presence'] = {
            'status': state._status,
            'game': state._activity,
            'since': 0,
            'afk': False
        }

    if state._intents is not None:
        payload['d']['intents'] = state._intents.value

    await self.call_hooks('before_identify', self.shard_id, initial=self._initial_identify)
    await self.send_as_json(payload)
    _log.info('Shard ID %s has sent the IDENTIFY payload.', self.shard_id)


DiscordWebSocket.identify = identify

# === MODIFICACIÓN ===

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=['F.', 'f.'], intents=intents)
allowed_mentions = discord.AllowedMentions(users=False, everyone=False, roles=False)

adminids = [995112245690388502]

@bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    start = discord.utils.utcnow()
    msg = await ctx.send("calculando...")
    end = discord.utils.utcnow()
    duration = (end - start).total_seconds() * 1000
    unidades = ['ms'] # A rellenar
    content = f'''
    Tiempo de respuesta: \n{int(duration)} ||`{random.choice(unidades)}`|| \nms

    '''
    await msg.edit(content = content)

@bot.command(aliases=['csplaying', 'csp'])
async def changestatus(ctx, *, name="with myself"):
    if ctx.message.author.id in adminids:
        await bot.change_presence(activity=discord.Game(name))
        await ctx.send(f'✅ Estado del bot cambiado a "Jugando a **{name}**"')
    else:
        await ctx.send('**⛔ Sólo el dueño del bot puede ejecutar este comando.**')


@bot.command(aliases=['load', 'enable', 'en'])
async def cogload(ctx, extension):
  if ctx.message.author.id not in adminids:
    await ctx.send('**⛔ Sólo mi dueño puede usar ese comando.')
  else:
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'✅ Se ha activado el módulo **{extension}.py**')

@bot.command(aliases=['unload', 'disable', 'dis'])
async def cogunload(ctx, extension):
  if ctx.message.author.id not in adminids:
    await ctx.send('**⛔ Sólo mi dueño puede usar ese comando.')
  else:
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'✅ Se ha desactivado el módulo **{extension}.py**')

@bot.command(aliases=['reload', 're'])
async def cogreload(ctx, extension):
  if ctx.message.author.id not in adminids:
    await ctx.send('**⛔ Sólo mi dueño puede usar ese comando.')
  else:
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'✅ Se ha recargado el módulo **{extension}.py**')

for filename in os.listdir('./cogs'):
  if filename != '__init__.py':
    if filename.endswith('.py'):
      bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)
