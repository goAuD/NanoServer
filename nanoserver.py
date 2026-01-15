import customtkinter as ctk
import subprocess
import threading
import sqlite3
import socket
import os
import webbrowser
from tkinter import filedialog, messagebox

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def check_php_installed():
    """Check if PHP is available in PATH"""
    try:
        result = subprocess.run(
            ["php", "-v"], 
            capture_output=True, 
            text=True, 
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    return None

class NanoServerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Check PHP first
        self.php_available = check_php_installed()

        # Window Settings
        self.title("NanoServer v1.1.0 - Pro Edition")
        self.geometry("700x600")
        self.resizable(False, False)

        # State Variables
        self.server_process = None
        self.is_running = False
        self.project_root = os.getcwd()
        self.server_root = os.getcwd()  # This might be /public for Laravel
        self.port = 8000
        self.db_name = "database.sqlite"
        self.is_laravel = False

        self.create_widgets()
        
        # Show PHP warning if not installed
        if not self.php_available:
            self.after(500, self.show_php_warning)

    def create_widgets(self):
        # 1. Header
        self.label_title = ctk.CTkLabel(self, text="NanoServer", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=15)

        self.label_subtitle = ctk.CTkLabel(self, text="Lightweight PHP Development Environment", text_color="gray")
        self.label_subtitle.pack(pady=0)

        # 2. Server Control Section
        self.frame_web = ctk.CTkFrame(self)
        self.frame_web.pack(pady=15, padx=20, fill="x")

        self.label_web = ctk.CTkLabel(self.frame_web, text="Server Control", font=("Roboto", 16, "bold"))
        self.label_web.pack(pady=10)

        self.btn_folder = ctk.CTkButton(self.frame_web, text="Select Project Folder", command=self.select_folder)
        self.btn_folder.pack(pady=5)

        self.label_folder = ctk.CTkLabel(self.frame_web, text=f"Path: {self.project_root}", text_color="#aaaaaa", wraplength=600)
        self.label_folder.pack(pady=5)

        self.label_status = ctk.CTkLabel(self.frame_web, text="Mode: Standard PHP/HTML", text_color="#4caf50")
        self.label_status.pack(pady=5)

        # Button container for Start and Restart
        self.frame_btns = ctk.CTkFrame(self.frame_web, fg_color="transparent")
        self.frame_btns.pack(pady=15)

        self.btn_toggle = ctk.CTkButton(self.frame_btns, text="Start Server", fg_color="green", hover_color="darkgreen", command=self.toggle_server, width=150)
        self.btn_toggle.pack(side="left", padx=10)

        self.btn_restart = ctk.CTkButton(self.frame_btns, text="Restart Server", fg_color="#e67e22", hover_color="#d35400", command=self.restart_server, width=150, state="disabled")
        self.btn_restart.pack(side="left", padx=10)

        self.btn_open_browser = ctk.CTkButton(self.frame_web, text="Open in Browser 🌐", fg_color="#34495e", command=self.open_browser)
        self.btn_open_browser.pack(pady=5)

        # 3. Database Section
        self.frame_db = ctk.CTkFrame(self)
        self.frame_db.pack(pady=10, padx=20, fill="both", expand=True)

        self.label_db = ctk.CTkLabel(self.frame_db, text="Quick SQLite Manager", font=("Roboto", 16, "bold"))
        self.label_db.pack(pady=5)
        
        self.entry_sql = ctk.CTkEntry(self.frame_db, placeholder_text="SQL Query (e.g., SELECT * FROM users)", width=500)
        self.entry_sql.pack(pady=10)

        self.btn_run_sql = ctk.CTkButton(self.frame_db, text="Run SQL", command=self.run_sql)
        self.btn_run_sql.pack(pady=5)

        self.label_sql_result = ctk.CTkLabel(self.frame_db, text="Result: -", text_color="#aaaaaa")
        self.label_sql_result.pack(pady=10)

    # --- Functions ---

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.project_root = folder
            self.check_project_type()
            self.label_folder.configure(text=f"Path: {self.project_root}")

    def check_project_type(self):
        # Check for Laravel 'artisan' file
        artisan_path = os.path.join(self.project_root, 'artisan')
        
        if os.path.exists(artisan_path):
            self.is_laravel = True
            # Laravel serves from the /public folder
            self.server_root = os.path.join(self.project_root, 'public')
            self.label_status.configure(text="Mode: Laravel Framework Detected 🚀", text_color="#ff2d20")
            
            # Try to find Laravel specific database
            laravel_db = os.path.join(self.project_root, 'database', 'database.sqlite')
            if os.path.exists(laravel_db):
                self.db_name = laravel_db
            else:
                self.db_name = "database.sqlite" # Fallback
        else:
            self.is_laravel = False
            self.server_root = self.project_root
            self.label_status.configure(text="Mode: Standard PHP/HTML", text_color="#4caf50")
            self.db_name = "database.sqlite"

    def toggle_server(self):
        if not self.is_running:
            self.start_php_server()
        else:
            self.stop_php_server()

    def show_php_warning(self):
        """Show warning if PHP is not installed"""
        messagebox.showwarning(
            "PHP Not Found",
            "PHP is not installed or not in your system PATH.\n\n"
            "To fix this:\n"
            "1. Download PHP from https://windows.php.net/download/\n"
            "2. Extract to a folder (e.g., C:\\php)\n"
            "3. Add that folder to your PATH environment variable\n"
            "4. Restart NanoServer"
        )
        self.btn_toggle.configure(state="disabled")
        self.label_status.configure(text="Status: PHP Not Found!", text_color="#e74c3c")

    def start_php_server(self):
        # Check PHP availability first
        if not self.php_available:
            self.show_php_warning()
            return
        
        # Check for port collision and find available port
        if is_port_in_use(self.port):
            new_port = find_available_port(self.port)
            if new_port is None:
                messagebox.showerror("Error", f"Ports {self.port}-{self.port + 9} are all in use. Please close other applications.")
                return
            self.port = new_port
            print(f"Port collision detected, using port {self.port}")
        
        # Construct command: php -S localhost:PORT -t "folder"
        cmd = ["php", "-S", f"localhost:{self.port}", "-t", self.server_root]
        
        try:
            # Hide console window on Windows
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.server_process = subprocess.Popen(
                cmd, 
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            self.is_running = True
            self.btn_toggle.configure(text="Stop Server", fg_color="red", hover_color="darkred")
            self.btn_restart.configure(state="normal")
            
            # Update browser button to show current port
            self.btn_open_browser.configure(text=f"Open in Browser (:{self.port})")
            
            # Print info to console
            print(f"--- Server Started ---")
            print(f"Project Root: {self.project_root}")
            print(f"Document Root: {self.server_root}")
            print(f"URL: http://localhost:{self.port}")
            
        except FileNotFoundError:
            self.php_available = False
            self.show_php_warning()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")

    def stop_php_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            
        self.is_running = False
        self.port = 8000  # Reset port for next start
        self.btn_toggle.configure(text="Start Server", fg_color="green", hover_color="darkgreen")
        self.btn_restart.configure(state="disabled")
        self.btn_open_browser.configure(text="Open in Browser")
        print("--- Server Stopped ---")

    def restart_server(self):
        # Quick restart
        self.stop_php_server()
        # Small delay might be needed, but usually instant is fine
        self.after(500, self.start_php_server)

    def open_browser(self):
        webbrowser.open(f"http://localhost:{self.port}")

    def run_sql(self):
        query = self.entry_sql.get()
        if not query: return

        # Database path logic
        if os.path.isabs(self.db_name):
            db_path = self.db_name
        else:
            db_path = os.path.join(self.project_root, self.db_name)

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                self.label_sql_result.configure(text=f"Rows returned: {len(result)} (Check Console)")
                print(f"\nSQL Result for: {query}")
                for row in result:
                    print(row)
            else:
                conn.commit()
                self.label_sql_result.configure(text="Query executed successfully!")
            
            conn.close()
        except Exception as e:
            self.label_sql_result.configure(text=f"SQL Error: {e}")

    def on_closing(self):
        if self.is_running:
            self.stop_php_server()
        self.destroy()

if __name__ == "__main__":
    app = NanoServerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()