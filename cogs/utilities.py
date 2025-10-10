import discord, urllib, requests
from discord.ext import commands
import re

def linkify_definition(text: str) -> str:
    """
    Convierte [palabra] en enlaces clicables a Urban Dictionary,
    manejando espacios, saltos de línea y caracteres especiales.
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

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Utilities(bot)) # add the cog to the bot
