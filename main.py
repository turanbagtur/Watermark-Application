import webview
import os
import sys
import base64
import logging

# --- ENHANCED LOGGING SYSTEM (DEBUG Level) ---
appdata_dir = os.path.join(os.getenv('APPDATA'), 'WatermarkApp')
os.makedirs(appdata_dir, exist_ok=True)
log_file = os.path.join(appdata_dir, 'app_error.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,  # Force capture absolutely everything
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

logging.info("=== WatermarkApp initialized with Nuitka ===")

def get_asset_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class NativeAPI:
    def __init__(self):
        self.window = None

    def save_file(self, default_filename, b64_data, last_dir, file_type):
        logging.info(f"Save request received: {default_filename}")
        try:
            if not last_dir or not os.path.exists(last_dir) or "Program Files" in last_dir or "Windows" in last_dir:
                last_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                logging.debug(f"Directory adjusted to: {last_dir}")

            if file_type == 'zip':
                file_types = ('ZIP Files (*.zip)', 'All Files (*.*)')
            elif file_type == 'png':
                file_types = ('PNG Images (*.png)', 'All Files (*.*)')
            elif file_type in ['jpg', 'jpeg']:
                file_types = ('JPEG Images (*.jpg;*.jpeg)', 'All Files (*.*)')
            elif file_type == 'webp':
                file_types = ('WEBP Images (*.webp)', 'All Files (*.*)')
            else:
                file_types = ('All Files (*.*)',)

            logging.debug("Opening system file dialog...")
            result = self.window.create_file_dialog(
                dialog_type=webview.SAVE_DIALOG,
                directory=last_dir,
                save_filename=default_filename,
                file_types=file_types
            )

            if not result or len(result) == 0:
                logging.info("User canceled the save.")
                return "CANCELLED"

            # FIRST LETTER BUG FIX
            if isinstance(result, (list, tuple)):
                file_path = result[0]  # If it's a list, grab the first item
            else:
                file_path = result     # If it's a string, use it directly
                
            logging.debug(f"User-selected path: {file_path}")

            try:
                file_data = base64.b64decode(b64_data)
                logging.debug("Base64 decoded successfully.")
            except Exception as decode_err:
                logging.error(f"Error decoding base64: {decode_err}")
                return f"ERROR: Base64 decode failed"

            # Attempt to save with aggressive error handling
            try:
                logging.debug("Attempting to write file to disk...")
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                logging.info(f"FILE SAVED SUCCESSFULLY: {file_path}")
                return os.path.dirname(file_path)

            except PermissionError as perm_err:
                logging.error(f"PermissionError (Windows lock) at: {file_path} | Detail: {perm_err}")
                return "FALLBACK_BROWSER"
            except OSError as os_err:
                logging.error(f"OSError (Disk/Path failure) at {file_path} | Detail: {os_err}")
                return "FALLBACK_BROWSER"
            except Exception as write_err:
                logging.error(f"Unknown error writing {file_path} | Detail: {write_err}")
                return "FALLBACK_BROWSER"

        except Exception as e:
            logging.error(f"Critical error in save_file: {str(e)}", exc_info=True)
            return f"ERROR: {str(e)}"

# --- SECURITY BLOCKS ---
JS_SECURITY_INJECTION = """
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
           (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 74)) || 
           (e.ctrlKey && e.keyCode == 85)) {
            return false;
        }
    };
"""

def bind_events(window):
    def on_loaded():
        try:
            window.evaluate_js(JS_SECURITY_INJECTION)
        except Exception as e:
            logging.error(f"Error injecting JS: {str(e)}")
            
    window.events.loaded += on_loaded

def main():
    try:
        html_path = get_asset_path(os.path.join('app', 'watermarkadder.html'))
        api = NativeAPI()
        
        window = webview.create_window(
            title='Advanced Professional Watermark',
            url=f'file://{html_path}',
            width=950,
            height=720,
            min_size=(850, 600),
            background_color='#0f172a',
            confirm_close=False,
            js_api=api,
            text_select=False 
        )
        
        api.window = window
        window.expose(api.save_file)
        bind_events(window)
        webview.start(debug=False)
        
    except Exception as e:
        logging.error(f"Critical initialization error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()