import aiohttp
import json
from typing import List, Dict, Optional

async def search_shopee(query: str, limit: int = 5, category_id: Optional[int] = None) -> List[Dict]:
    """
    Busca produtos na Shopee usando a API não oficial
    
    Args:
        query: Termo de busca
        limit: Número máximo de produtos (padrão: 5)
        category_id: ID da categoria (opcional)
    """
    base_url = "https://shopee.com.br/api/v4/search/search_items"
    
    async with aiohttp.ClientSession() as session:
        params = {
            "keyword": query,
            "limit": limit,
            "newest": 0,
            "order": "desc",  # Ordenação: desc (maior preço) ou asc (menor preço)
            "page_type": "search",
            "scenario": "PAGE_GLOBAL_SEARCH",
            "version": 2
        }
        
        # Adiciona categoria se especificada
        if category_id:
            params["category_id"] = category_id
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            async with session.get(base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    
                    return [{
                        "id": item["item_basic"]["itemid"],
                        "name": item["item_basic"]["name"],
                        "price": item["item_basic"]["price"] / 100000,
                        "original_price": item["item_basic"].get("price_before_discount", 0) / 100000,
                        "discount": item["item_basic"].get("raw_discount", 0),
                        "stock": item["item_basic"].get("stock", 0),
                        "sales": item["item_basic"].get("historical_sold", 0),
                        "rating": item["item_basic"].get("item_rating", {}).get("rating_star", 0),
                        "rating_count": item["item_basic"].get("item_rating", {}).get("rating_count", [0])[0],
                        "image": f"https://cf.shopee.com.br/file/{item['item_basic']['image']}",
                        "link": f"https://shopee.com.br/product/{item['item_basic']['shopid']}/{item['item_basic']['itemid']}"
                    } for item in items if items]
                
                return []
        except Exception as e:
            print(f"Erro na busca: {e}")
            return [] 