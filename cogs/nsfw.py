import discord
import random
import urllib
import requests
import os
from hurry.filesize import size, si
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Carga variables desde el archivo .env

tagblacklist = os.getenv("TAG-BLACKLIST")
e621login = os.getenv("E621-LOGIN")
e621token = os.getenv("E621-TOKEN")
gelboorutoken = os.getenv("GELBOORU-TOKEN")
gelbooruuser = os.getenv("GELBOORU-USER")

nsfwerror = '**🔞 Comando NSFW, requiere un canal marcado como NSFW en sus configuraciones.**'

class Nsfw(commands.Cog): # create a class for our cog that inherits from commands.Cog
    # this class is used to create a cog, which is a module that can be added to the bot

    def __init__(self, bot): # this is a special method that is called when the cog is loaded
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('nsfw.py was loaded.')

# f.e621
    @commands.command(name='e621')
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def e621(self, ctx, *, tags):
        global nsfwerror, tagblacklist, e621login, e621token
        async with ctx.typing():
            if ctx.message.channel.is_nsfw() is False:
                await ctx.send(nsfwerror)
                return
            deftags = urllib.parse.quote(tags)
            apiurl = f'https://e621.net/posts.json?tags={deftags}&limit=100&login={e621login}&api_key={e621token}'
            headers = {'User-Agent': f'{e621login}/1.0'}
            response = requests.get(apiurl, headers=headers)
            w = response.json()['posts']
            if not w:
                await ctx.send('**⛔ No se encontraron resultados.**')
                return
            pages = []
            for i, post in enumerate(w, start=1):
                getfile = post['file']
                getpreview = post['preview']
                getscore = post['score']
                def tags(tagset: str) -> str:
                    gettags = post['tags']
                    maximum = {
                        'artist' : 85,
                        'copyright' : 170,
                        'character' : 340,
                        'species' : 170,
                        'general' : 935
                        }
                    tagfilter = [tag for tag in gettags[tagset] if tag not in tagblacklist.split()]
                    tagcc = ' '.join(tagfilter)
                    if len(tagcc) > maximum[tagset]:
                        tagcc = tagcc[:maximum[tagset]] + '...'
                    return tagcc
                msg = f'''
```diff
+ Artist
{tags('artist')}
``````diff
- Copyright
{tags('copyright')}
``````md
# Character
{tags('character')}
``````cs
# Species
{tags('species')}
``````
# General
{tags('general')}
````Score: {getscore['total']}` `Favcount: {post['fav_count']}` `Rating: {post['rating']}` `Size: {getfile['width']}x{getfile['height']} {size(getfile['size'], system=si)}B` <https://e621.net/posts/{post['id']}>
{str(getfile['url'].replace(' ', '%2B'))}
`{i}/{len(w)}`'''
                pages.append(msg)

            # Crear view con botones
            class Paginator(discord.ui.View):
                def __init__(self, author, pages):
                    super().__init__(timeout=60)
                    self.author = author
                    self.pages = pages
                    self.index = 0

                async def update(self, interaction: discord.Interaction):
                    await interaction.response.edit_message(content=pages[self.index], view=self)

                async def interaction_check(self, interaction: discord.Interaction) -> bool:
                    """Este método se ejecuta antes de cualquier botón.
                    Si devuelve False, la interacción se rechaza."""
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message(
                            "**⛔ Sólo el autor del comando puede usar esos botones.**",
                            ephemeral=True
                        )
                        return False
                    return True

                @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
                async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index > 0:
                        self.index -= 1
                        await self.update(interaction)

                @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
                async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index < len(pages) - 1:
                        self.index += 1
                        await self.update(interaction)

                @discord.ui.button(label="🔀", style=discord.ButtonStyle.secondary)
                async def random(self, button: discord.ui.Button, interaction: discord.Interaction):
                    self.index = random.randint(0, len(pages))
                    await self.update(interaction)

                @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
                async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
                    for child in self.children:
                        child.disabled = True
                    await interaction.response.edit_message(view=self)
                    self.stop()

            # Mandar primer página
            view = Paginator(ctx.author, pages)
            await ctx.send(content=pages[0], view=view)
    @e621.error
    async def e621error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send('**⛔ Cooldown** `Intenta de nuevo en {:.2f} segundos.`'.format(error.retry_after))
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('**f.e621 [tags]**: Buscador de imagenes de e621.')

# f.gb
    @commands.command(name='gelbooru', aliases=['gb'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def gelbooru(self, ctx, *, tags):
        global nsfwerror, tagblacklist, gelboorutoken, gelbooruuser
        async with ctx.typing():
            if ctx.message.channel.is_nsfw() is False:
                await ctx.send(nsfwerror)
                return
            deftags = urllib.parse.quote(tags)
            apiurl = f'https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={deftags}&api_key={gelboorutoken}&user_id={gelbooruuser}&json=1'
            response = requests.get(apiurl)
            w = response.json()['post']
            if not w:
                await ctx.send('**⛔ No se encontraron resultados.**')
                return
            pages = []
            for i, post in enumerate(w, start=1):
                imgfile = post['file_url']
                tags = post['tags'][:1800]
                tagfilter = [tag for tag in tags.split() if tag not in tagblacklist.split()]
                taglist = ' '.join(tagfilter)
                if len(post['tags']) >= 1800:
                    taglist = taglist + '...'

                msg = f'''Tags:
```
{taglist}````Score: {post['score']}` `Rating: {post['rating']}` <https://gelbooru.com/index.php?page=post&s=view&id={post['id']}>
{str(imgfile.replace(' ', '%2B'))}
`{i}/{len(w)}`'''
                pages.append(msg)
            # Crear view con botones
            class Paginator(discord.ui.View):
                def __init__(self, author, pages):
                    super().__init__(timeout=60)
                    self.author = author
                    self.pages = pages
                    self.index = 0

                async def update(self, interaction: discord.Interaction):
                    await interaction.response.edit_message(content=pages[self.index], view=self)

                async def interaction_check(self, interaction: discord.Interaction) -> bool:
                    """Este método se ejecuta antes de cualquier botón.
                    Si devuelve False, la interacción se rechaza."""
                    if interaction.user.id != self.author.id:
                        await interaction.response.send_message(
                            "**⛔ Sólo el autor del comando puede usar esos botones.**",
                            ephemeral=True
                        )
                        return False
                    return True

                @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
                async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index > 0:
                        self.index -= 1
                        await self.update(interaction)

                @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
                async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
                    if self.index < len(pages) - 1:
                        self.index += 1
                        await self.update(interaction)

                @discord.ui.button(label="🔀", style=discord.ButtonStyle.secondary)
                async def random(self, button: discord.ui.Button, interaction: discord.Interaction):
                    self.index = random.randint(0, len(pages))
                    await self.update(interaction)

                @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
                async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
                    for child in self.children:
                        child.disabled = True
                    await interaction.response.edit_message(view=self)
                    self.stop()

            # Mandar primer página
            view = Paginator(ctx.author, pages)
            await ctx.send(content=pages[0], view=view)

    @gelbooru.error
    async def gelbooruerror(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send('**⛔ Cooldown** `Intenta de nuevo en {:.2f} segundos.`'.format(error.retry_after))
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f'**f.gelbooru | gb [tags]**: Buscador de imágenes de Gelbooru.')
#        if isinstance(error, commands.errors.CommandInvokeError):
#            await ctx.send(f'**⛔ Se ha producido un error: `{str(error)}`.**\nℹ️ Si el error persiste, intenta reportarlo con **f.report**.')

def setup(bot): # this is called by Pycord to setup the cog
    bot.add_cog(Nsfw(bot)) # add the cog to the bot
