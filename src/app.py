import discord  # discord.pyライブラリをインポート。Discord Botの作成に必要です。
from discord.ext import commands  # commandsフレームワークをインポート。コマンドベースのBotを簡単に作成できます。
import logging  # loggingモジュールをインポート。ログ出力のために使用します。
import os  # osモジュールをインポート。環境変数へのアクセスに使用します。
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)

# 環境変数からDiscord Botのトークンを取得
TOKEN = os.getenv('DISCORD_BOT_TOKEN')


# loggingの基本設定を行います。ログレベルをINFOに設定し、ログのフォーマットを指定します。
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s: %(message)s')

# Botクライアントの初期化。コマンドのプレフィックスを'!'に設定し、Botが受信するイベントの設定します。
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容へのアクセスを有効にします。これにより、メッセージのテキストを読み取れるようになります。

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # BotがDiscordに接続したときに実行されるイベント。Botのログインが完了したことをログに記録します。
    logging.info(f'Botが準備できました: {bot.user}')

@bot.command()
async def make(ctx, *,text: str):
    # '!make <text>'というコマンドに反応して実行される関数。 
    try:
        # ... (rest of the code remains the same)
        # Create a new thread
        # 创建一个新的线程
        try:
            thread = await ctx.channel.create_thread(
                name=f"discussion{ctx.message.id}",  # 为线程命名
                auto_archive_duration=10080,  # 一周后自动存档
                type=discord.ChannelType.public_thread  # 私有线程或公开线程
            )
        except:
            thread = ctx

        messages = [message async for message in thread.history(limit=100)]

        # 除去触发命令的消息
        messages = [m for m in messages if m.id != thread.message.id]

        # 逆順にソート
        messages.reverse()
        # logging.info(str(messages))

        context = "\n".join([m.author.name + ":" + m.content for m in messages]) + "\n\n" + ctx.message.author.name + ":" + text
        # 确保文本长度不超过4000字符
        context = context[-4000:]
        # logging.info(context)

        # メッセージをテキストに結合

        # for message in messages:
        #     text += message.content + '\n'
        # text = text[-4000:]  # latest 4000 characters

        message_to_model = [
                {
                    "role": "system",
                    "content": 'think in english, answer in japanese. this is discord thread bot. make anser from thred massages and your answer in "chappy_myu65"'
                },
                {
                    "role": "user",
                    "content": context
                },
            ]

        logging.info('応答作成')
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=message_to_model,
            temperature=0.7,
            max_completion_tokens=4096,
            top_p=0.95,
            stop=None,
        )

        # Split the response into multiple messages if it's too long
        response = completion.choices[0].message.content
        max_chars_per_message = 2000
        messages_to_send = []
        while len(response) > max_chars_per_message:
            messages_to_send.append(response[:max_chars_per_message])
            response = response[max_chars_per_message:]
        messages_to_send.append(response)

        # Send the responses
        for message in messages_to_send:
            await thread.send(message)


    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

bot.run(TOKEN)  # Botを起動します。この関数により、BotはDiscordサーバーに接続し、コマンドの待受を開始します。