import streamlit as st
import requests
import json

# Configuración de las claves de API (guardadas en los secretos de Streamlit)
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

st.title("Buscador de Precios Más Bajos en Guatemala")

# Función para generar la consulta de búsqueda
def generate_search_query(product):
    together_url = "https://api.together.xyz/inference"
    payload = json.dumps({
        "model": "togethercomputer/llama-2-70b-chat",
        "prompt": f"Genera una consulta de búsqueda para encontrar el precio más bajo de '{product}' en Guatemala. La consulta debe ser efectiva para buscar en Google y encontrar resultados de tiendas en línea guatemaltecas. Responde solo con la consulta, sin explicaciones adicionales.",
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["\n"],
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOGETHER_API_KEY}'
    }
    response = requests.post(together_url, headers=headers, data=payload)
    return response.json()['output']['choices'][0]['text'].strip()

# Función para buscar el producto usando Serper
def search_product(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "gt",
        "hl": "es"
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)
    return response.json()

# Función para encontrar el resultado con el precio más bajo
def find_lowest_price(results):
    lowest_price = float('inf')
    lowest_price_link = ""
    for result in results.get('organic', []):
        title = result.get('title', '').lower()
        if 'q' in title or 'quetzal' in title or 'precio' in title:
            try:
                price = float(''.join(filter(str.isdigit, title.split('q')[0])))
                if price < lowest_price:
                    lowest_price = price
                    lowest_price_link = result.get('link', '')
            except ValueError:
                continue
    return lowest_price_link

# Interfaz de usuario
product = st.text_input("Ingrese el nombre del producto que desea buscar:")

if st.button("Buscar precio más bajo"):
    if product:
        with st.spinner("Buscando el mejor precio..."):
            search_query = generate_search_query(product)
            search_results = search_product(search_query)
            lowest_price_link = find_lowest_price(search_results)
            
            if lowest_price_link:
                st.success(f"¡Encontramos el precio más bajo para '{product}'!")
                st.markdown(f"[Haz clic aquí para ver el mejor precio]({lowest_price_link})")
            else:
                st.warning(f"No pudimos encontrar un precio para '{product}'. Intenta con otro producto o una descripción más específica.")
    else:
        st.warning("Por favor, ingrese el nombre de un producto para buscar.")

st.markdown("---")
st.caption("Nota: Los precios y la disponibilidad pueden variar. Siempre verifica la información en la tienda antes de realizar una compra.")
