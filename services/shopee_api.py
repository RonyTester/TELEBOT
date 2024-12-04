import os
from dotenv import load_dotenv
import time
import hmac
import hashlib
import json
import re
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, parse_qs
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API da Shopee
PARTNER_ID = os.getenv('SHOPEE_PARTNER_ID')
API_KEY = os.getenv('SHOPEE_API_KEY')
API_URL = "https://open-api.affiliate.shopee.com.br/graphql"

def generate_signature(timestamp: int) -> str:
    """Gera a assinatura para autenticação na API"""
    base_string = f"{PARTNER_ID}{timestamp}{API_KEY}"
    return hmac.new(
        API_KEY.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

async def get_graphql_client() -> Client:
    """Cria e retorna um cliente GraphQL configurado"""
    timestamp = int(time.time())
    signature = generate_signature(timestamp)
    
    # Configura o transporte com os headers necessários
    transport = AIOHTTPTransport(
        url=API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": signature,
            "X-Shopee-Partner-Id": PARTNER_ID,
            "X-Shopee-Timestamp": str(timestamp)
        }
    )
    
    return Client(
        transport=transport,
        fetch_schema_from_transport=True
    )

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
    """Obtém detalhes do produto usando a API GraphQL da Shopee"""
    try:
        # Extrai IDs do produto
        product_info = extract_product_info(url)
        if not product_info:
            print(f"Não foi possível extrair IDs da URL: {url}")
            return None

        shop_id, item_id = product_info
        
        # Query GraphQL para obter detalhes do produto
        query = gql("""
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
        """)
        
        variables = {
            "shopId": shop_id,
            "itemId": item_id
        }
        
        # Obtém o cliente GraphQL
        client = await get_graphql_client()
        
        try:
            # Executa a query
            result = await client.execute_async(query, variable_values=variables)
            print(f"Resposta GraphQL: {json.dumps(result, indent=2)}")
            
            if result and 'product' in result:
                product = result['product']
                
                # Gera link de afiliado
                affiliate_link = await generate_affiliate_link(url)
                
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
                    'link': affiliate_link or url
                }
            
            print("Dados do produto não encontrados na resposta")
            return None
            
        except TransportQueryError as e:
            print(f"Erro na query GraphQL: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Erro ao buscar produto: {str(e)}")
        return None

async def generate_affiliate_link(url: str) -> Optional[str]:
    """Gera um link de afiliado para o produto usando GraphQL"""
    try:
        # Query GraphQL para gerar link de afiliado
        query = gql("""
            mutation GenerateAffiliateLink($url: String!) {
                generateAffiliateLink(originalUrl: $url) {
                    affiliateUrl
                    shortUrl
                }
            }
        """)
        
        variables = {
            "url": url
        }
        
        # Obtém o cliente GraphQL
        client = await get_graphql_client()
        
        try:
            # Executa a mutation
            result = await client.execute_async(query, variable_values=variables)
            print(f"Resposta GraphQL (link afiliado): {json.dumps(result, indent=2)}")
            
            if result and 'generateAffiliateLink' in result:
                # Retorna o link curto se disponível, senão o link normal
                return (result['generateAffiliateLink'].get('shortUrl') or 
                        result['generateAffiliateLink'].get('affiliateUrl'))
            
            print("Link de afiliado não encontrado na resposta")
            return None
            
        except TransportQueryError as e:
            print(f"Erro na mutation GraphQL: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Erro ao gerar link afiliado: {str(e)}")
        return None