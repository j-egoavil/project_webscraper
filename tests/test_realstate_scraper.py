import sys
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SimpleListingScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def get_random_property_url(self, search_url):
        """Obtiene una URL aleatoria de propiedad desde la página de búsqueda"""
        print(f"🔍 Buscando propiedades en COLOMBIA: {search_url}")
        self.driver.get(search_url)
        
        # Esperar a que cargue
        time.sleep(random.uniform(5, 8))
        
        print("📄 Página cargada, buscando propiedades en Colombia...")
        
        property_urls = []
        
        try:
            # Buscar todos los links que parezcan ser de propiedades
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"🔗 Encontrados {len(all_links)} links en total")
            
            for i, link in enumerate(all_links):
                try:
                    href = link.get_attribute('href')
                    if href and 'properati.com.co' in href:
                        # Incluir solo URLs que parezcan propiedades específicas (con IDs o slugs largos)
                        if ('/s/' in href or '/propiedad/' in href) and len(href) > 50:
                            # Excluir páginas de categoría general
                            if not any(pattern in href for pattern in ['/venta', '/alquiler', '?page=', '?operation=']):
                                if href not in property_urls:
                                    property_urls.append(href)
                                    print(f"✅ Propiedad COLOMBIA encontrada ({len(property_urls)}): {href}")
                except Exception as e:
                    continue
            
            print(f"📋 Total de propiedades COLOMBIA encontradas: {len(property_urls)}")
            
            # Si no encontramos con filtro estricto, buscar más flexible
            if not property_urls:
                print("🔍 Búsqueda flexible de propiedades...")
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        if href and 'properati.com.co' in href and '/s/' in href:
                            if href not in property_urls:
                                property_urls.append(href)
                                print(f"✅ Propiedad encontrada (flexible): {href}")
                    except:
                        continue
            
            if property_urls:
                # Elegir una propiedad aleatoria
                selected_url = random.choice(property_urls)
                print(f"🎯 URL COLOMBIA seleccionada: {selected_url}")
                return selected_url
            else:
                print("❌ No se encontraron propiedades en Colombia")
                return None
                
        except Exception as e:
            print(f"❌ Error buscando propiedades: {e}")
            return None

class SimpleDetailScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
    
    def scrape(self, url):
        print(f"🌐 Navegando a propiedad COLOMBIA: {url}")
        self.driver.get(url)
        
        # Esperar más tiempo y de forma más inteligente
        time.sleep(random.uniform(4, 7))
        
        # Verificar si cargó correctamente
        if "properati.com.co" not in self.driver.current_url:
            return {"error": "No se cargó la página de Properati Colombia"}
        
        data = {}
        
        try:
            # Esperar a que cargue el contenido
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Título - buscar en diferentes lugares
            title_selectors = [
                "h1",
                ".posting-title",
                "[data-qa='posting-title']",
                ".title",
                "h1.title",
                ".property-title"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and len(text) > 5 and "404" not in text and "403" not in text:
                        data['title'] = text
                        print(f"✅ Título COLOMBIA: {text}")
                        break
                except:
                    continue
            else:
                data['title'] = "No encontrado"
                print("❌ No se encontró el título")
                
        except Exception as e:
            print(f"❌ Error con título: {e}")
            data['title'] = "Error"
        
        try:
            # Precio - específico para Colombia (COP)
            price_selectors = [
                "[data-qa='posting-price']",
                ".posting-price",
                ".price",
                "[class*='price']",
                ".price-value",
                "div[class*='price']",
                ".property-price"
            ]
            
            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        # Buscar precios en pesos colombianos
                        if text and ('$' in text or 'COP' in text or 'cop' in text.lower() or 'pesos' in text.lower()):
                            data['price'] = text
                            print(f"✅ Precio COLOMBIA: {text}")
                            break
                    if 'price' in data:
                        break
                except:
                    continue
            else:
                data['price'] = "No encontrado"
                print("❌ No se encontró el precio")
                
        except Exception as e:
            print(f"❌ Error con precio: {e}")
            data['price'] = "Error"
        
        try:
            # Ubicación - específico para Colombia
            location_selectors = [
                "[data-qa='posting-location']",
                ".posting-location",
                ".location",
                "[class*='location']",
                ".address",
                ".property-location"
            ]
            
            for selector in location_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 3:
                            data['location'] = text
                            print(f"✅ Ubicación COLOMBIA: {text}")
                            break
                    if 'location' in data:
                        break
                except:
                    continue
            else:
                data['location'] = "No encontrado"
                print("❌ No se encontró la ubicación")
                
        except Exception as e:
            print(f"❌ Error con ubicación: {e}")
            data['location'] = "Error"
        
        # Información adicional para Colombia
        try:
            # Área en m²
            area_selectors = [".area", "[class*='area']", "[class*='size']", ".property-area"]
            for selector in area_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and ('m²' in text or 'mt2' in text or 'metros' in text.lower()):
                            data['area'] = text
                            print(f"✅ Área: {text}")
                            break
                    if 'area' in data:
                        break
                except:
                    continue
        except:
            pass
        
        return data

def test_scraper_colombia():
    """Test que obtiene una propiedad real de COLOMBIA y la prueba"""
    
    print("🔧 Configurando driver...")
    print("🇨🇴 TEST ESPECÍFICO PARA COLOMBIA")
    
    # Configuración STEALTH - navegador visible
    chrome_options = Options()
    
    # QUITAMOS headless - navegador visible para evitar detección
    # chrome_options.add_argument("--headless=new")  # COMENTADO
    
    # Opciones para parecer más humano
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent real
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Ejecutar script para ocultar automation
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        print("🚀 Iniciando test COLOMBIA...")
        print("💡 Buscando propiedades reales en Properati Colombia")
        
        # Paso 1: Obtener una URL real de propiedad en COLOMBIA
        listing_scraper = SimpleListingScraper(driver)
        
        # URL de búsqueda en Properati COLOMBIA
        search_urls = [
            "https://www.properati.com.co/s/venta",
            "https://www.properati.com.co/s/bogota/venta",
            "https://www.properati.com.co/s/medellin/venta",
            "https://www.properati.com.co/s/cali/venta"
        ]
        
        property_url = None
        for search_url in search_urls:
            print(f"\n🔍 Probando búsqueda en: {search_url}")
            property_url = listing_scraper.get_random_property_url(search_url)
            if property_url:
                break
        
        if not property_url:
            print("❌ No se pudo obtener una URL de propiedad en Colombia")
            return False
        
        print(f"\n🎯 URL COLOMBIA OBTENIDA DEL SITIO: {property_url}")
        
        # Paso 2: Hacer scraping de la propiedad
        detail_scraper = SimpleDetailScraper(driver)
        datos = detail_scraper.scrape(property_url)
        
        print("\n" + "="*60)
        print("📊 RESULTADOS DEL SCRAPING - COLOMBIA")
        print("="*60)
        
        for key, value in datos.items():
            print(f"   {key.capitalize()}: {value}")
        
        # Verificaciones
        title_ok = datos.get('title') not in ["No encontrado", "Error"] and datos.get('title')
        price_ok = datos.get('price') not in ["No encontrado", "Error"] and datos.get('price')
        location_ok = datos.get('location') not in ["No encontrado", "Error"] and datos.get('location')
        
        if title_ok and price_ok:
            print("\n✅ ¡TEST EXITOSO EN COLOMBIA!")
            print("   Se extrajeron correctamente título y precio")
            if location_ok:
                print("   También se extrajo la ubicación")
            return True
        else:
            print("\n❌ TEST FALLADO EN COLOMBIA")
            if not title_ok:
                print("   - No se pudo extraer el título")
            if not price_ok:
                print("   - No se pudo extraer el precio")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n🔚 Cerrando driver en 10 segundos...")
        time.sleep(10)
        driver.quit()

if __name__ == "__main__":
    print("🇨🇴 TEST: Scraping con URL real de COLOMBIA")
    print("⚠️  Este test abrirá Chrome y buscará propiedades en Colombia")
    
    confirmacion = input("¿Ejecutar el test? (s/n): ")
    if confirmacion.lower() == 's':
        success = test_scraper_colombia()
        if success:
            print("\n🎉 ¡El scraper funciona correctamente en Colombia!")
        else:
            print("\n💥 El scraper tiene problemas con propiedades de Colombia")
    else:
        print("Test cancelado")