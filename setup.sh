#!/bin/bash

# ShopGenie Bot Setup Script
# This script sets up a virtual environment and installs dependencies

echo "🤖 ShopGenie Bot - Setup Script"
echo "================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv shopgenie_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source shopgenie_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To run the bot:"
echo "1. Activate the virtual environment:"
echo "   source shopgenie_env/bin/activate"
echo ""
echo "2. Configure your bot token:"
echo "   cp env.example .env"
echo "   # Edit .env and add your TELEGRAM_BOT_TOKEN"
echo ""
echo "3. Test the bot:"
echo "   python test_bot.py"
echo ""
echo "4. Run the bot:"
echo "   python main.py                # Normal mode"
echo "   python run_dev.py             # Development mode with auto-reload"
echo ""
echo "5. When you're done, deactivate the virtual environment:"
echo "   deactivate"
echo ""
echo "💡 Next time, just run 'source shopgenie_env/bin/activate' to start working!"