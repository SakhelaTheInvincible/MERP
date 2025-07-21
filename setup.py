import os
import sys
import subprocess
from pathlib import Path

def create_virtualenv():
    print("\nCreating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created successfully.")
    except subprocess.CalledProcessError:
        print("Error creating virtual environment.")
        sys.exit(1)

def activate_virtualenv():
    print("\nActivating virtual environment...")
    if sys.platform == "win32":
        activate_script = Path("venv/Scripts/activate")
    else:
        activate_script = Path("venv/bin/activate")
    
    if not activate_script.exists():
        print("Virtual environment activation script not found.")
        sys.exit(1)
    
    print(f"Run the following command to activate the virtual environment:")
    if sys.platform == "win32":
        print(f"  venv\\Scripts\\activate")
    else:
        print(f"  source venv/bin/activate")

def install_dependencies():
    print("\nInstalling dependencies...")
    try:
        subprocess.run([
            "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing dependencies.")
        sys.exit(1)

def run_migrations():
    print("\nRunning migrations...")
    try:
        subprocess.run([
            "python", "manage.py", "makemigrations", "events"
        ], check=True)
        subprocess.run([
            "python", "manage.py", "migrate"
        ], check=True)
        print("Migrations completed successfully.")
    except subprocess.CalledProcessError:
        print("Error running migrations.")
        sys.exit(1)

def create_superuser():
    print("\nCreating superuser...")
    try:
        subprocess.run([
            "python", "manage.py", "createsuperuser"
        ], check=True)
    except subprocess.CalledProcessError:
        print("Superuser creation skipped or failed.")

def create_directories():
    print("\nCreating required directories...")
    directories = ["static", "media"]
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except OSError as e:
            print(f"Error creating directory {directory}: {e}")

def main():
    print("Setting up Django project...")
    
    # Step 1: Create virtual environment
    create_virtualenv()
    
    # Step 2: Show activation instructions
    activate_virtualenv()
    
    # Step 3: Install dependencies
    install_dependencies()
    
    # Step 4: Run migrations
    run_migrations()
    
    # Step 5: Create superuser (optional)
    create_superuser_input = input("\nDo you want to create a superuser? (y/n): ").strip().lower()
    if create_superuser_input == 'y':
        create_superuser()
    
    # Step 6: Create required directories
    create_directories()
    
    print("\nSetup completed successfully!")
    print("Remember to activate your virtual environment before working on the project.")

if __name__ == "__main__":
    main()