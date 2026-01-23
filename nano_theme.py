"""
Nano Design System - CustomTkinter Theme
Egységes színpaletta és UI beállítások a Nano Product Family-hez.

Használat:
    from nano_theme import NANO_COLORS, apply_nano_theme
    apply_nano_theme()  # Globális beállítások
"""

import customtkinter as ctk


# === Nano Color Palette ===
NANO_COLORS = {
    # Háttér színek
    "bg_primary": "#0a0a0f",       # Fő háttér - majdnem fekete
    "bg_secondary": "#12121a",      # Másodlagos háttér
    "bg_card": "#1a1a24",           # Kártya/panel háttér
    "bg_hover": "#242430",          # Hover állapot
    
    # Akcentus színek
    "accent_cyan": "#00d4ff",       # Fő kiemelő - cián (Nano brand)
    "accent_magenta": "#ff00ff",    # Másodlagos - magenta
    "accent_green": "#4caf50",      # Siker/Online/Start
    "accent_red": "#e74c3c",        # Hiba/Offline/Stop
    "accent_orange": "#e67e22",     # Figyelmeztetés/Restart
    "accent_yellow": "#f1c40f",     # Highlight
    "accent_purple": "#9b59b6",     # Special
    
    # Szöveg színek
    "text_primary": "#ffffff",      # Fő szöveg
    "text_secondary": "#a0a0b0",    # Másodlagos szöveg
    "text_muted": "#606070",        # Halvány szöveg
    "text_link": "#00CED1",         # Link / Nano family text
    
    # Szegély
    "border": "#2a2a3a",            # Szegélyek
    "border_hover": "#3a3a4a",      # Hover szegély
    
    # Speciális
    "laravel_red": "#ff2d20",       # Laravel szín (NanoServer)
    "success": "#4caf50",           # Alias
    "danger": "#e74c3c",            # Alias
    "warning": "#e67e22",           # Alias
    "neutral": "#34495e",           # Neutral gray
    "primary": "#3498db",           # Blue primary
}


# === Button Presets ===
NANO_BUTTONS = {
    "primary": {
        "fg_color": NANO_COLORS["accent_cyan"],
        "hover_color": "#00a8cc",
        "text_color": NANO_COLORS["bg_primary"],
    },
    "success": {
        "fg_color": NANO_COLORS["accent_green"],
        "hover_color": "#45a049",
        "text_color": "#ffffff",
    },
    "danger": {
        "fg_color": NANO_COLORS["accent_red"],
        "hover_color": "#c0392b",
        "text_color": "#ffffff",
    },
    "warning": {
        "fg_color": NANO_COLORS["accent_orange"],
        "hover_color": "#d35400",
        "text_color": "#ffffff",
    },
    "neutral": {
        "fg_color": NANO_COLORS["neutral"],
        "hover_color": "#3d566e",
        "text_color": "#ffffff",
    },
    "ghost": {
        "fg_color": "transparent",
        "hover_color": NANO_COLORS["bg_hover"],
        "border_color": NANO_COLORS["accent_cyan"],
        "border_width": 1,
        "text_color": NANO_COLORS["accent_cyan"],
    },
}


# === Fonts ===
NANO_FONTS = {
    "heading_xl": ("Roboto", 24, "bold"),
    "heading_lg": ("Roboto", 18, "bold"),
    "heading_md": ("Roboto", 16, "bold"),
    "heading_sm": ("Roboto", 14, "bold"),
    "body": ("Roboto", 13),
    "body_small": ("Roboto", 11),
    "mono": ("Consolas", 13),
    "mono_small": ("Consolas", 11),
    "brand": ("Roboto", 10),  # Nano family label
}


def apply_nano_theme():
    """Apply global Nano theme settings."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")


def create_nano_button(master, text: str, style: str = "primary", **kwargs) -> ctk.CTkButton:
    """
    Create a button with Nano styling.
    
    Args:
        master: Parent widget
        text: Button text
        style: One of 'primary', 'success', 'danger', 'warning', 'neutral', 'ghost'
        **kwargs: Additional CTkButton arguments
    
    Returns:
        CTkButton with Nano styling applied
    """
    preset = NANO_BUTTONS.get(style, NANO_BUTTONS["primary"])
    
    button_args = {
        "master": master,
        "text": text,
        **preset,
        **kwargs,
    }
    
    return ctk.CTkButton(**button_args)


def create_nano_label(master, text: str, style: str = "body", **kwargs) -> ctk.CTkLabel:
    """
    Create a label with Nano styling.
    
    Args:
        master: Parent widget
        text: Label text
        style: Font style key from NANO_FONTS
        **kwargs: Additional CTkLabel arguments
    
    Returns:
        CTkLabel with Nano styling applied
    """
    font = NANO_FONTS.get(style, NANO_FONTS["body"])
    
    return ctk.CTkLabel(
        master=master,
        text=text,
        font=font,
        **kwargs
    )


# Version
__version__ = "1.0.0"
