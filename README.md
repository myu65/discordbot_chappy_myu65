# discordbot_chappy_myu65

discordにgroqで応答するBOT。

要件：
- 適当なサーバー。EC2のt2-microとかでOK。これの無料枠で行ける。discordのbotはポート開放もいらない。自鯖でもOK。
- groqのAPIキー。https://console.groq.com/keys ここで登録して発行。2025-01-31現在、無料プランしか存在しない。 環境変数`GROQ_API_KEY`にいれる
- discordのbotのAPIキー。なんかhttps://discord.com/developers らへんで発行する。botとしてはスレッドを作って読めて書き込める必要あり。環境変数`DISCORD_BOT_TOKEN`に入れる

## docker-composeでの起動方法
.envに
```
GROQ_API_KEY=<YOUR_KEY>
DISCORD_BOT_TOKEN=<YOUR_KEY>
```
を記載。

docker compose up -d

dockerfileの記載にmkdirがなくてマウントしてないとビルドうまくいかないかも？（ちゃんとやれ）pipの記載も適当すぎる。

## pythonでの起動方法
```
pip install discord.py groq
```
で

`python ./src/app.py`

とかでいけるはず




