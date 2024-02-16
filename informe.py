import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import streamlit_shadcn_ui as ui
import plotly.express as px
import datetime
import calendar
from colorama import Fore, Style

 
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

def kpi_ingresos_mes():
    engine = connect_to_db()
    query = """
    SELECT
	KPI_INGRESOS_IMG_MES.periodo, 
	KPI_INGRESOS_IMG_MES.`año`, 
	KPI_INGRESOS_IMG_MES.period, 
	KPI_INGRESOS_IMG_MES.branch_office, 
	KPI_INGRESOS_IMG_MES.`value`, 
	sum(KPI_INGRESOS_IMG_MES.ticket_number)as ticket_number, 
	sum(KPI_INGRESOS_IMG_MES.abonados)as abonados, 
	sum(KPI_INGRESOS_IMG_MES.net_amount)as net_amount, 
	sum(KPI_INGRESOS_IMG_MES.transbank)as transbank, 
	sum(KPI_INGRESOS_IMG_MES.Venta_Neta)as Venta_Neta, 
	sum(KPI_INGRESOS_IMG_MES.Ingresos)as Ingresos, 
	sum(KPI_INGRESOS_IMG_MES.ppto)as ppto, 
	sum(KPI_INGRESOS_IMG_MES.Venta_SSS)as Venta_SSS, 
	sum(KPI_INGRESOS_IMG_MES.Ingresos_SSS)as Ingresos_SSS, 
	KPI_INGRESOS_IMG_MES.metrica
    FROM
	KPI_INGRESOS_IMG_MES LEFT JOIN QRY_BRANCH_OFFICES
	ON KPI_INGRESOS_IMG_MES.branch_office = QRY_BRANCH_OFFICES.branch_office
	WHERE QRY_BRANCH_OFFICES.status_id = 15
    GROUP BY
    KPI_INGRESOS_IMG_MES.periodo, 
	KPI_INGRESOS_IMG_MES.`año`, 
	KPI_INGRESOS_IMG_MES.period, 
	KPI_INGRESOS_IMG_MES.branch_office
    """
    df_ingresos = pd.read_sql(query, engine)
    return df_ingresos

def qry_branch_offices():
    engine = connect_to_db()
    query = "SELECT * FROM QRY_BRANCH_OFFICES"
    sucursales = pd.read_sql(query, engine)
    return sucursales 

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)


def calcular_variacion(df, columna_actual, columna_anterior):
    df = df.fillna(0)    
    zero_mask = (df[columna_actual] == 0) | (df[columna_anterior] == 0)
    variacion = df.apply(lambda row: 0 if zero_mask[row.name] else ((row[columna_actual] / row[columna_anterior]) - 1) * 100, axis=1)
    variacion = variacion.apply(lambda x: f"{x:.2f}%" if x >= 0 else f"{x:.2f}%")    
    return variacion

def calcular_ticket_promedio(df, columna_ingresos, columna_tickets):
    df = df.fillna(0)
    zero_mask = (df[columna_ingresos] == 0) | (df[columna_tickets] == 0) 
    ticket_promedio = df.apply(lambda row: 0 if zero_mask[row.name] else (row[columna_ingresos] / row[columna_tickets]), axis=1)
    return ticket_promedio

def reemplazar_inf(df):
    return df.fillna(0)

#Totales
def calcular_variacion_total(df, columna_actual, columna_anterior):
    total_actual = df[columna_actual].sum()
    total_anterior = df[columna_anterior].sum()
    variacion = (total_actual / total_anterior - 1) * 100
    return f"{variacion:.2f}%"

def calcular_desviacion_total(df, columna_actual, columna_ppto):
    total_actual = df[columna_actual].sum()
    total_ppto = df[columna_ppto].sum() 
    desviacion = (total_actual / total_ppto - 1) * 100
    return f"{desviacion:.2f}%"

def calcular_ticket_total(df, columna_ingresos, columna_ticket):
    total_actual = df[columna_ingresos].sum()
    total_ticket = df[columna_ticket].sum()
    ticket_prom = (total_actual / total_ticket )
    return ticket_prom

def formato_condicional(valor):
    try:
        valor = float(valor)
        if valor < 0:
            return f"{Fore.RED}{valor:.2f}%{Style.RESET_ALL}"
        elif valor > 0:
            return f"{Fore.BLACK}{valor:.2f}%{Style.RESET_ALL}"
        else:
            return f"{valor:.2f}%"
    except ValueError:
        # Manejar el caso en el que el valor no es un número
        return str(valor)

    

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
        st.title("INFORME DE VENTAS")
        df_total = kpi_ingresos_mes()
        df_sucursales = qry_branch_offices()

        ### INGRESOS ACTUAL 2024
        df_ingresos_2024 = df_total[(df_total["año"] == 2024)]
        columns_ingresos = ["periodo", "branch_office" , "ticket_number" , "Venta_Neta" , "Venta_SSS" , "Ingresos" ,"ppto" , "Ingresos_SSS" ]
        df_ingresos_act = df_ingresos_2024[columns_ingresos]
    
        df_ingresos_act = df_ingresos_act.rename(columns={"ticket_number": "ticket_number_Act", 
                                            "Venta_Neta" : "Venta_Neta_Act" ,
                                            "Venta_SSS": "Venta_SSS_Act",
                                            "Ingresos" : "Ingresos_Act",
                                            "Ingresos_SSS" : "Ingresos_SSS_Act",
                                            "ppto" : "Presupuesto"})
        
        ### INGRESOS ANTERIOR 2023
        df_ingresos_2023 = df_total[(df_total["año"] == 2023)]
        columns_ingresos = ["periodo", "branch_office" , "ticket_number" , "Venta_Neta" , "Venta_SSS" , "Ingresos" ,  "Ingresos_SSS" ]
        df_ingresos_ant = df_ingresos_2023[columns_ingresos]  
            
        df_ingresos_ant = df_ingresos_ant.rename(columns={"ticket_number": "ticket_number_Ant", 
                                                "Venta_Neta" : "Venta_Neta_Ant" ,
                                                "Venta_SSS": "Venta_SSS_Ant",
                                                "Ingresos" : "Ingresos_Ant",
                                                "Ingresos_SSS" : "Ingresos_SSS_Ant"})    
        
        df_ingresos = df_ingresos_act.merge(df_ingresos_ant, on=["branch_office", "periodo"], how="outer", suffixes=('_Act', '_Ant'))
        df_ingresos = df_ingresos.fillna(0)  
        df_ingresos = df_ingresos.groupby(["periodo", "branch_office"]).first().reset_index()    
        
        ### COLUMNAS CALCULADAS    
        df_ingresos= df_ingresos.assign(
            var_SSS = calcular_variacion(df_ingresos, 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant'),
            var_Q = calcular_variacion(df_ingresos, 'ticket_number_Act', 'ticket_number_Ant'),
            ticket_prom_act = calcular_ticket_promedio(df_ingresos, 'Ingresos_Act', 'ticket_number_Act'),
            ticket_prom_ant = calcular_ticket_promedio(df_ingresos, 'Ingresos_Ant', 'ticket_number_Ant'),        
            desv = calcular_variacion(df_ingresos, 'Ingresos_Act', 'Presupuesto'))
            
        #st.dataframe(df_ingresos)

        ### BRANCH OFFICES SUPERVISORES
        columns_sucursal = ["names", "branch_office"]
        df_sucursales = df_sucursales[columns_sucursal]
        df_sucursales.rename(columns={"names": "supervisor"}, inplace=True)

        df_general= pd.merge(df_ingresos, df_sucursales, on=["branch_office"], how="left")
        
        df_general.rename(columns={"branch_office": "sucursal"}, inplace=True)
        df_general.rename(columns={"ticket_number_Act": "ticket_number"}, inplace=True)

        #st.dataframe(df_general)
        columns_to_show = ['periodo' , 'sucursal' , 'supervisor' , 'Ingresos_Act', 'Ingresos_Ant', 
                            'Venta_Neta_Act', 'Venta_Neta_Ant' , 'ticket_prom_act',  'ticket_prom_ant' ,
                            'var_Q' ,'var_SSS', 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant', 'Presupuesto', 'desv', 'ticket_number', 'ticket_number_Ant'] 

        columns_to_show_in_visualization = ['sucursal','periodo', 'Ingresos_Act', 'Ingresos_Ant','var_SSS','Presupuesto', 'desv','Venta_Neta_Act', 'Venta_Neta_Ant',
                                                'var_Q','Ingresos_SSS_Act', 'Ingresos_SSS_Ant', 'ticket_number', 'ticket_number_Ant', 'ticket_prom_act','ticket_prom_ant']

        df_general = reemplazar_inf(df_general)
        df_inicial_display = df_general[columns_to_show_in_visualization].copy()    
        periodos_2024_con_datos = df_total[df_total['año'] == 2024]['periodo'].unique()
        ultimo_periodo = periodos_2024_con_datos[-1]
        periodos_seleccionados_por_defecto = ultimo_periodo
        

        st.sidebar.title('Filtros Disponibles')    
        periodos = df_general['periodo'].unique()
        supervisors = df_general['supervisor'].unique()
        supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
        branch_offices = df_general[df_general['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
        branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
        periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=periodos_seleccionados_por_defecto)
        
        if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
            df_filtrado = df_general[
                (df_general['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
                (df_general['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
                (df_general['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)]
            df_filtrado = df_filtrado[columns_to_show]
            columns_to_exclude = ['periodo', 'sucursal', 'supervisor', 'ticket_prom_act', 'ticket_prom_ant', 'var_Q', 'var_SSS', 'desv']
    
                        
            # Calcula la suma de las columnas seleccionadas  
            sum_total = df_filtrado.drop(columns=columns_to_exclude).sum()
            sum_total_row = pd.Series({'periodo': 'Total', 'sucursal': '', 'supervisor': ''})
            sum_total_row = sum_total_row.append(sum_total)     

            # Asigna los valores calculados a sum_total_row
            sum_total_row['var'] = calcular_variacion_total(df_filtrado, 'Ingresos_Act', 'Ingresos_Ant')
            sum_total_row['var_SSS'] = calcular_variacion_total(df_filtrado, 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant')
            sum_total_row['var_P'] = calcular_variacion_total(df_filtrado, 'ticket_prom_act', 'ticket_prom_ant')
            sum_total_row['var_Q'] = calcular_variacion_total(df_filtrado, 'ticket_number', 'ticket_number_Ant')
            sum_total_row['desv'] = calcular_desviacion_total(df_filtrado, 'Ingresos_Act', 'Presupuesto')
            sum_total_row['ticket_prom_act'] = calcular_ticket_total(df_filtrado, 'Ingresos_Act', 'ticket_number')
            sum_total_row['ticket_prom_ant'] = calcular_ticket_total(df_filtrado, 'Ingresos_Ant', 'ticket_number_Ant')       

            df_filtrado = df_filtrado.append(sum_total_row, ignore_index=True)

            # Crea un nuevo DataFrame con las columnas deseadas para df_filtrado
            df_filtrado_display = df_filtrado[columns_to_show_in_visualization].copy()        
        else:
            df_filtrado_display = df_inicial_display.copy()

        #st.dataframe(df_filtrado)  

        # Obtener los totales de las columnas deseadas
        ingresos_act = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Act'].values[0])
        ingresos_ant = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Ingresos_Ant'].values[0])
        ingresos_ppto = format_currency(df_filtrado[df_filtrado['periodo'] == 'Total']['Presupuesto'].values[0])
        
        var_sss_formatted = sum_total_row['var_SSS'] 
        desv_formatted = sum_total_row['desv']
        ticket_promedio_formatted = format_currency(sum_total_row['ticket_prom_act'])

        
        #INDICADORES EN CARD METRIC
        #Primera Fila
        col1, col2, col3 = st.columns(3)
        with col1:         
            ui.metric_card(title="INGRESOS ACTUAL", content=ingresos_act, key="card1")         
        with col2:
            ui.metric_card(title="INGRESOS ANTERIOR", content=ingresos_ant,  key="card2")
        with col3:
            ui.metric_card(title="PRESUPUESTO", content=ingresos_ppto,  key="card3")

        #Segunda Fila                
        col4, col5, col6 = st.columns(3)
        with col4:
            ui.metric_card(title="VAR % SSS", content=var_sss_formatted,  key="card4")            
        with col5:
            ui.metric_card(title="DESVIACION %", content=desv_formatted,  key="card5")           
        with col6:
            ui.metric_card(title="TICKET PROM", content=ticket_promedio_formatted,  key="card6")   

        # Muestra el DataFrame
        df_filtrado_display = df_filtrado[columns_to_show_in_visualization].copy()
        df_filtrado_display = df_filtrado_display.reset_index(drop=True)
        df_filtrado_display.set_index('sucursal', inplace=True)

        # Aplicar la función format_currency a las columnas específicas
        columns_to_format = [ 'Venta_Neta_Act', 'Venta_Neta_Ant', 'Ingresos_SSS_Act', 'Ingresos_SSS_Ant', 'ticket_prom_act', 'ticket_prom_ant' ]
        df_filtrado_display[columns_to_format] = df_filtrado_display[columns_to_format].applymap(format_currency)

        # Obtener nombre del mes actual 
        nombre_mes = datetime.datetime.now().strftime("%B").capitalize()
        numero_mes = datetime.datetime.now().month
        ultimo_mes = f"{numero_mes}-{nombre_mes}"      

        # Partiendo del dataframe df_filtrado_display    
        df_grouped = df_filtrado_display.groupby('periodo')[['Ingresos_Act','Ingresos_Ant', 'Presupuesto']].sum().reset_index()
        
        # Eliminar último mes  
        df_grouped = df_grouped[df_grouped['periodo'] != ultimo_mes]
        df_grouped = df_grouped.sort_values('periodo')

        # Gráfico de barras agrupadas
        print()
        fig = px.bar(df_grouped, x='periodo', y=['Ingresos_Act', 'Ingresos_Ant', 'Presupuesto'],
                barmode='group') 
        fig.update_layout(            
                legend=dict(
                orientation="h",  
                yanchor="middle",            
                y=-0.25,
                xanchor="auto",
                x=1.05 ),
                width=850        
                )
        st.plotly_chart(fig)
 
if __name__ == "__main__":
    main()   
