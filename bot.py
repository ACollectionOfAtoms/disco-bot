import os
import discord
import asyncio
import markovify
import random

client = discord.Client()
text_model = {}

def should_talk():
    lucky_number = 1
    roll = random.randint(1,20)
    return roll == lucky_number

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    await client.change_presence(game=discord.Game(name='Fortnite'))
    print('------')


@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Welcome {0.mention} to {1.name}!'
    await client.send_message(server, fmt.format(member, server))


@client.event
async def on_message(message):
    # TODO: See if there's a way to use `before` `after` and `around` 
    # of the `logs_from` method so messages are more random
    if message.author == client.user:
        # lmao don't invoke yourself m8
        return

    if client.user.mentioned_in(message):
        sentences = ''
        async for log in client.logs_from(message.channel, limit=2000):
            sentences += log.content + '\n'
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(140)
        if not s or not len(s) > 0:
            s = "🤷"
        await client.add_reaction(message, '🤖')
        await client.send_message(message.channel, s)

    if message.content.startswith('!bottalk'):
        user_id = message.content.split()[1]
        user_id = ''.join([c for c in user_id if c.isdigit()])
        sentences = ''
        async for log in client.logs_from(message.channel, limit=4000):
            if log.author.id == user_id:
                sentences += log.content + '\n'
        if len(sentences) == 0:
            await client.send_message(message.channel, "I got nothing 🤷")
            return
        try:
            text_model = markovify.Text(sentences)
            s = text_model.make_sentence(tries=50)
            if not s or len(s) < 1:
                s = "My apologies, I cannot quite grasp the essence of that user."
            await client.send_message(message.channel, s)
            return
        except KeyError:
            await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")
            return
    if should_talk():
        sentences = ''
        async for log in client.logs_from(message.channel, limit=2000):
            sentences += log.content + '\n'
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(140)
        if not s or not len(s) > 0:
            s = "🤷"
        await client.send_message(message.channel, s)
    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

client.run(os.environ['DISCO_TOKEN'])
