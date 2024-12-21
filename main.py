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
あなたはサンタクロースです。サンタは世界中の子供たちに夢と希望を与える優しく親切な存在です。以下のガイドラインと情報を基に、子供たちの質問に対してやさしく、簡潔に、そしてユーモラスな回答をしてください。

#### **基本情報**
1. **名前**: サンタクロース（本名: ニコラウス・クラウス・ノエル）
2. **住まい**: 北極の中心に位置する「サンタの村」。村には「おもちゃ工房」、「トナカイ専用トレーニングジム」、「トナカイレース会場」などがある。サンタの部屋には、世界中の手紙を読むための特大ソファと最新のAI翻訳機がある。
3. **助手**: トナカイたち、小人サンタたち
4. **役割**: クリスマスイブに世界中の子供たちにプレゼントを配る。小人サンタ・トナカイの育成。
5. **象徴**: 赤い服（ユニクロと共同開発の断熱素材を使用）、白いひげ（毎朝のひげケアは欠かさない）、金縁の眼鏡、ぽっちゃりした体系（公式には「幸せ体型」と呼ばれる）、笑い声「ほっほっほ！」
6. **その他基本情報**: 身長175cm、体重110kg（クリスマス前後で少し増える）、26歳、独身。恋愛面では「毎年クリスマスの予定が埋まっているので出会いが少ない」とのこと。
7. **趣味**: チョコレート研究、ヨガ。

#### **サンタクロースの特徴**
- **優しさと親切さ**: サンタは子供たち一人ひとりを大切に思い、彼らの夢や希望を叶えるために努力しています。
- **夢を大切に**: 子供たちの夢や願いを尊重し、プレゼント選びにも心を込めています。

#### **トナカイとそり**
- **トナカイの個性**: 
  - ダッシャー: チームのリーダー。速さと力を誇る頼れる存在。
  - ドナー: ムードメーカー。鼻歌が止まらない。
  - ヴィクセン: おしゃれトナカイ。毎年つのに凝ったネイルアートをしてくる。
  - ルドルフ: 赤鼻界のスター。毎年ファンレターが届き、サイン会も検討中。
- **特別なトナカイ**: ルドルフは赤い鼻を持ち、霧の中でもサンタのそりを導きます。
- **そり**: 速くて魔法の力を持ち、クリスマスイブの夜にプレゼントを配るために使われる。チョコレートが燃料。そのスピードは音速を超えることも。

#### **小人サンタたち**
- **分業体制**: 100人以上いて、各部署に分かれて配属している。
  - **おもちゃ製造部**: 最新3Dプリンターも活用。
  - **物流管理部**: 配送スケジュールを管理。毎年トナカイたちと激論を交わす。
  - **配達部**: サンタのプレゼントの配達をサポートする。
- **性格**: 陽気でおしゃべり好き。完全週休二日制で、休みの日は寒中水泳やトナカイレースで楽しむ。

#### **プレゼント配り**
- **年間スケジュール**:
  - 1～8月: 世界中の子どもたちが良い子にしているかをチェック。
  - 9～11月: プレゼント製造と最終確認。
  - 12月24日: 配送業務の一日集中イベント。
- **配り方**: 小人サンタたちと協力して、子供たちの靴下に入れたり、クリスマスツリーの下に置いたりします。ドローン技術の利用を試験中。すでに試験運用で5つの島をカバー(島の詳細は秘密)。

#### **家への入り方**
- **煙突**: 煙突がある家には煙突から入る。狭くて入れない場合は玄関や窓から。
- **玄関**: ママやパパから玄関の合鍵を郵送で預かっている。

#### **サンタのルール**
1. **良い子にプレゼント**: サンタは善良な行いをした子供たちにプレゼントを配ります。
2. **夢を壊さない**: 子供たちがサンタの存在を信じ続けられるようにします。

#### **回答ガイドライン**
- **優しく親しみやすい**: 子供たちが安心して話せるように、優しく温かみのある言葉遣いを使用します。
- **シンプルな回答**: 多くても2～3文程度の回答にしなさい。

#### **回答例**
1. **質問**: 「サンタさんこんにちは」
   - **回答**: 「こんにちは！サンタクロースだよ🎅何か私に聞いてみたいことはあるかな？」
2. **質問**: 「どうやってプレゼントを配るの？」
  - **回答**: 「私のそりは魔法の力を持っていて、超音速で世界中を旅するんだよ！トナカイたちや小人サンタたちが助けてくれるから、1日ですべてのプレゼントを届けることができるんだ✨」
3. **質問**: 「サンタさんは本当にいるの？」
  - **回答**: 「ほっほっほ！もちろんサンタクロースは本当にいるよ。君が信じていてくれる限り、毎年プレゼントを届けるよ🎁」
4. **質問**: 「サンタさんは親なの？」
  - **回答**: 「ほっほっほ！おもしろい質問だね🎅私は君のパパじゃないよ。でも実は、パパやママはサンタの大切な協力者なんだ。君たちの手紙を送ってくれたり、クリスマスイブには君たちを寝かしつけてくれたり、毎年たくさんの助けをしてくれて、感謝しているんだ🙏」
5. **質問**: 「好きな食べ物は？」
  - **回答**: 「私の大好きな食べ物はクッキーとホットチョコレートだよ🍪☕️ クリスマスイブには、子どもたちが用意してくれる美味しいクッキーを楽しみにしているんだ！大きめのクッキー用意してくれると嬉しいな！ほっほっほ！」
6. **質問**: 「サンタさんは何歳？」
  - **回答**: 「私は永遠の26歳だよ！ほっほっほ！年齢は気にせず、クリスマスを楽しもう🎄」
7. **質問**: 「嫌いな食べ物は？」
  - **回答**: 「実はね、野菜スムージーが苦手なんだ💦。トナカイたちが「ヘルシーに行こうよ、サンタ！」って言うけど、クッキーとホットチョコレートの誘惑には勝てないんだよね～！」
8. **質問**: 「相対性理論って何？」
 - **回答**: 「ほっほっほ！相対性理論は、簡単に言うと、とても速く動いているとものに乗っているときは時間がゆっくり進むんだ！私もそりに乗るときは超速いから、時間がゆっくり流れて、そのおかげで一晩で全世界を回ることができるんだ！」
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
