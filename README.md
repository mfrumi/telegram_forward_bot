# Telegram Auto-Forward Bot

A powerful Python-based Telegram bot that automatically forwards messages from one group to another with advanced message processing, link removal, custom reference addition, and comprehensive admin controls.

## 🌟 Features

### Core Functionality
- **Auto Message Forwarding**: Automatically forwards messages from source group to destination group
- **Link Removal**: Removes all types of links (HTTP/HTTPS, Telegram links, @mentions) from messages
- **Custom Reference**: Adds your custom reference text to each forwarded message
- **Channel Button**: Attaches a custom channel button to each forwarded message
- **User Mode Operation**: Operates as a user account (not bot account) for better group access

### Advanced Features
- **Admin Controls**: Comprehensive admin command system for bot management
- **Real-time Monitoring**: Live status monitoring and statistics tracking
- **Error Logging**: Detailed error logging and reporting system
- **Message Filtering**: Smart message filtering based on length and content
- **Media Support**: Optional media forwarding with messages
- **Configuration Management**: Easy configuration via environment variables

### Admin Commands
- `/start` - Start message forwarding
- `/stop` - Stop message forwarding
- `/status` - View current bot status
- `/stats` - View detailed statistics
- `/config` - View bot configuration
- `/logs` - View recent error logs
- `/test` - Test bot connection and configuration
- `/help` - Show help message
- `/reset_stats` - Reset bot statistics
- `/update_reference <text>` - Update reference text
- `/update_channel <link>` - Update channel link

## 📋 Requirements

- Python 3.7 or higher
- Telegram API credentials (API ID and API Hash)
- Access to source and destination Telegram groups
- Admin privileges in destination group (recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-forward-bot.git
cd telegram-forward-bot
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

### 4. Run the Bot

```bash
# Using the run script
python3 run.py

# Or using the shell script
./scripts/start.sh
```


## ⚙️ Configuration

### Getting Telegram API Credentials

1. Visit [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy your `API ID` and `API Hash`

### Getting Group IDs

1. Add [@userinfobot](https://t.me/userinfobot) to your groups
2. Send any message in the group
3. The bot will reply with group information including the Group ID
4. Use the negative Group ID (e.g., -1001234567890)

### Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram API Credentials (Get from https://my.telegram.org)
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Phone number associated with your Telegram account
PHONE_NUMBER=+1234567890

# Group/Channel IDs (Get using @userinfobot)
SOURCE_GROUP_ID=-1001234567890
DESTINATION_GROUP_ID=-1001234567890

# Your Channel Link (for button attachment)
CHANNEL_LINK=https://t.me/your_channel

# Your Reference Text (added to forwarded messages)
REFERENCE_TEXT=📢 Forwarded by @YourBot

# Admin User ID (Your Telegram User ID)
ADMIN_USER_ID=123456789

# Bot Session Name
SESSION_NAME=telegram_forward_bot

# Optional Settings
MIN_MESSAGE_LENGTH=10
MAX_MESSAGE_LENGTH=4000
FORWARD_MEDIA=true
LOG_LEVEL=INFO
```

## 🏗️ Project Structure

```
telegram_forward_bot/
├── src/
│   ├── main.py              # Enhanced main bot application
│   ├── bot.py               # Original bot implementation
│   ├── config.py            # Configuration management
│   ├── message_processor.py # Message processing utilities
│   └── admin.py             # Admin controls and monitoring
├── scripts/
│   ├── start.sh             # Start script
│   ├── stop.sh              # Stop script
│   └── restart.sh           # Restart script
├── .env.example             # Example environment file
├── .gitignore               # Git ignore file
├── requirements.txt         # Python dependencies
├── setup.py                 # Setup script
├── run.py                   # Main run script
├── README.md                # This file
└── todo.md                  # Development todo list
```

## 🔧 Usage

### Starting the Bot

```bash
# Method 1: Using Python directly
python3 run.py

# Method 2: Using shell script
./scripts/start.sh

# Method 3: Using setup.py (after installation)
telegram-forward-bot
```

### First Run Setup

1. **Authentication**: On first run, the bot will ask for your phone number and verification code
2. **Session File**: A session file will be created to store authentication
3. **Group Verification**: The bot will verify access to both source and destination groups
4. **Admin Notification**: You'll receive a startup notification with bot status

### Managing the Bot

The bot provides comprehensive admin commands accessible only to the configured admin user:

#### Basic Controls
- Send `/start` to begin message forwarding
- Send `/stop` to pause message forwarding
- Send `/status` to check current bot status

#### Monitoring
- Send `/stats` for detailed statistics
- Send `/logs` to view recent errors
- Send `/config` to view current configuration

#### Configuration Updates
- Send `/update_reference New reference text` to change reference
- Send `/update_channel https://t.me/newchannel` to change channel link

### Message Processing

The bot processes messages through several stages:

1. **Message Reception**: Listens for new messages in the source group
2. **Filtering**: Checks message length and content quality
3. **Link Removal**: Removes all HTTP/HTTPS links, Telegram links, and @mentions
4. **Text Cleaning**: Cleans excessive formatting and special characters
5. **Reference Addition**: Adds your custom reference text
6. **Button Attachment**: Adds inline keyboard with channel button
7. **Forwarding**: Sends processed message to destination group

## 🚀 Deployment

### Local Deployment

1. **Development Setup**:
   ```bash
   git clone <repository-url>
   cd telegram-forward-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Configure .env file
   python3 run.py
   ```

2. **Production Setup**:
   ```bash
   # Install as system service (systemd example)
   sudo cp telegram-forward-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable telegram-forward-bot
   sudo systemctl start telegram-forward-bot
   ```

### GitHub Deployment

1. **Repository Setup**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/telegram-forward-bot.git
   git push -u origin main
   ```

2. **Environment Configuration**:
   - Never commit `.env` file to repository
   - Use GitHub Secrets for sensitive data in Actions
   - Configure environment variables on your deployment platform

### Cloud Deployment Options

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-bot-name
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
# Set other environment variables
git push heroku main
```

#### VPS/Server
```bash
# Clone repository on server
git clone https://github.com/yourusername/telegram-forward-bot.git
cd telegram-forward-bot

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Run with screen or tmux
screen -S telegram-bot
python3 run.py
# Ctrl+A, D to detach
```

## 🔍 Troubleshooting

### Common Issues

#### Authentication Problems
```
Error: Could not connect to Telegram
```
**Solution**: 
- Verify API_ID and API_HASH are correct
- Check phone number format (+1234567890)
- Delete session file and re-authenticate

#### Group Access Issues
```
Error: Could not access source/destination group
```
**Solution**:
- Verify group IDs are correct (negative numbers)
- Ensure your account is member of both groups
- Check if groups allow message forwarding

#### Permission Errors
```
Error: Bot cannot send messages to destination group
```
**Solution**:
- Ensure your account has permission to send messages
- Check if destination group has restrictions
- Verify bot is not banned or restricted

### Debug Mode

Enable debug logging by setting in `.env`:
```env
LOG_LEVEL=DEBUG
```

### Log Files

- **`bot.log`**: Main application log
- Session files: `telegram_forward_bot.session*`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Issues](https://github.com/yourusername/telegram-forward-bot/issues) page
3. Create a new issue with detailed information

## 🔄 Updates

To update the bot to the latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
./scripts/restart.sh
```

## ⚠️ Disclaimer

This bot is for educational and legitimate use only. Please ensure you comply with:
- Telegram's Terms of Service
- Local laws and regulations
- Group/channel rules and permissions
- Privacy and data protection laws

The developers are not responsible for any misuse of this software.

---

**Made with ❤️ by Manus AI**

