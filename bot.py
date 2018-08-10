import os
import discord
import asyncio
import markovify
import random
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = discord.Client()
text_model = {}

NIETZSCHE_QUOTES = [
    "That which does not kill us makes us stronger.",
    "He who fights with monsters might take care lest he thereby become a monster. And if you gaze for long into an abyss, the abyss gazes also into you.",
    "Without music, life would be a mistake.",
    "There are no facts, only interpretations.",
    "The man of knowledge must be able not only to love his enemies but also to hate his friends.",
    "We should consider every day lost on which we have not danced at least once.",
    "Man is the cruelest animal.",
    "Is man merely a mistake of God's? Or God merely a mistake of man?",
    "The thought of suicide is a great consolation: by means of it one gets through many a dark night.",
    "Be careful, lest in casting out your demon you exorcise the best thing in you.",
    "A good writer possesses not only his own spirit but also the spirit of his friends.",
    "Art is the proper task of life.",
    "What does your conscience say? — 'You should become the person you are'.",
    "The pure soul is a pure lie.",
    "That for which we find words is something already dead in our hearts",
    "I have forgotten my umbrella.",
]

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

async def create_gold_role(server):
    logger.info('Checking if gold role exists in {}'.format(server))
    gold_name = 'Mr. Data Gold'
    role_names = [r.name for r in server.roles]
    top_role_index = len(role_names) + 1
    if gold_name in role_names:
        logger.info("Gold role already available in {}.".format(server))
        return
    fields = {
        "name": gold_name,
        "colour": discord.Color.gold(),
        "position": top_role_index
    }
    logger.info('Creating gold role in {}'.format(server))
    await client.create_role(server, **fields)
    return top_role_index


async def set_gold_role_to_top(server, role, position):
    logger.info('setting gold role to top for server {}'.format(server))
    client.edit_role(server, role, position=position)


async def change_role_colour(server):
    top_index = await create_gold_role(server)
    role = discord.utils.get(server.roles, name='Mr. Data Gold')
    logger.info('Found gold role, trying to add to self at server: {}'.format(server))
    try:
        await client.add_roles(server.me, role)
    except Exception as e:
        logger.exception(e)
    logger.info('Succesfully added role')
    await set_gold_role_to_top(server, role, top_index)
    logger.info('succesfully set gold role to top')

@client.event
async def on_ready():
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    coroutines = []
    try:
        for s in client.servers:
            logger.info('I am in {}'.format(s))
            logger.info('attempting to update role...')
            coroutines.append(change_role_colour(s))
        coroutines.append(client.change_presence(game=discord.Game(name='The Oregon Trail')))
    except Exception as e:
        logger.exception(e)
    await asyncio.gather(*coroutines)


@client.event
async def on_server_join(server):
    logger.info('Joined server: {}'. format(server))


@client.event
async def on_member_join(member):
    try:
        logger.info('A member joined')
        server = member.server
        fmt = "Welcome to {0.name}! {1}"
        await client.send_message(server, fmt.format(server, random_welcome_message()))
    except Exception as e:
        logger.exception(e)


@client.event
async def on_message(message):
    # TODO: See if there's a way to use `before` `after` and `around` 
    # of the `logs_from` method so messages are more random
    if message.author == client.user:
        # lmao don't invoke yourself m8
        return
    
    if message.content.startswith('!neechee'):
        quote = NIETZSCHE_QUOTES[random.randint(0, len(NIETZSCHE_QUOTES))]
        await client.send_message(message.channel, quote)

    if message.content.startswith('!topic'):
        await client.send_message(message.channel, message.channel.topic)
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


def run_bot(attempt=0, max_retries=5):
    attempt += 1
    if attempt < max_retries:
        try:
            client.run(os.environ['DISCO_TOKEN'])
        except Exception as e:
            logger.exception('Something went wrong!')
            time.sleep(5)
            run_bot(attempt)
    else:
        logger.error('Max retries met! Shutting down...')

run_bot()
