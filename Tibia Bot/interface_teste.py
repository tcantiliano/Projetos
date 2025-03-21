import customtkinter as ctk
import pyautogui as pag
import time
import threading
import keyboard  # Importa a biblioteca keyboard

# Área de controle
parar = False

# Área de funções
def rotacaoMagias():
    global parar
    while not parar:
        time.sleep(2)
        pag.PAUSE = 2
        pag.press("num6")
        pag.press("num4")
        pag.press("num2")
        pag.press("num1")
        print('Rotacao de magias Iniciada')

def iniciarRotacao():
    global parar
    parar = False
    threading.Thread(target=rotacaoMagias).start()

def pararRotacao():
    global parar
    parar = True
    print('Rotacao de magias finalizada')

# Funções para controle via teclado
def on_key_iniciar():
    iniciarRotacao()

def on_key_parar():
    pararRotacao()

# Configurações de teclas
keyboard.add_hotkey('ctrl+f11', on_key_iniciar)
keyboard.add_hotkey('ctrl+f12', on_key_parar)

# Cria a janela principal
root = ctk.CTk()

# Define o título da janela
root.geometry("300x200")
root.title("Interface Teste")

# Cria um rótulo
label = ctk.CTkLabel(root, text="Este é um label")
label.pack(pady=20)

# Cria um botão para iniciar a rotação de magias
button_iniciar = ctk.CTkButton(root, text="Iniciar rotação Magias", command=iniciarRotacao)
button_iniciar.pack(pady=10)

# Cria um botão para parar a rotação de magias
button_parar = ctk.CTkButton(root, text="Parar rotação Magias", command=pararRotacao)
button_parar.pack(pady=10)

# Executa a aplicação
root.mainloop()

#falta apromirar interface com o bot, exibir um log de ações, e adicionar mais funções de controle e fazer que o proprio usuario possa configurar as rotação de skill que ele deseja