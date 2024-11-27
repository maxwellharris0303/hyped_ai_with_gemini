import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
sample_pdf = genai.upload_file("1.html")
response = model.generate_content(["what is the price of product to usd and release date? And in stock or out stock? No extra word", sample_pdf])
print(response.text)

print("My files:")
for f in genai.list_files():
    print("  ", f.name)
    f.delete()

# from openai import OpenAI

# client = OpenAI(
#     api_key=os.environ["API_KEY"],
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# response = client.chat.completions.create(
#     model="gemini-1.5-flash",
#     n=1,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": "Explain to me how AI works"
#         }
#     ]
# )

# print(response.choices[0].message)