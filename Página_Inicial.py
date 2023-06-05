import streamlit as st 
import json
import pandas as pd
import plotly.express as px
import requests
from datafunc import dados_df



if __name__ == "__main__":
    df = dados_df()  
    n_cidades = len(df.cidade.unique())-1
    n_escolas = len(df.colegio.unique())-2
    f"""# Respostas Discentes

Foram coletadas {df.shape[0]} respostas, de {n_escolas} escolas diferentes, abrangendo {n_cidades} cidades."""
    tab_graficos, tab_tabelas = st.tabs(["Gráficos", "Tabelas"])
    with tab_graficos:

        interesse = df.groupby("interesse").agg({"stamp": "count"}).reset_index()
        interesse.columns = ["interesse", "contagem"]
        "## Interesse em fazer faculdade"
        fig = px.pie(interesse, values="contagem", names="interesse", color_discrete_sequence=["blue", 'red'])     
        #fig.update_layout(width=500, height=500)
        st.plotly_chart(fig,use_container_width=True) 
        "## Conhecimento da UFSC Blumenau"
        
        existencia = df.groupby("existencia").agg({"stamp": "count"}).reset_index()
        existencia.columns = ["existencia", "contagem"]
        fig = px.pie(existencia, values="contagem", names="existencia", color_discrete_sequence=["blue", 'red'])     
        st.plotly_chart(fig, use_container_width=True)   

        "## Cursos"
        interessados = df.query("interesse == 'Sim'")

        grande_area_curso = interessados.groupby(['grande_area', 'curso']).agg({'stamp': 'count'}).sort_values(['grande_area','stamp']).reset_index()
        grande_area_curso.columns = ['grande_area', 'curso', 'interessados']
        fig = px.sunburst(grande_area_curso, path=['grande_area', 'curso'], values='interessados')
        st.plotly_chart(fig, use_container_width=True)   
        st.caption("Clique no setor interno para expandir a grande área.")
        
        "### 10 cursos mais escolhidos"
        fig = px.bar(interessados.groupby("curso").agg({"interesse": 'count'}).sort_values(by='interesse', ascending=False).head(n=10).reset_index(),
             x='curso', y='interesse')
        st.plotly_chart(fig, use_container_width=True)   
    with tab_tabelas: 
        st.caption("Clique nas colunas da tabela para ordenar os dados")
        "## Interesse em fazer faculdade"
        interesse_total = pd.DataFrame(data=[["Total", interesse.contagem.sum()]], columns=interesse.columns)
        interesse_full = pd.concat([interesse, interesse_total ], ignore_index=True)
        interesse_full["porcentagem"] = 100*interesse_full.contagem/interesse.contagem.sum() 
        st.dataframe(interesse_full)

        "## Conhecimento da UFSC Blumenau"
        existencia_total = pd.DataFrame(data=[["Total", existencia.contagem.sum()]], columns=existencia.columns)
        existencia_full = pd.concat([existencia, existencia_total ], ignore_index=True)
        existencia_full["porcentagem"] = 100*existencia_full.contagem/existencia.contagem.sum()
        st.dataframe(existencia_full)

        "## Grandes áreas"

        grandes_areas = interessados.groupby(["grande_area"]).agg({'stamp': 'count'}).reset_index()
        grandes_areas.columns = ["Grande Área", "Interessados"]
        grandes_areas_total = pd.DataFrame([["Total", grandes_areas.Interessados.sum()]], columns=grandes_areas.columns)
        grandes_areas_full = pd.concat([grandes_areas, grandes_areas_total], ignore_index=True)
        grandes_areas_full["porcentagem"] = 100*grandes_areas_full.Interessados/grandes_areas.Interessados.sum()
        st.dataframe(grandes_areas_full)

        "## Cursos"

        select_grande_area = st.selectbox("Escolha uma grande área:", interessados.grande_area.unique())
        sub_cursos = interessados.query(f"grande_area == '{select_grande_area}'")

        agg_cursos = sub_cursos.groupby("curso").agg({"stamp": "count"}).reset_index()
        agg_cursos.columns = ["Curso", "Interessados"]
        st.dataframe(agg_cursos)


