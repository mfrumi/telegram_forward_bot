# Installation Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- Telegram account with API credentials

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-forward-bot.git
cd telegram-forward-bot
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click on "API Development Tools"
4. Create a new application:
   - App title: Your Bot Name
   - Short name: your_bot_name
   - URL: (optional)
   - Platform: Desktop
   - Description: (optional)
5. Copy your `API ID` and `API Hash`

### 5. Get Group IDs

1. Add [@userinfobot](https://t.me/userinfobot) to both your source and destination groups
2. Send any message in each group
3. The bot will reply with group information
4. Copy the Group ID (negative number like -1001234567890)

### 6. Get Your User ID

1. Send a message to [@userinfobot](https://t.me/userinfobot) in private
2. Copy your User ID (positive number)

### 7. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration file
nano .env  # or use your preferred editor
```

Fill in the following values in `.env`:

```env
API_ID=your_api_id_here
API_HASH=your_api_hash_here
PHONE_NUMBER=+1234567890
SOURCE_GROUP_ID=-1001234567890
DESTINATION_GROUP_ID=-1001234567890
CHANNEL_LINK=https://t.me/your_channel
REFERENCE_TEXT=📢 Forwarded by @YourBot
ADMIN_USER_ID=123456789
SESSION_NAME=telegram_forward_bot
```

### 8. Test Installation

```bash
# Test if all dependencies are installed
python3 -c "import telethon, dotenv; print('All dependencies installed successfully!')"

# Test configuration
python3 run.py --test-config  # (if implemented)
```

### 9. First Run

```bash
# Start the bot
python3 run.py
```

On first run:
1. Enter your phone number when prompted
2. Enter the verification code sent to your Telegram
3. If you have 2FA enabled, enter your password
4. The bot will create a session file for future runs

### 10. Verify Installation

1. Check if the bot sends you a startup notification
2. Send `/status` to the bot to check if it's working
3. Send `/help` to see all available commands

## Troubleshooting

### Common Installation Issues

#### Python Version Error
```
Error: Python 3.7 or higher is required
```
**Solution**: Update Python to version 3.7 or higher

#### Permission Denied Error
```
Error: Permission denied when installing packages
```
**Solution**: Use virtual environment or install with `--user` flag:
```bash
pip install --user -r requirements.txt
```

#### Module Not Found Error
```
ModuleNotFoundError: No module named 'telethon'
```
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### API Credentials Error
```
Error: Invalid API credentials
```
**Solution**: 
- Verify API_ID and API_HASH are correct
- Check for extra spaces or quotes in .env file
- Ensure you're using the correct Telegram account

#### Group Access Error
```
Error: Cannot access group
```
**Solution**:
- Verify group IDs are correct (negative numbers)
- Ensure your account is a member of both groups
- Check if groups allow bots/automation

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for usage instructions
2. Configure your bot settings in the `.env` file
3. Start the bot with `python3 run.py`
4. Send admin commands to control the bot
5. Monitor the bot logs for any issues

## Support

If you encounter issues during installation:

1. Check this troubleshooting section
2. Review the [README.md](README.md) documentation
3. Check the GitHub issues page
4. Create a new issue with detailed error information

