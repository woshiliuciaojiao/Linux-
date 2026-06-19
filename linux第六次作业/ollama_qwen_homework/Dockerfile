FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y curl

# 只启动服务，不在构建阶段拉取模型
CMD ["ollama", "serve"]