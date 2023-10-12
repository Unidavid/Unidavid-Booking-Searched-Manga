from urllib.request import urlopen
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import re, time, smtplib, traceback, base64

sender_addr = "sender_addr@gmail.com"
receiver_addr = "receiver_addr@gmail.com"

'''
    Clase donde vamos a ir guardando los mangas que leemos del fichero
'''
class Manga:

    def __init__(self, titulo, tomoActual, url):
        self.titulo = titulo
        self.tomoActual = int(tomoActual)
        self.url = url


'''
    Procedimiento de envio del correo
'''
def sendMsg(sender_addr, receiver_addr, subject, body):
         
    # Create message object instance
    msg = MIMEMultipart()
        
    # Setup the parameters of the message
    msg['From'] = sender_addr
    msg['To'] = receiver_addr
    msg['Subject'] = subject
        
    # Add in the message body
    msg.attach(MIMEText(body, 'plain'))
        
    # Create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
        
    # Login Credentials for sending the mail
    server.login(sender_addr, generateToken64())
        
    # Send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()    

'''
    Permite leer de un fichero los mangas y los almacena como objeto en una lista de clase Manga
'''
def leerMangas():
    fichero = open("Mangas.txt")
    fichero.readline() # Quitamos la cabecera
    lista_mangas_fichero = fichero.read().split("\n")
    fichero.close()
    lista_mangas = list()
    
    for manga in lista_mangas_fichero:
        lista_mangas.append(Manga(manga.split("\t")[2], manga.split("\t")[0], manga.split("\t")[3]))

    return lista_mangas

'''
    Generamos el token necesario para el servicio smtp
'''
def generateToken64():
    
    token = "yourSMTPtoken"
    token_bytes = base64.b64decode(token.encode("ascii"))

    return token_bytes.decode("ascii")

'''
    Busca si a partir de una url (catalogo) y el numero de tomos actual
    si hay mas tomos en la web que de los que posees, enviando un correo notificando su disponibilidad
'''
def searchStockAvailable(tomos, url):

    pattern = url.split('/')[-2]
        
    html = urlopen(url).read().decode("utf-8")
    list_tomos_web = re.findall(pattern + "...jpg", html)

    for i in range(len(list_tomos_web)):
        list_tomos_web[i] = list_tomos_web[i].replace(".jpg","")
            
    num_tomos_web = len(list_tomos_web)

    list_tomos_faltantes = list_tomos_web[tomos:]

    print(" Dispones de un total de " + str(tomos) + " tomos")
    print("")
        
    if num_tomos_web > tomos:
        print(" Hay tomos disponibles por comprar")

        message = ""
            
        for tomo in list_tomos_faltantes:
            message = message + "Tomo " + tomo.replace(pattern,"") + ": " + tomo +"\n"
            print(" Tomo " + tomo.replace(pattern,"") + ": " + tomo)

        sendMsg(sender_addr, receiver_addr, "STOCK DISPONIBLE", message)
            
    else:
        print(" No hay tomos disponibles por comprar")


'''
    Buscador de Mangas y notificacion de la Editorial IVREA (de momento)
'''
try:

    print(" Starting - ", time.ctime(time.time()))

    # Leemos fichero
    lista_de_mangas = leerMangas()

    for manga in lista_de_mangas:
        # Check if there is stock of Manga
        print(' ------------------ Buscando Disponibilidad Manga ' + manga.titulo + ' ------------------ ')
        
        time.sleep(2)
        searchStockAvailable(manga.tomoActual, manga.url)
        
        print(' ------------------ ---------------------------------------- ------------------ \n')
        
    # Finnish
    time.sleep(2)

    print(" Running - ", time.ctime(time.time()))
    print("")

except Exception as e:
    error_trace = traceback.format_exc()
    sendMsg(sender_addr, receiver_addr, "Error en el servidor", error_trace)
    print("ERROR - ", time.ctime(time.time()))
    print(error_trace)
