"""
NanoServer v1.2.0 - Lightweight PHP Development Environment
Main UI module using CustomTkinter.

Cross-platform compatible (Windows/Linux/macOS).
Refactored based on community feedback.
"""

import customtkinter as ctk
import webbrowser
import os
import logging
from tkinter import filedialog, messagebox

# Configure logging before importing our modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
from config import Config
from server import PHPServer, check_php_installed
from database import DatabaseManager

# --- UI Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

VERSION = "1.2.0"


class NanoServerApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.config = Config()
        self.server = PHPServer(on_log=self.append_log)
        self.database = DatabaseManager()
        self.php_available = check_php_installed()
        
        # Window Settings
        self.title(f"NanoServer v{VERSION} - Pro Edition")
        self.geometry(self.config.get("window_geometry", "700x780"))
        self.minsize(600, 700)  # Minimum size to show all elements
        
        # State
        self.project_root = self.config.last_project or os.getcwd()
        self.is_laravel = False
        
        self.create_widgets()
        self.check_project_type()
        
        # Show PHP warning if not installed
        if not self.php_available:
            self.after(500, self.show_php_warning)
        
        logger.info(f"NanoServer v{VERSION} started")
    
    def create_widgets(self):
        """Create all UI widgets."""
        # 1. Header
        self.label_title = ctk.CTkLabel(
            self, text="NanoServer", 
            font=("Roboto", 24, "bold")
        )
        self.label_title.pack(pady=10)
        
        self.label_subtitle = ctk.CTkLabel(
            self, 
            text="Lightweight PHP Development Environment",
            text_color="gray"
        )
        self.label_subtitle.pack(pady=0)
        
        self.label_family = ctk.CTkLabel(
            self, 
            text="Part of the Nano Product Family",
            font=("Roboto", 10),
            text_color="#00CED1"  # Nano cyan
        )
        self.label_family.pack(pady=(0, 5))
        
        # 2. Server Control Section
        self.frame_web = ctk.CTkFrame(self)
        self.frame_web.pack(pady=10, padx=20, fill="x")
        
        self.label_web = ctk.CTkLabel(
            self.frame_web, 
            text="Server Control",
            font=("Roboto", 16, "bold")
        )
        self.label_web.pack(pady=8)
        
        self.btn_folder = ctk.CTkButton(
            self.frame_web,
            text="Select Project Folder",
            command=self.select_folder
        )
        self.btn_folder.pack(pady=5)
        
        self.label_folder = ctk.CTkLabel(
            self.frame_web,
            text=f"Path: {self.project_root}",
            text_color="#aaaaaa",
            wraplength=600
        )
        self.label_folder.pack(pady=5)
        
        self.label_status = ctk.CTkLabel(
            self.frame_web,
            text="Mode: Standard PHP/HTML",
            text_color="#4caf50"
        )
        self.label_status.pack(pady=5)
        
        # Button container
        self.frame_btns = ctk.CTkFrame(self.frame_web, fg_color="transparent")
        self.frame_btns.pack(pady=10)
        
        self.btn_toggle = ctk.CTkButton(
            self.frame_btns,
            text="Start Server",
            fg_color="green",
            hover_color="darkgreen",
            command=self.toggle_server,
            width=140
        )
        self.btn_toggle.pack(side="left", padx=10)
        
        self.btn_restart = ctk.CTkButton(
            self.frame_btns,
            text="Restart",
            fg_color="#e67e22",
            hover_color="#d35400",
            command=self.restart_server,
            width=140,
            state="disabled"
        )
        self.btn_restart.pack(side="left", padx=10)
        
        self.btn_open_browser = ctk.CTkButton(
            self.frame_web,
            text="Open in Browser",
            fg_color="#34495e",
            command=self.open_browser
        )
        self.btn_open_browser.pack(pady=5)
        
        # 3. Server Log Section (NEW in v1.2.0)
        self.frame_log = ctk.CTkFrame(self)
        self.frame_log.pack(pady=5, padx=20, fill="both", expand=True)
        
        self.label_log = ctk.CTkLabel(
            self.frame_log,
            text="Server Log",
            font=("Roboto", 14, "bold")
        )
        self.label_log.pack(pady=5)
        
        self.textbox_log = ctk.CTkTextbox(
            self.frame_log,
            height=120,
            font=("Consolas", 11),
            state="disabled"
        )
        self.textbox_log.pack(pady=5, padx=10, fill="both", expand=True)
        
        # 4. Database Section
        self.frame_db = ctk.CTkFrame(self)
        self.frame_db.pack(pady=5, padx=20, fill="x")
        
        self.label_db = ctk.CTkLabel(
            self.frame_db,
            text="Quick SQLite Manager",
            font=("Roboto", 14, "bold")
        )
        self.label_db.pack(pady=5)
        
        self.entry_sql = ctk.CTkEntry(
            self.frame_db,
            placeholder_text="SQL Query (e.g., SELECT * FROM users)",
            width=500
        )
        self.entry_sql.pack(pady=5)
        self.entry_sql.bind("<Return>", lambda e: self.run_sql())  # Enter key support
        
        self.btn_run_sql = ctk.CTkButton(
            self.frame_db,
            text="Run SQL",
            command=self.run_sql
        )
        self.btn_run_sql.pack(pady=5)
        
        self.label_sql_result = ctk.CTkLabel(
            self.frame_db,
            text="Result: -",
            text_color="#aaaaaa"
        )
        self.label_sql_result.pack(pady=5)
    
    # --- Server Functions ---
    
    def select_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory(initialdir=self.project_root)
        if folder:
            self.project_root = folder
            self.config.last_project = folder  # Save to config
            self.check_project_type()
            self.label_folder.configure(text=f"Path: {self.project_root}")
            logger.info(f"Project folder selected: {folder}")
    
    def check_project_type(self):
        """Detect if project is Laravel or standard PHP."""
        artisan_path = os.path.join(self.project_root, 'artisan')
        
        if os.path.exists(artisan_path):
            self.is_laravel = True
            self.server.document_root = os.path.join(self.project_root, 'public')
            self.label_status.configure(
                text="Mode: Laravel Framework Detected",
                text_color="#ff2d20"
            )
            
            # Find Laravel database
            laravel_db = os.path.join(self.project_root, 'database', 'database.sqlite')
            if os.path.exists(laravel_db):
                self.database.set_database(laravel_db)
        else:
            self.is_laravel = False
            self.server.document_root = self.project_root
            self.label_status.configure(
                text="Mode: Standard PHP/HTML",
                text_color="#4caf50"
            )
            
            # Default database path
            default_db = os.path.join(self.project_root, 'database.sqlite')
            if os.path.exists(default_db):
                self.database.set_database(default_db)
    
    def toggle_server(self):
        """Start or stop the server."""
        if not self.server.is_running:
            self.start_server()
        else:
            self.stop_server()
    
    def start_server(self):
        """Start the PHP server."""
        if not self.php_available:
            self.show_php_warning()
            return
        
        doc_root = self.server.document_root
        if self.server.start(doc_root, self.config.port):
            self.btn_toggle.configure(
                text="Stop Server",
                fg_color="red",
                hover_color="darkred"
            )
            self.btn_restart.configure(state="normal")
            self.btn_open_browser.configure(
                text=f"Open (:{self.server.port})"
            )
    
    def stop_server(self):
        """Stop the PHP server."""
        self.server.stop()
        self.btn_toggle.configure(
            text="Start Server",
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_restart.configure(state="disabled")
        self.btn_open_browser.configure(text="Open in Browser")
    
    def restart_server(self):
        """Restart the server."""
        self.stop_server()
        self.after(500, self.start_server)
    
    def open_browser(self):
        """Open server URL in default browser."""
        webbrowser.open(self.server.url)
    
    def append_log(self, message: str):
        """Append a message to the log textbox (thread-safe)."""
        def _append():
            self.textbox_log.configure(state="normal")
            self.textbox_log.insert("end", message + "\n")
            self.textbox_log.see("end")  # Auto-scroll
            self.textbox_log.configure(state="disabled")
        
        # Schedule on main thread
        self.after(0, _append)
    
    def show_php_warning(self):
        """Show warning if PHP is not installed."""
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
        self.label_status.configure(
            text="Status: PHP Not Found!",
            text_color="#e74c3c"
        )
    
    # --- Database Functions ---
    
    def run_sql(self):
        """Execute SQL query from input field."""
        query = self.entry_sql.get().strip()
        if not query:
            return
        
        success, result = self.database.execute(query)
        
        if success:
            if 'rows' in result:
                count = result['count']
                self.label_sql_result.configure(
                    text=f"Rows returned: {count}",
                    text_color="#4caf50"
                )
                # Log results
                self.append_log(f"\n[SQL] {query}")
                for row in result['rows'][:10]:  # Limit display
                    self.append_log(f"  {row}")
                if count > 10:
                    self.append_log(f"  ... and {count - 10} more rows")
            else:
                affected = result.get('affected', 0)
                self.label_sql_result.configure(
                    text=f"Query OK, {affected} rows affected",
                    text_color="#4caf50"
                )
        else:
            self.label_sql_result.configure(
                text=f"Error: {result}",
                text_color="#e74c3c"
            )
    
    # --- Window Functions ---
    
    def on_closing(self):
        """Clean up before closing."""
        if self.server.is_running:
            self.server.stop()
        
        # Save window geometry
        self.config.set("window_geometry", self.geometry())
        
        logger.info("NanoServer closed")
        self.destroy()


if __name__ == "__main__":
    app = NanoServerApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()