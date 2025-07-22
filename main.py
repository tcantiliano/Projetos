import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import DictProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.uix.spinner import Spinner
from kivy.utils import platform
import webbrowser
import urllib.parse
from datetime import datetime
from kivy.uix.image import Image # Importar o widget Image
import kivy.graphics # Importar gráficos Kivy

kivy.require('2.0.0')

class EditarCardapioPopup(Popup):
    lanchonete_app = ObjectProperty(None) # Referência para a instância principal do app

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Editar Cardápio"
        self.size_hint = (0.95, 0.95) # Popup maior para edição

        # Layout principal do popup
        main_layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        # ScrollView para a lista de itens
        scroll_view = ScrollView(do_scroll_x=False)
        self.itens_grid = GridLayout(cols=1, spacing='5dp', size_hint_y=None)
        self.itens_grid.bind(minimum_height=self.itens_grid.setter('height'))
        scroll_view.add_widget(self.itens_grid)
        main_layout.add_widget(scroll_view)

        # Botões de ação (por enquanto, apenas Fechar e um placeholder para Adicionar)
        action_buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', spacing='10dp')
        
        add_item_btn = Button(text="Adicionar Novo Item", font_size='16sp')
        add_item_btn.bind(on_press=self.placeholder_add_item) # Placeholder para adicionar item
        action_buttons_layout.add_widget(add_item_btn)

        close_btn = Button(text="Fechar", font_size='16sp')
        close_btn.bind(on_press=self.dismiss)
        action_buttons_layout.add_widget(close_btn)
        
        main_layout.add_widget(action_buttons_layout)
        self.content = main_layout
        
        # Atualiza a lista quando o popup é aberto
        self.bind(on_open=self.atualizar_lista_edicao)

    def atualizar_lista_edicao(self, instance, value):
        # Limpa o grid antes de adicionar os itens novamente
        self.itens_grid.clear_widgets()

        if self.lanchonete_app:
            for categoria, itens_da_categoria in self.lanchonete_app.cardapio.items():
                # Adiciona o título da categoria
                categoria_label = Label(
                    text=f"[b]{categoria}[/b]", # Usando markup para negrito
                    font_size='18sp',
                    size_hint_y=None,
                    height='35dp',
                    halign='left',
                    text_size=(self.itens_grid.width, None), # Permite que o texto se ajuste à largura do grid
                    markup=True # Habilita o markup para negrito
                )
                self.itens_grid.add_widget(categoria_label)

                for item, preco in itens_da_categoria.items():
                    item_info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
                    
                    item_label = Label(
                        text=f"{item}: R$ {preco:.2f}", 
                        font_size='16sp', 
                        halign='left', 
                        text_size=(self.itens_grid.width * 0.7, None) # Ajusta largura para o texto do item
                    )
                    item_info_layout.add_widget(item_label)

                    # Placeholder para botões de ação do item (Editar/Remover)
                    item_action_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing='5dp')
                    edit_item_btn = Button(text="Edit", size_hint_x=0.5, font_size='12sp')
                    delete_item_btn = Button(text="Del", size_hint_x=0.5, font_size='12sp')
                    item_action_layout.add_widget(edit_item_btn)
                    item_action_layout.add_widget(delete_item_btn)
                    item_info_layout.add_widget(item_action_layout)

                    self.itens_grid.add_widget(item_info_layout)
                
                # Espaço entre categorias
                self.itens_grid.add_widget(Label(size_hint_y=None, height='10dp'))

    def placeholder_add_item(self, instance):
        # Placeholder para a funcionalidade de adicionar item
        if self.lanchonete_app:
            self.lanchonete_app.mostrar_mensagem("Funcionalidade em Desenvolvimento", 
                                                "A interface para adicionar um novo item será implementada aqui!")


class FinalizarPedidoPopup(Popup):
    nome_cliente_input = ObjectProperty()
    endereco_cliente_input = ObjectProperty()
    frete_input = ObjectProperty()
    forma_pagamento_spinner = ObjectProperty()
    lanchonete_app = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def finalizar(self):
        nome_cliente = self.nome_cliente_input.text
        endereco_cliente = self.endereco_cliente_input.text
        forma_pagamento = self.forma_pagamento_spinner.text
        valor_frete_str = self.frete_input.text

        if not nome_cliente:
            self.lanchonete_app.mostrar_mensagem("Erro", "Por favor, digite o nome do cliente.")
            return
        if not endereco_cliente:
            self.lanchonete_app.mostrar_mensagem("Erro", "Por favor, digite o endereço do cliente.")
            return
        if not valor_frete_str:
            self.lanchonete_app.mostrar_mensagem("Erro", "Por favor, digite o valor do frete (pode ser 0).")
            return
        try:
            valor_frete = float(valor_frete_str)
            self.lanchonete_app.finalizar_pedido_com_detalhes(nome_cliente, endereco_cliente, valor_frete, forma_pagamento)
            self.dismiss()
        except ValueError:
            self.lanchonete_app.mostrar_mensagem("Erro", "Valor do frete inválido. Digite um número.")


class LanchoneteApp(App):
    cardapio = DictProperty({
        "Lanches": {
            "Hambúrguer Clássico": 12.50,
            "Sanduíche Natural": 18.00,
            "Lanche Natural de Frango": 15.00,
            "Cachorro Quente": 9.00,
            "X-Burguer": 15.00,
            "X-Salada": 16.50,
            "X-Bacon": 18.00,
        },
        "Porções": {
            "Batata Frita Média": 7.00,
            "Coxinha de Frango (unid)": 4.50,
            "Esfiha de Carne (unid)": 6.00,
            "Anéis de Cebola (P)": 10.00,
            "Porção de Calabresa": 25.00,
        },
        "Pizzas": {
            "Pizza Calabresa (grande)": 35.00,
            "Pizza Mussarela (grande)": 32.00,
            "Pizza Frango com Catupiry (grande)": 38.00,
        },
        "Bebidas": {
            "Refrigerante Lata": 5.50,
            "Suco de Laranja Natural": 6.00,
            "Água Mineral": 3.00,
            "Cerveja Long Neck": 10.00,
            "Chá Gelado": 5.00,
            "Café Expresso": 4.00,
            "Chocolate Quente": 7.50,
        },
        "Sobremesas": {
            "Milkshake de Chocolate": 10.00,
            "Açaí Pequeno": 15.00,
            "Açaí Médio": 20.00,
            "Açaí Grande": 25.00,
            "Salada de Frutas": 12.00,
            "Bolo de Cenoura": 8.00,
            "Pudim": 9.00,
            "Torta de Limão": 11.00,
            "Brigadeiro (unid)": 2.50,
            "Sorvete de Creme (bola)": 6.00,
            "Doce de Leite": 5.00,
        },
        "Beirutes": {
            "Beirute de Rosbife": 30.00,
            "Beirute de Queijo Branco": 28.00,
            "Beirute de Frango com Catupiry": 32.00,
        },
        "Combos": {
            "Combo Família (2 Lanches + 1 Batata G + 2 Refri)": 45.00,
            "Combo Solteiro (1 Lanche + 1 Batata P + 1 Refri)": 25.00,
        }
    })
    pedido = DictProperty({})
    total_pedido_itens = NumericProperty(0.00)
    valor_frete = NumericProperty(0.00)
    total_final = StringProperty("0.00")
    whatsapp_link = StringProperty("")

    def build(self):
        self.root = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')

        # Layout do Cardápio
        cardapio_layout = BoxLayout(orientation='vertical', size_hint_y=0.6)
        
        # BoxLayout para o título do cardápio e botão Editar
        titulo_cardapio_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing='10dp')
        
        cardapio_label = Label(text="Cardápio", font_size='20sp', bold=True, size_hint_x=0.7)
        
        editar_cardapio_btn = Button(
            text="Editar",
            font_size='16sp',
            size_hint_x=0.3,
            on_press=self.abrir_popup_editar_cardapio
        )
        
        titulo_cardapio_layout.add_widget(cardapio_label)
        titulo_cardapio_layout.add_widget(editar_cardapio_btn)
        
        cardapio_layout.add_widget(titulo_cardapio_layout)
        
        # O restante do cardapio_layout permanece o mesmo
        self.cardapio_grid = GridLayout(cols=1, spacing='5dp', size_hint_y=None)
        self.cardapio_grid.bind(minimum_height=self.cardapio_grid.setter('height'))

        cardapio_scroll = ScrollView(do_scroll_x=False, bar_width='10dp', bar_color=(0.7, 0.7, 0.7, 1))
        cardapio_scroll.add_widget(self.cardapio_grid)
        cardapio_layout.add_widget(cardapio_scroll)

        self.atualizar_cardapio_ui()

        self.root.add_widget(cardapio_layout)

        # Layout do Pedido (permanece como antes)
        pedido_layout = BoxLayout(orientation='vertical', size_hint_y=0.4, padding=(0, '10dp', 0, 0))
        pedido_label = Label(text="Pedido", font_size='20sp', bold=True, size_hint_y=None, height='40dp')
        pedido_layout.add_widget(pedido_label)

        self.pedido_grid = BoxLayout(orientation='vertical', spacing='5dp', size_hint_y=None)
        self.pedido_grid.bind(minimum_height=self.pedido_grid.setter('height'))
        
        pedido_scroll = ScrollView(do_scroll_x=False, bar_width='10dp', bar_color=(0.7, 0.7, 0.7, 1))
        pedido_scroll.add_widget(self.pedido_grid)
        pedido_layout.add_widget(pedido_scroll)

        total_final_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='35dp')
        total_final_label = Label(text="Total: R$ ", font_size='18sp', bold=True)
        self.total_final_value_label = Label(text=self.total_final, font_size='18sp', bold=True)
        total_final_layout.add_widget(total_final_label)
        total_final_layout.add_widget(self.total_final_value_label)
        pedido_layout.add_widget(total_final_layout)

        finalizar_pedido_btn = Button(text="Finalizar Pedido", on_press=self.abrir_popup_finalizar_pedido, size_hint_y=None, height='60dp', font_size='18sp')
        pedido_layout.add_widget(finalizar_pedido_btn)

        # CORREÇÃO: BoxLayout para o botão de compartilhamento com ícone
        self.compartilhar_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='60dp',
            padding='10dp',
            spacing='10dp'
        )
        # Adicionar as instruções de canvas.before *depois* da criação do BoxLayout
        with self.compartilhar_box.canvas.before:
            self.compartilhar_box_color = kivy.graphics.Color(0.13, 0.81, 0.29, 1) # Armazena a cor para poder alterá-la
            self.compartilhar_box_rect = kivy.graphics.Rectangle(pos=self.compartilhar_box.pos, size=self.compartilhar_box.size)

        # Vincular a posição e o tamanho do retângulo às propriedades do BoxLayout
        self.compartilhar_box.bind(pos=self._update_compartilhar_rect, size=self._update_compartilhar_rect)

        # Adicionar o ícone do WhatsApp
        whatsapp_icon = Image(source='whatsapp_icon.png', size_hint_x=0.2, allow_stretch=True, keep_ratio=True)
        self.compartilhar_box.add_widget(whatsapp_icon)
        
        # Adicionar o texto "Compartilhar" (opcional, remova se quiser apenas o ícone)
        compartilhar_label = Label(text="Compartilhar Pedido", font_size='18sp', color=(1, 1, 1, 1), bold=True)
        self.compartilhar_box.add_widget(compartilhar_label)

        # Adicionar o comportamento de clique ao BoxLayout
        self.compartilhar_box.bind(on_touch_down=self.on_compartilhar_touch_down)
        self.compartilhar_box.bind(on_touch_up=self.on_compartilhar_touch_up)

        pedido_layout.add_widget(self.compartilhar_box)

        self.root.add_widget(pedido_layout)

        return self.root

    # NOVO: Método para atualizar a posição e o tamanho do retângulo de fundo
    def _update_compartilhar_rect(self, instance, value):
        self.compartilhar_box_rect.pos = instance.pos
        self.compartilhar_box_rect.size = instance.size

    # NOVO: Método para abrir o popup de edição de cardápio
    def abrir_popup_editar_cardapio(self, instance):
        editar_popup = EditarCardapioPopup(lanchonete_app=self)
        editar_popup.open()

    # Métodos para simular o feedback visual de um botão
    def on_compartilhar_touch_down(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.compartilhar_box_color.rgba = (0.1, 0.6, 0.2, 1) # Escurece um pouco ao tocar
            return True
        return False

    def on_compartilhar_touch_up(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.compartilhar_box_color.rgba = (0.13, 0.81, 0.29, 1) # Volta à cor normal
            self.abrir_link_whatsapp(instance) # Chama a função de compartilhamento
            return True
        return False

    def atualizar_cardapio_ui(self):
        self.cardapio_grid.clear_widgets()
        for categoria, itens_da_categoria in self.cardapio.items():
            categoria_label = Label(
                text=categoria,
                font_size='18sp',
                bold=True,
                size_hint_y=None,
                height='40dp',
                halign='left',
            )
            categoria_label.bind(width=lambda instance, value:
                                 instance.setter('text_size')(instance, (value, None)))
            self.cardapio_grid.add_widget(categoria_label)

            for item, preco in itens_da_categoria.items():
                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
                item_label = Label(text=f"{item}: R$ {preco:.2f}", font_size='16sp')
                add_button = Button(text="+", size_hint_x=0.2, font_size='20sp')
                add_button.bind(on_press=lambda instance, item_nome=item: self.adicionar_ao_pedido(item_nome))
                item_layout.add_widget(item_label)
                item_layout.add_widget(add_button)
                self.cardapio_grid.add_widget(item_layout)
            
            self.cardapio_grid.add_widget(Label(size_hint_y=None, height='10dp'))


    def adicionar_ao_pedido(self, item):
        if item in self.pedido:
            self.pedido[item] += 1
        else:
            self.pedido[item] = 1
        self.atualizar_pedido_ui()

    def get_item_price(self, item_name):
        for category_items in self.cardapio.values():
            if item_name in category_items:
                return category_items[item_name]
        return 0.00

    def atualizar_pedido_ui(self):
        self.pedido_grid.clear_widgets()
        total_pedido = 0
        for item, quantidade in self.pedido.items():
            preco = self.get_item_price(item)
            subtotal = preco * quantidade

            item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')

            item_label = Label(text=f"{item} x {quantidade}", font_size='16sp')
            subtotal_label = Label(text=f"R$ {subtotal:.2f}", size_hint_x=0.3, font_size='16sp')
            remove_button = Button(text="-", size_hint_x=0.15, font_size='20sp')
            remove_button.bind(on_press=lambda instance, item_nome=item: self.remover_do_pedido(item_nome))

            item_layout.add_widget(item_label)
            item_layout.add_widget(subtotal_label)
            item_layout.add_widget(remove_button)

            self.pedido_grid.add_widget(item_layout)
            total_pedido += subtotal

        self.total_pedido_itens = total_pedido
        self.atualizar_total_final()

    def remover_do_pedido(self, item):
        if item in self.pedido:
            self.pedido[item] -= 1
            if self.pedido[item] == 0:
                del self.pedido[item]
            self.atualizar_pedido_ui()

    def abrir_popup_finalizar_pedido(self, instance):
        conteudo = BoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        
        nome_cliente_input = TextInput(hint_text="Nome do Cliente", font_size='16sp', multiline=False, size_hint_y=None, height='45dp')
        endereco_cliente_input = TextInput(hint_text="Endereço Completo", font_size='16sp', multiline=False, size_hint_y=None, height='45dp')
        frete_input = TextInput(hint_text="Valor do Frete (obrigatório, pode ser 0)", font_size='16sp', input_type='number', multiline=False, size_hint_y=None, height='45dp')
        forma_pagamento_label = Label(text="Forma de Pagamento:", font_size='16sp', size_hint_y=None, height='30dp')
        forma_pagamento_spinner = Spinner(
            text='Dinheiro',
            values=('Dinheiro', 'Cartão de Crédito', 'Cartão de Débito', 'Pix'),
            font_size='16sp',
            size_hint_y=None, height='45dp'
        )
        erro_label = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height='30dp') 
        botoes_layout = BoxLayout(orientation='horizontal', spacing='10dp', size_hint_y=None, height='50dp')
        confirmar_btn = Button(text="Confirmar", font_size='18sp')
        cancelar_btn = Button(text="Cancelar", font_size='18sp')
        botoes_layout.add_widget(confirmar_btn)
        botoes_layout.add_widget(cancelar_btn)
        
        conteudo.add_widget(nome_cliente_input)
        conteudo.add_widget(endereco_cliente_input)
        conteudo.add_widget(frete_input)
        conteudo.add_widget(forma_pagamento_label)
        conteudo.add_widget(forma_pagamento_spinner)
        conteudo.add_widget(erro_label) 
        conteudo.add_widget(botoes_layout)

        finalizar_popup = FinalizarPedidoPopup(
            title="Detalhes do Pedido",
            content=conteudo,
            size_hint=(0.9, 0.6),
            lanchonete_app=self
        )
        finalizar_popup.nome_cliente_input = nome_cliente_input
        finalizar_popup.endereco_cliente_input = endereco_cliente_input
        finalizar_popup.frete_input = frete_input
        finalizar_popup.forma_pagamento_spinner = forma_pagamento_spinner

        confirmar_btn.bind(on_press=lambda btn: finalizar_popup.finalizar())
        cancelar_btn.bind(on_press=lambda btn: finalizar_popup.dismiss())

        finalizar_popup.open()

    def finalizar_pedido_com_detalhes(self, nome_cliente, endereco_cliente, valor_frete, forma_pagamento):
        if self.pedido:
            data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            pedido_str = f"--- Pedido Finalizado ---\n"
            pedido_str += f"Cliente: {nome_cliente}\n"
            pedido_str += f"Endereço: {endereco_cliente}\n"
            pedido_str += f"Data: {data_hora_atual}\n"
            pedido_str += f"Forma de Pagamento: {forma_pagamento}\n"
            for item, quantidade in self.pedido.items():
                preco = self.get_item_price(item)
                subtotal = preco * quantidade
                pedido_str += f"{item}: {quantidade} x R$ {preco:.2f} = R$ {subtotal:.2f}\n"
            if valor_frete > 0:
                pedido_str += f"Frete: R$ {valor_frete:.2f}\n"
            else:
                pedido_str += "Frete: Não foi cobrado frete\n"
            pedido_str += f"Total: R$ {self.total_pedido_itens + valor_frete:.2f}"
            self.mostrar_mensagem("Pedido", pedido_str)
            self.valor_frete = valor_frete
            self.atualizar_total_final()
            self.gerar_link_whatsapp(pedido_str)
            self.pedido.clear()
            self.total_pedido_itens = 0.00
            self.atualizar_pedido_ui()
        else:
            self.mostrar_mensagem("Pedido", "Seu carrinho está vazio.")

    def atualizar_total_final(self):
        self.total_final = f"{self.total_pedido_itens + self.valor_frete:.2f}"
        self.total_final_value_label.text = self.total_final

    def gerar_link_whatsapp(self, mensagem):
        mensagem_codificada = urllib.parse.quote(mensagem)
        self.whatsapp_link = f"https://wa.me/?text={mensagem_codificada}"

    def abrir_link_whatsapp(self, instance):
        if self.whatsapp_link:
            webbrowser.open(self.whatsapp_link)

    def mostrar_mensagem(self, titulo, mensagem):
        popup_content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        popup_label = Label(text=mensagem, font_size='16sp', halign='center', valign='middle')
        popup_content.add_widget(popup_label)
        
        close_button = Button(text="Fechar", size_hint_y=None, height='40dp', font_size='16sp')
        popup_content.add_widget(close_button)

        popup = Popup(title=titulo, content=popup_content,
                      size_hint=(0.9, 0.5))
        
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    LanchoneteApp().run()