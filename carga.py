import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
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

def update_kpi_ingresos_mensual_act(cargar=False):
    engine = connect_to_db()
    # Utiliza engine.connect() para obtener una conexión
    with engine.connect() as connection:        
        if cargar:
            # Consulta de eliminación
            delete_query = text("DELETE FROM KPI_INGRESOS_IMG_MES WHERE año = '2024' and metrica = 'ingresos' AND periodo != 'Acumulado'")
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)      
            # Consulta de inserción
            insert_query = text("""              
            INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto, Venta_SSS, Ingresos_SSS, metrica)
            SELECT
            DM_PERIODO.Periodo,
            DM_PERIODO.period,
            DM_PERIODO.`Año`,
            QRY_BRANCH_OFFICES.branch_office, 
            QRY_IND_SSS.`value`, 
            SUM(QRY_INGRESOS_TOTALES_PBI.ticket_number)AS ticket_number, 
            SUM(QRY_INGRESOS_TOTALES_PBI.abonados) AS abonados, 
            SUM(QRY_INGRESOS_TOTALES_PBI.net_amount) AS net_amount, 
            SUM(QRY_INGRESOS_TOTALES_PBI.transbank) AS transbank,	
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank)) AS Venta_Neta, 
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados)) AS Ingresos, 
            '0' as ppto,
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank) * (QRY_IND_SSS.`value`))) AS Venta_SSS, 
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados) * (QRY_IND_SSS.`value`))) AS Ingresos_SSS,
            'ingresos' as metrica
            FROM QRY_INGRESOS_TOTALES_PBI
            LEFT JOIN QRY_BRANCH_OFFICES
            ON QRY_INGRESOS_TOTALES_PBI.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            LEFT JOIN QRY_IND_SSS
            ON QRY_INGRESOS_TOTALES_PBI.clave = QRY_IND_SSS.clave
            LEFT JOIN DM_PERIODO
            ON QRY_INGRESOS_TOTALES_PBI.date = DM_PERIODO.Fecha
            WHERE	
                QRY_BRANCH_OFFICES.status_id = 15 AND
                #DAY(`QRY_INGRESOS_TOTALES_PBI`.`date`) <= (DAY(CURDATE())-1) AND
                #MONTH(`QRY_INGRESOS_TOTALES_PBI`.`date`) = ((MONTH(curdate())-1)) AND
                YEAR(`QRY_INGRESOS_TOTALES_PBI`.`date`) = YEAR(curdate())
                AND QRY_BRANCH_OFFICES.branch_office = 'UNIMARC EL PAMPINO'
            GROUP BY 
                DM_PERIODO.Periodo,
                DM_PERIODO.period,
                DM_PERIODO.`Año`,
                QRY_BRANCH_OFFICES.branch_office
            ORDER BY
                QRY_INGRESOS_TOTALES_PBI.date ASC""") 
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)           
            st.write("Ingresos Actual Mensual, Cargados con exito.")

def update_kpi_ingresos_mensual_ant(cargar=False):
    engine = connect_to_db()
    with engine.connect() as connection:        
        if cargar:
            # Consulta de eliminación
            delete_query = text("DELETE FROM KPI_INGRESOS_IMG_MES WHERE año = '2023' and metrica = 'ingresos' AND periodo != 'Acumulado'")
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)      
            # Consulta de inserción
            insert_query = text("""              
            INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto , Venta_SSS, Ingresos_SSS, metrica)
            SELECT
            DM_PERIODO.Periodo,
            DM_PERIODO.period,
            DM_PERIODO.`Año`,
            QRY_BRANCH_OFFICES.branch_office, 
            QRY_IND_SSS.`value`, 
            SUM(QRY_INGRESOS_TOTALES_PBI.ticket_number)AS ticket_number, 
            SUM(QRY_INGRESOS_TOTALES_PBI.abonados) AS abonados, 
            SUM(QRY_INGRESOS_TOTALES_PBI.net_amount) AS net_amount, 
            SUM(QRY_INGRESOS_TOTALES_PBI.transbank) AS transbank,	
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank)) AS Venta_Neta, 
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados)) AS Ingresos, 
            '0' as ppto,
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank) * (QRY_IND_SSS.`value`))) AS Venta_SSS, 
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados) * (QRY_IND_SSS.`value`))) AS Ingresos_SSS,
            'ingresos' as metrica
            FROM QRY_INGRESOS_TOTALES_PBI
            LEFT JOIN QRY_BRANCH_OFFICES
            ON QRY_INGRESOS_TOTALES_PBI.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            LEFT JOIN QRY_IND_SSS
            ON QRY_INGRESOS_TOTALES_PBI.clave = QRY_IND_SSS.clave
            LEFT JOIN DM_PERIODO
            ON QRY_INGRESOS_TOTALES_PBI.date = DM_PERIODO.Fecha
            WHERE	
                QRY_BRANCH_OFFICES.status_id = 15 AND
                #DAY(`QRY_INGRESOS_TOTALES_PBI`.`date`) <= (DAY(CURDATE())-1) AND
                #MONTH(`QRY_INGRESOS_TOTALES_PBI`.`date`) = ((MONTH(curdate())-1)) AND
                YEAR(`QRY_INGRESOS_TOTALES_PBI`.`date`) = YEAR(curdate())-1                
            GROUP BY 
                DM_PERIODO.Periodo,
                DM_PERIODO.period,
                DM_PERIODO.`Año`,
                QRY_BRANCH_OFFICES.branch_office
            ORDER BY
                QRY_INGRESOS_TOTALES_PBI.date ASC""")
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)       
            st.write("Ingresos Anterior Mensual, Cargados con exito.")

def update_kpi_ingresos_mensual_ppto(cargar=False):
    engine = connect_to_db()
    with engine.connect() as connection:        
        if cargar:
            # Configurar el locale para lc_time_names
            set_locale_query = text("SET lc_time_names = 'es_ES'")
            connection.execute(set_locale_query)
            # Consulta de eliminación
            delete_query = text("DELETE FROM KPI_INGRESOS_IMG_MES WHERE metrica = 'ppto' and Period != 'Acumulado'")
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)
            # Consulta de inserción
            insert_query = text("""            
            INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto, Venta_SSS, Ingresos_SSS, metrica)
            SELECT 	
            CONCAT(LPAD(MONTH(QRY_PPTO_DIA.date), 2, '0'),'-',UPPER(SUBSTRING(MONTHNAME(QRY_PPTO_DIA.date), 1, 1)), 
                   LOWER(SUBSTRING(MONTHNAME(QRY_PPTO_DIA.date), 2))) AS periodo,
            CONCAT(YEAR(QRY_PPTO_DIA.date), '-', LPAD(MONTH(QRY_PPTO_DIA.date), 2, '0')) AS period,
            YEAR(QRY_PPTO_DIA.date) as año,    
            QRY_BRANCH_OFFICES.branch_office as branch_office,
                '0' as `value`,
                '0' as `ticket_number`,
                '0' as `abonados`,
                '0' as `net_amount`,
                '0' as transbank,
                '0' as Venta_Neta,	
                '0' as Ingresos,
            SUM(QRY_PPTO_DIA.ppto) as ppto,
                '0' as Venta_SSS,		
                '0' as Ingresos_SSS,
                'ppto' as metrica
            FROM QRY_PPTO_DIA 
            LEFT JOIN QRY_BRANCH_OFFICES
                ON QRY_PPTO_DIA.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            WHERE 
                #DAY(QRY_PPTO_DIA.date) < (DAY(CURDATE())) AND
                #MONTH(QRY_PPTO_DIA.date) = ((MONTH(curdate()))) AND
                YEAR(QRY_PPTO_DIA.date) = YEAR(curdate())                
            GROUP BY
                QRY_BRANCH_OFFICES.branch_office""")
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)       
            st.write("Ingresos Presupuesto Mensual, Cargados con exito.")

def update_kpi_ingresos_acumulado_act(cargar=False):    
    engine = connect_to_db()
    # Utiliza engine.connect() para obtener una conexión
    with engine.connect() as connection:
        if cargar:
            # Consulta de eliminación
            delete_query = text("""
                DELETE FROM KPI_INGRESOS_IMG_MES WHERE año = '2024' AND Periodo = 'Acumulado' and metrica = 'ingresos'
            """)
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)  
            # INSERTA INGRESOS MENSUALES AÑO ANTERIOR ACUMULADO MES
            insert_query = text("""
            INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto, Venta_SSS, Ingresos_SSS, metrica)
            SELECT
            'Acumulado' as Periodo,
            DM_PERIODO.period,
            DM_PERIODO.`Año`,
            QRY_BRANCH_OFFICES.branch_office, 
            QRY_IND_SSS.`value`, 
            SUM(QRY_INGRESOS_TOTALES_PBI.ticket_number)AS ticket_number, 
            SUM(QRY_INGRESOS_TOTALES_PBI.abonados) AS abonados, 
            SUM(QRY_INGRESOS_TOTALES_PBI.net_amount) AS net_amount, 
            SUM(QRY_INGRESOS_TOTALES_PBI.transbank) AS transbank,	
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank)) AS Venta_Neta, 
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados)) AS Ingresos, 
            '0' as ppto,
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank) * (QRY_IND_SSS.`value`))) AS Venta_SSS, 
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados) * (QRY_IND_SSS.`value`))) AS Ingresos_SSS,
            'ingresos' as metrica
            FROM QRY_INGRESOS_TOTALES_PBI
            LEFT JOIN QRY_BRANCH_OFFICES
            ON QRY_INGRESOS_TOTALES_PBI.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            LEFT JOIN QRY_IND_SSS
            ON QRY_INGRESOS_TOTALES_PBI.clave = QRY_IND_SSS.clave
            LEFT JOIN DM_PERIODO
            ON QRY_INGRESOS_TOTALES_PBI.date = DM_PERIODO.Fecha
            WHERE	
                QRY_BRANCH_OFFICES.status_id = 15 AND
                DAY(`QRY_INGRESOS_TOTALES_PBI`.`date`) < (DAY(CURDATE())) AND
                MONTH(`QRY_INGRESOS_TOTALES_PBI`.`date`) = ((MONTH(curdate()))) AND
                YEAR(`QRY_INGRESOS_TOTALES_PBI`.`date`) = YEAR(curdate())
            GROUP BY 
                DM_PERIODO.Periodo,
                DM_PERIODO.period,
                DM_PERIODO.`Año`,
                QRY_BRANCH_OFFICES.branch_office
            ORDER BY
                QRY_INGRESOS_TOTALES_PBI.date ASC                           
            """)
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)           
            st.write("Ingresos Actual Acumulado, Cargados con exito.")
        
def update_kpi_ingresos_acumulado_ant(cargar=False):
    engine = connect_to_db()
    with engine.connect() as connection:        
        if cargar:
            # Consulta de eliminación
            delete_query = text("DELETE FROM KPI_INGRESOS_IMG_MES WHERE año = '2023' AND Periodo = 'Acumulado' and metrica = 'ingresos'")
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)      
            # Consulta de inserción
            insert_query = text("""              
            INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto, Venta_SSS, Ingresos_SSS, metrica)
            SELECT
            'Acumulado' as Periodo,
            DM_PERIODO.period,
            DM_PERIODO.`Año`,
            QRY_BRANCH_OFFICES.branch_office, 
            QRY_IND_SSS.`value`, 
            SUM(QRY_INGRESOS_TOTALES_PBI.ticket_number)AS ticket_number, 
            SUM(QRY_INGRESOS_TOTALES_PBI.abonados) AS abonados, 
            SUM(QRY_INGRESOS_TOTALES_PBI.net_amount) AS net_amount, 
            SUM(QRY_INGRESOS_TOTALES_PBI.transbank) AS transbank,	
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank)) AS Venta_Neta, 
            SUM((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados)) AS Ingresos, 
            '0' as ppto,
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank) * (QRY_IND_SSS.`value`))) AS Venta_SSS, 
            SUM(((QRY_INGRESOS_TOTALES_PBI.net_amount + QRY_INGRESOS_TOTALES_PBI.transbank + QRY_INGRESOS_TOTALES_PBI.abonados) * (QRY_IND_SSS.`value`))) AS Ingresos_SSS,
            'ingresos' as metrica
            FROM QRY_INGRESOS_TOTALES_PBI
            LEFT JOIN QRY_BRANCH_OFFICES
            ON QRY_INGRESOS_TOTALES_PBI.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            LEFT JOIN QRY_IND_SSS
            ON QRY_INGRESOS_TOTALES_PBI.clave = QRY_IND_SSS.clave
            LEFT JOIN DM_PERIODO
            ON QRY_INGRESOS_TOTALES_PBI.date = DM_PERIODO.Fecha
            WHERE	
                QRY_BRANCH_OFFICES.status_id = 15 AND
                DAY(`QRY_INGRESOS_TOTALES_PBI`.`date`) < (DAY(CURDATE())) AND
                MONTH(`QRY_INGRESOS_TOTALES_PBI`.`date`) = ((MONTH(curdate()))) AND
                YEAR(`QRY_INGRESOS_TOTALES_PBI`.`date`) = YEAR(curdate())-1
            GROUP BY 
                DM_PERIODO.Periodo,
                DM_PERIODO.period,
                DM_PERIODO.`Año`,
                QRY_BRANCH_OFFICES.branch_office
            ORDER BY
                QRY_INGRESOS_TOTALES_PBI.date ASC""")
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)       
            st.write("Ingresos Anterior Acumulado, Cargados con exito.")

def update_kpi_ingresos_acumulado_ppto(cargar=False):
    engine = connect_to_db()
    with engine.connect() as connection:        
        if cargar:
            # Configurar el locale para lc_time_names
            set_locale_query = text("SET lc_time_names = 'es_ES'")
            # Consulta de eliminación
            delete_query = text("DELETE FROM KPI_INGRESOS_IMG_MES WHERE metrica = 'ppto' AND periodo = 'Acumulado'")
            # Ejecutar la consulta de eliminación
            connection.execute(delete_query)      
            # Consulta de inserción
            insert_query = text("""INSERT INTO KPI_INGRESOS_IMG_MES (periodo, period, año, branch_office, `value`, ticket_number, abonados, net_amount , transbank, Venta_Neta , Ingresos, ppto, Venta_SSS, Ingresos_SSS, metrica)
            SELECT
            'Acumulado' AS periodo,
            CONCAT(YEAR(QRY_PPTO_DIA.date),'-',LPAD(MONTH(QRY_PPTO_DIA.date), 2, '0')) AS period,
            YEAR(QRY_PPTO_DIA.date) AS año,
            QRY_BRANCH_OFFICES.branch_office AS branch_office,
            '0' AS `value`,
            '0' AS `ticket_number`,
            '0' AS `abonados`,
            '0' AS `net_amount`,
            '0' AS transbank,
            '0' AS Venta_Neta,
            '0' AS Ingresos,
            SUM(QRY_PPTO_DIA.ppto) AS ppto,
            '0' AS Venta_SSS,
            '0' AS Ingresos_SSS,
            'ppto' AS metrica
            FROM QRY_PPTO_DIA
            LEFT JOIN QRY_BRANCH_OFFICES
            ON QRY_PPTO_DIA.branch_office_id = QRY_BRANCH_OFFICES.branch_office_id
            WHERE 
            DAY(QRY_PPTO_DIA.date) < DAY(CURDATE()) AND
            MONTH(QRY_PPTO_DIA.date) = MONTH(CURDATE()) AND
            YEAR(QRY_PPTO_DIA.date) = YEAR(CURDATE())
            GROUP BY
            QRY_BRANCH_OFFICES.branch_office""")
            # Ejecutar la consulta de inserción
            connection.execute(insert_query)       
            st.write("Ingresos Presupuesto Acumulado, Cargados con exito.")
            


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
        st.title("CARGA ETL")        
        with st.form(key='data_form'):
                st.write("Formulario de Cargas ETL")
                periodo = st.selectbox("Selecciona el periodo", ["Acumulado", "Mensual"])
                version = st.selectbox("Selecciona la versión", ["Actual", "Año Anterior", "Presupuesto"])
                cargar_button = st.form_submit_button("Cargar")
                

    if cargar_button:
                if periodo == "Mensual":
                    if version == "Actual":
                        update_kpi_ingresos_mensual_act(cargar=True)
                    elif version == "Año Anterior":
                        update_kpi_ingresos_mensual_ant(cargar=True)
                    elif version == "Presupuesto":
                        update_kpi_ingresos_mensual_ppto(cargar=True)
                elif periodo == "Acumulado":
                    if version == "Actual":
                        update_kpi_ingresos_acumulado_act(cargar=True)
                    elif version == "Año Anterior":
                        update_kpi_ingresos_acumulado_ant(cargar=True)
                    elif version == "Presupuesto":
                        update_kpi_ingresos_acumulado_ppto(cargar=True)
    
if __name__ == "__main__":
    main()   
