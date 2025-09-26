import os
import sys
import subprocess

def setup_directories():
    directories = [
        "artifacts",
        "artifacts/screenshots",
        "artifacts/dom_snapshots",
        "artifacts/logs",
        "artifacts/network",
        "reports"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✓ Directories created")

def create_env_file():
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        print("✓ Created .env file - please add your OpenAI API key if you have one")
    else:
        print("✓ .env file already exists")

def check_playwright():
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "--help"], 
                      capture_output=True, check=True)
        print("✓ Playwright is installed")
    except:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install"])

def main():
    print("Setting up Multi-Agent Game Tester POC...")
    print("=" * 50)
    
    setup_directories()
    create_env_file()
    check_playwright()
    
    print("=" * 50)
    print("Starting server...")
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()