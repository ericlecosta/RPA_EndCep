from botcity.web import WebBot, Browser, By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By



def esperar_arquivo_por_nome(parte_nome, pasta, timeout=60):
    import os, time
    nome_ren = 'cofap_dados.csv'
    arq_ren = os.path.join(pasta, nome_ren)

    tempo_inicial = time.time()

    while True:
        arquivos = os.listdir(pasta)

        candidatos = [f for f in arquivos if parte_nome in f and not f.endswith(".crdownload")]
        temporarios = [f for f in arquivos if parte_nome in f and f.endswith(".crdownload")]

        if candidatos and not temporarios:
            arq_down= os.path.join(pasta, candidatos[0])
            os.replace(arq_down, arq_ren)
            return arq_ren

        if time.time() - tempo_inicial > timeout:
            raise TimeoutError("Arquivo não encontrado")

        time.sleep(1)

def baixar_arquivo():
    
    #download_path = r"C:\projetos\RPA_EndCep"
    download_path = r"C:\Users\Turma02\pyteste\RPA_EndCep"
    
    bot = WebBot()
    bot.browser = Browser.CHROME
    bot.driver_path = ChromeDriverManager().install()
    bot.start_browser()


    # 👇 COLOCA AQUI
    bot.driver.command_executor._commands["send_command"] = ("POST", "/session/$sessionId/chromium/send_command")

    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {
            "behavior": "allow",
            "downloadPath": download_path
        }
    }

    bot.driver.execute("send_command", params)

    bot.browse("http://cofap.semsa/")
    bot.sleep(3000)

    # 1. Scroll até o menu
    bot.execute_javascript("""
    var el = document.querySelector('[data-target="#collapseListasQualidade"]');
    el.scrollIntoView({block: 'center'});
    """)

    bot.wait(1000)

    # 2. Expandir menu
    bot.find_element('//a[@data-target="#collapseListasQualidade"]', by="xpath").click()
    bot.wait(1000)

    #roalr para infantil
    bot.execute_javascript("""
    var el = document.querySelector('a[href*="pendencias-cuidadoinfantil"]');
    el.scrollIntoView({block: 'center'});
    """)
    bot.wait(1000)
    bot.find_element('a[href*="pendencias-cuidadoinfantil"]', by="css selector").click()
    bot.wait(2000)

    if bot.driver.current_url == "http://cofap.semsa/login":
        print("Redirecionado para login")
        bot.find_element('input#cpf', by="css selector").send_keys("55821235200")
        bot.wait(1000)
        bot.find_element('input#password', by="css selector").send_keys("12345678")
        bot.wait(1000)
        #bot.find_element('//button[text()="Log in"]', by="xpath").click()
        #bot.find_element('button[type="submit"]', by="css selector").click()
        bot.find_element('//button[normalize-space()="Log in"]', by="xpath").click()

        bot.find_element('[data-target="#collapseOne"]', by="css selector", waiting_time=10000).click()
        # 1. Abrir o select
        bot.wait(2000)
        bot.find_element("filtro_unidade", by="id").click()
        bot.wait(1000)
        bot.find_element('option[value="SEM VINCULO"]', by="css selector").click()
        bot.wait(1000)


        bot.find_element('//button[normalize-space()="Aplicar Filtros"]', by="xpath").click()

        # espera linhas aparecerem
        WebDriverWait(bot.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//table[@id="tabela-gestantes"]/tbody/tr'))
        )


        bot.find_element('//button[normalize-space()="Aplicar Filtros"]', by="xpath").click()
        bot.wait(1000)

        bot.find_element(
            '//div[@id="botoes-exportacao"]//button[.//span[contains(text(),"CSV")]]',
            by="xpath",
            waiting_time=10000).click()


        arquivo = esperar_arquivo_por_nome("infantil", download_path)

        print("Download finalizado:", arquivo)
        return arquivo