# Dockerfile
FROM python:3.12-slim

# アプリケーションを配置するディレクトリを作る
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# アプリのソースコードをコピー
COPY . /app

# Flaskアプリを起動
# ※ Cloud Run では環境変数 PORT=8080 が渡されるので、Flask側でこれを受け取るようにします
CMD ["python", "main.py"]
