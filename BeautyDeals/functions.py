#importação das bibliotecas
import requests
import pandas as pd
from stqdm import stqdm
from bs4 import BeautifulSoup
import streamlit as st
from unidecode import unidecode
import altair as alt

#configura o cabeçalho ’https’
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept-Language': 'pt-BR,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

#mantem as informações no cabeçalho
session = requests.Session()
session.headers.update(headers)

#função que raspa os dados do Mercado Livre
def raspaML(query):
    query = query.replace(' ', '%20').strip()
    url = f'https://lista.mercadolivre.com.br/'
    lista_produtos = []
    mercadolivre = session.get(url + query)
    soup = BeautifulSoup(mercadolivre.content, 'lxml')
#seleciona os produtos da página
    produtos = soup.select('.andes-card')
#extrai os dados dos produtos
    for produto in produtos:
        try:
            titulo = produto.select_one('a')['title']
            imagem = produto.find('div',{'class': 'ui-search-result__image'}).find("a").find('img')['data-src']
            imagem = imagem.replace('https://', 'http://')
            preco = produto.select_one('.price-tag-amount').get_text(strip=True)
            preco_clean = float(preco.replace('R$', '').replace('.', '').replace(',', '.'))
            link = produto.select_one('a')['href']
            origem = 'Mercado Livre'
            dados = {'título': titulo, 'imagem': imagem, 'preço': preco, 'preço_clean': preco_clean,'link': link, 'origem': origem}
            lista_produtos.append(dados)
        except:
            pass
    return lista_produtos

#função que raspa os dados da Amazon
def raspaAmazon(query):
    query = query.replace(' ', '+').strip()
    url = f'https://www.amazon.com.br/s?k={query}&ref=nb_sb_noss_2'
    lista_produtos = []
    amazon = requests.get(url, headers)
    soup = BeautifulSoup(amazon.content, 'lxml')
#seleciona os produtos da página
    produtos = soup.select('.s-card-container')
#extrai os dados dos produtos
    for produto in produtos:
        if produto.select_one('.a-offscreen'):
            titulo = produto.select_one('.a-text-normal').get_text(strip=True)
            imagem = produto.select_one('.s-image')['src']
            preco = produto.select_one('.a-offscreen').get_text(strip=True)
            preco_clean = float(preco.replace('.', '').replace(',', '.').replace('R$', ''))
            link = produto.select_one('a')['href']
            link = 'https://www.amazon.com.br' + link
            origem = 'Amazon'
            dados = {'título': titulo, 'imagem': imagem, 'preço': preco, 'preço_clean': preco_clean,'link': link, 'origem': origem}
            lista_produtos.append(dados)
    return lista_produtos

#função que raspa os dados da Beauty Box
def raspaBeautyBox(query):
  query = query.replace(' ', '+')
  url = 'https://www.beautybox.com.br/busca?q='
  pagina = session.get(url+query)
  soup = BeautifulSoup(pagina.content, 'lxml')
#seleciona os produtos da página
  produtos = soup.find_all('div', {'class': 'showcase-item'})
  lista_produtos = []
#extrai os dados dos produtos
  for item in produtos:
    titulo = item.find('a', {'class':'showcase-item-title'}).get('title')
    link = item.find('a', {'class':'showcase-item-title'}).get('href')
    if item.find('p', {'class':'item-price-unavailable'}):
      pass
    else:
      preco = item.find('div', {'class':'item-price-value'}).get_text()
      preco_clean = float(preco.replace('.', '').replace(',', '.').replace('R$', ''))
    imagem = item.find('img').get('data-src')
    origem = 'BeautyBox'
    dados = {'título': titulo, 'imagem': imagem, 'preço': preco, 'preço_clean': preco_clean, 'link': link, 'origem': origem}
    lista_produtos.append(dados)
  return lista_produtos

#função que raspa os dados da Beleza na Web
def raspaBelezaNaWeb(query):
  query = query.replace(' ', '+')
  url = 'https://www.belezanaweb.com.br/busca?q='
  pagina = session.get(url+query)
  soup = BeautifulSoup(pagina.content, 'lxml')
#seleciona os produtos da página
  produtos = soup.find_all('div', {'class': 'showcase-item'})
  lista_produtos = []
#extrai os dados dos produtos
  for item in produtos:
    titulo = item.find('a', {'class':'showcase-item-title'}).get('title')
    link = item.find('a', {'class':'showcase-item-title'}).get('href')
    if item.find('p', {'class': 'item-price-unavailable'}):
        pass
    else:
        preco = item.find('div', {'class': 'item-price-value'}).get_text()
        preco_clean = float(preco.replace('.', '').replace(',', '.').replace('R$', ''))
    imagem = item.find('img').get('data-src')
    origem = 'Beleza na Web'
    dados = {'título': titulo, 'imagem': imagem, 'preço': preco, 'preço_clean': preco_clean, 'link': link, 'origem': origem}
    lista_produtos.append(dados)
  return lista_produtos

#função que faz a busca geral nos sites
def buscadorGeral(query):
    query = unidecode(query)
    while True:
        result_amazon = raspaAmazon(query)
        if len(result_amazon) == 0:
            continue
        else:
            result_amazon = result_amazon
            break
    result_ml = raspaML(query)
    result_bb = raspaBeautyBox(query)
    result_bnw = raspaBelezaNaWeb(query)
    df = pd.DataFrame(result_bnw + result_bb + result_ml + result_amazon)
    df.dropna(subset=['preço_clean'], inplace=True)
    df = df.sort_values(by=['preço_clean'])
    df['título'] = df['título'].apply(lambda x: unidecode(x))
    df = df[df['título'].apply(lambda x: checaLista(query, x))]
    return df[['título', 'imagem', 'preço', 'link', 'preço_clean', 'origem']]

#função para ver se a query está no título do produto
def checaLista(query, row):
    query = query.lower().split()
    lista = row.lower().split()
    if set(query).issubset(lista):
        return True
    else:
        return False

#função para exibir os produtos no Streamlit
def showProducts(df_produtos):
    for index, produto in df_produtos.iterrows():
        with st.expander(produto['título'], expanded=True):
            if produto['origem'] != 'Mercado Livre':
                st.image(produto['imagem'], width=200)
            if index == 0:
                st.subheader(f"Preço: {produto['preço']} - OPÇÃO MAIS BARATA")
            else:
                st.markdown(f"**Preço:** {produto['preço']}")
            st.write(produto['link'])

#função para gerar histograma de preço
def histoPreco(df):
    graph = alt.Chart(df).encode(alt.X('preço_clean:Q', bin=True, title='Faixa de Preço'), y=alt.Y('count()', title='Nº de produtos'), text='count()')
    return graph.mark_bar() + graph.mark_text(dy=-6)

#função para gerar o gráfico de média de preço por origem
def mediaPreco(df):
    media = df.groupby('origem')['preço_clean'].mean().reset_index(name='media_preco')
    graph = alt.Chart(media).encode(alt.Y('origem:N', title='Site'), alt.X('media_preco', title='Média do Preço'), text=alt.Text('media_preco', format='.2f'))
    return graph.mark_bar() + graph.mark_text(dx=18)
