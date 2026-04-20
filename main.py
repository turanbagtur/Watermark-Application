import webview
import os
import sys
import base64
import logging

# --- SISTEMA DE LOGS MELHORADO (Nível DEBUG) ---
appdata_dir = os.path.join(os.getenv('APPDATA'), 'WatermarkApp')
os.makedirs(appdata_dir, exist_ok=True)
log_file = os.path.join(appdata_dir, 'app_error.log')

logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,  # Força a capturar absolutamente tudo
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

logging.info("=== WatermarkApp Inicializado com Nuitka ===")

def get_asset_path(relative_path):
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class NativeAPI:
    def __init__(self):
        self.window = None

    def save_file(self, default_filename, b64_data, last_dir, file_type):
        logging.info(f"Recebida requisição para salvar: {default_filename}")
        try:
            if not last_dir or not os.path.exists(last_dir) or "Program Files" in last_dir or "Windows" in last_dir:
                last_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                logging.debug(f"Diretório ajustado para: {last_dir}")

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

            logging.debug("Abrindo janela de diálogo do sistema...")
            result = self.window.create_file_dialog(
                dialog_type=webview.SAVE_DIALOG,
                directory=last_dir,
                save_filename=default_filename,
                file_types=file_types
            )

            if not result or len(result) == 0:
                logging.info("Usuário cancelou o salvamento.")
                return "CANCELLED"

            # CORREÇÃO DO BUG DA PRIMEIRA LETRA
            if isinstance(result, (list, tuple)):
                file_path = result[0]  # Se for uma lista, agarra o primeiro item
            else:
                file_path = result     # Se for uma palavra (string), usa a palavra inteira
                
            logging.debug(f"Caminho escolhido pelo usuário: {file_path}")

            try:
                file_data = base64.b64decode(b64_data)
                logging.debug("Base64 decodificado com sucesso.")
            except Exception as decode_err:
                logging.error(f"Erro ao decodificar base64: {decode_err}")
                return f"ERROR: Base64 decode failed"

            # Tenta salvar com tratamento super agressivo
            try:
                logging.debug("Tentando escrever arquivo no disco...")
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                logging.info(f"ARQUIVO SALVO COM SUCESSO: {file_path}")
                return os.path.dirname(file_path)

            except PermissionError as perm_err:
                logging.error(f"PermissionError (Bloqueio do Windows) em: {file_path} | Detalhe: {perm_err}")
                return "FALLBACK_BROWSER"
            except OSError as os_err:
                logging.error(f"OSError (Falha de Disco/Caminho) em {file_path} | Detalhe: {os_err}")
                return "FALLBACK_BROWSER"
            except Exception as write_err:
                logging.error(f"Erro Desconhecido ao escrever {file_path} | Detalhe: {write_err}")
                return "FALLBACK_BROWSER"

        except Exception as e:
            logging.error(f"Erro Crítico geral em save_file: {str(e)}", exc_info=True)
            return f"ERROR: {str(e)}"

# --- BLOQUEIOS DE SEGURANÇA ---
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
        window.expose(api.save_file)
        bind_events(window)
        webview.start(debug=False)
        
    except Exception as e:
        logging.error(f"Erro Crítico na Inicialização: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()