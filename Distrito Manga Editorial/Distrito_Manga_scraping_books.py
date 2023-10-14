# Editorial Distrito Manga

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select        
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import  time, traceback, re

'''
    Clase donde vamos a ir guardando los mangas que leemos del fichero
'''
class MangaBuscador:

    def __init__(self, titulo, tomoActual):
        self.titulo = titulo
        self.tomoActual = int(tomoActual)

'''
    Clase donde vamos a ir guardando los mangas que obtenemos de la pagina
'''
class Manga:

    def __init__(self, titulo):
        self.titulo = titulo

'''
    Método que establece los filtros deseados y recarga la página
'''
def setFilters(webdriver):
    
    action = ActionChains(webdriver)

    time.sleep(2)

    # Show the filter box
    webdriver.execute_script("document.getElementById('FiltroBox').style.display='block';")

    # Get the element and generate a click action
    filtro = webdriver.find_element(By.ID,'FiltroBox')

    action.click(filtro)
    action.perform()

    time.sleep(2)

    # Selected the first filter
    tematica = webdriver.find_element(By.ID,'Tematica')    
    Select(tematica).select_by_value("49")
    
    time.sleep(2)

    # Selected the second filter
    subtematica = webdriver.find_element(By.ID,'subTematica')
    Select(subtematica).select_by_value("198626")

    time.sleep(2)

    # Hide the filter box
    webdriver.execute_script("document.getElementById('FiltroBox').style.display='none';")

    # Wait until the page update the search
    WebDriverWait(webdriver, 10).until_not(lambda d : webdriver.find_element(By.ID,'infinity-loader-icon').is_displayed()) 

    time.sleep(10)

'''
    Metodo que limpia la pagina (borra cookies y el boton de ayuda)
    y permite moverse entre ellas
'''
def cleanPage(webdriver):
    webdriver.execute_script("document.getElementById('launcher').style.display='none';")

    webdriver.find_element(By.ID,'cierreBanner').click()

'''
    Método que devuelve una lista de todos los productos de la pagina X
'''
def getProducts(webdriver):

    lits_products_title = []

    # Get the list of all products (evitamos obtener de los autores)
    list_products_id = webdriver.find_element(By.ID,'products-row')

    WebDriverWait(webdriver, 10).until(EC.visibility_of_element_located((By.ID, 'products-row')))

    # Metodo que me devuelve todos los titulos de los libros de la Pagina X
    list_products = list_products_id.find_elements(By.CSS_SELECTOR,'.img-fluid.product-thumbnail-first')
    
    for products in list_products:
        lits_products_title.append(Manga(products.get_attribute("title")))

    return lits_products_title

'''
    Obtiene el numero total de paginas retornando el maximo
'''
def getPages(webdriver):
    list_pages_html = webdriver.find_elements(By.CLASS_NAME, 'js-search-link')
    list_pages = []
    for page in list_pages_html:
        if page.get_attribute("rel") == "nofollow":
            list_pages.append(page.get_attribute("data-page").strip())

    return max(list_pages)

'''
    Pasa a la siguiente pagina
'''
def nextPage(webdriver):
        
        # Search the button
        next_page = webdriver.find_element(By.CSS_SELECTOR,'.next.js-search-link')

        next_page.click()

        # Wait until the page update the search
        WebDriverWait(webdriver, 10).until_not(lambda d : webdriver.find_element(By.ID,'infinity-loader-icon').is_displayed()) 

        time.sleep(12)


try:

    # Example
    title = 'Shikimori es más que una cara bonita'

    url = "https://www.penguinlibros.com/es/module/elastico/elasticosearch"

    currentNumberTitle = 8

    buscador = MangaBuscador(title, currentNumberTitle)

    driver = webdriver.Chrome()

    driver.get(url)

    # Check filters (con esto cargamos la pagina con los filtros)
    setFilters(driver)

    # Clean the page to avoid problemas while move between pages
    cleanPage(driver)

    list_products_per_page = []
    max_page= int(getPages(driver))
    page = 1

    while page <= max_page:
        
        # Get all products for and specific page
        list_products = getProducts(driver) 

        list_products_per_page.append(list_products)
        
        # If we finnish to collect all page, stop navigate to next page
        if page != max_page: nextPage(driver)

        page += 1 
   
    # Show the titles
    #for list_products in list_products_per_page:
    #    for product in list_products:
    #        print(product.titulo)
    find = []

    for list_products in list_products_per_page:
        for product in list_products:
            if re.match(buscador.titulo + ' \d+',product.titulo):
                find.append(product.titulo)

    find.sort()

    for tomo_faltante in find[buscador.tomoActual:]:
        print("Falta por comprar el siguiente tomo: " + tomo_faltante)

except Exception as e:
    error_trace = traceback.format_exc()
    print("ERROR - ", time.ctime(time.time()))
    print(error_trace)
finally:
    driver.close()
