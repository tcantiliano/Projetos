import pyautogui as py
import time
py.PAUSE = 1
py.press('win')
py.write('google chrome')
py.press('enter')
py.write('https://sia.estacio.br/sianet/logon')
py.press('enter')
time.sleep(2)
py.click(x=1263, y=319)

py.alert(text="Aguarde o carregamento da pagina\nLogado com Sucesso",title="Fim",button='OK')