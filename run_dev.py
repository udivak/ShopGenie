"""
Development runner for ShopGenie bot with auto-reload functionality.
"""
import sys
import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

class BotReloader(FileSystemEventHandler):
    """File system event handler for auto-reloading the bot."""
    
    def __init__(self):
        self.process = None
        self.restart_bot()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        # Only reload for Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Ignore __pycache__ and other temp files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return
        
        print(f"\n🔄 File changed: {event.src_path}")
        print("♻️  Restarting bot...")
        self.restart_bot()
    
    def restart_bot(self):
        """Restart the bot process."""
        # Kill existing process
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except:
                pass
        
        # Start new process
        try:
            self.process = subprocess.Popen([
                sys.executable, 'main.py'
            ], cwd=Path(__file__).parent)
            print(f"🚀 Bot started with PID: {self.process.pid}")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

def main():
    """Main function to run bot with auto-reload."""
    print("🤖 ShopGenie Bot - Development Mode with Auto-Reload")
    print("=" * 60)
    print("📁 Watching for file changes in:")
    print("   • *.py files in current directory")
    print("   • bot/ directory")
    print("   • scrapers/ directory") 
    print("   • utils/ directory")
    print("\n🔄 Bot will auto-restart when files are modified")
    print("⏹️  Press Ctrl+C to stop\n")
    
    # Setup file watcher
    event_handler = BotReloader()
    observer = Observer()
    
    # Watch current directory and subdirectories
    observer.schedule(event_handler, ".", recursive=True)
    
    try:
        observer.start()
        
        while True:
            time.sleep(1)
            
            # Check if bot process is still running
            if event_handler.process and event_handler.process.poll() is not None:
                print("⚠️  Bot process stopped unexpectedly")
                print("🔄 Restarting...")
                event_handler.restart_bot()
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping development server...")
        observer.stop()
        
        # Stop bot process
        if event_handler.process:
            try:
                event_handler.process.terminate()
                event_handler.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                event_handler.process.kill()
                event_handler.process.wait()
        
        print("👋 Development server stopped. Goodbye!")
    
    observer.join()

if __name__ == "__main__":
    main()