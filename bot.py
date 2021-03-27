import asyncio
import discord
from src.response import ResponseGenerator
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

intents = discord.Intents(messages=True, guilds=True, typing = False, presences = False, members=False, reactions=True)
client = discord.AutoShardedClient(intents=intents, chunk_guilds_at_startup=False)
config_general=json.loads(open("config-bot.json","r").read())

model=ResponseGenerator("https://miyuu-serve.herokuapp.com/v1/models/jade:predict")

@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+str(client.user.id)+') | Connected to '+str(len(client.guilds))+' servers')
    print('--------')
    print("Discord.py verison: " + discord.__version__)
    print('--------')
    print(str(len(client.shards))+" shard(s)")
    
@client.event
async def on_raw_reaction_add(payload):
    loop = asyncio.get_event_loop()
    if str(payload.emoji) == "❌":
        channel=await client.fetch_channel(payload.channel_id)
        message=await channel.fetch_message(payload.message_id)
        await message.edit(content="Loading...")
        await message.clear_reactions()
        out = await loop.run_in_executor(ThreadPoolExecutor(), model.update_resp, message.mentions[0].id, payload.message_id, False)
        await message.edit(content=out.replace("@everyone","").replace("@here", ""))
    
@client.event
async def on_message(message):
    loop = asyncio.get_event_loop()
    if message.author.bot == False and message.guild != None:
        if message.content.lower().startswith(config_general["prefix"]):
            message.content=message.content[len(config_general["prefix"]):]
            if message.content == "-h":
                logs=model.register(message.author.id, time.time())
                await message.reply("History:\n> "+"\n> ".join(logs["history"])+f"\nLast seen: {datetime.fromtimestamp(logs['timestamp'])}")
            elif message.content == "-r":
                model.reset(message.author.id)
                await message.reply("Successfully reset your history with JaAyakade")
            else:
                print(message.content)
                msg=await message.reply("Loading...")
                async with message.channel.typing():
                    out = await loop.run_in_executor(ThreadPoolExecutor(), model.response, message.author, message.content, msg.id, True)
                await msg.edit(content=out.replace("@everyone","").replace("@here", ""))

client.run(config_general["token"])