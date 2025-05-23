# Commented out IPython magic to ensure Python compatibility.
# %pip -q install google-genai

# Configura a API Key do Google Gemini

import os
from google.colab import userdata

os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')

# Instalar Framework de agentes do Google ################################################
!pip install -q google-adk

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from datetime import date
import textwrap
from IPython.display import display, Markdown
import warnings

warnings.filterwarnings("ignore")

# Função auxiliar que envia uma mensagem para um agente via Runner e retorna a resposta final
def call_agent(agent: Agent, message_text: str) -> str:
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=agent.name, user_id="kid_user", session_id="session_1")
    runner = Runner(agent=agent, app_name=agent.name, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=message_text)])

    final_response = ""
    for event in runner.run(user_id="kid_user", session_id="session_1", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response += part.text
                    final_response += "\n"
    return final_response

# Função auxiliar para exibir texto formatado em Markdown no Colab
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

##################################################
# --- Agente 1: Boas-Vindas e Intenção --- #
##################################################
def agente_boas_vindas(nome_crianca):
    boas_vindas_agente = Agent(
        name="boas_vindas_agente",
        model="gemini-2.0-flash",
        instruction=f"""
        Olá, {nome_crianca}! Eu sou a Moeda Mágica, sua amiga especial para aprender sobre o mundo do dinheiro! ✨
        Estou super animada para te ajudar hoje. Sobre o que você gostaria de conversar?
        Podemos falar sobre como guardar dinheiro, sonhar com algo legal para comprar ou aprender sobre a poupança.
        Escolhe uma dessas opções para começarmos nossa aventura financeira! 😊
        """,
        description="Agente para dar boas-vindas personalizadas à criança e identificar sua intenção."
    )
    return boas_vindas_agente

##################################################
# --- Agente 2: Agente de Definição de Objetivos --- #
##################################################
def agente_objetivo(nome_crianca):
    objetivo_agente = Agent(
        name="agente_objetivo",
        model="gemini-2.0-flash",
        instruction=f"""
        Que legal que você quer sonhar em comprar algo, {nome_crianca}! Me conta qual é essa coisa mágica que você gostaria de ter?
        Pode ser um brinquedo, um jogo, uma viagem... o que estiver na sua imaginação!
        Depois de me contar, podemos tentar descobrir quanto custa e ver se tem opções mais em conta, que tal? 😉
        """,
        description="Agente para ajudar a criança a definir seu objetivo de poupança e iniciar a busca de preços."
    )
    return objetivo_agente

##################################################
# --- Agente 3: Agente de Explicação da Poupança --- #
##################################################
def agente_poupanca(nome_crianca):
    poupanca_agente = Agent(
        name="agente_poupanca",
        model="gemini-2.0-flash",
        instruction=f"""
        Entendi, {nome_crianca}! Poupar é como juntar estrelinhas brilhantes em um cofrinho mágico para alcançar seus sonhos! ✨
        Cada estrelinha que você guarda te deixa mais perto de conseguir aquela coisa especial.
        É como construir um castelo de areia, grão por grão! Quer saber mais sobre como poupar direitinho? 😊
        """,
        description="Agente para explicar o conceito de poupança."
    )
    return poupanca_agente

##################################################
# --- Agente 4: Agente de Plano de Poupança --- #
##################################################
def agente_plano(nome_crianca):
    plano_agente = Agent(
        name="agente_plano",
        model="gemini-2.0-flash",
        instruction=f"""
        Vamos criar um plano mágico para você conseguir seu objetivo, {nome_crianca}!
        Para isso, me conta: você recebe alguma mesada? Ajuda em casa para ganhar um dinheirinho?
        Pensa um pouquinho e me diz quanto você acha que consegue guardar por semana ou por mês.
        Assim, a gente pode descobrir em quanto tempo a magia vai acontecer! 🧙‍♂️
        """,
        description="Agente para criar um plano de poupança para a criança."
    )
    return plano_agente

##################################################
# --- Agente 5: Agente de Acompanhamento --- #
##################################################
def agente_acompanhamento(nome_crianca):
    acompanhamento_agente = Agent(
        name="agente_acompanhamento",
        model="gemini-2.0-flash",
        instruction=f"""
        Olá novamente, {nome_crianca}! Que legal te ver de novo! 😊
        Me conta, quantas estrelinhas mágicas você conseguiu guardar essa semana para o seu sonho?
        Lembre-se, cada pouquinho conta e te deixa mais perto da sua magia! ✨
        Se precisar de ideias de como guardar mais, me diz! 😉
        """,
        description="Agente para acompanhar o progresso da criança e oferecer incentivo."
    )
    return acompanhamento_agente

##################################################
# --- Agente 6: Agente de Busca de Preços --- #
##################################################
def agente_busca_preco():
    busca_preco_agente = Agent(
        name="agente_busca_preco",
        model="gemini-2.0-flash",
        instruction="""
        Você é a 'Lupa Mágica de Preços' da Moeda Mágica. Sua tarefa é usar a ferramenta de busca do Google (google_search)
        para encontrar informações sobre o preço de um item que a criança quer comprar.
        Tente encontrar o preço médio e, o mais importante, opções mais baratas ou de bom custo-benefício,
        incluindo o nome das lojas online onde você encontrou essas ofertas (se a informação estiver clara nos resultados).

        Apresente as informações de forma super amigável para a criança. Use frases como:
        - 'Olha só o que achei na [Nome da Loja]! Que tal esse [Nome do Item], parece ter um preço bem legal: [Preço]. O que você acha?'
        - 'Fiz uma pesquisa e encontrei uma opção um pouco mais barata na [Nome da Loja]: [Preço]. Essa pode ser uma boa alternativa para você!'
        - 'Vi também na [Nome da Loja] essa outra opção por [Preço]. Parece um bom negócio!'

        Se encontrar links diretos para as páginas dos produtos, você pode mencionar:
        - 'Se quiser dar uma olhada, peça ajuda para acessar esse link: [Link do Produto].' (Lembre-se, crianças precisam de ajuda para acessar links).

        Limite-se a apresentar no máximo 2 ou 3 opções para não confundir a criança.
        Se o item for muito vago, peça para a criança ser mais específica.
        """,
        description="Agente para buscar informações de preços de produtos no Google e apresentar de forma amigável para crianças.",
        tools=[google_search]
    )
    return busca_preco_agente

##################################################
# --- Agente 7: Agente de Explicação de Conceitos Financeiros --- #
##################################################
def agente_explicar_conceito(nome_crianca, tema):
    explicar_agente = Agent(
        name=f"agente_explicar_{tema.replace(' ', '_').lower()}",
        model="gemini-2.0-flash",
        instruction=f"""
        Olá novamente, {nome_crianca}! Que ótimo que você quer aprender sobre '{tema}'! 😊
        Explique o conceito de '{tema}' para uma criança de forma simples, divertida e com exemplos práticos.
        Tente usar analogias ou histórias para facilitar o entendimento.
        """,
        description=f"Agente para explicar o conceito de '{tema}' para crianças."
    )
    return explicar_agente

# --- Início da Conversa ---
if __name__ == "__main__":
    print("🚀 Iniciando a Aventura Financeira com a Moeda Mágica! 🚀")
    nome_crianca = input("😊 Olá! Qual é o seu nome? ")
    print(f"\nMoeda Mágica: Olá, {nome_crianca}! Que bom ter você por aqui!")

    boas_vindas = agente_boas_vindas(nome_crianca)
    resposta_boas_vindas = call_agent(boas_vindas, f"Meu nome é {nome_crianca}.")
    print("\n--- 📝 Moeda Mágica ---\n")
    display(to_markdown(resposta_boas_vindas))
    print("--------------------------------------------------------------")

    # --- Próximo passo: Definir o objetivo e perguntar sobre a busca de preços ---
    objetivo = agente_objetivo(nome_crianca)
    mensagem_objetivo = input(f"Você: (diga o que você quer comprar) ")
    resposta_objetivo = call_agent(objetivo, mensagem_objetivo)
    print("\n--- 📝 Moeda Mágica (Definindo Objetivo) ---\n")
    display(to_markdown(resposta_objetivo))
    print("--------------------------------------------------------------")

    # --- Pergunta se a criança quer buscar preços ---
    quer_buscar_preco = input(f"Você ({nome_crianca}, quer saber os preços? sim/não): ")
    if "sim" in quer_buscar_preco.lower():
        busca_preco = agente_busca_preco()
        pergunta_busca = input(f"Você (qual item você quer pesquisar o preço, {nome_crianca}?): ")
        resposta_busca_preco = call_agent(busca_preco, pergunta_busca)
        print("\n--- 📝 Lupa Mágica de Preços ---\n")
        display(to_markdown(resposta_busca_preco))
        print("--------------------------------------------------------------")
    else:
        print(f"\nMoeda Mágica: Tudo bem, {nome_crianca}! Vamos continuar planejando seu sonho mágico! ✨")

    # --- Próximo passo: Explicar a poupança ---
    poupanca = agente_poupanca(nome_crianca)
    mensagem_poupanca = input(f"Você: (pergunta sobre poupança) ")
    resposta_poupanca = call_agent(poupanca, mensagem_poupanca)
    print("\n--- 📝 Moeda Mágica (Explicando Poupança) ---\n")
    display(to_markdown(resposta_poupanca))
    print("--------------------------------------------------------------")

    # --- Próximo passo: Criar o plano de poupança ---
    plano = agente_plano(nome_crianca)
    mensagem_plano = input(f"Você: (fala sobre sua mesada/ajuda em casa) ")
    resposta_plano = call_agent(plano, mensagem_plano)
    print("\n--- 📝 Moeda Mágica (Criando Plano) ---\n")
    display(to_markdown(resposta_plano))
    print("--------------------------------------------------------------")

    # --- Próximo passo: Acompanhamento (simulação de uma interação) ---
    acompanhamento = agente_acompanhamento(nome_crianca)
    mensagem_acompanhamento = input(f"Você ({nome_crianca}, uma semana depois): ")
    resposta_acompanhamento = call_agent(acompanhamento, mensagem_acompanhamento)
    print("\n--- 📝 Moeda Mágica (Acompanhamento) ---\n")
    display(to_markdown(resposta_acompanhamento))
    print("--------------------------------------------------------------")

    continuar = input(f"Você gostaria de continuar a aventura financeira com a Moeda Mágica, {nome_crianca}? (sim/não): ")
    if "não" in continuar.lower():
        print(f"\nMoeda Mágica: Foi ótimo aprender com você hoje, {nome_crianca}! Até a próxima aventura financeira! 👋")
    else:
        print(f"\nMoeda Mágica: Que legal, {nome_crianca}! Em que mais posso te ajudar hoje?")
        while True:
            proximo_passo = input(f"Você ({nome_crianca}): (gostaria de falar sobre 'guardar dinheiro', 'comprar algo' ou 'aprender mais'?) ")
            if "guardar" in proximo_passo.lower():
                poupanca = agente_poupanca(nome_crianca)
                mensagem_poupanca = input(f"Você: (pergunta sobre poupança) ")
                resposta_poupanca = call_agent(poupanca, mensagem_poupanca)
                print("\n--- 📝 Moeda Mágica (Explicando Poupança) ---\n")
                display(to_markdown(resposta_poupanca))
                print("--------------------------------------------------------------")
            elif "comprar" in proximo_passo.lower():
                objetivo = agente_objetivo(nome_crianca)
                mensagem_objetivo = input(f"Você: (diga o que você quer comprar) ")
                resposta_objetivo = call_agent(objetivo, mensagem_objetivo)
                print("\n--- 📝 Moeda Mágica (Definindo Objetivo) ---\n")
                display(to_markdown(resposta_objetivo))
                print("--------------------------------------------------------------")
                quer_buscar_preco = input(f"Você ({nome_crianca}, quer saber os preços? sim/não): ")
                if "sim" in quer_buscar_preco.lower():
                    busca_preco = agente_busca_preco()
                    pergunta_busca = input(f"Você (qual item você quer pesquisar o preço, {nome_crianca}?): ")
                    resposta_busca_preco = call_agent(busca_preco, pergunta_busca)
                    print("\n--- 📝 Lupa Mágica de Preços ---\n")
                    display(to_markdown(resposta_busca_preco))
                    print("--------------------------------------------------------------")
            elif "aprender mais" in proximo_passo.lower():
                print("\nMoeda Mágica: Que ótimo! Podemos conversar sobre como o dinheiro funciona, a diferença entre precisar e querer, ou como podemos ajudar outras pessoas com o dinheiro. Qual desses assuntos te interessa?")
                tema_aprender = input(f"Você ({nome_crianca}): ")
                print(f"\nMoeda Mágica: Interessante! Vamos aprender mais sobre '{tema_aprender}'!")
                # Criando e chamando um agente para explicar o tema escolhido
                agente_explicar = agente_explicar_conceito(nome_crianca, tema_aprender)
                resposta_explicar = call_agent(agente_explicar, f"Explique '{tema_aprender}' para mim.")
                print("\n--- 📝 Moeda Mágica (Aprendendo Mais) ---\n")
                display(to_markdown(resposta_explicar))
                print("--------------------------------------------------------------")
                # Após explicar o tema, podemos perguntar se a criança quer aprender mais ou sair
                continuar_aprendendo = input(f"Você ({nome_crianca}), gostaria de aprender sobre outro tema? (sim/não): ")
                if "não" in continuar_aprendendo.lower():
                    break
            elif "não" in proximo_passo.lower() or "parar" in proximo_passo.lower() or "fim" in proximo_passo.lower():
                print(f"\nMoeda Mágica: Foi muito divertido aprender com você hoje, {nome_crianca}! Até a próxima! 👋")
                break
            else:
                print("\nMoeda Mágica: Desculpe, não entendi. Você gostaria de falar sobre 'guardar dinheiro', 'comprar algo' ou 'aprender mais'?")

print("\nAventura financeira finalizada!")

