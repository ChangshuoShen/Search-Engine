import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn

# 初始化 FastAPI 实例
app = FastAPI()

# 设置 CPU 线程数，以提高推理性能
torch.set_num_threads(16)

# 尝试加载模型和 tokenizer
try:
    # 检查当前设备是否支持 GPU，否则回退到 CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # 加载 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        "THUDM/glm-4-9b-chat", 
        trust_remote_code=True
    )

    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        "THUDM/glm-4-9b-chat",
        torch_dtype=torch.bfloat16,  # 使用 bfloat16 提高推理效率
        low_cpu_mem_usage=True,     # 减少 CPU 内存占用
        trust_remote_code=True
    ).to(device).eval()

    print("Model and tokenizer loaded successfully.")
except Exception as e:
    print(f"Error loading model or tokenizer: {e}")
    raise RuntimeError("Failed to initialize the model or tokenizer.")


# 定义请求体格式
class QueryRequest(BaseModel):
    query: str


# 定义 API 路由，用于接收查询并返回生成的文本
@app.post("/generate")
async def generate_text(request: QueryRequest):
    """
    接收用户请求，使用 GLM 模型生成回答。
    """
    query = request.query.strip()  # 去除多余空白
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # 构建模型输入
        inputs = tokenizer.apply_chat_template(
            [{"role": "user", "content": query}],
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True
        ).to(device)

        # 设置生成参数
        gen_kwargs = {
            "max_length": 1000,  # 最大生成长度
            "do_sample": True,   # 采样生成
            "top_k": 50          # 限制最高概率的词个数
        }

        # 使用模型生成回答
        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_kwargs)
            # 提取生成的部分（排除输入部分）
            outputs = outputs[:, inputs['input_ids'].shape[1]:]
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # 返回生成结果
        return {"response": response}

    except Exception as e:
        # 捕获异常并返回错误信息
        raise HTTPException(status_code=500, detail=f"Model generation failed: {str(e)}")


# 在主程序中启动 API 服务
if __name__ == "__main__":
    # 使用 Uvicorn 启动 FastAPI 服务
    uvicorn.run(
        "chatglm_api:app",        # 指定模块和 FastAPI 实例
        host="0.0.0.0",           # 监听所有网络接口
        port=8000,                # 默认端口
        reload=True                # 开启自动重载（开发模式下使用）
    )