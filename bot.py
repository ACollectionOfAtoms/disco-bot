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

# TODO: Is this still needed?!
# async def send_message_without_tag(client, message, message_to_send):
#     # tags like these are processed client side.
#     # example: <@!4524524324> => @user_name
#     tag_regex = '<@!?[0-9]*?>'
#     message_without_tag = re.sub(tag_regex, 'discord user', message_to_send)
#     message_without_tag.replace('@', '')
#     await client.send_message(message.channel, message_without_tag)


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
        for g in client.guilds:
            logger.info('I am in {}'.format(g))
            logger.info('attempting to update role...')
            coroutines.append(change_role_colour(g))
        coroutines.append(client.change_presence(activity=discord.Game(name='Hatoful Boyfriend: A School of Hope and White Wings')))
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
        search_term = ' '.join(message.content.split()[1:])
    except IndexError:
        await message.channel.send("I need a search term.")
        return
    try:
        definition = urban_dictionary.get_first_ud_definition(search_term)
    except Exception as e:
        logger.exception(e)
        logger.info('Could not get ud response!')
        await message.channel.send("I've failed to get the definition! Check my error logs.")
        return
    if definition == '':
        await message.channel.send('Sorry, no results for that term.')
        return
    await message.channel.send(definition)


async def weather_response(message):
        try:
            zip_code = message.content.split()[1]
        except IndexError:
            await message.channel.send("I need an american zip code.")
            return
        if not zip_code.isdigit():
            await message.channel.send("That does not look like a zip code!")
            return
        try:
            response = weather.get_weather_response(zip_code)
        except Exception as e:
            logger.exception(e)
            logger.info('Could not get weather data!')
            await message.channel.send("Somethings not right... Please check error logs!")
            return
        try:
            parsed_response = weather.parse_weather_response(response)
        except KeyError as e:
            logger.exception(e)
            logger.info('Could not parse weather data!')
            await message.channel.send("That zip code didn't work for me. Is it valid?")
            return
        await message.channel.send(parsed_response)


async def nietzsche_response(message):
    quote = nietzsche.QUOTES[random.randint(0, len(nietzsche.QUOTES) - 1)]
    await message.channel.send(quote)


async def random_markov_response(message):
    try:
        sentences = u''
        random_dt = random_date(message.channel)
        async for log in message.channel.history(limit=101, around=random_dt):
            sentences += log.content + '\n'
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(180, tries=20)
        if not s or not len(s) > 0:
            s = "🤷"
        await message.add_reaction('🤖')
        await message.channel.send(s)
    except Exception as e:
        logger.info("ERROR!: {}".format(e))
        logger.error("Shat self: {}".format(e))           
        await message.channel.send("Sorry, I've just gone and shat myself.")


async def user_markov_response(message):
    user = message.mentions[0]
    logger.info('found user {} for bottalk command'.format(user))
    sentences = u''
    async for log in message.channel.history(limit=101):
        if log.author == user:
            sentences += log.content + '\n'
    if len(sentences) == 0:
        await message.channel.send("I got nothing 🤷")
        return
    try:
        text_model = markovify.Text(sentences)
        s = text_model.make_short_sentence(300, tries=50)
        if not s or len(s) < 1:
            s = "My apologies, I cannot quite grasp the essence of that user."
        await message.channel.send(s)
    except Exception as e:
        logger.error("Shat self: {}".format(e))
        await message.channel.send("Sorry, I've just gone and shat myself.")

def should_talk():
    # about equal to a three of a kind
    lucky_number = 1
    roll = random.randint(1,88)
    return roll == lucky_number


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!ud'):
        await urban_dictionary_response(message)
    if message.content.startswith('!weather'):
        await weather_response(message)
    if message.content.startswith('!neechee'):
        await nietzsche_response(message)
    if message.content.startswith('!topic'):
        if message.channel.topic:
            await message.channel.send(message.channel.topic)
        else:
            await message.channel.send('This channel is without a topic.')
    if client.user.mentioned_in(message):
        await random_markov_response(message)
    if message.content.startswith('!bottalk'):
        await user_markov_response(message)
    if should_talk():
        await random_markov_response(message)


# TODO: Add message to alert user on start/restart
logger.info('Starting up!')
client.run(os.environ['DISCO_TOKEN'])
