import openai

client = openai.OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="unsloth/gemma-3-1b-it",
    messages=[
        {"role": "system", "content": """Sen kullanıcıların isteklerine Türkçe cevap veren bir asistansın ve sana bir problem verildi. Problem hakkında düşün ve çalışmanı göster. Çalışmanı <start_working_out> ve <end_working_out> arasına yerleştir. Sonra, çözümünü <SOLUTION> ve </SOLUTION> arasına yerleştir. Lütfen SADECE Türkçe kullan."""},
        {"role": "user", "content": "121'in karekökü kaçtır?"}
    ],
    temperature=0.7,
    max_tokens=256
)

print(response.choices[0].message.content)