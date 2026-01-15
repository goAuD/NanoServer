# NanoServer

**A lightweight, modern PHP development environment for students and developers.**

NanoServer is a portable, GUI-based tool written in Python that replaces heavy software like XAMPP or Laragon for simple development tasks. It uses the built-in PHP web server and SQLite, wrapped in a modern Dark Mode interface.

![Python](https://img.shields.io/badge/Made%20with-Python-blue)
![License](https://img.shields.io/badge/License-MIT-green)

<br> ![NanoServer Screenshot](nanoserver.png)

<br>

## Features

* **Zero Configuration:** Just select your project folder and click Start.
* **Modern UI:** Clean, Dark Mode interface using `CustomTkinter`.
* **Lightweight:** No Apache/Nginx installation required. Uses `php -S`.
* **Laravel Support:** Automatically detects Laravel projects and serves from the `/public` directory.
* **SQLite Manager:** Built-in tool to run SQL queries directly on your local database.
* **Portable:** Perfect for school computers or restricted environments where you can't install complex software.
* **Smart Error Handling (v1.1.0):**
  * Automatic PHP installation detection with helpful setup instructions.
  * Automatic port collision detection - finds the next available port if 8000 is busy.

## Requirements

* **Python 3.x** installed.
* **PHP** installed and added to your system PATH (type `php -v` in terminal to check).

## How to Run

1.  Clone or download this repository.
2.  Install the required Python library:
    ```bash
    pip install customtkinter
    ```
3.  Run the application:
    ```bash
    python nanoserver.py
    ```

## How to Use

1.  **Select Project Folder:** Click the button to choose your website's root folder.
2.  **Start Server:** Click "Start Server". Your site will run at `http://localhost:8000`.
3.  **Database:** You can run SQL commands in the bottom section. The database file (`database.sqlite`) is created automatically in your project folder.

## Why I made this?

I created NanoServer because the software at my school (Laragon) had expired licenses, and I needed a quick, free, and modern way to host my PHP/HTML homework locally without administrative privileges.

## License

This project is open-source and free to use under the MIT License.