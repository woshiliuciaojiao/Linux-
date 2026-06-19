from flask import Flask, request, Response
import requests

app = Flask(__name__)
OLLAMA_API = "http://ollama:11434/api/chat"

@app.route("/api/chat", methods=["POST"])
def chat_proxy():
    # 直接转发原始请求，不做任何解析处理
    resp = requests.post(
        OLLAMA_API,
        data=request.data,
        headers=request.headers,
        stream=True
    )
    return Response(resp.iter_content(chunk_size=1024), status=resp.status_code, content_type=resp.headers.get('content-type'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)