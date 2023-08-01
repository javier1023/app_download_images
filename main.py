import importlib


def import_module(module_name):
    r'''
    Importa una biblioteca. En caso de que no esté instalada, la instala.
    :param module_name:
    :return:
    '''
    try:
        importlib.import_module(module_name)
        print(f"{module_name} está instalado.")
    except ImportError:
        print(f"{module_name} no está instalado. Instalando...")
        try:
            import pip
            pip.main(["install", module_name])
            print(f"{module_name} se ha instalado correctamente.")
        except Exception as e:
            print(f"No se pudo instalar {module_name}. Error: {e}")

# Lista de bibliotecas
libraries = [
    "tkinter",
    "rx",
    "aiohttp",
    "asyncio",
    "PIL",
    "bs4",
]

for library in libraries:
    import_module(library)


import tkinter as tk
from tkinter import messagebox
from rx import Observable
from rx.core import Observer
import aiohttp
import asyncio
from PIL import Image, ImageTk
import io
from bs4 import BeautifulSoup
from tkinter import ttk

#URL PARA COMPROBAR QUE FUNCIONA: https://www.revolracing.com/our-mission/?v=bc78a8d162c6

class ImageObserver(Observer):
    r'''
    Observer que recibe los datos de la imagen y los muestra de forma secuencial en la lista de imágenes.
    '''
    def __init__(self, total_images):
        super().__init__()
        self.total_images = total_images
        self.completed_images = 0

    def on_next(self, value):
        image_listbox.insert(tk.END, value)
        self.completed_images += 1
        # Actualizamos la barra de progreso
        progress_bar['value'] = (self.completed_images / self.total_images) * 100
        # Actualizamos el root de la aplicación
        root.update()

        # En el caso de que la ultima imagen se haya descargado, se muestra el mensaje de las imagenes totales encontradas
        if self.completed_images == self.total_images:
            image_count_label.config(text="Se encontraron {} imágenes".format(self.total_images))

    def on_error(self, error):
        messagebox.showerror("Error", str(error))

    def on_completed(self):
        pass

async def download_images_from_url(url):
    r'''
    Descarga las imágenes de forma asíncrona de la página web especificada en el URL.
    :param url:
    :return:
    '''
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    #Nos guardamos todas las imagenes
                    img_tags = soup.find_all('img')
                    #Obtenemos el total de imágenes encontradas
                    total_images = len(img_tags)

                    if total_images == 0:
                        raise messagebox.showerror("Error", "No se encontraron imágenes en la página web.")

                    image_observer = ImageObserver(total_images)
                    image_observable.subscribe(image_observer)

                    for img_tag in img_tags:
                        # Obtenemos la url de la imagen
                        img_url = img_tag['src']
                        #await asyncio.sleep(0.1)

                        #Llamamos a la funión de descarga de la imagen
                        await download_image(session, img_url, total_images, image_observer)
                else:
                    raise Exception("No se pudo descargar la página. Código de estado: " + str(response.status))
    except Exception as e:
        image_observer.on_error(e)

async def download_image(session, url, total_images, image_observer):
    r'''
    Descarga la imagen de forma asíncrona.
    :param session: sesión de aiohttp inciada en download_images_from_url
    :param url: url de la imagen
    :param total_images: imagenes totales encontradas
    :param image_observer: observer que recibe los datos de la imagen
    '''
    try:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                image_name = url.split("/")[-1]  # Obtener el nombre de la imagen del URL
                image_observer.on_next((image_name, url, image_data))  # Notificar al Observer con el nombre, URL y datos de la imagen
            else:
                raise Exception("No se pudo descargar la imagen. Código de estado: " + str(response.status))
    except Exception as e:
        # Ignorar el error y continuar con la siguiente imagen
        pass

def start_asyncio_event_loop():
    r'''
    Inicia el event loop de asyncio.
    '''
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(download_images_from_url(url_entry.get()))

def show_image(event):
    r'''
    Muestra la imagen seleccionada en la lista de imágenes en caso de que se clique en una de ellas
    :param event: el evento que se ha producido (clicar encima de una imagen)
    :return:
    '''
    selected_image_index = image_listbox.curselection()[0]
    selected_image_data = image_listbox.get(selected_image_index)
    selected_image_name, selected_image_url, selected_image_data = selected_image_data[0], selected_image_data[1], selected_image_data[2]

    # Abrimos la imagen clicada
    image = Image.open(io.BytesIO(selected_image_data))
    image.thumbnail((800, 800))
    # Creamos el label de la imagen
    photo = ImageTk.PhotoImage(image)
    image_label.configure(image=photo)
    image_label.image = photo


# El codigo de la aplicación empieza aquí
root = tk.Tk()
root.title("Aplicación de Descarga de Imágenes")
root.geometry("1200x600")

# Creamos el label de la imagen
image_observable = Observable()
image_observer = None

url_label = tk.Label(root, text="URL de la página:")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

download_button = tk.Button(root, text="Descargar", command=start_asyncio_event_loop)
download_button.pack()

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

image_listbox = tk.Listbox(frame, width=60)
image_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)

image_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=image_listbox.yview)

# Añadimos un evento para que cuando se haga clic en una imagen se muestre
image_listbox.bind("<<ListboxSelect>>", show_image)

image_frame = tk.Frame(root)
image_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)

image_label = tk.Label(image_frame)
image_label.pack(fill=tk.BOTH, expand=True)

progress_frame = tk.Frame(root)
progress_frame.pack(fill=tk.X, padx=10, pady=10)

progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

image_count_label = tk.Label(progress_frame)
image_count_label.pack(side=tk.LEFT)


if __name__ == '__main__':
    root.mainloop()

