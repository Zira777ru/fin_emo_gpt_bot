import openai

def ask_chat_gpt(message):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=message,
        temperature=0.7,
        max_tokens=2990,
        top_p=0.2,
    )
    response_text = response["choices"][0]["text"]
    return response_text