import aiohttp
import os
from dotenv import load_dotenv
import time
import hashlib
import hmac
import json
import re
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, parse_qs

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API da Shopee
PARTNER_ID = os.getenv('SHOPEE_PARTNER_ID')
API_KEY = os.getenv('SHOPEE_API_KEY')
API_BASE = "https://partner.shopeemobile.com/api/v1"

def generate_signature(endpoint: str, timestamp: int) -> str:
    """Gera a assinatura para autenticação na API"""
    base_string = f"{PARTNER_ID}{endpoint}{timestamp}{API_KEY}"
    return hmac.new(
        API_KEY.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

async def resolve_short_url(url: str) -> Optional[str]:
    """Resolve URLs curtas da Shopee para a URL completa"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    return str(response.url)
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
        # Padrões de extração de IDs
        patterns = [
            r"i\.(\d+)\.(\d+)",  # Formato curto (i.SHOP_ID.ITEM_ID)
            r"/product/(\d+)/(\d+)",  # Formato completo (/product/SHOP_ID/ITEM_ID)
            r"-i\.(\d+)\.(\d+)",  # Formato alternativo (-i.SHOP_ID.ITEM_ID)
            r"\.(\d+)\.(\d+)$",  # Formato no final da URL (.SHOP_ID.ITEM_ID)
        ]
        
        # Remove parâmetros de query da URL
        clean_url = url.split('?')[0]
        
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
            
        print(f"Nenhum padrão conhecido encontrado na URL: {url}")
        return None
    except Exception as e:
        print(f"Erro ao extrair IDs: {str(e)}")
        return None

async def get_product_details(url: str) -> Optional[Dict]:
    """Obtém detalhes do produto usando a API oficial da Shopee"""
    try:
        # Se for uma URL curta, resolve para a URL completa
        if 's.shopee' in url:
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
        timestamp = int(time.time())
        endpoint = "/item/get"
        signature = generate_signature(endpoint, timestamp)

        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "partner_id": int(PARTNER_ID),
            "timestamp": timestamp,
            "sign": signature,
            "shop_id": shop_id,
            "item_id": item_id
        }

        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}{endpoint}"
            print(f"Fazendo requisição para: {api_url}")
            print(f"Parâmetros: {params}")
            
            async with session.get(api_url, headers=headers, params=params) as response:
                response_text = await response.text()
                print(f"Resposta da API (get_product_details): {response_text}")
                
                if response.status == 200:
                    data = json.loads(response_text)
                    if data.get("item"):
                        item = data["item"]
                        
                        # Gera link de afiliado
                        affiliate_link = await generate_affiliate_link(url)
                        
                        return {
                            'id': item_id,
                            'name': item.get('name', ''),
                            'price': float(item.get('price', 0)) / 100000,  # Convertendo para reais
                            'original_price': float(item.get('original_price', 0)) / 100000,
                            'discount': calculate_discount(
                                item.get('price', 0),
                                item.get('original_price', 0)
                            ),
                            'sales': item.get('historical_sold', 0),
                            'rating': item.get('item_rating', {}).get('rating_star', 0),
                            'rating_count': sum(item.get('item_rating', {}).get('rating_count', [0])),
                            'shop_name': item.get('shop_name', ''),
                            'shop_rating': item.get('shop_rating', 0),
                            'description': item.get('description', ''),
                            'stock': item.get('stock', 0),
                            'link': affiliate_link or url  # Usa URL original se falhar geração do link afiliado
                        }
                    else:
                        print(f"Erro nos dados retornados: {data.get('error_msg', 'Erro desconhecido')}")
                else:
                    print(f"Erro na requisição: Status {response.status}")
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return None

async def generate_affiliate_link(url: str) -> Optional[str]:
    """Gera um link de afiliado para o produto"""
    try:
        timestamp = int(time.time())
        endpoint = "/link/generate"
        signature = generate_signature(endpoint, timestamp)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "partner_id": int(PARTNER_ID),
            "timestamp": timestamp,
            "sign": signature,
            "original_url": url
        }
        
        async with aiohttp.ClientSession() as session:
            api_url = f"{API_BASE}{endpoint}"
            async with session.post(api_url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("affiliate_link"):
                        return result["affiliate_link"]
                print(f"Resposta da API (generate_affiliate_link): {await response.text()}")
        return None
    except Exception as e:
        print(f"Erro ao gerar link afiliado: {str(e)}")
        return None

def calculate_discount(current_price: float, original_price: float) -> int:
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