"""
NanoServer - Server Module
Handles PHP built-in server management.
Cross-platform compatible (Windows/Linux/macOS).
"""

import subprocess
import socket
import os
import sys
import logging
import threading
from typing import Optional, Callable

from config import trace_execution

logger = logging.getLogger(__name__)


# --- Platform Detection ---
IS_WINDOWS = sys.platform == 'win32'


def get_subprocess_flags():
    """Get platform-specific subprocess flags."""
    if IS_WINDOWS:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return {
            'startupinfo': startupinfo,
            'creationflags': subprocess.CREATE_NO_WINDOW
        }
    else:
        # Linux/macOS don't need special flags
        return {}


@trace_execution
def check_php_installed() -> bool:
    """Check if PHP is available in PATH."""
    try:
        result = subprocess.run(
            ["php", "-v"],
            capture_output=True,
            text=True,
            **get_subprocess_flags()
        )
        if result.returncode == 0:
            # Extract version info
            version_line = result.stdout.split('\n')[0]
            logger.info(f"PHP found: {version_line}")
            return True
        return False
    except FileNotFoundError:
        logger.warning("PHP not found in PATH")
        return False


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    return None


class PHPServer:
    """
    Manages the PHP built-in development server.
    Captures stdout/stderr for log display.
    """
    
    def __init__(self, on_log: Callable[[str], None] = None):
        """
        Initialize PHP Server manager.
        
        Args:
            on_log: Callback function to receive server log lines.
        """
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.port = 8000
        self.document_root = os.getcwd()
        self.on_log = on_log or (lambda x: None)
        self._log_thread: Optional[threading.Thread] = None
        self._stop_logging = threading.Event()
    
    @trace_execution
    def start(self, document_root: str, port: int = 8000) -> bool:
        """
        Start the PHP development server.
        
        Args:
            document_root: Directory to serve files from.
            port: Port to listen on (will auto-increment if busy).
            
        Returns:
            True if server started successfully.
        """
        if self.is_running:
            logger.warning("Server already running")
            return False
        
        # Check for port collision
        if is_port_in_use(port):
            new_port = find_available_port(port)
            if new_port is None:
                logger.error(f"Ports {port}-{port + 9} are all in use")
                return False
            logger.info(f"Port {port} busy, using {new_port}")
            port = new_port
        
        self.port = port
        self.document_root = document_root
        
        cmd = ["php", "-S", f"localhost:{port}", "-t", document_root]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=True,
                bufsize=1,  # Line buffered
                **get_subprocess_flags()
            )
            
            self.is_running = True
            self._stop_logging.clear()
            
            # Start log capture thread
            self._log_thread = threading.Thread(target=self._capture_logs, daemon=True)
            self._log_thread.start()
            
            logger.info(f"Server started at http://localhost:{port}")
            self.on_log(f"[NanoServer] Started at http://localhost:{port}")
            self.on_log(f"[NanoServer] Document root: {document_root}")
            
            return True
            
        except FileNotFoundError:
            logger.error("PHP not found - cannot start server")
            return False
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
    
    def _capture_logs(self):
        """Background thread to capture PHP server output."""
        try:
            while not self._stop_logging.is_set() and self.process:
                line = self.process.stdout.readline()
                if line:
                    line = line.rstrip()
                    logger.debug(f"PHP: {line}")
                    self.on_log(line)
                elif self.process.poll() is not None:
                    # Process terminated
                    break
        except Exception as e:
            logger.error(f"Log capture error: {e}")
    
    @trace_execution
    def stop(self) -> None:
        """Stop the PHP server."""
        self._stop_logging.set()
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
        
        self.is_running = False
        logger.info("Server stopped")
        self.on_log("[NanoServer] Server stopped")
    
    def restart(self) -> bool:
        """Restart the server with same settings."""
        doc_root = self.document_root
        port = self.port
        self.stop()
        return self.start(doc_root, port)
    
    @property
    def url(self) -> str:
        """Get the server URL."""
        return f"http://localhost:{self.port}"
