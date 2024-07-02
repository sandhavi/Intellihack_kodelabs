import winreg
import sv_ttk


# Function to detect system mode
def is_dark_mode():
    try:
        # Check if the system is in dark mode
        reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        reg_value = 'AppsUseLightTheme'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
            value, regtype = winreg.QueryValueEx(key, reg_value)
            return value == 0  # 0 means dark mode, 1 means light mode
    except Exception as e:
        print(f"Error checking system mode: {e}")
        return False  # Fallback to default


# Function to set theme based on system mode
def set_theme():
    if is_dark_mode():
        sv_ttk.use_dark_theme()
    else:
        sv_ttk.use_light_theme()  # Define your light theme function if necessary

