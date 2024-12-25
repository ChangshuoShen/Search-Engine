import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# FastAPI 实例化
app = FastAPI()

# 设置 CPU 线程数
torch.set_num_threads(16)  # 使用16个线程来执行推理

# 载入模型和 tokenizer
device = "cuda" if torch.cuda.is_available() else 'cpu'
print(f"using device: {device}")

tokenizer = AutoTokenizer.from_pretrained("THUDM/glm-4-9b-chat", trust_remote_code=True)

model = AutoModelForCausalLM.from_pretrained(
    "THUDM/glm-4-9b-chat",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,  # 若不需要低内存模式，可以去掉该行
    trust_remote_code=True
).to(device).eval()

# 定义请求体格式
class QueryRequest(BaseModel):
    query: str

# API 路由，接收请求并返回生成结果
@app.post("/generate")
async def generate_text(request: QueryRequest):
    query = request.query

    inputs = tokenizer.apply_chat_template(
        [{"role": "user", "content": query}],
        add_generation_prompt=True,
        tokenize=True,
        return_tensors="pt",
        return_dict=True
    )

    inputs = inputs.to(device)

    gen_kwargs = {
        "max_length": 1000, 
        "do_sample": True,
        "top_k": 50
    }

    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {"response": response}

