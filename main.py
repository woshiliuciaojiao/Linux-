from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import time
import uvicorn

app = FastAPI(title="MCP Homework Service")
VALID_TOKENS = {}

# 接口1：无需鉴权，返回Token
@app.post("/get_auth_token")
def get_auth_token():
    token = secrets.token_hex(8)
    VALID_TOKENS[token] = time.time() + 3600
    return {"token": token}

# 鉴权依赖
security = HTTPBearer()
def verify_token(cred: HTTPAuthorizationCredentials = Depends(security)):
    token = cred.credentials
    if token not in VALID_TOKENS or VALID_TOKENS[token] < time.time():
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    return token

# 接口2：需要鉴权，自定义功能（问候接口）
@app.post("/hello")
def hello(name: str, _=Depends(verify_token)):
    return {"message": f"Hello {name}，鉴权通过，MCP服务调用成功！"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
