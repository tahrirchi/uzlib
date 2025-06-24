import openai

client = openai.OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

# Используйте полный ID модели с LoRA из вывода команды curl
# Возможно, вам нужно будет скопировать его целиком из вашего терминала.
lora_model_id = "lora" 

response = client.chat.completions.create(
    # Указываем правильную, уже объединенную модель
    model=lora_model_id, 
    messages=[
        {
            "role": "system",
            "content": (
                "Canon EOS DCS 1 Kodakning uchinchi Canon asosidagi raqamli SLR kamerasi bo'lib, "
                "bu Kodak EOS DCS-1 ning brendini o'zgartirilgan versiyasidir. U 1995 yil dekabrda "
                "chiqarilgan, bu yil boshida chiqqan arzonroq EOS DCS 3 dan keyin mavjud bo'lgan. "
                # ... (остальной текст)
            )
        },
        {
            "role": "user",
            "content": "Canon EOS DCS 1 ning rezolyutsiyasi qanday edi?"
        }
    ],
    temperature=0.7,
    max_tokens=256
    # Параметр extra_body={"lora": "lora"} удален, так как он не нужен и вызывает ошибку
)

print(response.choices[0].message.content)