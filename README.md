# Reddit Place Script 2023

## About

This repository contains scripts that allow you to contribute your Reddit accounts to a centralized botnet and draw onto [`r/place`](https://www.reddit.com/r/place/).

## Requirements

Follow download and install instructions at the link:

[Python 3](https://www.python.org/downloads/)

**MacOS**

Run `python3 --version` in terminal to check if installation is successful.

**Windows**

If you have previously installed Windows Subsystem for Linux (WSL), you can check installation is successful with `python3 --version`. If you haven't, move onto the next step.

## Download the Bot

Click the following link to download the repository as a zip file. Extracts the content to a location of your choice:

[Download](https://github.com/broad-well/reddit-place-umich-botnet/archive/refs/heads/main.zip)

## Open the Terminal

Open the location of your extracted files in file explorer.

**MacOS**

Drag and drop the folder containing the scripts into the terminal app. ([Detailed Instructions](https://www.maketecheasier.com/launch-terminal-current-folder-mac/))

**Windows**

Open the folder containing the scripts and type `cmd` into the address bar. ([Detailed Instructions](https://www.lifewire.com/open-command-prompt-in-a-folder-5185505))

## Python Package Requirements

In the opened terminal/command prompt:

**Optional**

Create a virtual environment so the installed packages don't pollute your system. This step is optional. It just helps you organize your Python packages better.

```shell
python3 -m venv env

# Linux/macOS users, run this
. env/bin/activate

# Windows users, run this
env\Scripts\activate.bat
```

Install requirements from 'requirements.txt' file.

```shell
python3 -m pip install -r requirements.txt
```

## Bot Setup

Make a copy of `.env_TEMPLATE` and name it `.env`, and place it in the project folder.

The content should look like this:

```text
ENV_PLACE_USERNAME='["YOUR_USERNAME_HERE"]'
ENV_PLACE_PASSWORD='["YOUR_PASSWORD_HERE"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'
```

- `ENV_PLACE_USERNAME` is a list of reddit usernames
- `ENV_PLACE_PASSWORD` is a list of passwords corresponding to the usernames
- ENV_DIRECTOR_URL is the URL of the Botnet Director. _Do not change!_

## Run the Script

In the opened terminal/command prompt:

```python
python3 main.py
```

## Multiple Bots

If you want two threads drawing the image at once you could have a setup like this:

```text
ENV_PLACE_USERNAME='["Usename1", "Username2]'
ENV_PLACE_PASSWORD='["Password1", "Password2"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'
```

The same pattern can be used for multiple drawing at once. Note that the `ENV_PLACE_USERNAME`, `ENV_PLACE_PASSWORD` must have matching lengths! The passwords must match the accounts in order!

## Other Settings

```text
ENV_THREAD_DELAY='0'
ENV_UNVERIFIED_PLACE_FREQUENCY='True'
```

- `ENV_THREAD_DELAY` Adds a delay between starting a new thread. Can be used to spread out places over the 5-minute rate limit.
- `ENV_UNVERIFIED_PLACE_FREQUENCY` is for setting the pixel place frequency to the unverified account frequency (20 minutes)

- Transparency can be achieved by using the RGB value (69, 42, 0) in any part of your image
- If you'd like, you can enable Verbose Mode by adding --verbose to "python main.py". This will output a lot more information, and not neccessarily in the right order, but it is useful for development and debugging.
