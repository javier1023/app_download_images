import asyncio
import rx
import rx.operators as ops
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def download_image(session, url):
    async def fetch(url):
        async with session.get(url) as response:
            return await response.read()

    return await fetch(url)


async def process_url(url):
    async with ClientSession() as session:
        html = await fetch_html(session, url)
        image_urls = extract_image_urls(html)

        total_images = len(image_urls)
        progress_step = 100 / total_images

        for image_url in image_urls:
            image_data = await download_image(session, image_url)
            display_image(image_data)
            progress_bar.step(progress_step)
            await asyncio.sleep(0.1)

        messagebox.showinfo("Finalizado", "Todas las imágenes han sido descargadas.")


async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()


def extract_image_urls(html):
    soup = BeautifulSoup(html, 'html.parser')
    image_tags = soup.find_all('img')
    image_urls = [img.get('src') for img in image_tags]
    return image_urls


def display_image(image_data):
    image = Image.open(image_data)
    image.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(image)
    image_listbox.insert(tk.END, "")
    image_listbox.image_names.append(photo)
    image_listbox.image_data.append(image_data)


def handle_listbox_selection(event):
    selected_index = image_listbox.curselection()
    if selected_index:
        image_data = image_listbox.image_data[selected_index[0]]
        image = Image.open(image_data)
        image.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(image)
        image_label.configure(image=photo)
        image_label.image = photo


def start_download():
    print('hola caracola')
    url = url_entry.get()
    if url:
        loop.create_task(process_url(url))


# Crear ventana principal
window = tk.Tk()
window.title("Descargar imágenes")
window.geometry("800x600")

# Crear elementos de la interfaz
url_label = tk.Label(window, text="URL:")
url_entry = tk.Entry(window, width=50)
download_button = tk.Button(window, text="Descargar", command=start_download)
progress_bar = Progressbar(window, orient=tk.HORIZONTAL, length=300, mode='determinate')
image_listbox = tk.Listbox(window, selectmode=tk.SINGLE)
image_listbox.bind('<<ListboxSelect>>', handle_listbox_selection)
image_label = tk.Label(window)

# Posicionar elementos en la interfaz
url_label.pack(pady=10)
url_entry.pack(pady=10)
download_button.pack(pady=10)
progress_bar.pack(pady=10)
image_listbox.pack(side=tk.LEFT, padx=10, pady=10)
image_label.pack(side=tk.RIGHT, padx=10, pady=10)

# Configurar lista de imágenes
image_listbox.image_names = []
image_listbox.image_data = []

# Obtener bucle de eventos
loop = asyncio.get_event_loop()

# Iniciar bucle de eventos de Tkinter
window.mainloop()

loop.close()