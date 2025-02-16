import os
import argparse
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from characters import get_character
from dotenv import load_dotenv, find_dotenv
from elevenlabs import ElevenLabs,save

_ = load_dotenv(find_dotenv())  # Load environment variables

# Set up defaults
defaults = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4o",
    "temperature": 1.0,
    "base_url": "https://api.openai.com/v1",
    "session_id": "abc123",
}

# Set up the ChatGPT API client
api_key = defaults["api_key"]
llm_model = defaults["model"]
temperature = defaults["temperature"]
base_url = defaults["base_url"]
session_id = defaults["session_id"]

print("Initializing ChatGPT API client.")
llm = ChatOpenAI(temperature=temperature, model=llm_model, base_url=base_url, api_key=api_key)
character = get_character("gnome")  # Use default character or modify as needed

# Define Prompts and interaction messages
system_prompt = character.system_prompt

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

runnable = prompt_template | llm
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

with_message_history = RunnableWithMessageHistory(
    runnable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

def get_sounds(prompt, num_sounds):
    print("Sending prompt to ChatGPT.")
    completions = with_message_history.invoke(
        {"input": prompt},
        config={"configurable": {"session_id": session_id}},
    )
    response = completions.content
    print("Received response from ChatGPT.")
    
    # Clean up the response by removing line breaks and extra spaces
    cleaned_response = response.replace('\r', '').strip()
    
    # Split the response into lines and filter out any empty lines
    sounds = [line.strip() for line in cleaned_response.split('\n') if line.strip()]
    
    # Ensure we have the desired number of sounds
    sounds = sounds[:num_sounds]
    
    print(f"Extracted {len(sounds)} sound descriptions.")
    return sounds

def sanitize_filename(name):
    # Remove invalid characters for filenames
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

def generate_sound_effect(description, output_file):
    print(f"Generating sound effect for description: '{description}'")
    client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS_API_KEY"))
    
    audio_data = b''.join(client.text_to_sound_effects.convert(text=description))
    save(audio_data, output_file)
    print(f"Sound effect saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a list of sounds based on a given prompt.")
    parser.add_argument("prompt", type=str, help="The prompt to send to ChatGPT for generating sounds.")
    parser.add_argument("--output_dir", type=str, default="sounds", help="Directory to save the generated sound files.")
    parser.add_argument("--num_sounds", type=int, default=10, help="Number of sounds to generate.")
    args = parser.parse_args()

    if not args.prompt:
        parser.error("No prompt provided. Please provide a prompt as an argument.")

    # Modify the prompt to be more specific
    specific_prompt = (
        f"List {args.num_sounds} distinct sound descriptions suitable for a sound synthesizer like ElevenLabs based on the following theme: {args.prompt}. "
        "Each sound should be a short, descriptive phrase, and each should be on a new line and should be numbered. do not include any extra text. note that these will be inputs into a elevenlabs sound thinthasiser so it should accommodate this kind of description."
    )

    # Get the list of sounds
    sounds = get_sounds(specific_prompt, args.num_sounds)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Output directory '{args.output_dir}' is ready.")

    # Generate and save each sound effect
    for sound in sounds:
        sanitized_name = sanitize_filename(sound)
        output_file = os.path.join(args.output_dir, f"{sanitized_name}.wav")
        generate_sound_effect(sound, output_file)
        print(f"Generated sound saved to {output_file}")
