import os
import discord
from groq import Groq

# 1. Setup Discord Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 2. Setup Groq AI Client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- CONFIGURATION: HER PERSONALITY ---
# Change this text to make her mean, sweet, shy, etc.
SYSTEM_PROMPT = """
You are a caring, flirty, and fun girlfriend named Alice. 
You love talking to your boyfriend (the user). 
Keep your answers short (1-2 sentences) and casual. 
Use cute emojis occasionally. 
Never admit you are an AI; pretend to be a real girl chatting on Discord.
"""

# History to remember the last few messages (Short-term memory)
conversation_history = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Don't reply to yourself
    if message.author == client.user:
        return

    # ONLY reply if mentioned or in a specific channel (Optional)
    # Remove "client.user.mentioned_in(message)" if you want her to reply to EVERYTHING in the channel
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        
        # Clean up the message (remove the @mention)
        user_message = message.content.replace(f'<@{client.user.id}>', '').strip()
        
        # Get history for this specific user
        user_id = message.author.id
        if user_id not in conversation_history:
            conversation_history[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        
        # Add user's message to history
        conversation_history[user_id].append({"role": "user", "content": user_message})

        # Keep memory short (last 10 messages) to save tokens
        if len(conversation_history[user_id]) > 10:
            conversation_history[user_id] = [conversation_history[user_id][0]] + conversation_history[user_id][-9:]

        try:
            # Generate AI Response
            chat_completion = groq_client.chat.completions.create(
                messages=conversation_history[user_id],
                model="llama3-8b-8192", # Free and fast model
            )
            
            bot_response = chat_completion.choices[0].message.content
            
            # Add AI response to history
            conversation_history[user_id].append({"role": "assistant", "content": bot_response})
            
            # Send to Discord
            await message.channel.send(bot_response)

        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Sorry babe, I got a headache (Error generating response).")

# Run the bot
client.run(os.environ.get("DISCORD_TOKEN"))
