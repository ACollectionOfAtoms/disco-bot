import os
import discord
import asyncio
import markovify
import random
import time
import logging
import datetime
import re

from lib import nietzsche
from lib import weather
from lib import urban_dictionary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = discord.Client()
text_model = {}

async def send_message_without_tag(client, message, message_to_send):
    # tags like these are processed client side.
    # example: <@!4524524324> => @user_name
    tag_regex = '<@!?[0-9]*?>'
    message_without_tag = re.sub(tag_regex, 'discord user', message_to_send)
    await client.send_message(message.channel, message_without_tag)


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
        coroutines.append(client.change_presence(game=discord.Game(name='Hatoful Boyfriend: A School of Hope and White Wings')))
    except Exception as e:
        logger.exception(e)
    await asyncio.gather(*coroutines)


@client.event
async def on_server_join(server):
    logger.info('Joined server: {}'. format(server))


def random_float(float_a, float_b):
    return random.uniform(float_a, float_b)


def random_date(channel):
    """
    Return a random datetime for a given channel
    within the range of datetime.now(), and channel creation
    """
    min_date = channel.created_at.timestamp()
    max_date = datetime.datetime.now().timestamp()
    random_timestamp = random_float(min_date, max_date)
    return datetime.datetime.utcfromtimestamp(random_timestamp)

async def urban_dictionary_response(message):
    try:
        search_term = message.content.split()[1]
    except IndexError:
        await client.send_message(message.channel, "I need a search term.")
    try:
        definition = urban_dictionary.get_first_ud_definition(search_term)
    except Exception as e:
        logger.exception(e)
        logger.info('Could not get ud response!')
        await client.send_message(message.channel, "I've failed to get the definition! Check my error logs.")
        return
    if definition == '':
        await client.send_message(message.channel, 'Sorry, no results for that term.')
    await client.send_message(message.channel, definition)


async def weather_response(message):
        try:
            zip_code = message.content.split()[1]
        except IndexError:
            await client.send_message(message.channel, "I need an american zip code.")
            return
        if not zip_code.isdigit():
            await client.send_message(message.channel, "That does not look like a zip code!")
            return
        try:
            response = weather.get_weather_response(zip_code)
        except Exception as e:
            logger.exception(e)
            logger.info('Could not get weather data!')
            await client.send_message(message.channel, "Somethings not right... Please check error logs!")
            return
        parsed_response = weather.parse_weather_response(response)
        await client.send_message(message.channel, parsed_response)


async def nietzsche_response(message):
    quote = nietzsche.QUOTES[random.randint(0, len(nietzsche.QUOTES) - 1)]
    await client.send_message(message.channel, quote)


async def random_markov_response(message):
    try:
        sentences = u''
        random_dt = random_date(message.channel)
        async for log in client.logs_from(message.channel, limit=2000, after=random_dt):
            sentences += log.content + '\n'
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(180, tries=20)
        if not s or not len(s) > 0:
            s = "🤷"
        await client.add_reaction(message, '🤖')
        await send_message_without_tag(client, message, s)
    except Exception as e:
        logger.info("ERROR!: {}".format(e))
        logger.error("Shat self: {}".format(e))           
        await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")


async def user_markov_response(message):
    user_id = message.content.split()[1]
    user_id = ''.join([c for c in user_id if c.isdigit()])
    sentences = u''
    logger.info('looking up user {} for bottalk command'.format(user_id))
    user = await client.get_user_info(user_id)
    logger.info('found user {} for bottalk command'.format(user))
    async for log in client.logs_from(message.channel, limit=4000):
        if log.author == user:
            sentences += log.content + '\n'
    if len(sentences) == 0:
        await client.send_message(message.channel, "I got nothing 🤷")
    try:
        text_model = markovify.Text(sentences)
        s = text_model.make_sentence(tries=50)
        if not s or len(s) < 1:
            s = "My apologies, I cannot quite grasp the essence of that user."
        await send_message_without_tag(client, message, s)
    except Exception as e:
        logger.error("Shat self: {}".format(e))
        await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")


async def random_markov_response(message):
    try:
        sentences = u''
        random_dt = random_date(message.channel)
        async for log in client.logs_from(message.channel, limit=2000, after=random_dt):
            sentences += log.content + '\n'
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(280, tries=20)
        if not s or not len(s) > 0:
            s = "🤷"
        await send_message_without_tag(client, message, s)
    except Exception as e:
        logger.info("ERROR!: {}".format(e))
        logger.error("Shat self: {}".format(e))
        await client.send_message(message.channel, "Sorry, I've just gone and shat myself.")


def should_talk():
    # about equal to a three of a kind
    lucky_number = 1
    roll = random.randint(1,47)
    return roll == lucky_number


@client.event
async def on_message(message):
    if message.author == client.user:
        # lmao don't invoke yourself m8
        return
    if message.content.startswith('!ud'):
        await urban_dictionary_response(message)
    if message.content.startswith('!weather'):
        await weather_response(message)
    if message.content.startswith('!neechee'):
        await nietzsche_response(message)
    if message.content.startswith('!topic'):
        await client.send_message(message.channel, message.channel.topic)
    if client.user.mentioned_in(message):
        await random_markov_response(message)
    if message.content.startswith('!bottalk'):
        await user_markov_response(message)
    if should_talk():
        await random_markov_response(message)


# TODO: Add message to alert user on start/restart
logger.info('Starting up!')
client.run(os.environ['DISCO_TOKEN'])
