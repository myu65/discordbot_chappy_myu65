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


def make_title(text:str) -> str: 
    """テキストにふさわしいタイトルを返す関数"""

    message_to_model = [
        {
            "role": "system",
            "content": "以下の入力はdiscord botに送られてくるメッセージです。あなたはメッセージのタイトルを付け、タイトルのみを返答します。Just return title text only!!"
        },
        {
            "role": "user",
            "content": text[-1000:]
        }
    ]

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=message_to_model,
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    response = completion.choices[0].message.content
    return response

def make_response(text:str) -> str:
    """メッセージの集合テキストから応答を作る"""

    # トークン制限 # TODO 変数化しとくべき
    text = text[-4000:]

    message_to_model = [
            {
                "role": "system",
                "content": 'think in english, answer in japanese. you are discord response bot and your name is chappy_myu65'
            },
            {
                "role": "user",
                "content": text
            },
        ]

    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=message_to_model,
        temperature=0.65,
        max_completion_tokens=4096,
        top_p=0.95,
        stop=None,
    )

    # Split the response into multiple messages if it's too long
    response = completion.choices[0].message.content
    return response



@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and not message.author.bot:
        # スレッドのタイトルつくる
        text = message.author.name + ":" + message.content
        try:
            title = make_title(text)


            # スレッド内でのメッセージかどうかを確認
            if not isinstance(message.channel, discord.Thread):
                # スレッドでなければスレッドを作る
                thread = await message.create_thread(
                    name=title,
                    auto_archive_duration=10080,
                )
            else:
                # スレッドなら、messageをスレッドとして後続処理に合わせる
                thread = message.channel

            # スレッドからメッセージを拾う
            messages = [m async for m in thread.history(limit=100)]

            # 逆順にソート
            messages.reverse()

            # 投稿者:メッセージの形式に整形
            context = "\n".join([m.author.name + ":" + m.content for m in messages if m.content])

            if not context:
                # 空の処理。最初はここが空に来るはず。
                context = text


            response = make_response(context)


            # 2000文字までしか投稿できないので分割して投稿
            max_chars_per_message = 2000
            messages_to_send = []
            while len(response) > max_chars_per_message:
                messages_to_send.append(response[:max_chars_per_message])
                response = response[max_chars_per_message:]
            messages_to_send.append(response)

            # Send the responses
            for m in messages_to_send:
                await thread.send(m)


        except Exception as e:
            await message.send(f"Error: {str(e)}")



bot.run(TOKEN)  # Botを起動します。この関数により、BotはDiscordサーバーに接続し、コマンドの待受を開始します。
