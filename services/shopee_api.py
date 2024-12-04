from playwright.async_api import async_playwright
import re
from typing import Dict, Optional
import json
import asyncio

async def extract_product_info_from_url(url: str) -> Optional[Dict]:
    """
    Extrai shopid e itemid do link da Shopee
    """
    url = url.split('?')[0]
    patterns = [
        r"i\.(\d+)\.(\d+)",
        r"/i\.(\d+)\.(\d+)",
        r"-i\.(\d+)\.(\d+)",
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
    Busca detalhes de um produto usando Playwright para simular um navegador real
    """
    try:
        async with async_playwright() as p:
            # Inicia o navegador em modo headless
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Cria uma nova página
            page = await context.new_page()
            
            print(f"Acessando URL: {url}")
            
            # Navega até a página do produto
            await page.goto(url, wait_until="networkidle")
            
            # Espera elementos importantes carregarem
            await page.wait_for_selector("._44qnta", timeout=10000)  # Nome do produto
            await page.wait_for_selector("._3n5NQx", timeout=10000)  # Preço
            
            # Extrai dados usando JavaScript
            product_data = await page.evaluate("""() => {
                function getText(selector, defaultValue = '') {
                    const element = document.querySelector(selector);
                    return element ? element.innerText.trim() : defaultValue;
                }
                
                function getPrice(selector) {
                    const text = getText(selector, '0');
                    return parseFloat(text.replace('R$', '').replace('.', '').replace(',', '.'));
                }
                
                const priceElement = document.querySelector('._3n5NQx');
                const originalPriceElement = document.querySelector('._1_FtxE');
                
                return {
                    name: getText('._44qnta'),
                    price: getPrice('._3n5NQx'),
                    original_price: originalPriceElement ? getPrice('._1_FtxE') : 0,
                    description: getText('.f7AU53'),
                    shop_name: getText('.VlDReK'),
                    rating: parseFloat(getText('._1k47d8', '0')),
                    rating_count: parseInt(getText('._1k47d8 + div', '0')),
                    sales: parseInt(getText('._2y51f5', '0')),
                    stock: parseInt(getText('._2y51f5 + div', '0')),
                    categories: Array.from(document.querySelectorAll('._3YDLCj')).map(el => el.innerText),
                    images: Array.from(document.querySelectorAll('._2y51f5 img')).map(img => img.src)
                };
            }""")
            
            print(f"Dados extraídos: {json.dumps(product_data, indent=2)}")
            
            # Fecha o navegador
            await browser.close()
            
            # Adiciona informações extras
            product_data["link"] = url
            
            # Calcula desconto se houver preço original
            if product_data["original_price"] > product_data["price"]:
                discount = ((product_data["original_price"] - product_data["price"]) / product_data["original_price"]) * 100
                product_data["discount"] = round(discount)
            else:
                product_data["discount"] = 0
            
            return product_data
            
    except Exception as e:
        print(f"Erro ao extrair dados do produto: {e}")
        return None 