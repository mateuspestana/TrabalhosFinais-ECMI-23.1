import streamlit as st  # Importa o módulo Streamlit para a criação de aplicativos web.
import app_01  # Importa o módulo app_01, que contém o código para raspar o corpo docente da ECMI.
import app_02  # Importa o módulo app_02, que contém o código para raspar o corpo docente da EMAP.

# Função para exibir a página inicial
def show_landing_page():
    st.title("Bem-vindo ao Programa de Raspagem da FGV!")  # Define o título da página.
    # Escreve uma descrição geral do programa na página.
    st.write("Este programa permite raspar o site da FGV para demonstrar somente informações essenciais sobre os integrantes.")

# Crie um dicionário de opções de páginas. Cada entrada é um par chave-valor,
# onde a chave é o nome da página a ser exibida na interface do usuário,
# e o valor é a função que renderiza a página.
PAGES = {
    "Página Inicial": show_landing_page,
    "Corpo docente da ECMI": app_01.app,
    "Corpo docente da EMAP": app_02.app,
}

# Função principal para controlar a navegação e a renderização do aplicativo
def main():
    st.sidebar.title('Raspagem do Corpo Docente da FGV')  # Define o título da barra lateral.
    st.sidebar.markdown('---')  # Adiciona uma linha de separação na barra lateral.
    # Adiciona um subtítulo na barra lateral.
    st.sidebar.subheader('Selecione qual das opções você deseja raspar:')
    
    # Obtenha a seleção do usuário a partir de um grupo de opções de rádio na barra lateral.
    # A lista de opções é obtida das chaves do dicionário PAGES.
    selection = st.sidebar.radio("", list(PAGES.keys()))

    # Renderize o aplicativo selecionado. Se a seleção for "Página Inicial", a função show_landing_page é chamada.
    # Caso contrário, a função correspondente à seleção do usuário no dicionário PAGES é chamada.
    if selection == "Página Inicial":
        show_landing_page()
    else:
        page = PAGES[selection]
        page()

if __name__ == "__main__":
    main()  # Executa a função principal do aplicativo.
