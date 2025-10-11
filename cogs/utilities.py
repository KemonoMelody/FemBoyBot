import discord, urllib, requests
from discord.ext import commands
import re
import os
from dotenv import load_dotenv

load_dotenv()

weathertoken = os.getenv("WEATHER-TOKEN")

def linkify_definition(text: str) -> str:
    """
    Urban Dic Hyperlinks
    """
    pattern = r'\[(.+?)\]'

    def replacer(match):
        term = match.group(1)
        safe_term = urllib.parse.quote(term)  # encode seguro para URL
        return f'[{term}](https://www.urbandictionary.com/define.php?term={safe_term})'

    return re.sub(pattern, replacer, text, flags=re.S)

class Utilities(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('utilities.py was loaded.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("rpl"):
            channel = self.bot.get_channel(message.channel.id)
            msg = await channel.history(limit=50).flatten()
            args0 = message.content.split('/')
            query = args0[1]
            repl = args0[2]
            # msg0 = msg[0]
            # print(msg)
            if message.author.bot is True:
                None
            elif len(query) == 0:
                await channel.send('No puedo reemplazar textos que no existen.')
            else:
                i = 0
                for arg in msg:
                    i += 1
                    # if msg[i].content.startswith('f,'):
                    #    continue
                    if str(query) in msg[i].content:
                        message = {
                            "name" : msg[i].author.display_name,
                            "content" : msg[i].content,
                        }
                        await channel.send(f'{message["name"]}: {message["content"].replace(query, repl)}')
                        break

    @commands.command(aliases=['urbandictionary', 'urbandic', 'urban']) # creates a prefixed command
    async def _urban(self, ctx, *, args): # all methods now must have both self and ctx parameters
        async with ctx.typing():
            defargs = urllib.parse.quote(args)
            urbanlink = f'''https://api.urbandictionary.com/v0/define?term={defargs}'''
            response = requests.get(urbanlink)
            data = response.json()['list']
            if not data:
                await ctx.send("❌ No se encontraron resultados.")
                return
            embeds = []
            for i, entry in enumerate(data, start=1):
                word = entry['word']
                definition = linkify_definition(entry['definition'])
                example = linkify_definition(entry['example'])

                embed = discord.Embed(
                    title = 'Definition URL',
                    url = entry['permalink'],
                    description = definition,
                    colour = 0xef4210
                )
                embed.add_field(name='Example', value = example, inline=False)
                embed.set_author(name = word)
                embed.set_footer(text=f"ℹ️ Published on {entry['written_on']} by {entry['author']} \n👍 {entry['thumbs_up']} 👎 {entry['thumbs_down']}\n\n{i}/{len(data)}")
                embeds.append(embed)


            # Crear view con botones
            class Paginator(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=60)  # se desactiva después de 60s
                    self.index = 0

                @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
                async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index > 0:
                        self.index -= 1
                        await interaction.response.edit_message(embed=embeds[self.index], view=self)


                @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
                async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index < len(embeds) - 1:
                        self.index += 1
                        await interaction.response.edit_message(embed=embeds[self.index], view=self)

            # Mandar primer embed con botones
            view = Paginator()

            await ctx.send(embed=embeds[0], view=view)

    @commands.command(aliases=['weather'])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def _weather(self, ctx, *, args):
        global weathertoken
        from cogs.mods.ISO3166 import countryname
        async with ctx.typing():
            complete_url = f'http://api.openweathermap.org/data/2.5/weather?appid={weathertoken}&q={args}&lang=es'
            response = requests.get(complete_url)
            x = response.json()
            if x["cod"] != "404":
                v = x["sys"]
                w = x["wind"]
                y = x["main"] # Copypaste del bot anterior, en proceso de reescritura
                z = x["weather"]
                country = countryname(v['country'])
                weather_description = z[0]["description"]
                await ctx.send(f'''
:flag_{v['country'].lower()}: | **__Clima actual de {x['name']}, {country}:__**
**Clima:** {weather_description.capitalize()}
**Temperatura:** {round(y['temp'] - 273.15)} °C | {round((y['temp'] - 273.15) * 1.8 + 32.00)} °F | {y['temp']} K
**Nubes:** {x['clouds']['all']}%
**Humedad:** {y['humidity']}%
**Viento:** Velocidad: {w['speed']} m/s | Dirección: {w['deg']}°
**Presión Atmosférica:** {y['pressure']} hPa
''')
            else:
                await ctx.send("**⛔ Ciudad no encontrada.**")
    @_weather.error
    async def weather_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send('**f.weather [ciudad]**: Obten el clima de la ciudad que desees.')
        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send('**⛔ Cooldown** `Intenta de nuevo en {:.2f} segundos.`'.format(error.retry_after))
        if isinstance(error, discord.ext.commands.errors.CommandInvokeError):
            await ctx.send(f'**⛔ Se ha producido un error: `{str(error)}`.**')

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utilities(bot)) # add the cog to the bot
