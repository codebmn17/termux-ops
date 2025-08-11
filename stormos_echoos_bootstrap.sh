#!/data/data/com.termux/files/usr/bin/bash
# === StormOS + EchoOS Ultimate Bootstrap ===
# Architect Override — Full Home + UI in One Go

echo "🚀 Starting StormOS + EchoOS Ultimate Bootstrap..."

# 0. Update and install essentials
pkg update -y && pkg upgrade -y
pkg install -y git openssh curl unzip clang cmake ninja openjdk-17

# 1. Ensure SSH directory exists
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 2. Generate SSH key if not already there
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "🔑 Generating new SSH key..."
    ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519 -N ""
    chmod 600 ~/.ssh/id_ed25519
    chmod 644 ~/.ssh/id_ed25519.pub
else
    echo "✅ SSH key already exists — skipping."
fi

# 3. Start SSH agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 4. Display SSH key for GitHub
echo "=== COPY THIS KEY INTO GITHUB SSH KEYS ==="
cat ~/.ssh/id_ed25519.pub
echo "=========================================="
echo "📌 Go to: GitHub → Settings → SSH and GPG Keys → New SSH Key"
echo "Name it: StormOS-EchoOS"
echo "Paste the above key & Save"

# 5. Clone or link your repo
if [ ! -d ~/aip-community-registry ]; then
    echo "📂 Cloning your GitHub repo..."
    git clone git@github.com:codebmn17/aip-community-registry.git ~/aip-community-registry
else
    echo "🔗 Repo already exists — switching to SSH remote..."
    cd ~/aip-community-registry || exit
    git remote set-url origin git@github.com:codebmn17/aip-community-registry.git
fi

# 6. Test GitHub SSH connection
echo "🔍 Testing SSH connection to GitHub..."
ssh -T git@github.com || echo "⚠️ Make sure you added the SSH key to GitHub."

# 7. Install Flutter SDK
if [ ! -d ~/flutter ]; then
    echo "📦 Installing Flutter SDK..."
    cd ~
    curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.22.1-stable.tar.xz
    tar xf flutter_linux_3.22.1-stable.tar.xz
    rm flutter_linux_3.22.1-stable.tar.xz
    echo 'export PATH="$HOME/flutter/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/flutter/bin:$PATH"
else
    echo "✅ Flutter SDK already installed."
fi

# 8. Create EchoOS Flutter app
if [ ! -d ~/aip-community-registry/echoos_ui ]; then
    echo "🎨 Creating EchoOS Flutter app..."
    cd ~/aip-community-registry
    flutter create echoos_ui
    cd echoos_ui
    # Apply purple-galaxy theme
    sed -i 's/primarySwatch: Colors.blue/primarySwatch: Colors.deepPurple/g' lib/main.dart
else
    echo "✅ EchoOS Flutter app already exists."
fi

# 9. Final output
echo "-----------------------------------------"
echo "🌌 StormOS + EchoOS Bootstrap Complete!"
echo "-----------------------------------------"
echo "1️⃣ Add the printed SSH key to GitHub (if not already done)"
echo "2️⃣ Test GitHub: ssh -T git@github.com"
echo "3️⃣ Build EchoOS APK: "
echo "cd ~/aip-community-registry/echoos_ui && flutter build apk --release"
echo "4️⃣ Install APK on your phone: "
echo "Find it in: build/app/outputs/flutter-apk/app-release.apk"
echo "-----------------------------------------"
