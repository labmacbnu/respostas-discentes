import streamlit as st
import folium
import pandas as pd

from streamlit_folium import st_folium

from datafunc import dados_df, cidades_df, geojson, escolas_df

if __name__ == "__main__":

    df = dados_df()
    escolas_geoloc = escolas_df() 
    escolas_geoloc_df = pd.merge(df, escolas_geoloc, left_on='colegio', right_on='escola')
    escolas_geoloc_df = escolas_geoloc_df.groupby("escola").agg({"stamp": "count", "lat": "mean", "long": "mean"}).reset_index() 
    tab_mapas, tab_tabelas = st.tabs(["Mapas", "Tabelas"])
    with tab_tabelas:
        "## Cidades" 
        cidades = df.groupby("cidade").agg({"stamp": "count"}).reset_index()
        cidades.columns = ["cidade", "contagem"]

        st.dataframe(cidades)

        "## Escolas"

        st.dataframe(escolas_geoloc_df[["escola", "stamp"]].rename(columns={"stamp": "Alunos Respondentes"}))

    with tab_mapas:
        "## Cidades"
        cidades_mapeadas = pd.DataFrame(cidades_df())
        BOUNDARIES = geojson()
        IDS = cidades_mapeadas.codigo.unique()
        SEMI_BOUNDARIES = {"type":"FeatureCollection", "features":  [ x for x in BOUNDARIES['features'] if x['properties']['id'] in IDS ] }
        abrangencia_mapa = folium.Map(width=800,height=400,location=[-26.872752975560978, -49.094156560879235],
                            zoom_start = 12, tiles="cartodbpositron") 

        highlight_function = lambda x: { 'fillOpacity': 0.8, 
                                        'weight': 0.5}
        folium.Choropleth(
            geo_data=SEMI_BOUNDARIES, 
            data=cidades_mapeadas,
            columns=["codigo", "N"],
            key_on="feature.properties.id", 
            fill_color="RdBu",
            fill_opacity=0.5,
            line_opacity=0.2, 
            highlight=True,
            legend_name="Quantidade de respostas",
        ).add_to(abrangencia_mapa)

        abrangencia_mapa.fit_bounds(abrangencia_mapa.get_bounds(), padding=(0.05,0.05))
        ST_MAPA = st_folium(abrangencia_mapa)

        "## Escolas"
        
        abrangencia_mapa = folium.Map(width=800,height=600,location=[-26.872752975560978, -49.094156560879235],
                            zoom_start = 12, tiles="cartodbpositron") 
  
        locations = [[row['lat'],row['long']] for (index, row) in escolas_geoloc_df.iterrows()]
        labels = [row['escola']+": "+str(row["stamp"]) for (index, row) in escolas_geoloc_df.iterrows()]
 
        folium.plugins.MarkerCluster(locations=locations, popups=labels).add_to(abrangencia_mapa)

        abrangencia_mapa.fit_bounds(abrangencia_mapa.get_bounds(), padding=(10, 10))
        ST_MAPA2 = st_folium(abrangencia_mapa)

