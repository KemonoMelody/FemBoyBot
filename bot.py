import discord
import logging
from os import getenv, listdir
from discord.ext.commands import Bot
from discord.gateway import DiscordWebSocket


# Setup logger
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
))
logger.addHandler(handler)


# Parchear indicador de estado movil en identify
class MyDiscordWebSocket(DiscordWebSocket):
    async def send_as_json(self, data):
        if data.get("op") == self.IDENTIFY and "d" in data:
            data["d"]["properties"].update({
                "browser": "Discord Android",
                "device": "Discord Android"
            })
        await super().send_as_json(data)


DiscordWebSocket.from_client = MyDiscordWebSocket.from_client


# Bot variables
adminid = int(getenv("PRIVILEGED-USERID"))
intents = discord.Intents.default()
intents.message_content = True
bot = Bot(command_prefix=['F.', 'f.'], intents=intents)
allowed_mentions = discord.AllowedMentions(
    users=False, everyone=False, roles=False
)
for filename in listdir("./cogs"):
    if filename != "__init__.py":
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


async def autorizar_comando_admin(ctx) -> bool:
    if ctx.message.author.id == adminid:
        return True
    await ctx.send("**⛔ Sólo mi dueño puede usar ese comando.**")
    return False


@bot.remove_command('help')
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")


@bot.command()
async def ping(ctx):
    start = discord.utils.utcnow()
    msg = await ctx.send("calculando...")
    end = discord.utils.utcnow()
    duration = round((end - start).total_seconds() * 1000)
    content = f"✅ {duration}ms"
    await msg.edit(content=content)


@bot.command(aliases=['csplaying', 'csp'])
async def changestatus(ctx, *, name="with myself"):
    if await autorizar_comando_admin(ctx):
        await bot.change_presence(activity=discord.Game(name))
        await ctx.send(f'✅ Estado del bot cambiado a "Jugando a **{name}**"')


@bot.command(aliases=['load', 'enable', 'en'])
async def cogload(ctx, extension):
    if await autorizar_comando_admin(ctx):
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'✅ Se ha activado el módulo **{extension}.py**')


@bot.command(aliases=['unload', 'disable', 'dis'])
async def cogunload(ctx, extension):
    if await autorizar_comando_admin(ctx):
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'✅ Se ha desactivado el módulo **{extension}.py**')


@bot.command(aliases=['reload', 're'])
async def cogreload(ctx, extension):
    if await autorizar_comando_admin(ctx):
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'✅ Se ha recargado el módulo **{extension}.py**')


bot.run(getenv("DISCORD-TOKEN"))
