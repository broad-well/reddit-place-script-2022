# Reddit Place Script 2023

## About

This is a script to draw an image onto r/place (<https://www.reddit.com/r/place/>) with a botnet's control.

## Installation Video (Windows)

[Watch the installation video](https://cdn.discordapp.com/attachments/959639366127480842/1131997818643550248/2023-07-21_13-09-47.mp4), install [Tor Browser](https://www.torproject.org/download/), open it, and connect to Tor through it.

## Requirements

- [Python 3](https://www.python.org/downloads/)
    - Run `python3 --version` in the terminal to check that you have it installed
- [Tor Browser](https://www.torproject.org/download/)
    - Tor Browser **MUST** be open and connected. If you see "Connection refused" as an error, connect Tor Browser.

## Download the bot

[Download](https://github.com/broad-well/reddit-place-umich-botnet/archive/refs/heads/main.zip) this repository as a zip file, and extract it to a location of choice.

Navigate to this location in Windows Terminal (Windows) or Terminal (macOS).

## Python Package Requirements

**Optional**
Create a virtual environment so the installed packages don't pollute your system.
This step is optional. It just helps you organize your Python packages better.

```shell
python3 -m venv env

# Linux/macOS users, run this
. env/bin/activate

# Windows users, run this
env\Scripts\activate.bat
```

Install requirements from 'requirements.txt' file.

```shell
pip3 install -r requirements.txt
```

## Get Started

Make a copy of `.env_TEMPLATE` called `.env`, and place it in the project directory.

Put in the following contents:

```text
ENV_PLACE_USERNAME='["username"]'
ENV_PLACE_PASSWORD='["password"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'
```

- ENV_PLACE_USERNAME is an array of usernames of Reddit accounts
- ENV_PLACE_PASSWORD is an array of the passwords of Reddit accounts, aligned with ENV_PLACE_USERNAME
- ENV_DIRECTOR_URL is the URL of the Botnet Director

## Run the Script

```python
python3 main.py
```

## Multiple Bots

If you want two threads drawing the image at once you could have a setup like this:

```text
ENV_PLACE_USERNAME='["username_1", "username_2"]'
ENV_PLACE_PASSWORD='["password_1", "password_2"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'
```

The same pattern can be used for multiple drawing at once. Note that the "ENV_PLACE_USERNAME", "ENV_PLACE_PASSWORD" variables MUST be string arrays of the same size.

## Other Settings

```text
ENV_THREAD_DELAY='0'
ENV_UNVERIFIED_PLACE_FREQUENCY='True'
```

- ENV_THREAD_DELAY Adds a delay between starting a new thread. Can be used to spread out places over the 5-minute rate limit.
- ENV_UNVERIFIED_PLACE_FREQUENCY is for setting the pixel place frequency to the unverified account frequency (20 minutes)

- Transparency can be achieved by using the RGB value (69, 42, 0) in any part of your image
- If you'd like, you can enable Verbose Mode by adding --verbose to "python main.py". This will output a lot more information, and not neccessarily in the right order, but it is useful for development and debugging.
