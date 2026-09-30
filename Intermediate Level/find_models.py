import requests

try:
    response = requests.get("https://openrouter.ai/api/v1/models")
    models = response.json().get("data", [])

    free_models = []
    for m in models:
        pricing = m.get("pricing", {})
        if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
            free_models.append(m["id"])

    print("Available free models:")
    for fm in free_models:
        print(fm)
except Exception as e:
    print("Error:", e)
