#!/usr/bin/env python3
"""
Live Keyboard Input Detector for Termux
Detects individual keypresses without requiring Enter key
"""

import sys
import os
import termios
import tty
import select
import signal

class KeyboardDetector:
    def __init__(self):
        self.old_settings = None
        self.running = True
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C and termination signals"""
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def setup_terminal(self):
        """Configure terminal for raw input mode"""
        try:
            # Save current terminal settings
            self.old_settings = termios.tcgetattr(sys.stdin)
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
        except termios.error:
            print("Error: Unable to set terminal to raw mode")
            print("Make sure you're running this in Termux terminal")
            sys.exit(1)
    
    def cleanup(self):
        """Restore terminal to original settings"""
        if self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except:
                pass
    
    def get_key(self):
        """Get a single keypress without waiting for Enter"""
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.read(1)
            return key
        return None
    
    def parse_key(self, key):
        """Parse and identify special keys"""
        if key == '\x1b':  # ESC or escape sequence
            # Check for escape sequences (arrow keys, etc.)
            if select.select([sys.stdin], [], [], 0.01)[0]:
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        next2 = sys.stdin.read(1)
                        if next2 == 'A':
                            return 'UP_ARROW'
                        elif next2 == 'B':
                            return 'DOWN_ARROW'
                        elif next2 == 'C':
                            return 'RIGHT_ARROW'
                        elif next2 == 'D':
                            return 'LEFT_ARROW'
                        elif next2 == 'H':
                            return 'HOME'
                        elif next2 == 'F':
                            return 'END'
                        else:
                            return f'ESC[{next2}'
                else:
                    return 'ESC'
            else:
                return 'ESC'
        
        elif key == '\x7f':  # Backspace
            return 'BACKSPACE'
        elif key == '\t':  # Tab
            return 'TAB'
        elif key == '\r':  # Enter
            return 'ENTER'
        elif key == ' ':  # Space
            return 'SPACE'
        elif key == '\x03':  # Ctrl+C
            return 'CTRL_C'
        elif key == '\x04':  # Ctrl+D
            return 'CTRL_D'
        elif key == '\x1a':  # Ctrl+Z
            return 'CTRL_Z'
        else:
            return key
    
    def run(self):
        """Main loop to detect keyboard input"""
        print("Live Keyboard Input Detector for Termux")
        print("=" * 40)
        print("Press keys to detect (Ctrl+C to exit)")
        print("Press 'q' to quit")
        print("-" * 40)
        
        self.setup_terminal()
        
        key_count = 0
        
        try:
            while self.running:
                key = self.get_key()
                
                if key:
                    parsed_key = self.parse_key(key)
                    
                    # Format output based on key type
                    if parsed_key in ['UP_ARROW', 'DOWN_ARROW', 'RIGHT_ARROW', 
                                     'LEFT_ARROW', 'HOME', 'END']:
                        print(f"\r→ {parsed_key} (Special key)      ")
                    elif parsed_key in ['BACKSPACE', 'TAB', 'ENTER', 'SPACE', 'ESC']:
                        print(f"\r→ {parsed_key} (Control key)     ")
                    elif parsed_key.startswith('CTRL_'):
                        print(f"\r→ {parsed_key}                    ")
                    else:
                        key_count += 1
                        hex_val = ord(parsed_key)
                        print(f"\r→ '{parsed_key}' (ASCII: {hex_val}, Hex: 0x{hex_val:02x})    ")
                    
                    # Check for quit command
                    if parsed_key == 'q':
                        print("\nQuit key pressed. Exiting...")
                        break
        
        except Exception as e:
            print(f"\nError: {e}")
        
        finally:
            self.cleanup()
            print(f"\nTotal regular keys pressed: {key_count}")
            print("Keyboard detector stopped.")

def main():
    """Main function with interactive menu"""
    detector = KeyboardDetector()
    
    print("\n" + "="*50)
    print("KEYBOARD INPUT DETECTOR FOR TERMUX")
    print("="*50)
    print("\nOptions:")
    print("1. Start live key detection")
    print("2. Show raw key values (debug mode)")
    print("3. Exit")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '2':
            print("\nDEBUG MODE - Raw key values")
            print("Press keys to see raw bytes (Ctrl+C to exit)")
            print("-" * 40)
            
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
            
            try:
                while True:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        byte = sys.stdin.read(1)
                        print(f"Raw byte: 0x{ord(byte):02x} ({repr(byte)})")
                        print("")
                        if byte == '\x03':  # Ctrl+C
                            break
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                
        elif choice == '1':
            detector.run()
        elif choice == '3':
            print("Exiting...")
        else:
            print("Invalid choice. Exiting...")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
