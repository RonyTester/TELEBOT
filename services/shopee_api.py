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
        
        # Query GraphQL para obter detalhes do produto
        query = """
            query GetProductDetails($shopId: Int!, $itemId: Int!) {
                product(shopId: $shopId, itemId: $itemId) {
                    itemId
                    name
                    price
                    stock
                    description
                    images
                    rating
                    historicalSold
                    shop {
                        name
                        rating
                    }
                }
            }
        """
        
        # Gera timestamp e assinatura
        timestamp = int(time.time())
        signature = hmac.new(
            API_KEY.encode(),
            f"{PARTNER_ID}{timestamp}{API_KEY}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Prepara headers e payload
        headers = {
            "Content-Type": "application/json",
            "Authorization": signature,
            "X-Shopee-Partner-Id": PARTNER_ID,
            "X-Shopee-Timestamp": str(timestamp)
        }
        
        payload = {
            "query": query,
            "variables": {
                "shopId": shop_id,
                "itemId": item_id
            }
        }
        
        # Faz a requisição GraphQL
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Resposta GraphQL: {json.dumps(data, indent=2)}")
                    
                    if data.get('data', {}).get('product'):
                        product = data['data']['product']
                        return {
                            'id': item_id,
                            'name': product.get('name', ''),
                            'price': float(product.get('price', 0)) / 100000,  # Convertendo para reais
                            'stock': product.get('stock', 0),
                            'description': product.get('description', ''),
                            'sales': product.get('historicalSold', 0),
                            'rating': product.get('rating', 0),
                            'shop_name': product.get('shop', {}).get('name', ''),
                            'shop_rating': product.get('shop', {}).get('rating', 0),
                            'link': url  # Por enquanto, usa a URL original
                        }
                    
                    print("Dados do produto não encontrados na resposta")
                else:
                    print(f"Erro na requisição GraphQL: Status {response.status}")
                    print(await response.text())
                
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return None