from backend_logic import RAGPipeline
try:
    p = RAGPipeline(api_key="dummy", model_type="OpenRouter", openrouter_model="huggingfaceh4/zephyr-7b-beta:free")
    print("Initialization successful!")
except Exception as e:
    print(f"Error: {e}")
