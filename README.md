# SteamBot

A Python-based Steam client automation tool that provides programmatic access to Steam functionality using the Steam Web API and client protocols.

## Overview

SteamBot is designed to automate Steam client operations by logging into Steam accounts and performing various tasks. The bot uses Steam Guard authentication and can manage multiple user configurations.

## Features

- **Automated Steam Login**: Secure login using username, password, and Steam Guard two-factor authentication
- **Account Summary**: Retrieve and display account information including:
  - User profile details
  - Community profile URL
  - Login/logout timestamps
  - Friends list count
  - VAC ban status
- **Multi-User Support**: Manage multiple Steam accounts with individual configuration files
- **Logging**: Comprehensive logging with file output and colorized console output
- **Lock File Management**: Prevents multiple instances from running simultaneously for the same user

## Installation

Clone this repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a configuration directory (default: `~/steam_configs`)
2. Create a base configuration file: `config.json`
3. Create individual user configuration files: `{username}.json`

### Base Configuration (`config.json`)
```json
{
    "log_dir": "~/steam_logs"
}
```

### User Configuration (`{username}.json`)
```json
{
    "password": "your_steam_password",
    "steam_guard": "your_steam_guard_secret"
}
```

## Usage

Run the bot with a specific Steam username:

```bash
python steambot.py -u your_username -c /path/to/configs
```

### Command Line Options

- `-u, --username`: Steam username to use
- `-c, --configs_dir`: Directory containing configuration files (default: `~/steam_configs`)
- `-v, --verbose`: Enable verbose logging

## Security Notes

- Steam Guard secrets and passwords are stored in local configuration files
- Lock files prevent concurrent execution for the same user
- All authentication uses Steam's official protocols

## Dependencies

- `steam`: Python Steam client library
- `trulogger`: Logging utility
- Additional dependencies listed in `requirements.txt`