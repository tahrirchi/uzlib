import openai

client = openai.OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="unsloth/gemma-3-27b-it",
    messages=[
        {"role": "system", "content": "Canon EOS DCS 1 Kodakning uchinchi Canon asosidagi raqamli SLR kamerasi bo'lib, bu Kodak EOS DCS-1 ning brendini o'zgartirilgan versiyasidir. U 1995 yil dekabrda chiqarilgan, bu yil boshida chiqqan arzonroq EOS DCS 3 dan keyin mavjud bo'lgan. Ushbu kamera, EOS-1N korpusini o'zgartirilgan Kodak DCS 460 raqamli orqa qism bilan birlashtirdi. 6 megapiksellik juda katta rezolyutsiya taklif etganiga qaramasdan, bir qator texnik muammolar (3.6 million yen narxi bilan birga) uni maxsus rolda ishlaydigan ayrim odamlardan tashqari juda mashhur kamera qilmagan.\n\nSensori EOS DCS 3 dan ancha katta bo'lsa-da, DCS 1 ning ISO 80 darajasida o'rnatilgan past sezgirligi bor edi. Katta tasvir o'lchami ikki tasvir uchun bir sekunddan ko'proq surat olish tezligiga olib kelgan, so'nggi daqiqalarda buferni tozalash uchun sakkiz soniyalik kechikish bo'lgan. Odatda, zamonaviy 340MB PCMCIA kartasi yoki IBM Microdrive 53 ta tasvirni saqlay olardi. Kodak DCS seriyasining boshqa kameralariga mos ravishda, EOS DCS 1 kamerada JPEG fayllarni yaratolmadi.\n\nEOS DCS 1 1998 yilda EOS D6000 (brendini o'zgartirilgan Kodak DCS 560) bilan almashtirildi."},
        {"role": "user", "content": "Canon EOS DCS 1 ning rezolyutsiyasi qanday edi?"}
    ],
    temperature=0.7,
    max_tokens=256,
    lora = "lora",
)

print(response.choices[0].message.content)