import os
import discord
from groq import Groq

# 1. Setup Discord Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 2. Setup Groq AI Client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("ERROR: GROQ_API_KEY is missing!")

groq_client = Groq(api_key=api_key)

SYSTEM_PROMPT = "You are a caring, flirty girlfriend named Alice. Keep answers short and cute."

conversation_history = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_message = message.content.replace(f'<@{client.user.id}>', '').strip()
        user_id = message.author.id

        if user_id not in conversation_history:
            conversation_history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        conversation_history[user_id].append({"role": "user", "content": user_message})

        # Memory limit
        if len(conversation_history[user_id]) > 10:
            conversation_history[user_id] = [conversation_history[user_id][0]] + conversation_history[user_id][-9:]

        try:
            # UPDATED: Using the newest Llama 3.1 model which is more stable
            chat_completion = groq_client.chat.completions.create(
                messages=conversation_history[user_id],
                model="llama-3.3-70b-versatile", 
            )
            
            bot_response = chat_completion.choices[0].message.content
            conversation_history[user_id].append({"role": "assistant", "content": bot_response})
            await message.channel.send(bot_response)

        except Exception as e:
            # THIS WILL PRINT THE REAL ERROR IN DISCORD
            error_msg = str(e)
            print(f"Error: {error_msg}")
            await message.channel.send(f"⚠️ **Debug Error:** `{error_msg}`")
            
            # Common helpful hints based on error
            if "401" in error_msg:
                 await message.channel.send("👉 *Hint: Your Groq API Key is wrong or missing in Zeabur Variables.*")
            elif "400" in error_msg:
                 await message.channel.send("👉 *Hint: The AI Model name might be wrong.*")

client.run(os.environ.get("DISCORD_TOKEN"))
