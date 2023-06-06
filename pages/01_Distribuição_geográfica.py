import streamlit as st
import folium
import pandas as pd 

from streamlit_folium import st_folium

from datafunc import dados_df, cidades_df, geojson, escolas_df

if __name__ == "__main__":

    df = dados_df()
    escolas_geoloc = escolas_df() 
    escolas_geoloc_df = pd.merge(df, escolas_geoloc, left_on='colegio', right_on='escola')
    escolas_geoloc_df = escolas_geoloc_df.groupby(["cidade_escola","escola"]).agg({"stamp": "count", "lat": "mean", "long": "mean"}).reset_index() 
    
    tab_mapas, tab_tabelas = st.tabs(["Mapas", "Tabelas"])
    
    with tab_tabelas:
        "## Cidades" 
        cidades = df.groupby("cidade").agg({"stamp": "count"}).reset_index()
        cidades.columns = ["cidade", "contagem"]

        st.dataframe(cidades)

        "## Escolas"

        filtrar_por_cidade = st.selectbox("Filtrar por cidade:",escolas_geoloc_df.cidade_escola.unique() )
        if filtrar_por_cidade:
            subset = escolas_geoloc_df.query(f"cidade_escola == '{filtrar_por_cidade}'")
        else:
            subset = escolas_geoloc_df
        st.dataframe(subset[["cidade_escola", "escola", "stamp"]].rename(columns={"stamp": "Alunos Respondentes", "cidade_escola": "Cidade"}))

    with tab_mapas:
        "## Cidades"
        cidades_mapeadas = pd.DataFrame(cidades_df())
        BOUNDARIES = geojson()
        IDS = cidades_mapeadas.codigo.unique()
        features_colection = []
        for x in BOUNDARIES['features']:
            if x['properties']['id'] in IDS:
                props = x.copy()
                municipio = x['properties']['município']
                props['properties']["quantidade"] = df.query(f"cidade == '{municipio}'").agg({"stamp": 'count'}).tolist()[0]
                features_colection.append(props)

        SEMI_BOUNDARIES = {"type":"FeatureCollection", "features":  features_colection}#[ x for x in BOUNDARIES['features'] if x['properties']['id'] in IDS ] }

        abrangencia_mapa = folium.Map(width=800,height=400,location=[-26.872752975560978, -49.094156560879235],
                            zoom_start = 12, tiles="cartodbpositron") 
        
        COLOR_MAP = dict(zip( [0, 10, 25, 50, 100, 200], ['#d1e5f0','#92c5de','#4393c3','#2166ac','#053061'])) 
          
        def color_func(n: int):
            cor_final = ""
            for k, cor in COLOR_MAP.items():
                if n >= k:
                    cor_final = cor
            return cor_final



        style_function = lambda x: {
            "fillColor": color_func(x["properties"]["quantidade"]) ,
            'color': '#333333',
            'weight': 0.4,
            'fillOpacity': 0.9

        }
        folium.GeoJson(
            data=SEMI_BOUNDARIES,  
            name="Quantidade de respostas",
            style_function=style_function,
            popup=folium.GeoJsonPopup(fields=["município", "quantidade"])
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

