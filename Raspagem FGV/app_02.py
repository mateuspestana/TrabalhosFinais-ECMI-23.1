import streamlit as st  # Importa o módulo Streamlit para a criação de aplicativos web.
from selenium import webdriver  # Importa o webdriver do Selenium, que é usado para controlar um navegador.
from selenium.webdriver.common.by import By  # Importa a classe 'By', usada para referenciar elementos da página.
from selenium.webdriver.support.ui import WebDriverWait  # Importa a classe 'WebDriverWait', usada para pausar o código até que uma condição seja atendida.
from selenium.webdriver.support import expected_conditions as EC  # Importa a classe 'expected_conditions', usada juntamente com 'WebDriverWait'.
import pandas as pd  # Importa o módulo Pandas para manipulação e análise de dados.
import re  # Importa o módulo de expressões regulares.

def app():  # Define a função principal do aplicativo.
    options = webdriver.FirefoxOptions()  # Cria uma instância das opções do navegador Firefox.
    options.add_argument("--headless")  # Adiciona a opção 'headless', que permite ao navegador funcionar em segundo plano.
    driver = webdriver.Firefox(options=options)  # Cria uma instância do webdriver do Firefox com as opções definidas.

    url = "https://emap.fgv.br/pessoas"  # Define a URL da página a ser raspada.
    driver.get(url)  # Navega até a URL especificada.

    teachers = dict()  # Cria um dicionário vazio para armazenar as informações dos professores.
    # Encontra todos os elementos na página que são links para as páginas de perfil dos professores.
    elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/professores/']")

    # Percorre todos os elementos encontrados e extrai o nome do professor e a URL do seu perfil.
    for element in elements:
        name = element.get_attribute('href').split('/')[-1]  # Extrai o nome do professor da URL.
        name = name.replace("-", " ").title()  # Substitui hífens por espaços e capitaliza o nome.
        teachers[name] = element.get_attribute('href')  # Armazena a URL do perfil do professor no dicionário.

    # Exibe um título na página do aplicativo.
    st.markdown("<h1 style='text-align: center; color: blue;'>FGV EMAP</h1>", unsafe_allow_html=True)

    # Prepara uma lista de nomes de professores para ser exibida em um menu dropdown.
    teachers_names = ["Digite ou selecione um professor"] + list(teachers.keys())
    teacher_input = st.selectbox("Professor:", teachers_names)  # Solicita ao usuário para selecionar um professor.

    # Verifica se o usuário selecionou um professor.
    if teacher_input != "Digite ou selecione um professor":
        st.write(f"Raspando dados por {teacher_input}...")  # Exibe uma mensagem indicando que os dados estão sendo raspados.
        link = teachers[teacher_input]  # Obtém a URL do perfil do professor selecionado.
        driver.get(link)  # Navega até a URL do perfil do professor.

        # Extrai a URL da imagem do perfil do professor.
        img_url = driver.find_element(By.CSS_SELECTOR, 'img.img-fluid.mb-3.image-style-square-300x300').get_attribute('src')
        # Extrai o endereço de e-mail do professor.
        email = driver.find_element(By.CSS_SELECTOR, "a[href^='mailto:']").get_attribute('href').split("mailto:",1)[1]

        # Encontra todos os parágrafos de texto na página do perfil.
        info_para = driver.find_elements(By.CSS_SELECTOR, "div.gray-border-bottom-2.pb-2.mb-4.field__item p")

        keywords = []  # Cria uma lista vazia para armazenar as palavras-chave.
        with open('keywords.txt', 'r') as f:  # Abre o arquivo de palavras-chave.
            keywords = [line.strip().lower() for line in f]  # Lê as palavras-chave do arquivo e as armazena na lista.

        bullet_points = []  # Cria uma lista vazia para armazenar os pontos de bala.
        # Percorre todos os parágrafos encontrados e extrai as sentenças que contêm as palavras-chave.
        for para in info_para:
            sentences = re.split(r'(?<=[.!?]) +', para.text)  # Divide o parágrafo em sentenças.
            for sentence in sentences:  # Percorre todas as sentenças.
                # Se uma sentença contém qualquer uma das palavras-chave, ela é adicionada à lista de pontos de bala.
                if any(keyword in sentence.lower() for keyword in keywords):
                    bullet_points.append(sentence.strip())

        col1, col2 = st.columns(2)  # Divide a página do aplicativo em duas colunas.
        with col1:  # Na primeira coluna, exibe a imagem do perfil do professor.
            st.image(img_url)
        with col2:  # Na segunda coluna, exibe as informações do professor.
            st.write(f"Informações sobre {teacher_input}:")
            for bullet in bullet_points:  # Exibe cada ponto de bala.
                st.write("- " + bullet.capitalize())
            if email != "ecmi@fgv.br":  # Se o professor tem um e-mail, exibe o e-mail. ecmi@fgv.br é disponibilizado qnd o integrante/professor não tem um email.
                st.write(f"Email: {email}")
            st.write(f"Link do professor: {link}")  # Exibe a URL do perfil do professor.

        driver.quit()  # Fecha o navegador.

if __name__ == "__main__":
    app()  # Executa a função principal do aplicativo.
