import aiohttp
import os
from dotenv import load_dotenv
import time
import hashlib
import hmac
import json

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API da Shopee
PARTNER_ID = os.getenv('SHOPEE_PARTNER_ID')
API_KEY = os.getenv('SHOPEE_API_KEY')

# Validação das credenciais
if not PARTNER_ID or not API_KEY:
    raise ValueError(
        "Credenciais da API Shopee não encontradas! "
        "Certifique-se de que SHOPEE_PARTNER_ID e SHOPEE_API_KEY "
        "estão definidos nas variáveis de ambiente."
    )

# Converte PARTNER_ID para inteiro após validação
PARTNER_ID = int(PARTNER_ID)
API_BASE = "https://open-api.affiliate.shopee.com.br/api/v2"

def generate_signature(endpoint, timestamp):
    """Gera a assinatura necessária para autenticação na API"""
    base_string = f"{PARTNER_ID}{endpoint}{timestamp}"
    sign = hmac.new(API_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    return sign

async def get_product_details(url):
    """Obtém detalhes do produto usando a API oficial da Shopee"""
    try:
        # Extrai os IDs do produto da URL
        ids = extract_product_ids(url)
        if not ids:
            print(f"Não foi possível extrair IDs da URL: {url}")
            return None

        shop_id, item_id = ids
        timestamp = int(time.time())
        endpoint = "/product/get_item_detail"
        
        # Gera a assinatura
        signature = generate_signature(endpoint, timestamp)

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json"
            }
            
            params = {
                "partner_id": PARTNER_ID,
                "timestamp": timestamp,
                "sign": signature,
                "shop_id": shop_id,
                "item_id": item_id
            }

            api_url = f"{API_BASE}{endpoint}"
            print(f"Fazendo requisição para: {api_url}")
            print(f"Parâmetros: {params}")
            
            async with session.get(api_url, headers=headers, params=params) as response:
                response_text = await response.text()
                print(f"Resposta da API: {response_text}")
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if data.get('error') == 0 and 'item' in data.get('data', {}):
                        item = data['data']['item']
                        return {
                            'id': item_id,
                            'name': item.get('name'),
                            'price': float(item.get('price', 0)) / 100000,  # Convertendo para reais
                            'original_price': float(item.get('original_price', 0)) / 100000,
                            'discount': calculate_discount(item.get('price'), item.get('original_price')),
                            'sales': item.get('historical_sold', 0),
                            'rating': item.get('item_rating', {}).get('rating_star', 0),
                            'rating_count': sum(item.get('item_rating', {}).get('rating_count', [0])),
                            'shop_name': item.get('shop_name', ''),
                            'shop_rating': item.get('shop_rating', 0),
                            'description': item.get('description', ''),
                            'link': generate_affiliate_link(url, shop_id, item_id)
                        }
                    else:
                        print(f"Erro nos dados retornados: {data.get('error_msg', 'Erro desconhecido')}")
                else:
                    print(f"Erro na requisição: Status {response.status}")
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return None

def extract_product_ids(url):
    """Extrai shop_id e item_id da URL da Shopee"""
    try:
        # Formato esperado: https://shopee.com.br/product/SHOP_ID/ITEM_ID
        parts = url.split('/')
        shop_id = None
        item_id = None
        
        for i, part in enumerate(parts):
            if part.isdigit():
                if not shop_id:
                    shop_id = int(part)
                else:
                    item_id = int(part)
                    break
        
        if shop_id and item_id:
            return (shop_id, item_id)
        print(f"IDs não encontrados na URL: {url}")
        return None
    except Exception as e:
        print(f"Erro ao extrair IDs: {str(e)}")
        return None

def calculate_discount(current_price, original_price):
    """Calcula o percentual de desconto"""
    try:
        current_price = float(current_price or 0)
        original_price = float(original_price or 0)
        if not original_price or not current_price or original_price <= current_price:
            return 0
        return int(((original_price - current_price) / original_price) * 100)
    except Exception as e:
        print(f"Erro ao calcular desconto: {str(e)}")
        return 0

def generate_affiliate_link(url, shop_id, item_id):
    """Gera o link de afiliado para o produto"""
    try:
        # Formato do link de afiliado da Shopee
        base_url = f"https://shope.ee/affiliate/{PARTNER_ID}"
        product_path = f"product/{shop_id}/{item_id}"
        return f"{base_url}/{product_path}"
    except Exception as e:
        print(f"Erro ao gerar link de afiliado: {str(e)}")
        return url  # Retorna a URL original em caso de erro