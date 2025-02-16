import os
from run_script import generate_response

def get_sounds(prompt):
    # Send the prompt to ChatGPT and get the response
    response = generate_response(prompt)
    
    # Assuming the response is a string with sound descriptions separated by commas
    sounds = response.split(',')
    
    # Trim whitespace and ensure we have exactly 10 sounds
    sounds = [sound.strip() for sound in sounds][:10]
    
    return sounds

if __name__ == "__main__":
    # Get the prompt from environment variable
    prompt = os.getenv("SOUND_PROMPT", "Describe 10 sounds appropriate for a forest setting.")
    
    # Get the list of sounds
    sounds = get_sounds(prompt)
    
    # Print the sounds
    print("Generated Sounds:")
    for sound in sounds:
        print(f"- {sound}")
