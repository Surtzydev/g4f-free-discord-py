import discord,time,json,poe,random
import aiohttp
from discord import app_commands
from discord.ext import commands
import asyncio

with open('config.json','r',encoding='utf-8') as f:
    config=json.load(f)

token=config['token']

bot=commands.Bot(command_prefix='!',intents=discord.Intents.all(),proxy="http://127.0.0.1:7890")

surtzy=[
'gpt-4',
'gpt-3.5-turbo',
'claude-v1',
'claude-instant',
'claude-instant-100k',
'sage'
]

models={
'gpt-4':'beaver',
'gpt-3.5-turbo':'chinchilla',
'claude-v1':'a2_2',
'claude-instant':'a2',
'claude-instant-100k':'a2_100k',
'sage':'capybara'
}

@bot.event
async def on_ready():
    print(f"{bot.user} connected successfully") #bot is online
    invite_link=discord.utils.oauth_url(bot.user.id,permissions=discord.Permissions(),scopes=("bot","applications.commands")) #generate invite link
    synced=await bot.tree.sync() #sync slash commands
    print(f'{len(synced)} commands active')
    print(f"Invite link:\n{invite_link}")

@bot.command(name='test',description='Returns pong')
async def test(ctx):
    await ctx.send('pong')

@bot.tree.command(name='help',description='Available models and commands')
async def help(interaction:discord.Interaction):
    embed=discord.Embed(title='Help Center',description='available models:\n```asm\n'+('\n'.join(surtzy))+'\n```\ncommands:\n```asm\n/help\n/create <prompt> <model>\n```',color=8716543)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='create',description='Generate a response using a language model')
@app_commands.describe(prompt='prompt',model='model')
async def create(interaction:discord.Interaction,prompt:str,model:str='gpt-4'):
    try:
        print(interaction.user.name,prompt,model)
        await interaction.response.defer(ephemeral=False,thinking=True) #wait signal
        base=f'*model*: `{model}`\n'
        system='system: your response will be displayed on Discord. Use highlight language like ```py ...```, * or ** ||\n prompt: '
        client=None
        attempts=0
        while attempts<=10:
            try:
                attempts+=1
                token=random.choice(open('tokens.txt','r').read().splitlines()) #get random token
                client=poe.Client(token.split(':')[0],proxy="http://127.0.0.1:7890") #initialize Poe client
                base+='\n'
                response=client.send_message(models[model],system+prompt,with_chat_break=True) #send message
                if client.get_remaining_messages(models[model])==None or client.get_remaining_messages(models[model])==0:
                    continue
                await interaction.followup.send(base)
                for token in response:
                    base+=token['text_new']
                    base=base.replace('Discord Message:','')
                    await interaction.edit_original_response(content=base)
                break
            except Exception as e:
                print("Token error:",e)
        if attempts>10:
            print("Replace used tokens")
    except Exception as e:
        await interaction.response.send_message(f'Error: {e}')

bot.run(token)