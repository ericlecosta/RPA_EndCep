import os
import sys # vai ser utilizado DENTRO DA INSTANCIA DO BOTCITY
import time
import base64

from botcity.web import WebBot, Browser, By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from dotenv import load_dotenv
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

# configurações
load_dotenv()

SERVER = os.getenv('MAESTRO_SERVER')
LOGIN = os.getenv('MAESTRO_LOGIN')
KEY = os.getenv('MAESTRO_KEY')
DATAPOOL = os.getenv('DATAPOOL_LABEL')
PORTAL_URL = os.getenv('PORTAL_URL') # vamos usar depois...
DELAY = 0.5

def conectar_maestro():
    if len(sys.argv) > 1:
        maestro = BotMaestroSDK.from_sys_args()
        task_id = maestro.get_execution().task_id
    else:
        maestro = BotMaestroSDK()
        maestro.login(server=SERVER, login=LOGIN, key=KEY)
        task_id = None
    return maestro, task_id

# funcao para configurar o webbot da botcity
def iniciar_bot():
    bot = WebBot()
    bot.headless = False
    bot.browser = Browser.CHROME
    bot.driver_path = ChromeDriverManager().install()
    bot.start_browser()
    return bot

def abrir_portal(bot, url_portal):
    url = "file:///" + str(url_portal).replace("\\", "/")
    bot.browse(url)
    # vamos utilizar o selenium para verificar dentro da arvore do
    # DOM quando o botão de novo cadastro tiver sido carregado, se foi, é um sinal
    # de que o portal foi carregado.
    WebDriverWait(bot.driver, timeout=10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#btnNovo"))
    )

def zerar_base(bot):
    bot.find_element("#btnClearAll", By.CSS_SELECTOR).click()
    bot.driver.switch_to.alert.accept()
    time.sleep(DELAY)

def b_cadastrar_usuario(bot, usuario):
    bot.find_element("#btnNovo", By.CSS_SELECTOR).click()
    time.sleep(DELAY)

    for campo_id, coluna in [
        ("f_nome", "nome"),
        ("f_sobrenome", "sobrenome"),
        ("f_cpf", "cpf"),
        ("f_telefone", "telefone"),
        ("f_email", "email"),
        ("f_nascimento", "nascimento"),
        ("f_endereco", "endereco"),
        ("f_observacao", "observacao"),
    ]:
        el = bot.find_element(f"#{campo_id}", By.CSS_SELECTOR)
        el.clear()
        el.send_keys(str(usuario[coluna]))

    Select(bot.find_element("#f_status", By.CSS_SELECTOR)).select_by_value(usuario['status'])
    bot.find_element('#btnSalvar', By.CSS_SELECTOR).click()
    time.sleep(DELAY)

def cadastro_todos(bot, datapool, task_id):
    ok, erros = 0, 0
    while datapool.has_next():
        item = datapool.next(task_id=task_id)
        if item is None:
            break
        usuario = item.values
        print(f"{ok+erros+1} {usuario['nome']} {usuario['sobrenome']} sendo cadastrado..")
        try:
            b_cadastrar_usuario(bot, usuario)
            item.report_done() # marca o dado como CONCLUIDO
            ok += 1
            print("     OK")
        except Exception as e:
            print(f"        ERRO: {e}")
            erros += 1
            try:
                bot.find_element("#btnCancelar", By.CSS_SELECTOR).click() # fecha o modal de cadastro
            except Exception:
                pass
            item.report_error() # marca o dado como ERRO
    print(f"\nConcluido: {ok} OK | {erros} ERROS.")
    return ok, erros

def tirar_screenshot(bot, arquivo="evidencia.png"):
    result = bot.driver.execute_cdp_cmd("Page.captureScreenshot", {
        "format": "png",
        "captureBeyondViewport": True
    })

    with open(arquivo, "wb") as f:
        f.write(base64.b64decode(result['data']))

    print(f"Screenshot salvo em: {arquivo}")

# essa funcao só servirá quando subirmos o bot na plataforma do maestro
def finalizar_task(maestro, task_id, ok, erros):
    if task_id:
        maestro.finish_task(
            task_id=task_id,
            status=AutomationTaskFinishStatus.SUCCESS if erros == 0 else AutomationTaskFinishStatus.PARTIALLY_COMPLETED,
            message=f"{ok} OK | {erros} ERROS."
        )

def main():
    # 1. autenticar o botcity
    maestro, task_id = conectar_maestro()
    # 2. iniciar o bot
    bot = iniciar_bot()
    # 3. abrir portal
    try:
        abrir_portal(bot, PORTAL_URL)
        # 4. zerar o banco de dados
        zerar_base(bot)
        # 4.5. ler o datapool
        datapool = maestro.get_datapool(label=DATAPOOL)
        # 5. cadastrar todos os usuarios
        ok, erros = cadastro_todos(bot, datapool, task_id)
        # 6. tirar uma evidencia com um print screen
        tirar_screenshot(bot)
        time.sleep(3) # fechar o navegador
    finally:
        # 7. fechar o navegador
        bot.stop_browser()
        # 8. finalizar a task
        finalizar_task(maestro, task_id, ok, erros)

if __name__ == "__main__":
    main()





















