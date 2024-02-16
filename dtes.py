import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import streamlit_shadcn_ui as ui

# Conexión a la base de datos MySQL
def connect_to_db():
    db_config = {
        'host': '103.72.78.28',
        'user': 'jysparki_jis',
        'password': 'Jis2020!',
        'database': 'jysparki_jis'
    }
    engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")
    return engine

def kpi_dtes_mensuales():
    engine = connect_to_db()
    query = """
    SELECT
	dtes.dte_id AS dte_id, 
	DATE_FORMAT(dtes.created_at,"%Y-%m-%d") AS date, 
	dtes.rut AS rut, 
	users.`names` AS cliente, 
	CONCAT_WS(" - ",dtes.rut,users.`names`)as razon_social,
	dtes.folio AS folio, 
	dtes.branch_office_id AS branch_office_id, 
	dtes.dte_type_id AS dte_type_id, 
	dtes.status_id AS status_id, 
	dtes.amount AS amount, 
	dtes.period AS period, 
	dtes.`comment` AS `comment`,
	statuses.`status` AS `status`, 
	dtes.chip_id AS chip_id
    FROM dtes
    LEFT JOIN customers ON dtes.rut = customers.rut
    LEFT JOIN users ON customers.rut = users.rut
    LEFT JOIN statuses ON dtes.status_id = statuses.status_id
    WHERE
	dtes.rut <> '66666666-6' AND	
	dtes.dte_version_id = 1 AND
	dtes.status_id > 17 AND
	dtes.status_id < 24 AND
	users.rol_id = 14 AND
	YEAR(dtes.created_at) = (YEAR(curdate())) AND
	MONTH(dtes.created_at) >= ((MONTH(curdate())-1))
    """
    df_dtes = pd.read_sql(query, engine)
    #st.table(df_ingresos)
    return df_dtes

def qry_branch_offices():
    engine = connect_to_db()
    query = "SELECT * FROM QRY_BRANCH_OFFICES"
    sucursales = pd.read_sql(query, engine)
    #st.table(sucursales)
    return sucursales 

def qry_periodos():
    engine = connect_to_db()
    query = "SELECT Periodo,Trimestre,period,Año FROM DM_PERIODO GROUP BY period"
    periodo = pd.read_sql(query, engine)    
    return periodo

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)


def main(authenticated=False):
    if not authenticated:
        #st.error("Necesitas autenticarte primero")
        #st.error("Necesitas autenticarte")
        #st.stop()
        raise Exception("No autenticado, Necesitas autenticarte primero")
        #return
        #st.error("Necesitas autenticarte primero")
        #return
    else:
        st.title("INFORME DE ABONADOS")        
        df_dtes_mensuales = kpi_dtes_mensuales()
        df_sucursales = qry_branch_offices()
        df_periodo = qry_periodos()

        dte_final = df_dtes_mensuales.merge(df_sucursales, on='branch_office_id', how='left')
        dte_final = dte_final.merge(df_periodo, left_on='period', right_on='period', how='left')
        dte_final = dte_final.rename(columns={"rut_x": "rut", 
                                            "branch_office" : "sucursal" ,
                                            "names": "supervisor",
                                            "dte_type_id" : "tipo",
                                            "amount": "monto"})
        
        # Asignar las columnas 'contador' y 'link' directamente a dte_final
        dte_final['contador'] = dte_final['tipo'].apply(lambda x: 1 if x in [33, 39] else 1)
        dte_final['link'] = dte_final['comment'].apply(lambda x: 'sí' if 'Código de autorización' in str(x) else 'no') 
        dte_final['folio'] = dte_final['folio'].astype(str)  
        ultimo_mes = dte_final['Periodo'].max()
        
        columns_to_show = ['rut', 'cliente', 'razon_social','folio', 'sucursal', 'supervisor', 'tipo', 'status', 'monto', 'Periodo', 'Año', 'comment', 'contador', 'link']
        df_status_dte = dte_final[columns_to_show]
        columns_to_show = ['rut', 'cliente' , 'razon_social','folio' , 'sucursal' ,'supervisor' , 'tipo' , 'status' , 'monto', 'Periodo' , 'Año', 'comment', 'contador', 'link'] 
        
        st.sidebar.title('Filtros Disponibles')    
        periodos = df_status_dte['Periodo'].unique()
        supervisors = df_status_dte['supervisor'].unique()
        status_options = df_status_dte['status'].unique()
        status_seleccionados = st.sidebar.multiselect('Seleccione Status:',status_options,default=status_options)
        supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
        branch_offices = df_status_dte[df_status_dte['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
        branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
        periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=[ultimo_mes])  

        if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
                df_filtrado = df_status_dte[
                    (df_status_dte['status'].isin(status_seleccionados) if status_seleccionados else True) &
                    (df_status_dte['Periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
                    (df_status_dte['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
                    (df_status_dte['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True) ]     
                df_filtrado = df_filtrado[columns_to_show]
                #st.dataframe(df_filtrado)
        else:
                pass  
        #st.dataframe(df_status_dte)

        #st.dataframe(df_filtrado)
        monto_pagada = format_currency(df_filtrado[df_filtrado['status'] == 'Imputada Pagada']['monto'].sum())
        monto_por_pagar = format_currency(df_filtrado[df_filtrado['status'] == 'Imputada por Pagar']['monto'].sum())
        cantidad_pagada = df_filtrado[df_filtrado['status'] == 'Imputada Pagada']['contador'].sum()
        cantidad_por_pagar = df_filtrado[df_filtrado['status'] == 'Imputada por Pagar']['contador'].sum()    
        cantidad_link_si = df_filtrado[df_filtrado['link'] == 'sí']['contador'].sum()
            
        df_agrupado = df_filtrado.sum()
        contador_sum = df_agrupado['contador']
        
        monto_sum = format_currency(df_agrupado['monto'])
        porc_pagados = format_percentage((cantidad_pagada  / contador_sum)*100)
        porc_por_pagar = format_percentage((cantidad_por_pagar  / contador_sum)*100)
        porc_link = format_percentage((cantidad_link_si  / contador_sum)*100)  
        
        #INDICADORES EN CARD METRIC
        #Primera Fila
        col1, col2, col3 = st.columns(3)
        with col1:     
            monto_pagada_str = str(monto_pagada)    
            ui.metric_card(title="DTES PAGADAS $", content=monto_pagada_str, key="card1")         
        with col2:
            monto_por_pagada_str = str(monto_por_pagar)
            ui.metric_card(title="DTES POR PAGAR $", content=monto_por_pagada_str,  key="card2")
        with col3:
            monto_total_str = str(monto_sum)
            ui.metric_card(title="DTES TOTAL $", content=monto_total_str,  key="card3")
        #Segunda Fila
        col4, col5, col6 = st.columns(3)
        with col4:     
            cantidad_pagada_str = str(cantidad_pagada)    
            ui.metric_card(title="DTES PAGADAS Q", content=cantidad_pagada_str, key="card4")         
        with col5:
            cantidad_por_pagar_str = str(cantidad_por_pagar)
            ui.metric_card(title="DTES POR PAGAR Q", content=cantidad_por_pagar_str,  key="card5")
        with col6:
            link_pagada_str = str(cantidad_link_si)
            ui.metric_card(title="DTES POR LINK Q", content=link_pagada_str,  key="card6")
        #Tercera Fila
        col7, col8, col9 = st.columns(3)
        with col7:     
            porc_pagados_str = str(porc_pagados)    
            ui.metric_card(title="% PAGADOS", content=porc_pagados_str, key="card7")         
        with col8:
            porc_por_pagar_str = str(porc_por_pagar)
            ui.metric_card(title="% POR PAGAR", content=porc_por_pagar_str,  key="card8")
        with col9:
            porc_link_str = str(porc_link)
            ui.metric_card(title="% PAGO DIGITAL", content=porc_link_str,  key="card9")
        st.divider()
      
        df_nuevo = df_filtrado[['folio','razon_social','sucursal', 'tipo', 'monto', 'status']].set_index('folio').sort_values(by='monto', ascending=False)          
        pivot_monto = df_filtrado.pivot_table(values='monto', index='supervisor', columns='status', aggfunc='sum', fill_value=0)
        pivot_monto['Total'] = pivot_monto.sum(axis=1)     
        pivot_monto = pivot_monto.sort_values(by='Total', ascending=False)
        pivot_contador = df_filtrado.pivot_table(values='contador', index='supervisor', columns='status', aggfunc='sum', fill_value=0)
        pivot_contador['Total'] = pivot_contador.sum(axis=1)
        
        merged_pivot = pd.merge(pivot_monto, pivot_contador, on='supervisor', suffixes=('_monto', '_contador'))
        merged_pivot = merged_pivot.sort_values(by='Imputada por Pagar_monto', ascending=False) 
        merged_pivot.loc['Total'] = merged_pivot.sum()
        merged_pivot = merged_pivot.rename(columns={"Imputada Pagada_monto": "Pagada $", 
                                                        "Imputada por Pagar_monto": "Por Pagar $",
                                                        "Total_monto": "Total $",
                                                        "Imputada Pagada_contador": "Pagada N°",
                                                        "Imputada por Pagar_contador": "Por Pagar N°",
                                                        "Total_contador": "Total N°"})

        st.dataframe(merged_pivot)
        pivot_monto_sucursal = df_filtrado.pivot_table(values='monto', index='sucursal', columns='status', aggfunc='sum', fill_value=0)
        pivot_monto_sucursal['Total'] = pivot_monto_sucursal.sum(axis=1)

        pivot_contador_sucursal = df_filtrado.pivot_table(values='contador', index='sucursal', columns='status', aggfunc='sum', fill_value=0)
        pivot_contador_sucursal['Total'] = pivot_contador_sucursal.sum(axis=1)

        merged_pivot_sucursal = pd.merge(pivot_monto_sucursal, pivot_contador_sucursal, on='sucursal', suffixes=('_monto', '_contador'))
        merged_pivot_sucursal = merged_pivot_sucursal.sort_values(by='Imputada por Pagar_monto', ascending=False)
        merged_pivot_sucursal.loc['Total'] = merged_pivot_sucursal.sum()
        merged_pivot_sucursal = merged_pivot_sucursal.rename(columns={"Imputada Pagada_monto": "Pagada $", 
                                                                        "Imputada por Pagar_monto": "Por Pagar $",
                                                                        "Total_monto": "Total $",
                                                                        "Imputada Pagada_contador": "Pagada N°",
                                                                        "Imputada por Pagar_contador": "Por Pagar N°",
                                                                        "Total_contador": "Total N°"})
            
        st.dataframe(merged_pivot_sucursal)
    st.dataframe(df_nuevo) 
    
if __name__ == "__main__":
    main()    
