import aiohttp
import json
from typing import Dict, Optional
import re

async def extract_product_info_from_url(url: str) -> Optional[Dict]:
    """
    Extrai shopid e itemid do link da Shopee
    Exemplo: https://shopee.com.br/produto-nome-i.123456789.987654321
    """
    pattern = r"i\.(\d+)\.(\d+)"
    match = re.search(pattern, url)
    if match:
        return {
            "shop_id": match.group(1),
            "item_id": match.group(2)
        }
    return None

async def get_product_details(url: str) -> Optional[Dict]:
    """
    Busca detalhes de um produto específico da Shopee usando a API não oficial
    """
    product_info = await extract_product_info_from_url(url)
    if not product_info:
        return None
    
    base_url = f"https://shopee.com.br/api/v4/item/get"
    params = {
        "itemid": product_info["item_id"],
        "shopid": product_info["shop_id"]
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    item = data.get("data")
                    if not item:
                        return None
                    
                    # Formata os dados do produto
                    return {
                        "id": item["itemid"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "price": item["price"] / 100000,
                        "original_price": item.get("price_before_discount", 0) / 100000,
                        "discount": item.get("raw_discount", 0),
                        "stock": item.get("stock", 0),
                        "sales": item.get("historical_sold", 0),
                        "rating": item.get("item_rating", {}).get("rating_star", 0),
                        "rating_count": sum(item.get("item_rating", {}).get("rating_count", [0])),
                        "shop_name": item.get("shop_name", ""),
                        "shop_rating": item.get("shop_rating", 0),
                        "images": [f"https://cf.shopee.com.br/file/{img}" for img in item.get("images", [])],
                        "link": url,
                        "categories": [cat.get("display_name") for cat in item.get("categories", [])]
                    }
    except Exception as e:
        print(f"Erro ao buscar detalhes do produto: {e}")
        return None 