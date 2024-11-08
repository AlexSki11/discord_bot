import sqlite3
import discord
from discord.ui import Button, View
from discord.ext import commands
from discord.errors import InteractionResponded

from dotenv import load_dotenv
import os
import database

connection = sqlite3.connect('evill_database.db')
connection.close()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

permission_roles = ["Казначей", "Модератор", "Офицер", 'Зам. гильд мастера', "Гильд мастер"]

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        roles = list(map(lambda x: x.name, ctx.author.roles))
        perm_role = ["Казначей", "Модератор"]
        if not bool(set(perm_role) & set(roles)):
            help_text = """
            Доступны следующие команды:
            \t $my_grade - Возвращает ваши очки 
            \t $send "Имя пользователя" "Количество очков" - отправляет пользователю введеное количество очков, нужно вводить имя пользователь которое на сервере 
                    """
        elif perm_role[0] in roles:
            help_text = """
            Доступны следующие команды:
            \t $add_myself - добавляет вас в бд 
            \t $add_player "Имя пользователя" - добавляет пользователя в бд
            \t $add_player_server Добавляет весь сервер в бд
            \t $my_grade - Возвращает ваши очки 
            \t $send "Имя пользователя" "Количество очков" - отправляет пользователю введеное количество очков
            \t $start "Название поста" - создает пост в текстовом канале "посты" 
            \t Можете завершить пост 
            \t $add_grade_player "Имя пользователя" "Количество очков" - можете выдать сколько угодно очков пользователю, в том числе и себе. Уведомления не будет 
                
                    """
            
        else:
            
            help_text = """
            Доступны следующие команды:
            \t $add_myself - добавляет вас в бд 
            \t $add_player "Имя пользователя" добавляет пользователя в бд
            \t $my_grade - Возвращает ваши очки 
            \t $send "Имя пользователя" "Количество очков" - отправляет пользователю введеное количество очков, нужно вводить имя пользователь которое на сервере 
            \t $start "Название поста" - создает пост в текстовом канале "посты"
            \t Можете завершить пост
                    """
        await ctx.send(help_text)

bot = commands.Bot(command_prefix='$', intents=intents, help_command=CustomHelpCommand())
list_user = {} # 'user':['server_id', 10-grade]



@bot.command()
async def add_myself(ctx, *args):
    roles = list(map(lambda x: x.name, ctx.author.roles))
    perm_role = permission_roles
    if not bool(set(perm_role) & set(roles)):
        print('3')
        print(roles)
        print(set(perm_role) & set(roles))
        return await ctx.send('Только модератор или казначей это может сделать')
    else:
        database.add_user(ctx.guild.id,ctx.author)
        await ctx.send('Успешно')

@bot.command()
async def add_grade_player(ctx, *args):

    list_name_roles = list(map(lambda x: x.name, ctx.author.roles))

    member = ctx.guild.get_member_named(args[0])
    print('begin')
    list_name_roles = list(map(lambda x: x.name, ctx.author.roles))
    if 'Казначей' in list_name_roles:
        database.update_user(server_id=ctx.guild.id,grade=int(args[1]),user_id=member.id)
        await ctx.send(f'Успешно')
    else:
        await ctx.send("Нельзя")

@bot.command()
async def joined(ctx, *, member: discord.Member):
    await ctx.send(f'{member} joined on {member.joined_at}')

@bot.command()
async def add_player_server(ctx, *args):
    roles = list(map(lambda x: x.name, ctx.author.roles))
    perm_role = ["Казначей"]
    if not bool(set(perm_role) & set(roles)):
        print('3')
        print(roles)
        print(set(perm_role) & set(roles))
        return await ctx.send('Только модератор или казначей это может сделать')
    server = ctx.guild.id
    list_user = [(member.id, member.global_name, member.name) for member in ctx.guild.members]
    list_server = [(server, member.id, 0) for member in ctx.guild.members]
    database.add_user_list(list_server, list_user)
    await ctx.send('Успех')

@bot.command()
async def add_player(ctx, *args):
    roles = list(map(lambda x: x.name, ctx.aurhoe.roles))
    perm_role = permission_roles
    if not bool(set(perm_role) & set(roles)):
        print('3')
        print(roles)
        print(set(perm_role) & set(roles))
        return await ctx.send('Только модератор или казначей это может сделать')
    member = ctx.guild.get_member_named(args[0])
    database.add_user(ctx.guild.id, member)
    await ctx.send('Успех')

@bot.command()
async def send(ctx, *args):
    grade = int(args[1])
    server = ctx.guild.id
    own = ctx.author
    member = ctx.guild.get_member_named(args[0])
    print(member)
    if not member:
        return await ctx.send('Пользователя нет на сервере')
    elif grade > database.get_grade(server, member):
        return await ctx.send('Недостаточно очков')
    
    database.update_user(own.id, server, grade*-1)
    database.update_user(member.id, server, grade)

    channel_id = 1304408106687791134
    channel = bot.get_channel(channel_id)
    all_grade = database.get_grade(server,member)
    await channel.send(f'Пользователь <@{member.id}> получает {grade} очков \nВсего очков:{all_grade}' )

    await ctx.send('Успешно отправлено')
"""
Пока не нужны
@bot.command()
async def add_order(ctx, *args):
    name = args[0]
    database.add_order(ctx.guild.id,name)
    await ctx.send('Успешно')

@bot.command()
async def end_order_id(ctx, *args):
    id = int(args[0]) 
    database.end_order(id, ctx.guild.id)
    await ctx.send('Успешно')



@bot.command()
async def auction(ctx, *args):
    order_id = args[0]
    grade = int(args[1])
    database.auction(order_id, ctx.author, ctx.guild.id, grade)
    await ctx.send('Успешно')

"""
@bot.command()
async def winner(ctx, *args):
    order_id = args[0]
    username = database.who_win(order_id)

    await ctx.send(f'Winner: {username}')


@bot.command()
async def my_grade(ctx, *args):
    grade = database.get_grade(ctx.guild.id, ctx.author)
    if not grade:
        return await ctx.send('Нету в бд')
    await ctx.send(f'Ваши очки: {grade}')


@bot.command()
async def start(ctx, *args):
    # Создаем кнопки
    button1 = Button(label="+5", style=discord.ButtonStyle.primary)
    button2 = Button(label="+1", style=discord.ButtonStyle.secondary)
    button3 = Button(label="Завершить", style=discord.ButtonStyle.red)
    

    # Сообщение о нажатии кнопок
    name = args[0]
    id = database.add_order(ctx.guild.id, name)
    message_content = f"Ордер id: {id}\nНазвание: {name}\nУчастники:\nСтавка:"

    async def button1_callback(interaction):
        id_now = interaction.message.content.split()[2]
        name_now = interaction.message.content.split()[4]
        users_text = ''
        user_name = interaction.user.name  # Получаем имя пользователя пусть пока висит
        database.auction(id,interaction.user,interaction.guild.id,5)
        list_users = database.get_users_auctions(id_now)
        for user in list_users:
            users_text+= f'\n{user[0]}:{user[1]} очков'
        print(users_text)
        winner = database.who_win(id_now)
        winner = f'1 место: {winner[0]}:{winner[1]} очков\n\n' if winner else ''
        message_content = f"Ордер id: {id_now} \nНазвание: {name_now}\n{winner}Участники:{users_text} \n\nСтавка:"
        await interaction.response.edit_message(content=message_content, view=view)

    async def button2_callback(interaction):
        id_now = interaction.message.content.split()[2]
        name_now = interaction.message.content.split()[4]
        users_text = ''
        database.auction(id,interaction.user,interaction.guild.id,1)
        list_users = database.get_users_auctions(id_now)
        for user in list_users:
            users_text+= f'\n{user[0]}:{user[1]} очков'
        print(users_text)
        winner = database.who_win(id_now)
        winner = f'1 место: {winner[0]}:{winner[1]} очков\n\n' if winner else ''
        message_content = f"Ордер id: {id_now} \nНазвание: {name_now}\n{winner}Участники:{users_text} \n\nСтавка:"
        await interaction.response.edit_message(content=message_content, view=view)

    async def button3_callback(interaction):
        id_now = interaction.message.content.split()[2]
        name_now = interaction.message.content.split()[4]
        roles = list(map(lambda x: x.name, interaction.user.roles))
        perm_role = permission_roles
        if not bool(set(perm_role) & set(roles)):
            print('3')
            print(roles)
            print(set(perm_role) & set(roles))
            return  
        winner = database.who_win(id_now)
        database.end_order(int(id_now), interaction.guild.id)
        if not winner:
            await interaction.response.defer()  # Отложенный ответ
                # Удаляем сообщение
            await interaction.message.delete()
                # Отправляем уведомление, редактируя оригинальный ответ
            await interaction.followup.send("Пост удален", ephemeral=True)
            return
        channel_id = 1304408106687791134
        channel = bot.get_channel(channel_id)
        await interaction.response.defer()
        if channel is not None:
            await channel.send(f'Победитель ордера {name_now} {id_now} <@{winner[2]}>')
        else:
            await interaction.response.send_message("Канал не найден!", ephemeral=True)
          
        await ctx.message.delete()  
        await interaction.message.delete()
        
        



    button1.callback = button1_callback
    button2.callback = button2_callback
    button3.callback = button3_callback

    # Создаем представление (View) и добавляем кнопки
    view = View()
    view.add_item(button1)
    view.add_item(button2)
    view.add_item(button3)

    channel_id = 1304422795849240626
    channel = bot.get_channel(int(channel_id))
    await channel.send(message_content, view=view)



#@bot.command()



database.first_connection()

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot.run(TOKEN)