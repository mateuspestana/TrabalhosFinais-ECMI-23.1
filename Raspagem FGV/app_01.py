import streamlit as st  # Importa o módulo Streamlit para a criação de aplicativos web.
from selenium import webdriver  # Importa o webdriver do Selenium, que é usado para controlar um navegador.
from selenium.webdriver.common.by import By  # Importa a classe 'By', usada para referenciar elementos da página.
from selenium.webdriver.support.ui import WebDriverWait  # Importa a classe 'WebDriverWait', usada para pausar o código até que uma condição seja atendida.
from selenium.webdriver.support import expected_conditions as EC  # Importa a classe 'expected_conditions', usada juntamente com 'WebDriverWait'.
import pandas as pd  # Importa o módulo Pandas para manipulação e análise de dados.
import re  # Importa o módulo de expressões regulares.

def app(): # Define a função principal do aplicativo.
    options = webdriver.FirefoxOptions() # Cria uma instância das opções do navegador Firefox.
    options.add_argument("--headless")  # Garante que a interface gráfica do usuário esteja desligada
    driver = webdriver.Firefox(options=options)  # Usa o caminho padrão do geckodriver

    url = "https://ecmi.fgv.br/corpo-docente"
    driver.get(url)  # Navega até o site

    wait = WebDriverWait(driver, 10)  # Espera por até 10 segundos até que ocorra uma exceção de tempo esgotado. Um total de 20 tentativas, pois ele verifica a condição a cada 500ms por padrão.

    teachers = dict()  # Cria um dicionário vazio para salvar os nomes dos professores

    # Encontra todos os elementos com as classes ".field-content.mb-0 a[href^='/integrante/']"
    # dentro de uma tag <a> cujo atributo href começa com "/integrante/"
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".field-content.mb-0 a[href^='/integrante/']")))

    unique_cargos = set()  # Cria um conjunto vazio para armazenar cargos únicos
    
    # extraindo o texto de cada elemento na lista (convertendo para minúsculas e removendo espaços extras) e coletando todos os valores únicos desses textos.
    for element in elements:
        cargo = element.get_attribute('innerHTML').lower().strip()  # Remove espaços em branco no início e no fim
        unique_cargos.add(cargo)

    # Usa a função de markdown do Streamlit para exibir uma string HTML com o maior cabeçalho <h1> centralizado e azul
    st.markdown("<h1 style='text-align: center; color: blue;'>FGV ECMI</h1>", unsafe_allow_html=True)
    
    # Configura uma caixa no Streamlit. A primeira opção padrão é solicitada ao usuário digitar ou selecionar uma opção.
    unique_cargos_list = ["Digite ou selecione um cargo"] + list(unique_cargos)
    cargoInput = st.selectbox("Cargo:", unique_cargos_list)

    if cargoInput != "Digite ou selecione um cargo":  # Checa se o usuário selecionou um cargo sem ser a primeira opção.
        for element in elements:
            cargo = element.get_attribute('innerHTML').lower().strip() # Pegando o HTML interno (cargo) do professor selecionado, necessário para saber que cargo corresponde com que professor.
            if cargoInput in cargo: # checando pra ver se o cargo selecionado pelo usuário na aplicação streamlit combina com o cargo do professor atual. Se o cargo selecionado pelo usuário combina com o cargo do prof atual, essas linhas são executadas.

                nome = element.get_attribute('href').split('/')[-1] # pega o atributo href do elemento atual, que é o link para a página do prof, e extrai o nome do prof da ultima parte do link.
                teachers[nome] = element.get_attribute('href') # Isso esta adicionando uma entrada para o dicionario 'teachers', onde a chave é o nome do professor (nome) e o valor é o link para a pagina do prof. Necessario para depois raspar as paginas depois baseado no que o usuário selecionar. Por exemplo, se o attributo href no anchor tag for "/integrante/matheus-pestana, ele pega matheus-pestanha.

        # Criando uma lista onde o primeiro item é a string "Digite..." Depois usa lista comprehension para navegar todas as chaves no dicionario teachers, com os "-" substituidos por espaço para legibilidade.         
        teachers_names = ["Digite ou selecione um integrante"] + [name.replace("-", " ").title() for name in teachers.keys()]
        nomeInput = st.selectbox("Integrante:", teachers_names)

        # Checa para ver se o valor do nomeInput não é igual a string "digite..." para garantir que uma opção válida é selecionada no site.
        if nomeInput != "Digite ou selecione um integrante":
            dados = list() #criando uma lista vazia
            for nome, link in teachers.items(): # itera sobre os itens no dicionario teachers, desempacoteia cada par valor-chave no dicionario em variaveis (nome e link). O nome representa o nome do integrante, link o url da pagina.
                nome = nome.replace("-", " ").title() # Substitui os hyphens no nome do professor com espaço, e capitaliza a primeira letra de cada palavra.
                if nomeInput.lower() in nome.lower():
                    # checa para vr se o nomeInput esta presente no nome (tudo convertido para minusculo).
                    st.write(f"Raspando dados de {nome}...") # disponibiliza uma mensagem indicando que os dados estão sendo raspados.
                    driver.get(link) # Navega até o url da pagina do integrante e abre o para fazer a raspagem.
                    # utilizando selenium para localizar a foto do integrante no site usando o CSS selector. Quando ele localiza a imagem, o .get_attribute('src') é utilizado para extrair o url da imagem que é guardado dentro da variável img_url.
                    img_url = driver.find_element(By.CSS_SELECTOR, 'img.img-fluid.mb-3.image-style-square-300x300').get_attribute('src')
                    
                    # Utilizando selenium para localizar o email do integrante na pagina, o CSS selector localiza o hyperlink que tem um href que começa com (^=) malito:. Quando o elemento é localizado o .get_attribute('href') extrai o valor do href apos o malito: que é onde o email é contido. Isso é guardado dentro da variavel email.
                    email = driver.find_element(By.CSS_SELECTOR, "a[href^='mailto:']").get_attribute('href').split("mailto:",1)[1]
                    
                    # localiza e extrai a informação da pagina dos integrantes, primeiro espera até o elemento que contem os paragrafos esta presente na pagina, depois utiliza selenium para localizar todos os paragrafos (<p>) dentro do elemento, e guarda isso dentro da variavel infoPara.
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.gray-border-bottom-2.pb-2.mb-4.field__item p")))
                    infoPara = driver.find_elements(By.CSS_SELECTOR, "div.gray-border-bottom-2.pb-2.mb-4.field__item p")
                    
                    # Abre uma lista de keywords, o with open é mais prático que open() pois não precisa dar close()... 
                    with open('keywords.txt', 'r') as f:
                        keywords = [line.strip().lower() for line in f] # remove whitespace e é convertido para lowercase, e é guardado dentro da variavel keywords.

                    sentences = list() # criado lista vazia
                    for para in infoPara: # Navegando atraves de cada paragrafo dentro do infoPara.

                        texto = para.text # convertendo o paragrafo para tipo texto.
                        sentences.extend(re.split(r'(?<=[.!?]) +', texto)) # Dividindo o texto do paragrafo em frases que são adicionados na lista sentences.

                    bullet_points = [] # outro modo de criar lista vazia
                    keyword_found = False # Inicia uma variavel booleana para acompanhar se uma frase que contem uma frase chave foi achada.
                    for sentence in sentences: # itera sobre cada frase dentro da lista sentences que contem frases extraido da informação dos integrantes
                        # Checa para ver se qualquer valor chave dentro do keyword.txt esta na frase atual (tudo em lowercase), se for achado a frase é apended à lista bullet_points, e a variavel booleana keyword_found vira True.
                        if any(keyword in sentence.lower() for keyword in keywords):
                            bullet_points.append(sentence.strip())
                            keyword_found = True

                    if not keyword_found: # se a palavra-chave não for achada
                        bullet_points = sentences # então as frases são adicionadas à variavel bullet_points

                    col1, col2 = st.columns(2) # essa linha cria duas colunas na aplicação streamlit.
                    with col1: #bloco que definem que tipo de conteudo vao entrar em cada uma das duas colunas
                        st.image(img_url) # mostra uma imagem na primeira coluna com o url da imagem que foi obtida mais cedo, guardado dentro da variavel img_url
                    with col2: #bloco que definem que tipo de conteudo vao entrar em cada uma das duas colunas
                        st.write(f"Informações sobre {nome}:") # sequencia de chamadas st.write() que criam elementos texto na segunda coluna que incluem o nome do prof, os bullet points, email do prof, e o link para o perfil deles no site do corpo docente da ecmi.
                        for bullet in bullet_points:
                            st.write("- " + bullet.capitalize())
                        if email != "ecmi@fgv.br": # Se o professor tem um e-mail, exibe o e-mail. ecmi@fgv.br é disponibilizado qnd o integrante/professor não tem um email.
                            st.write(f"Email: {email}")
                        st.write(f"Veja no site do corpo docente da ECMI: {link}")
                        # adiciona um dicionario com os dados do professor atual à lista dados, que inclui o nome, bullet points e email.
                    dados.append({"Nome": nome, "Sentenças": bullet_points, "Email": email})

            driver.quit() # fechando a janela do browser controlada por selenium

            df = pd.DataFrame(dados) # cria um dataframe de pandas da lista de dados
            df.to_csv("scraped_data.csv", index=False) # sem indice, (0, 1, 2 nas colunas)
