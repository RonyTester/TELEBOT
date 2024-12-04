import aiohttp
import json
from typing import Dict, Optional
import re
import time

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
    Busca detalhes de um produto específico da Shopee usando GraphQL
    """
    product_info = await extract_product_info_from_url(url)
    if not product_info:
        return None
    
    base_url = "https://shopee.com.br/api/v4/pdp/get_pc"
    params = {
        "shop_id": product_info["shop_id"],
        "item_id": product_info["item_id"]
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": url,
        "X-Shopee-Language": "pt-BR",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-platform": '"Windows"',
        "AF-AC-Enc-Date": str(int(time.time() * 1000))
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Fazendo requisição para: {base_url}")
            print(f"Params: {params}")
            
            async with session.get(
                base_url,
                params=params,
                headers=headers,
                allow_redirects=True
            ) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"Resposta: {json.dumps(data, indent=2)}")
                    
                    if "data" not in data or not data["data"]:
                        print("Nenhum dado retornado da API")
                        return None
                    
                    item = data["data"]
                    
                    # Formata os dados do produto
                    return {
                        "id": item["itemid"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "price": float(item["price_info"]["price"]) / 100000,
                        "original_price": float(item["price_info"].get("price_before_discount", 0)) / 100000,
                        "discount": item["price_info"].get("raw_discount", 0),
                        "stock": item["stock_info"].get("stock", 0),
                        "sales": item["historical_sold"],
                        "rating": item.get("item_rating", {}).get("rating_star", 0),
                        "rating_count": sum(item.get("item_rating", {}).get("rating_count", [0])),
                        "shop_name": item["shop_info"]["name"],
                        "shop_rating": item["shop_info"].get("rating_star", 0),
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