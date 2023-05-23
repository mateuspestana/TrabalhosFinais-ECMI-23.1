import streamlit as st
import pandas as pd
import numpy as np
import os
from functions import *
import altair as alt

st.set_page_config(page_title="Buscador de Preço", page_icon="📐", layout="wide")

def main():

    with st.sidebar:
        st.title('NatannaTech')
        with st.form(key='form_busca'):
            # tipo = st.selectbox('Selecione o tipo', ['Base', 'Batom', 'Sombra'])
            query = st.text_input('Digite o produto')
            # query = tipo + ' ' + query
            buscar = st.form_submit_button('Buscar')
        st.caption('Desenvolvido por:')
        st.caption("- Anna Beatriz Veronez \n- Anna Clara Legey \n- Ana Paula Salvador \n- Nataly de Abreu")
        st.caption('Sob orientação do Prof. Matheus C. Pestana (matheus.pestana@fgv.br)')

    st.title('Buscador de preços')
    if buscar:
        st.header('Resultados da busca')
        with st.spinner('Buscando o melhor preço...'):
            df = buscadorGeral(query)
            st.subheader('Gráficos')
            graph1, graph2 = st.columns(2)
            graph1.altair_chart(histoPreco(df).properties(height=300, title='Produtos por faixa de preço'), use_container_width=True)
            graph2.altair_chart(mediaPreco(df).properties(height=300, title='Preço médio por site'), use_container_width=True)

            st.subheader('Produtos')
            showProducts(df.reset_index())

if __name__ == '__main__':
    main()
