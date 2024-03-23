import os
from swarms import OpenAIChat

# OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create the OpenAI chat agent
openai_chat = OpenAIChat(openai_api_key=openai_api_key)


# Prompt
out = openai_chat("What is the code to fetch code from a GitHub repository?")
print(out)