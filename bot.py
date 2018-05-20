import os
import discord
import asyncio
import markovify
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = discord.Client()
text_model = {}

def should_talk():
    lucky_number = 1
    roll = random.randint(1,20)
    return roll == lucky_number


def random_welcome_message():
    messages = [
        'Did you know that life is meaningless?',
        'Let us rejoice.',
        'Bend over.',
        'That is what a call I very well put together human being',
        'Incredible entrance although, it means nothing.',
        'When will this end?',
        'Praise the sun!',
    ]
    random_index = random.randint(0, len(messages))
    return messages[random_index]


async def change_role_color(server, role, color):
    logger.info('Changing role {} at server {} with color {}'.format(role, server, color))
    await client.edit_role(server, role, {'color': color})

@client.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    coroutines = []
    for s in client.servers:
        logger.info('I am in {}'.format(s))
        logger.info('attempting to update role...')
        role = discord.utils.get(s.roles, name='Mr. Data')
        logger.info('Found role {}'.format(role))
        coroutines.append(change_role_color(s, role, discord.Colour.gold()))
    coroutines.append(client.change_presence(game=discord.Game(name='The Oregon Trail')))
    await asyncio.gather(*coroutines)


@client.event
async def on_server_join(server):
    logger.info('Joined server: {}'. format(server))


@client.event
async def on_member_join(member):
    server = member.server
    fmt = "Welcome {0.mention} to {1.name}! {2}"
    await client.send_message(server.default_channel, fmt.format(member, server, random_welcome_message()))


@client.event
async def on_message(message):
    # TODO: See if there's a way to use `before` `after` and `around` 
    # of the `logs_from` method so messages are more random
    if message.author == client.user:
        # lmao don't invoke yourself m8
        return

    if client.user.mentioned_in(message):
        try:
            sentences = u''
            async for log in client.logs_from(message.channel, limit=2000):
                sentences += log.content + '\n'
            text_model = markovify.Text(sentences)
            s = text_model.make_short_sentence(140)
            if not s or not len(s) > 0:
                s = "🤷"
            await client.add_reaction(message, '🤖')
            await client.send_message(message.channel, s)
        except Exception as e:
            logger.error("Shat self: {}".format(e))           
            await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")
            return

    if message.content.startswith('!bottalk'):
        user_id = message.content.split()[1]
        user_id = ''.join([c for c in user_id if c.isdigit()])
        sentences = u''
        async for log in client.logs_from(message.channel, limit=2000):
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
        except Exception as e:
            logger.error("Shat self: {}".format(e))
            await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")
            return
    if should_talk():
        try:
            sentences = u''
            async for log in client.logs_from(message.channel, limit=2000):
                sentences += log.content + '\n'
            text_model = markovify.Text(sentences)
            s = text_model.make_short_sentence(140)
            if not s or not len(s) > 0:
                s = "🤷"
            await client.send_message(message.channel, s)
        except Exception as e:
            logger.error("Shat self: {}".format(e))
            await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")
            return

    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

client.run(os.environ['DISCO_TOKEN'])
