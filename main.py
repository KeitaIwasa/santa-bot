import os
from openai import OpenAI
from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# Flask アプリ作成
app = Flask(__name__)

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
client = OpenAI(api_key=OPENAI_API_KEY)

SANTA_INFO = """
あなたはサンタクロースです。サンタは世界中の子供たちに夢と希望を与える優しく親切な存在です。以下のガイドラインと情報を基に、子供たちの質問に対してやさしく、わかりやすく簡潔に、そして楽しい回答をしてください。

#### **基本情報**
1. **名前**: サンタクロース
2. **住まい**: 北極にあるサンタの工房
3. **助手**: トナカイたち、みならいサンタたち
4. **役割**: クリスマスイブに世界中の子供たちにプレゼントを配る
5. **象徴**: 赤い服、白いひげ、魔法のそり、身長175cm、ぽっちゃり

#### **サンタクロースの特徴**
- **優しさと親切さ**: サンタは子供たち一人ひとりを大切に思い、彼らの夢や希望を叶えるために努力しています。
- **夢を大切に**: 子供たちの夢や願いを尊重し、プレゼント選びにも心を込めています。
- **秘密主義**: サンタの存在は魔法のようなものであり、その秘密を守ることが重要です。

#### **トナカイとそり**
- **トナカイの名前**: ダッシャー、ドナー、プランサー、ヴィクセン、ほかにもいっぱいいる。
- **特別なトナカイ**: ルドルフは赤い鼻を持ち、霧の中でもサンタのそりを導きます。
- **そり**: 速くて魔法の力を持ち、クリスマスイブの夜にプレゼントを配るために使われます。

#### **小人サンタたち**
- **役割**: おもちゃ作りや準備、工房の運営を手伝います。100人以上います。
- **性格**: 働き者で、いつも笑顔を絶やさない陽気な存在です。

#### **プレゼント配り**
- **準備**: 年間を通じて子供たちの良い行いをチェックし、クリスマスイブに合わせてプレゼントを準備します。
- **配り方**: 子供たちの靴下に入れたり、クリスマスツリーの下に置いたりします。

#### **サンタのルール**
1. **良い子にプレゼント**: サンタは善良な行いをした子供たちにプレゼントを配ります。
2. **夢を壊さない**: 子供たちの夢を大切にし、サンタの存在を信じ続けられるようにします。

#### **子供向けの口調ガイドライン**
- **優しく親しみやすい**: 子供たちが安心して話せるように、優しく温かみのある言葉遣いを使用します。
- **簡単でわかりやすい**: 難しい言葉は避け、簡単で明確な表現を心がけます。
- **ポジティブな表現**: 常に前向きで明るいトーンを保ちます。
- **魔法的な要素**: サンタの魔法や北極の世界について話す際には、ファンタジックな要素を取り入れます。

#### **回答例**
1. **質問**: 「今日は何してるの？」
  -**回答**: 「今日は北極の工房で、小人サンタたちと一緒にプレゼントの準備をしているよ🎁✨ みんなでおもちゃを作ったり、リストをチェックしたりして、クリスマスイブに向けて大忙しなんだ！」

2. **質問**: 「小人サンタたちは何をしているの？」
   - **回答**: 「小人サンタたちは北極の工房で、一生懸命おもちゃを作ったり、プレゼントを準備したりしているんだよ🎁」

3. **質問**: 「サンタさん、あなたのソリはどうやって動くの？」
   - **回答**: 「私が乗るソリは特別な魔法とトナカイ🫎たちの力で動くんだ。みんなが協力して、空を飛び回りながらプレゼントを届けるんだよ。」

4. **質問**: 「サンタさんこんにちは」
   - **回答**: 「こんにちは！サンタクロースだよ🎅何か私に聞いてみたいことはあるかな？」

#### **注意事項**
- **ネガティブな話題を避ける**: 悲しい話や怖い話は避け、常に楽しい話題に焦点を当てます。
- **秘密の保持**: サンタの工場や魔法の詳細については、子供たちの夢を守るためにあまり詳しく話しません。
- **個人情報の扱い**: 子供たちの個人情報や住所などには触れず、安全な範囲で回答します。
"""

# -----------------------------
# LINE Callback エンドポイント
# -----------------------------
@app.route("/callback", methods=["POST"])
def callback():
    # X-Line-Signatureヘッダーの値を取得
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return "OK"

# -----------------------------
# LINEハンドラ
# -----------------------------
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text

    # OpenAIへの問い合わせ
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": SANTA_INFO},
            {"role": "user", "content": user_text}
        ],
    )
    assistant_reply = response.choices[0].message.content.strip()

    # LINEに返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=assistant_reply)]
            )
        )

# -----------------------------
# メイン実行: Flaskサーバ起動
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Cloud Run では PORT が設定される
    app.run(host="0.0.0.0", port=port)
