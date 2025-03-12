from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

# Configuração do Flask
app = Flask(__name__)


# Carregar variáveis do arquivo .env
load_dotenv()

# Obter o caminho do ChromeDriver do arquivo .env
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")


if not CHROMEDRIVER_PATH:
    raise Exception("A variável CHROMEDRIVER_PATH não está definida no arquivo .env.")

# Função para executar a pesquisa
def realizar_pesquisa(termo_busca, max_resultados):
    # Configurar o WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

    try:
        # Abrir o DuckDuckGo e realizar a busca
        driver.get("https://duckduckgo.com/")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(termo_busca)
        search_box.send_keys(Keys.RETURN)

        # Esperar os resultados carregarem
        WebDriverWait(driver, 5, poll_frequency=0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".react-results--main"))
        )

        # Capturar os resultados
        results = driver.find_elements(By.CSS_SELECTOR, ".react-results--main article")[:max_resultados]
        dados = []
        for result in results:
            try:
                titulo = result.find_element(By.CSS_SELECTOR, "h2 a").text
                link = result.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                dados.append({"Título": titulo, "Link": link})
            except Exception as e:
                print(f"Erro ao processar um resultado: {e}")
        return dados
    finally:
        # Fechar o navegador
        driver.quit()

# Rota principal: renderizar o formulário
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o formulário e exibir resultados
@app.route('/resultados', methods=['POST'])
def resultados():
    # Obter os dados do formulário
    termo_busca = request.form['termo_busca']
    max_resultados = int(request.form['max_resultados'])

    # Realizar a pesquisa
    dados = realizar_pesquisa(termo_busca, max_resultados)

    # Salvar os resultados em um arquivo Excel
    if dados:
        df = pd.DataFrame(dados)
        excel_filename = "resultados_duckduckgo.xlsx"
        df.to_excel(excel_filename, index=False)

    # Renderizar a página de resultados
    return render_template('resultados.html', dados=dados, termo_busca=termo_busca)

# Ponto de entrada do aplicativo
if __name__ == "__main__":
    app.run(debug=True)
