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
        'database': 'jysparki_jis'}
    engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")
    return engine

def kpi_recaudacion_dia():
    engine = connect_to_db()
    query = """
    SELECT
    date_format(`collections`.`created_at`,'%Y-%m-%d') AS Fecha,
    collections.branch_office_id AS branch_office_id, 	
    sum(collections.gross_amount) AS recaudacion	
    FROM collections LEFT JOIN cashiers
    ON collections.cashier_id = cashiers.cashier_id
    LEFT JOIN branch_offices
    ON collections.branch_office_id = branch_offices.branch_office_id
    WHERE
    collections.special_cashier = 0 AND
    cashiers.cashier_type_id <> 3 AND
	branch_offices.status_id = 15 AND
	DAY(collections.created_at)< (DAY(CURDATE())) AND
	YEAR(collections.created_at ) = YEAR(curdate()) 
    GROUP BY
    collections.created_at, 
    collections.branch_office_id   
    """
    df_recaudacion = pd.read_sql(query, engine)
    # Convertir la columna "Fecha" a tipo datetime
    df_recaudacion['Fecha'] = pd.to_datetime(df_recaudacion['Fecha'])
    return df_recaudacion

def kpi_deposito_dia():
    engine = connect_to_db()
    query = """
    SELECT
    date_format(deposits.collection_date,'%Y-%m-%d') AS Fecha, 
    deposits.branch_office_id AS branch_office_id, 
    sum(deposits.deposit_amount) AS deposito	
    FROM deposits 
    LEFT JOIN statuses
    ON deposits.status_id = statuses.status_id
    LEFT JOIN QRY_BRANCH_OFFICES
    ON deposits.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
    WHERE 	
    DAY(deposits.collection_date) < (DAY(CURDATE())) AND
	YEAR(deposits.collection_date ) = YEAR(curdate()) AND
	QRY_BRANCH_OFFICES.status_id = 15 
    GROUP BY
    deposits.collection_date, 
    deposits.branch_office_id
    """
    df_deposito = pd.read_sql(query, engine)
    # Convertir la columna "Fecha" a tipo datetime
    df_deposito['Fecha'] = pd.to_datetime(df_deposito['Fecha'])
    return df_deposito

def qry_branch_offices():
    engine = connect_to_db()
    query = "SELECT * FROM QRY_BRANCH_OFFICES WHERE QRY_BRANCH_OFFICES.status_id = 15"
    sucursales = pd.read_sql(query, engine)
    #st.table(sucursales)
    return sucursales 

def qry_periodos():
    engine = connect_to_db()
    query = "SELECT * FROM DM_PERIODO"
    periodo = pd.read_sql(query, engine)    
    return periodo

def format_currency(value):
    return "${:,.0f}".format(value)

def format_percentage(value):
    return "{:.2f}%".format(value)


df_recaudacion = kpi_recaudacion_dia()
df_deposito = kpi_deposito_dia()
df_periodo = qry_periodos()
df_sucursales = qry_branch_offices()


def main(authenticated=False):
    if not authenticated:
        #st.error("Necesitas autenticarte primero")
        #st.error("Necesitas autenticarte")
        #st.stop()
        raise Exception("No autenticado, Necesitas autenticarte primero")
        #return
    else:
        st.title("INFORME DE DEPOSITOS")
        df_estatus = df_recaudacion.merge(df_deposito, on=['branch_office_id', 'Fecha'], how='left')
        df_estatus['deposito'] = df_estatus['deposito'].fillna(0)
        df_estatus['diferencia'] = df_estatus['recaudacion'] - df_estatus['deposito']
        # Crear una nueva columna "nueva_diferencia" con valor 1 si "diferencia" es distinta de 0, y 0 en caso contrario
        df_estatus['status'] = df_estatus['diferencia'].apply(lambda x: "Si" if x != 0 else "No")

        df_estatus = df_estatus.merge(df_sucursales[['branch_office_id', 'names', 'branch_office']], on='branch_office_id', how='left')
        
        df_estatus['Fecha'] = pd.to_datetime(df_estatus['Fecha'])
        df_periodo['Fecha'] = pd.to_datetime(df_periodo['Fecha'])

        df_estatus['Fecha'] = df_estatus['Fecha'].dt.date
        df_periodo['Fecha'] = df_periodo['Fecha'].dt.date
        df_estatus = df_estatus.merge(df_periodo[['Fecha', 'Periodo', 'period', 'Año']], on='Fecha', how='left')
        #st.dataframe(df_estatus)

        df_estatus.rename(columns={"branch_office": "sucursal",
                                    "names": "supervisor",
                                    "Periodo": "periodo",
                                    "recaudacion": "recaudado",
                                    "deposito": "depositado"
                                    }, inplace=True)


        ultimo_mes = df_estatus['periodo'].max()
        # Crear Filtros en el sidebar
        st.sidebar.title('Filtros Disponibles')
        periodos = df_estatus['periodo'].unique()
        periodos_seleccionados = st.sidebar.multiselect('Seleccione Periodo:', periodos, default=[ultimo_mes])
        status = df_estatus['status'].unique()
        status_seleccionados = st.sidebar.multiselect('Seleccione Estado:', status)
        supervisors = df_estatus['supervisor'].unique()   
        supervisor_seleccionados = st.sidebar.multiselect('Seleccione Supervisores:', supervisors)
        branch_offices = df_estatus[df_estatus['supervisor'].isin(supervisor_seleccionados)]['sucursal'].unique()
        branch_office_seleccionadas = st.sidebar.multiselect('Seleccione Sucursales:', branch_offices)
        
        if periodos_seleccionados or branch_office_seleccionadas or supervisor_seleccionados:
            df_filtrado = df_estatus[
                (df_estatus['periodo'].isin(periodos_seleccionados) if periodos_seleccionados else True) &
                (df_estatus['supervisor'].isin(supervisor_seleccionados) if supervisor_seleccionados else True) &
                (df_estatus['sucursal'].isin(branch_office_seleccionadas) if branch_office_seleccionadas else True)&
                (df_estatus['status'].isin(status_seleccionados) if status_seleccionados else True)]
                #st.write(df_filtrado)
        else:
                #st.write(df_estatus)
            pass

        monto_recaudado = format_currency(df_filtrado['recaudado'].sum())
        monto_depositado = format_currency(df_filtrado['depositado'].sum())
        monto_diferencia = format_currency(df_filtrado['diferencia'].sum())

        #INDICADORES EN CARD METRIC
        col1, col2, col3 = st.columns(3)
        with col1:         
            ui.metric_card(title="RECAUDADO $", content=monto_recaudado, key="card1")         
        with col2:
            ui.metric_card(title="DEPOSITADO $", content=monto_depositado,  key="card2")
        with col3:
            ui.metric_card(title="DIFERENCIA $", content=monto_diferencia,  key="card3")

        # Agrupar por "supervisor" y calcular las sumas de "recaudado", "depositado" y "diferencia"
        df_agrupado_sup = df_filtrado.groupby('supervisor').agg({
        'recaudado': 'sum',
        'depositado': 'sum',
        'diferencia': 'sum'
            })
        
        # Ordenar el DataFrame por la columna "diferencia" en orden ascendente
        df_agrupado_sup = df_agrupado_sup.rename(columns={'supervisor': 'Responsable'})
        df_agrupado_sup = df_agrupado_sup.sort_values(by='diferencia' , ascending=False)
        
        
        # Agregar una fila adicional con los totales
        totales = df_agrupado_sup.sum()
        df_totales = pd.DataFrame({
                'recaudado': [totales['recaudado']],
                'depositado': [totales['depositado']],
                'diferencia': [totales['diferencia']]
            }, index=['Total'])
        
        # Concatenar la fila de totales al final del DataFrame
        df_agrupado_sup = pd.concat([df_agrupado_sup, df_totales])
        
        st.dataframe(df_agrupado_sup)
        # Agrupar por "sucursal" y calcular las sumas de "recaudado", "depositado" y "diferencia"
        df_agrupado = df_filtrado.groupby('sucursal').agg({
                'recaudado': 'sum',
                'depositado': 'sum',
                'diferencia': 'sum'
                })

        # Calcular el total de todas las sucursales y agregarlo como una fila al DataFrame
        total_general = df_agrupado.sum()
        df_total = pd.DataFrame({
                'recaudado': [total_general['recaudado']],
                'depositado': [total_general['depositado']],
                'diferencia': [total_general['diferencia']]
                }, index=['Total'])

        # Aplicar el formato de moneda a las columnas numéricas en df_agrupado y df_total
        df_agrupado['recaudado'] = df_agrupado['recaudado'].apply(format_currency)
        df_agrupado['depositado'] = df_agrupado['depositado'].apply(format_currency)
        df_agrupado['diferencia'] = df_agrupado['diferencia'].apply(format_currency)

        df_total['recaudado'] = df_total['recaudado'].apply(format_currency)
        df_total['depositado'] = df_total['depositado'].apply(format_currency)
        df_total['diferencia'] = df_total['diferencia'].apply(format_currency)

        # Establecer "sucursal" como el índice en df_agrupado
        df_agrupado.index.name = 'sucursal'

        # Concatenar df_total al final de df_agrupado para agregar la fila "Total"
        df_agrupado = pd.concat([df_agrupado, df_total])

        # Filtrar df_agrupado
        df_agrupado_filtrado = df_agrupado[df_agrupado['diferencia'] != "$0"]

            # Mostrar el DataFrame agrupado con "sucursal" como índice y la fila "Total"
        st.dataframe(df_agrupado_filtrado)


        # Calcular los totales de las columnas numéricas en df_filtrado
        totales = df_filtrado[['recaudado', 'depositado', 'diferencia']].sum()

        # Crear una fila 'Total' con los totales y valores en blanco para 'Fecha' y 'sucursal'
        fila_total = pd.DataFrame({'Fecha': ['Total'], 
                                    'sucursal': [''], 
                                    'recaudado': [totales['recaudado']], 
                                    'depositado': [totales['depositado']], 
                                    'diferencia': [totales['diferencia']]})

        # Concatenar la fila 'Total' al DataFrame df_filtrado
        df_nuevo = pd.concat([df_filtrado, fila_total])

        columnas_deseadas = ["Fecha", "sucursal", "recaudado", "depositado", "diferencia"]
        df_nuevo = df_nuevo[columnas_deseadas]
        df_nuevo.set_index("Fecha", inplace=True)

        # Aplicar el formato de moneda a las columnas numéricas
        df_nuevo['recaudado'] = df_nuevo['recaudado'].apply(format_currency)
        df_nuevo['depositado'] = df_nuevo['depositado'].apply(format_currency)
        df_nuevo['diferencia'] = df_nuevo['diferencia'].apply(format_currency)

        df_nuevo_filtrado = df_nuevo

        # Mostrar el DataFrame con la fila 'Total'
        st.dataframe(df_nuevo_filtrado)

        


if __name__ == "__main__":
    main()   
