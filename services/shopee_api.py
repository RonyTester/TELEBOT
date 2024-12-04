import aiohttp
import json

async def search_shopee(query: str):
    """
    Busca produtos na Shopee usando a API não oficial
    """
    base_url = "https://shopee.com.br/api/v4/search/search_items"
    
    async with aiohttp.ClientSession() as session:
        params = {
            "keyword": query,
            "limit": 5,
            "newest": 0,
        }
        
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                items = data.get("items", [])
                
                return [{
                    "name": item["item_basic"]["name"],
                    "price": item["item_basic"]["price"] / 100000,  # Converte para reais
                    "link": f"https://shopee.com.br/product/{item['item_basic']['shopid']}/{item['item_basic']['itemid']}"
                } for item in items]
            return [] 