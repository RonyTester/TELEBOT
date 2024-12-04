import os
from dotenv import load_dotenv
import time
import hmac
import hashlib
import json
import re
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, parse_qs, unquote
import aiohttp

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API da Shopee
PARTNER_ID = os.getenv('SHOPEE_PARTNER_ID')
API_KEY = os.getenv('SHOPEE_API_KEY')
API_URL = "https://open-api.affiliate.shopee.com.br/graphql"

def generate_auth_params(timestamp: int) -> Dict:
    """Gera os parâmetros de autenticação para a API da Shopee"""
    base_string = f"{PARTNER_ID}{timestamp}{API_KEY}"
    signature = hmac.new(
        API_KEY.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "id": PARTNER_ID,
        "signature": signature,
        "timestamp": str(timestamp)
    }

async def resolve_short_url(url: str) -> Optional[str]:
    """Resolve URLs curtas da Shopee para a URL completa"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, allow_redirects=True) as response:
                if response.status == 200:
                    final_url = str(response.url)
                    print(f"URL resolvida: {final_url}")
                    return final_url
                print(f"Erro ao resolver URL curta: Status {response.status}")
                return None
    except Exception as e:
        print(f"Erro ao resolver URL curta: {str(e)}")
        return None

def extract_product_info(url: str) -> Optional[Tuple[int, int]]:
    """
    Extrai shop_id e item_id do link da Shopee
    Suporta vários formatos de URL da Shopee
    """
    try:
        # Remove parâmetros de query e decode a URL
        clean_url = unquote(url.split('?')[0])
        print(f"URL limpa: {clean_url}")
        
        # Padrões de extração de IDs
        patterns = [
            r"i\.(\d+)\.(\d+)",  # Formato curto (i.SHOP_ID.ITEM_ID)
            r"product/(\d+)/(\d+)",  # Formato completo (/product/SHOP_ID/ITEM_ID)
            r"-i\.(\d+)\.(\d+)",  # Formato alternativo (-i.SHOP_ID.ITEM_ID)
            r"\.(\d+)\.(\d+)$",  # Formato no final da URL (.SHOP_ID.ITEM_ID)
            r"(?:/|-)i\.(\d+)\.(\d+)(?:/|$)",  # Formato com prefixo/sufixo
            r"(?:/|-)(\d+)\.(\d+)(?:/|$)",  # Formato numérico simples
        ]
        
        # Tenta cada padrão
        for pattern in patterns:
            match = re.search(pattern, clean_url)
            if match:
                shop_id = int(match.group(1))
                item_id = int(match.group(2))
                print(f"IDs extraídos: shop_id={shop_id}, item_id={item_id}")
                return shop_id, item_id
        
        # Se não encontrou com os padrões, tenta extrair da query string
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        if 'shop_id' in query_params and 'item_id' in query_params:
            shop_id = int(query_params['shop_id'][0])
            item_id = int(query_params['item_id'][0])
            print(f"IDs extraídos da query: shop_id={shop_id}, item_id={item_id}")
            return shop_id, item_id
        
        # Tenta extrair do final da URL
        parts = clean_url.split('-i.')
        if len(parts) > 1:
            last_part = parts[-1]
            id_parts = last_part.split('.')
            if len(id_parts) >= 2:
                try:
                    shop_id = int(id_parts[0])
                    item_id = int(id_parts[1].split('?')[0])
                    print(f"IDs extraídos do final: shop_id={shop_id}, item_id={item_id}")
                    return shop_id, item_id
                except ValueError:
                    pass
            
        print(f"Nenhum padrão conhecido encontrado na URL: {url}")
        return None
    except Exception as e:
        print(f"Erro ao extrair IDs: {str(e)}")
        return None

async def get_product_details(url: str) -> Optional[Dict]:
    """Obtém detalhes do produto usando a API GraphQL da Shopee"""
    try:
        # Se for uma URL curta, resolve para a URL completa
        if 's.shopee' in url or 'shope.ee' in url:
            print("Detectada URL curta, resolvendo...")
            resolved_url = await resolve_short_url(url)
            if resolved_url:
                url = resolved_url
                print(f"URL resolvida: {url}")
            else:
                print("Não foi possível resolver a URL curta")
                return None

        # Extrai IDs do produto
        product_info = extract_product_info(url)
        if not product_info:
            print(f"Não foi possível extrair IDs da URL: {url}")
            return None

        shop_id, item_id = product_info
        
        # Gera parâmetros de autenticação
        timestamp = int(time.time())
        auth_params = generate_auth_params(timestamp)
        
        # Query GraphQL
        query = """
        query GetItemDetail($shopId: String!, $itemId: String!) {
            getItemDetail(shopId: $shopId, itemId: $itemId) {
                item {
                    itemid
                    shopid
                    name
                    image
                    images
                    currency
                    stock
                    status
                    ctime
                    sold
                    historical_sold
                    liked_count
                    price
                    price_min
                    price_max
                    price_before_discount
                    show_discount
                    raw_discount
                    discount
                    shop_name
                    brand
                    item_status
                    price_min_before_discount
                    price_max_before_discount
                    has_lowest_price_guarantee
                    show_free_shipping
                    description
                    attributes {
                        name
                        value
                    }
                    rating_star
                    rating_count {
                        rating
                        count
                    }
                }
            }
        }
        """
        
        # Prepara a requisição
        headers = {
            "Content-Type": "application/json",
            "X-Shopee-Client-Id": auth_params["id"],
            "X-Shopee-Client-Signature": auth_params["signature"],
            "X-Shopee-Client-Timestamp": auth_params["timestamp"]
        }
        
        variables = {
            "shopId": str(shop_id),
            "itemId": str(item_id)
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Faz a requisição GraphQL
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload) as response:
                response_text = await response.text()
                print(f"Resposta da API: {response_text}")
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if "errors" in data:
                        print(f"Erro na resposta GraphQL: {data['errors']}")
                        return None
                        
                    if data.get("data", {}).get("getItemDetail", {}).get("item"):
                        item = data["data"]["getItemDetail"]["item"]
                        return {
                            'id': item_id,
                            'name': item.get('name', ''),
                            'price': float(item.get('price', 0)) / 100000,  # Convertendo para reais
                            'original_price': float(item.get('price_before_discount', 0)) / 100000,
                            'discount': item.get('raw_discount', 0),
                            'stock': item.get('stock', 0),
                            'description': item.get('description', ''),
                            'sales': item.get('historical_sold', 0),
                            'rating': item.get('rating_star', 0),
                            'rating_count': sum(rc.get('count', 0) for rc in item.get('rating_count', [])),
                            'shop_name': item.get('shop_name', ''),
                            'shop_rating': 5.0,  # Temporário
                            'link': url
                        }
                    
                    print("Dados do produto não encontrados na resposta")
                else:
                    print(f"Erro na requisição: Status {response.status}")
                
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return None