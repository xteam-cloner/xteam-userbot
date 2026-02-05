#!/bin/bash

echo "⚙️ Updating system..."
apt update && apt upgrade -y

echo "🐍 Installing Python and Pip..."
apt install -y python3 python3-pip python3-venv

echo "🟢 Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

echo "🎬 Installing FFMPEG..."
apt install -y ffmpeg

if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python requirements..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "⚠️ requirements.txt not found! Skipping pip installation."
fi

echo "✅ ALL DONE! Your bot is ready to run."
