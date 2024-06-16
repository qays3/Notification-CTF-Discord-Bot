import discord
from discord.ext import commands, tasks
import aiohttp
import pymysql.cursors
import asyncio
import os
import json
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents = discord.Intents.all()

client = commands.Bot(command_prefix='/', intents=intents)

hostname = 'localhost'
username = 'root'
password = ''
database = ''

first_blood_challenges = set()
new_challenges = set()

first_blood_data = {}
first_blood_file = "first_blood.json"

new_chall_data = []
new_chall_file = "new_chall.json"

reactions = ["🔥", "👽"]

if os.path.exists(first_blood_file):
    with open(first_blood_file, "r") as file:
        first_blood_data = json.load(file)

if os.path.exists(new_chall_file):
    with open(new_chall_file, "r") as file:
        new_chall_data = json.load(file)


def create_connection():
    try:
        connection = pymysql.connect(
            host=hostname,
            user=username,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        return None


async def get_first_blood():
    loop = asyncio.get_event_loop()
    connection = await loop.run_in_executor(None, create_connection)
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = """SELECT challenges.id, users.UserName, Team.TeamName, challenges.CHname, challenges.CHlevel, 
                         COUNT(solvedchallenges.id) AS first_blood_count, MIN(solvedchallenges.Time) AS first_blood_time 
                         FROM solvedchallenges 
                         INNER JOIN users ON solvedchallenges.userId = users.id 
                         INNER JOIN Team ON solvedchallenges.team_id = Team.Teamid 
                         INNER JOIN challenges ON solvedchallenges.CHid = challenges.id 
                         WHERE solvedchallenges.id IN (SELECT MIN(id) FROM solvedchallenges GROUP BY CHid) 
                         GROUP BY Team.TeamName, challenges.CHname, challenges.CHlevel, challenges.id"""
                cursor.execute(sql)
                first_blood_entries = cursor.fetchall()

                return first_blood_entries
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
        finally:
            connection.close()


async def get_new_chall():
    loop = asyncio.get_event_loop()
    connection = await loop.run_in_executor(None, create_connection)

    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, adminName, CHname, CHpoint, CHcategory, CHlevel, CHstatus FROM challenges"
                cursor.execute(sql)
                new_chall_entries = cursor.fetchall()

                return new_chall_entries
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
        finally:
            connection.close()


async def is_competition_started():
    loop = asyncio.get_event_loop()
    connection = await loop.run_in_executor(None, create_connection)
    if connection:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT time_start, time_end FROM COMPEINFO WHERE compe_id = 1"
                cursor.execute(sql)
                competition_info = cursor.fetchone()
                if competition_info:
                    current_time = datetime.now()
                    time_start = competition_info['time_start']
                    time_end = competition_info['time_end']
                    return time_start <= current_time <= time_end
                return False
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
        finally:
            connection.close()


@tasks.loop(seconds=1)
async def check_first_blood():
    global first_blood_data

    channel_id = 1163553906543034439
    channel = client.get_channel(channel_id)
    first_blood_entries = await get_first_blood()

    if first_blood_entries:
        for entry in first_blood_entries:
            challenge_id = entry['id']

            if challenge_id not in first_blood_challenges:
                user_name = entry['UserName']
                team_name = entry['TeamName']
                challenge_name = entry['CHname']
                challenge_level = entry['CHlevel']
                first_blood_count = first_blood_data.get(user_name, 0)
                first_blood_time = entry['first_blood_time']

                message = f"**{user_name}** from **{team_name}** team achieved first blood solved ({first_blood_count + 1} times) :tada: **{challenge_name} ({challenge_level})** challenge ! :tada:"
                embed = discord.Embed(
                    description=message,
                    color=0xFF5733
                )
                first_blood_message = await channel.send(embed=embed)

                for reaction in reactions:
                    await first_blood_message.add_reaction(reaction)

                first_blood_challenges.add(challenge_id)
                first_blood_data[user_name] = first_blood_count + 1

                with open(first_blood_file, "w") as file:
                    json.dump(first_blood_data, file)


@tasks.loop(seconds=60)
async def check_new_chall():
    global new_chall_data

    general_channel_id = 93
    admin_channel_id = 93101

    new_chall_entries = await get_new_chall()
    competition_started = await is_competition_started()

    general_channel = client.get_channel(general_channel_id)
    admin_channel = client.get_channel(admin_channel_id)

    if new_chall_entries:
        for entry in new_chall_entries:
            challenge_id = entry['id']

            if challenge_id not in new_challenges:
                admin_name = entry['adminName']
                challenge_name = entry['CHname']
                challenge_level = entry['CHlevel']
                challenge_points = entry['CHpoint']
                challenge_category = entry['CHcategory']
                challenge_status = entry['CHstatus']

                admin_message = f"**{admin_name}** has posted a new challenge, info: \n**Challenge name:** {challenge_name}\n**Challenge category:** {challenge_category}\n**Challenge level:** {challenge_level}\n**Challenge points:** {challenge_points}\n**Challenge Status:** {challenge_status}"

                admin_embed = discord.Embed(
                    description=admin_message,
                    color=0xFF5733
                )

                admin_new_chall_message = await admin_channel.send(embed=admin_embed)

                for emoji in reactions:
                    await admin_new_chall_message.add_reaction(emoji)

                
                if challenge_status == 'ON' and challenge_id not in new_challenges:
                    general_message = f"**{admin_name}** has posted a new challenge, info: \n**Challenge name:** {challenge_name}\n**Challenge category:** {challenge_category}\n**Challenge level:** {challenge_level}\n**Challenge points:** {challenge_points}"

                    general_embed = discord.Embed(
                        description=general_message,
                        color=0xFF5733
                    )

                    general_new_chall_message = await general_channel.send(embed=general_embed)

                    for emoji in reactions:
                        await general_new_chall_message.add_reaction(emoji)

                    new_challenges.add(challenge_id)

                with open(new_chall_file, "w") as file:
                    json.dump(new_chall_data, file)



@client.event
async def on_ready():
    print("Bot is ready.")
    check_first_blood.start()
    check_new_chall.start()


async def start_bot():
    while True:
        try:
            await client.start('') #token
        except aiohttp.ClientConnectorError as e:
            print(f"Connection failed: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("Bot stopped by the user.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)


loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
