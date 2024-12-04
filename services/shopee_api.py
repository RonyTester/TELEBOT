import aiohttp
import json
from typing import Dict, Optional
import re
import time
import random

async def get_shopee_cookies() -> Dict[str, str]:
    """Obtém cookies necessários para a API da Shopee"""
    base_url = "https://shopee.com.br"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-platform": '"Windows"'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, headers=headers) as response:
            cookies = response.cookies
            cookie_dict = {cookie.key: cookie.value for cookie in cookies.values()}
            
            # Adiciona SPC_EC para simular um usuário logado
            cookie_dict["SPC_EC"] = "-"
            return cookie_dict

async def extract_product_info_from_url(url: str) -> Optional[Dict]:
    """
    Extrai shopid e itemid do link da Shopee
    Exemplo: https://shopee.com.br/produto-nome-i.123456789.987654321
    """
    # Remove parâmetros da URL
    url = url.split('?')[0]
    
    # Tenta diferentes padrões de URL
    patterns = [
        r"i\.(\d+)\.(\d+)",  # Padrão normal
        r"/i\.(\d+)\.(\d+)",  # Com barra
        r"-i\.(\d+)\.(\d+)",  # Com hífen
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return {
                "shop_id": match.group(1),
                "item_id": match.group(2)
            }
    
    print(f"Não foi possível extrair IDs da URL: {url}")
    return None

async def get_product_details(url: str) -> Optional[Dict]:
    """
    Busca detalhes de um produto específico da Shopee usando a API pública
    """
    product_info = await extract_product_info_from_url(url)
    if not product_info:
        return None
    
    # Gera um ID de sessão aleatório
    session_id = f"{int(time.time())}.{random.randint(100000, 999999)}"
    
    base_url = "https://shopee.com.br/api/v4/item/get"
    params = {
        "itemid": product_info["item_id"],
        "shopid": product_info["shop_id"]
    }
    
    # Obtém cookies frescos
    cookies = await get_shopee_cookies()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": url,
        "X-Shopee-Language": "pt-BR",
        "X-API-SOURCE": "pc",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-platform": '"Windows"',
        "X-CSRFToken": cookies.get("csrftoken", ""),
        "sz-token": session_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Fazendo requisição para: {base_url}")
            print(f"Params: {params}")
            print(f"Headers: {headers}")
            print(f"Cookies: {cookies}")
            
            async with session.get(
                base_url,
                params=params,
                headers=headers,
                cookies=cookies,
                allow_redirects=True
            ) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Resposta: {json.dumps(data, indent=2)}")
                    
                    if "item" not in data or not data["item"]:
                        print("Nenhum dado retornado da API")
                        return None
                    
                    item = data["item"]
                    
                    # Formata os dados do produto
                    return {
                        "id": item["itemid"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "price": float(item["price"]) / 100000,
                        "original_price": float(item.get("price_before_discount", 0)) / 100000,
                        "discount": item.get("raw_discount", 0),
                        "stock": item.get("stock", 0),
                        "sales": item.get("historical_sold", 0),
                        "rating": item.get("item_rating", {}).get("rating_star", 0),
                        "rating_count": sum(item.get("item_rating", {}).get("rating_count", [0])),
                        "shop_name": item.get("shop_location", ""),
                        "shop_rating": item.get("shop_rating", 0),
                        "images": [f"https://cf.shopee.com.br/file/{img}" for img in item.get("images", [])],
                        "link": url,
                        "categories": [cat.get("display_name", "") for cat in item.get("categories", [])]
                    }
                else:
                    print(f"Erro na API: Status {response.status}")
                    print(f"Resposta: {await response.text()}")
                    return None
    except Exception as e:
        print(f"Erro ao buscar detalhes do produto: {e}")
        return None 