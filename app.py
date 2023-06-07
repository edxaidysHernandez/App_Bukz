import streamlit as st
import pandas as pd
import base64


st.title("Actualización de inventario celesa")

st.write("Cargar archivos CSV:")
st.set_option('deprecation.showfileUploaderEncoding', False)  # Evita el aviso de codificación

st.markdown("<h3>Archivo Productos</h3>", unsafe_allow_html=True)
uploaded_file1 = st.file_uploader("", type=["csv"], key="archivo_productos")

st.markdown("<h3>Archivo Azeta</h3>", unsafe_allow_html=True)
uploaded_file2 = st.file_uploader("", type=["csv"], key="archivo_azeta")


if uploaded_file1 is not None and uploaded_file2 is not None:
    st.write("Presiona el botón para continuar")
    if st.button("Continuar"):
        with st.spinner("Cargando..."):
            df_products = pd.read_csv(uploaded_file1)
            df_azeta = pd.read_csv(uploaded_file2, sep=';', header=None)
            df_azeta.columns = ['Variant SKU', 'Stock_Azeta']

            try:
                df_products = df_products.loc[df_products['Vendor'] == 'Bukz España']
                df_products = df_products[['ID', 'Variant Inventory Item ID', 'Variant ID', 'Vendor', 'Variant SKU', 'Variant Barcode', 'Inventory Available: Dropshipping [España]']]
                df_products.insert(1, 'Command', 'UPDATE')
                df_merged = pd.merge(df_products, df_azeta, on="Variant SKU")
                comparar_filas = lambda x: 1 if x['Inventory Available: Dropshipping [España]'] == x['Stock_Azeta'] else 0
                df_merged['Resultado'] = df_merged.apply(comparar_filas, axis=1)
                df_final = df_merged.loc[df_merged['Resultado'] == 0]
                df_final['Inventory Available: Dropshipping [España]'] = df_final['Stock_Azeta']
                df_final.drop(['Stock_Azeta', 'Resultado'], axis=1, inplace=True)
                df_final = df_final.astype({'ID':str, 'Variant Inventory Item ID':str, 'Variant ID':str, 'Vendor':str, 'Variant SKU':str, 
                                           'Variant Barcode':str, 'Inventory Available: Dropshipping [España]':str})
                st.write(df_final)

                # Botón de descarga
                csv = df_final.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="resultado_cruzado.csv">Descargar CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("Por favor, carga ambos archivos para continuar.")
