# Reddit Place Script 2022

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Message the bot channel on Discord if you have any questions regarding setup/errors.**

## About

This is a script to draw a JPG onto r/place (<https://www.reddit.com/r/place/>).

## Requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
    - Needed for the auto-pull image feature
    - Run `git --version` in the terminal to check that you have it installed
- [Python 3](https://www.python.org/downloads/)
    - Run `python3 --version` in the terminal to check that you have it installed

## Clone This Project!
In your terminal, `cd` into any directory you like, then run
```
git clone https://github.com/jc65536/reddit-place-script-2022.git
```

Go into the project directory with cd:
```
cd reddit-place-script-2022
```

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
ENV_PLACE_USERNAME='["developer_username"]'
ENV_PLACE_PASSWORD='["developer_password"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'
```

- ENV_PLACE_USERNAME is an array of usernames of developer accounts
- ENV_PLACE_PASSWORD is an array of the passwords of developer accounts
- ENV_DIRECTOR_URL is the URL of the Botnet Director. Do not change.

## Run the Script

```python
python3 main.py
```

## Multiple Bots

If you want two threads drawing the image at once you could have a setup like this:

```text
ENV_PLACE_USERNAME='["developer_username_1", "developer_username_2"]'
ENV_PLACE_PASSWORD='["developer_password_1", "developer_password_2"]'
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
