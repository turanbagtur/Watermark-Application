import webview
import os
import sys
import base64
import logging

# --- SISTEMA DE LOGS ---
appdata_dir = os.path.join(os.getenv('APPDATA'), 'WatermarkApp')
os.makedirs(appdata_dir, exist_ok=True)
log_file = os.path.join(appdata_dir, 'app_error.log')

logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_asset_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class NativeAPI:
    def __init__(self):
        self.window = None

    def save_file(self, default_filename, b64_data, last_dir, file_type):
        try:
            if not os.path.exists(last_dir):
                last_dir = ''
                
            file_types_filter = ('All Files (*.*)',)
            if file_type == 'zip':
                file_types_filter = ('ZIP Files (*.zip)', 'All Files (*.*)')
            elif file_type == 'png':
                file_types_filter = ('PNG Images (*.png)', 'All Files (*.*)')
            elif file_type in ['jpg', 'jpeg']:
                file_types_filter = ('JPEG Images (*.jpg;*.jpeg)', 'All Files (*.*)')
            elif file_type == 'webp':
                file_types_filter = ('WEBP Images (*.webp)', 'All Files (*.*)')

            result = self.window.create_file_dialog(
                dialog_type=webview.SAVE_DIALOG,
                directory=last_dir,
                save_filename=default_filename,
                file_types=file_types_filter
            )

            if result and len(result) > 0:
                file_path = result[0]
                with open(file_path, 'wb') as f:
                    f.write(base64.b64decode(b64_data))
                return os.path.dirname(file_path)
            
            return "CANCELLED"
        except Exception as e:
            logging.error(f"Erro ao salvar arquivo: {str(e)}")
            return f"ERROR: {str(e)}"

# --- BLOQUEIOS DE SEGURANÇA ---
JS_SECURITY_INJECTION = """
    // Desativa botão direito (Menu de contexto)
    document.addEventListener('contextmenu', event => event.preventDefault());
    
    // Desativa atalhos perigosos (F12, Ctrl+Shift+I, Ctrl+U)
    document.onkeydown = function(e) {
        if (e.keyCode == 123 || 
           (e.ctrlKey && e.shiftKey && (e.keyCode == 73 || e.keyCode == 74)) || 
           (e.ctrlKey && e.keyCode == 85)) {
            return false;
        }
    };
"""

def bind_events(window):
    # CRÍTICO: Só injeta o JS de segurança QUANDO o HTML já estiver renderizado
    def on_loaded():
        try:
            window.evaluate_js(JS_SECURITY_INJECTION)
        except Exception as e:
            logging.error(f"Erro ao injetar JS: {str(e)}")
            
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
        bind_events(window) # Associa os eventos de carregamento
        
        # CRÍTICO: Removido o gui='cef', permitindo que use o EdgeWebView2 nativo
        webview.start(debug=False)
        
    except Exception as e:
        logging.error(f"Erro Crítico na Inicialização: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()