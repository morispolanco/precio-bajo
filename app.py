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
    try:
        response = requests.post(together_url, headers=headers, data=payload)
        response.raise_for_status()  # Esto levantará una excepción para códigos de estado HTTP no exitosos
        
        response_json = response.json()
        st.write("Respuesta completa de Together API:", response_json)  # Depuración
        
        if 'output' in response_json and 'choices' in response_json['output'] and response_json['output']['choices']:
            return response_json['output']['choices'][0]['text'].strip()
        else:
            st.error("La respuesta de Together API no tiene la estructura esperada.")
            return f"precio más bajo de {product} en Guatemala"
    except requests.exceptions.RequestException as e:
        st.error(f"Error al hacer la solicitud a Together API: {str(e)}")
        return f"precio más bajo de {product} en Guatemala"
    except json.JSONDecodeError:
        st.error("Error al decodificar la respuesta JSON de Together API")
        return f"precio más bajo de {product} en Guatemala"
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        return f"precio más bajo de {product} en Guatemala"

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
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al hacer la solicitud a Serper API: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Error al decodificar la respuesta JSON de Serper API")
        return None

# Función para encontrar el resultado con el precio más bajo
def find_lowest_price(results):
    if not results or 'organic' not in results:
        return None
    
    lowest_price = float('inf')
    lowest_price_link = ""
    for result in results['organic']:
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
            st.write(f"Consulta de búsqueda generada: {search_query}")  # Depuración
            
            search_results = search_product(search_query)
            if search_results:
                st.write("Resultados de búsqueda:", search_results)  # Depuración
                
                lowest_price_link = find_lowest_price(search_results)
                
                if lowest_price_link:
                    st.success(f"¡Encontramos el precio más bajo para '{product}'!")
                    st.markdown(f"[Haz clic aquí para ver el mejor precio]({lowest_price_link})")
                else:
                    st.warning(f"No pudimos encontrar un precio para '{product}'. Intenta con otro producto o una descripción más específica.")
            else:
                st.error("No se pudieron obtener resultados de búsqueda.")
    else:
        st.warning("Por favor, ingrese el nombre de un producto para buscar.")

st.markdown("---")
st.caption("Nota: Los precios y la disponibilidad pueden variar. Siempre verifica la información en la tienda antes de realizar una compra.")
