import speech_recognition as sr
import os
import sys
import time
import platform
import subprocess
import pygame
import threading  # For handling background threads
from PIL import Image

# List of commands
commands = [
    ' are you ready', ' how are you', ' say hello', ' what are you', ' do you sleep',
    ' are you able to read', ' what can you understand', ' please laugh', 'Exit ',
    ' open notepad', ' Mode 1', ' Mode 0'  # Add new disable command
]

# Flag to track if hide Mode is enabled
hide_mode_enabled = False

# Thread control variable to stop the hide mode thread
hide_thread = None

# Function to open Notepad
def open_notepad():
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.Popen(['notepad.exe'])
        else:
            print(f"Unsupported OS: {system}")
    except Exception as e:
        print(f"Error opening notepad: {e}")

def open_CCleaner():
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.Popen(["C:\\Program Files\\CCleaner\\CCleaner64.exe", "/AUTO"])
        else:
            print(f"Unsupported OS: {system}")
    except Exception as e:
        print(f"Error opening CCleaner: {e}")


# Add new action for the "Enable hide Mode" command
def enable_hide_mode():
    global hide_mode_enabled, hide_thread  # Declare as global
    if not hide_mode_enabled:
        hide_mode_enabled = True
        # Start the hide Mode in a new thread so it doesn't block the main loop
        hide_thread = threading.Thread(target=play_hide_gif)
        hide_thread.start()
        talk("Activating Hide Mode...")

def play_hide_gif():
    global hide_mode_enabled  # Declare as global
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Full screen mode
    pygame.display.set_caption('Hide Mode')

    # Load the GIF using Pillow
    gif_path = 'Gifs/BG.png'  # Replace with your GIF's path
    gif = Image.open(gif_path)

    # Resize the GIF to fit the screen (full-screen mode)
    screen_width, screen_height = pygame.display.get_surface().get_size()
    gif = gif.resize((screen_width, screen_height), Image.Resampling.LANCZOS)

    # Convert the resized GIF frames to a format compatible with Pygame
    frames = []
    try:
        while True:
            frame = gif.copy()
            frame = frame.convert("RGBA")  # Convert to RGBA for pygame compatibility
            frames.append(frame)
            gif.seek(gif.tell() + 1)  # Move to the next frame
    except EOFError:
        pass  # No more frames

    # Convert frames to Pygame surfaces
    pygame_frames = [pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA') for frame in frames]

    clock = pygame.time.Clock()

    # Loop through the frames of the GIF
    while hide_mode_enabled:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                hide_mode_enabled = False
                pygame.quit()
                return

        # Display the current frame
        screen.fill((0, 0, 0))  # Clear the screen
        current_frame = pygame_frames[gif.tell() % len(pygame_frames)]  # Get the current frame
        screen.blit(current_frame, (0, 0))  # Draw the current frame
        pygame.display.update()  # Update the display
        clock.tick(30)  # Control the frame rate (adjust to suit the GIF's frame rate)

    pygame.quit()

# Add action for "Disable hide Mode"
def disable_hide_mode():
    global hide_mode_enabled  # Declare as global
    hide_mode_enabled = False
    if hide_thread is not None:
        hide_thread.join()  # Wait for the thread to finish
    pygame.quit()
    print("Disabled!")
    talk("Disabled!")

# Command responses (include new command here)
command_responses = [
    {'trigger': 'are you ready', 'response': 'iam'},
    {'trigger': 'how are you', 'response': 'OkSir'},
    {'trigger': 'say hello', 'response': 'Hello'},
    {'trigger': 'what are you', 'response': 'Iamacomputerprogrammadeinpython3'},
    {'trigger': 'do you sleep', 'response': 'whyyesidreamincode'},
    {'trigger': 'are you able to read', 'response': 'yesihaveaccesstotheworldsinfomation'},
    {'trigger': 'what can you understand', 'response': 'ihaveprintedalistofcommandthatiknowsir', 'print_list': True},
    {'trigger': 'please laugh', 'response': 'HAHAHAHAHAHAHAAAHAHAAAAHAAAHHHAAAA'},
    {'trigger': 'open notepad', 'response': 'OpeningNotepad', 'action': open_notepad},
    {'trigger': 'Auto clean', 'response': 'OpeningCleaner', 'action': open_CCleaner},
    {'trigger': 'mode one', 'response': 'Activating Mode...', 'action': enable_hide_mode},
    {'trigger': 'mode zero', 'response': 'Disabling Mode...', 'action': disable_hide_mode},
    {'trigger': 'exit', 'response': 'OkSirgoodnight', 'exit': True}
]

# Function to talk (unchanged)
def talk(audio, speed=155, lang="en"):
    os.system(f'espeak -s {speed} -v {lang} "{audio}"')

# Function to get command from microphone (unchanged)
def get_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=30, phrase_time_limit=30)
            command_text = recognizer.recognize_google(audio)
            print(f"Recognized command: {command_text}")
            return command_text.lower().strip()
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return None

# Improved command processing with regex for better matching
import re  # For regex matching
def process_command(command):
    if command is None:
        return

    # Normalize the command (strip spaces, convert to lowercase)
    command = command.lower().strip()

    # Use regular expression to handle case insensitivity and possible extra spaces
    for item in command_responses:
        # Ensure we are matching the 'trigger' as a substring in the command (ignoring case)
        if re.search(r'\b' + re.escape(item['trigger'].lower()) + r'\b', command):
            print(f"Matched command: {item['trigger']}")
            lang = item.get('lang', 'en')
            talk(item['response'], lang=lang)

            if 'action' in item:
                print(f"Executing action for: {item['trigger']}")
                item['action']()

            if item.get('print_list'):
                print("Known commands:")
                for cmd in commands:
                    print(f"- {cmd}")

            if item.get('exit'):
                print("Exiting program...")
                sys.exit(0)
            break
    else:
        print(f"No matching command found for: {command}")

# Main loop (unchanged)
def main_loop():
    while True:
        command = get_command()
        process_command(command)
        time.sleep(0.5)

if __name__ == "__main__":
    main_loop()