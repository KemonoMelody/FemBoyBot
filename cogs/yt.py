import discord, requests
from discord.ext import commands
from ytmusicapi import YTMusic

class Ytm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("yt.py was loaded.")

    @commands.command(name="music")
    async def ytm(self, ctx, *, args):
        async with ctx.typing():
            ytmusic = YTMusic()
            results = ytmusic.search(args)
            results = [r for r in results if r.get('resultType') in ('artist', 'album', 'song')]

            if not results:
                await ctx.send("**⛔ No se encontraron resultados.**")
                return

            result = results[0]
            resulttype = result.get("resultType", "")
            embeds = []

            # ========== ARTISTA ==========
            if resulttype == "artist":
                artist_name = result["artists"][0]['name']
                artist_id = result["artists"][0]['id']
                artist_url = f"https://music.youtube.com/channel/{artist_id}"

                artist_info = ytmusic.get_artist(artist_id)

                embed = discord.Embed(
                    title=artist_name,
                    url=artist_url,
                    description=f"Suscriptores: {artist_info.get('subscribers', 'Desconocido')}",
                    colour=0xff0033
                )
                if artist_info.get("thumbnails"):
                    embed.set_thumbnail(url=artist_info["thumbnails"][-1]["url"])

                embeds.append(embed)

            # ========== ÁLBUM ==========
            elif resulttype == "album":
                album_title = result["title"]
                album_id = result["browseId"]
                album_url = f"https://music.youtube.com/browse/{album_id}"
                artist = result["artists"][0]
                artist_name = artist["name"]
                artist_id = artist["id"]

                embed = discord.Embed(
                    title=album_title,
                    url=album_url,
                    colour=0xff0033
                )
                embed.set_author(
                    name=artist_name,
                    url=f"https://music.youtube.com/channel/{artist_id}"
                )
                if result.get("thumbnails"):
                    embed.set_thumbnail(url=result["thumbnails"][-1]["url"])

                album = ytmusic.get_album(album_id)
                tracks = album.get("tracks", [])

                if not tracks:
                    embed.description = "⚠️ No se encontraron canciones en este álbum."
                else:
                    for track in tracks:
                        title = track["title"]
                        vid = track.get("videoId")
                        duration = track.get("duration", "Desconocido")
                        views = track.get("views", "").replace("plays", "").strip() if track.get("views") else ""
                        trackno = track.get("trackNumber", "?")

                        # Evasión del Defective By Design de YouTube.
                        if track.get("videoType") == "MUSIC_VIDEO_TYPE_OMV":
                            query = f"{artist_name} {album_title} {title}"
                            search_audio = ytmusic.search(query=query, filter="songs")
                            if search_audio:
                                audio = search_audio[0]
                                vid = audio.get("videoId", vid)
                                duration = audio.get("duration", duration)
                                views = audio.get("views", views)

                        if vid:
                            embed.add_field(
                                name=f"{trackno}. {title}",
                                value=f"[▶️](https://music.youtube.com/watch?v={vid}) • {duration} • {views}",
                                inline=False
                            )

                embeds.append(embed)

            # ========== CANCIÓN ==========
            elif resulttype == "song":
                title = result["title"]
                video_id = result["videoId"]
                duration = result.get("duration", "")
                artist_name = result["artists"][0]["name"]
                artist_id = result["artists"][0]["id"]

                embed = discord.Embed(
                    title=title,
                    url=f"https://music.youtube.com/watch?v={video_id}",
                    description=f"[▶️ Escuchar en YouTube Music](https://music.youtube.com/watch?v={video_id}) • {duration}",
                    colour=0xff0033
                )
                embed.set_author(
                    name=artist_name,
                    url=f"https://music.youtube.com/channel/{artist_id}"
                )
                if result.get("thumbnails"):
                    embed.set_thumbnail(url=result["thumbnails"][-1]["url"])

                embeds.append(embed)

            # ========== SIN RESULTADO VÁLIDO ==========
            else:
                await ctx.send("**⛔ No se encontraron resultados.**")
                return

            # ========== ENVÍO FINAL ==========
            if not embeds:
                await ctx.send("**⛔ Error al generar embed.**")
                return

            await ctx.send(embed=embeds[0])

def setup(bot):
    bot.add_cog(Ytm(bot))
