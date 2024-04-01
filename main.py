import requests
import base64
from datetime import datetime, timedelta
import calendar
import argparse

def is_weekday(date):
    return date.weekday() < 4

def create_wiki_page(url, headers, content):
    response = requests.put(url, json=content, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        print(f"Página criada com sucesso.")
    else:
        print(f"Erro ao criar página: {response.text}")

def create_changelog_month(year, month):
    pat = ""
    base_url = "https://dev.azure.com/fitbank/Fit/_apis/wiki/wikis/Fit.wiki"
    headers = {
        "Authorization": "Basic " + base64.b64encode(bytes(f":{pat}", "ascii")).decode("ascii"),
        "Content-Type": "application/json"
    }

    meses_em_portugues = {
        "January": "Janeiro",
        "February": "Fevereiro",
        "March": "Março",
        "April": "Abril",
        "May": "Maio",
        "June": "Junho",
        "July": "Julho",
        "August": "Agosto",
        "September": "Setembro",
        "October": "Outubro",
        "November": "Novembro",
        "December": "Dezembro"
    }

    month_name = meses_em_portugues[calendar.month_name[month]]

    month_folder_path = f"/Wiki - Tecnologia Geral/Calendário de Implantações/2024/{month_name} {year}"
    month_folder_url = f"{base_url}/pages?path={month_folder_path}&api-version=6.0"
    response = requests.get(month_folder_url, headers=headers)

    if response.status_code != 200:
        print(f"A pasta do mês '{month_folder_path}' não existe. Criando...")
        month_folder_data = {
            "content": "",
            "contentType": "markdown",
            "isDefaultContent": True
        }
        response = requests.put(month_folder_url, json=month_folder_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print(f"Pasta do mês '{month_folder_path}' criada com sucesso.")
        else:
            print(f"Erro ao criar a pasta do mês '{month_folder_path}': {response.text}")
            exit()

    current_date = datetime(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]

    for day in range(1, last_day + 1):  
     try:
        date = datetime(year, month, day)

        if is_weekday(date):
            formatted_date = date.strftime("%d-%m-%Y")
            wiki_path_parent = f"{month_folder_path}/{formatted_date}"

            parent_page_url = f"{base_url}/pages?path={wiki_path_parent}&api-version=6.0"
            parent_page_response = requests.get(parent_page_url, headers=headers)

            if parent_page_response.status_code == 404:
                print(f"A página pai '{wiki_path_parent}' não existe. Criando...")

                parent_page_data = {
                    "content": "",
                    "contentType": "markdown",
                    "isDefaultContent": True
                }
                create_wiki_page(parent_page_url, headers, parent_page_data)
                
                # Criação dos arquivos 'ms.txt' e 'sites.txt' de segunda a quinta-feira
                child_files = {"Janela Microsserviços": "ms.txt", "Janela Sites": "sites.txt"}

                for file_name, file_content in child_files.items():
                    wiki_path_child = f"{wiki_path_parent}/{file_name}"
                    page_url = f"{base_url}/pages?path={wiki_path_child}&api-version=6.0"
                    
                    with open(file_content, "r") as file:
                        content = file.read()

                    # Verifica se é um dia útil de segunda a quinta-feira
                    if date.weekday() in [0, 1, 2, 3]:
                        data = {
                            "content": content,  
                            "contentType": "markdown",
                            "isDefaultContent": False
                        }

                        child_page_response = requests.get(page_url, headers=headers)

                        if child_page_response.status_code == 404:
                            create_wiki_page(page_url, headers, data)

                # Criação do arquivo 'api.txt' apenas nas terças e quintas
                if date.weekday() in [1, 3]:
                    file_name = "Janela Api.Rest"
                    file_content = "api.txt"
                    wiki_path_child = f"{wiki_path_parent}/{file_name}"
                    page_url = f"{base_url}/pages?path={wiki_path_child}&api-version=6.0"
                    
                    with open(file_content, "r") as file:
                        content = file.read()

                    data = {
                        "content": content,  
                        "contentType": "markdown",
                        "isDefaultContent": False
                    }

                    child_page_response = requests.get(page_url, headers=headers)

                    if child_page_response.status_code == 404:
                        create_wiki_page(page_url, headers, data)

            elif parent_page_response.status_code == 200:
                print(f"A página pai '{wiki_path_parent}' já existe.")
            else:
                print(f"Erro ao verificar a página pai '{wiki_path_parent}': {parent_page_response.text}")

     except ValueError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Criar changelog mensal')
    parser.add_argument('-y', '--year', type=int, help='Ano do changelog', required=True)
    parser.add_argument('-m', '--month', type=int, help='Mês do changelog', required=True)
    args = parser.parse_args()

    # Cria o changelog do mês especificado
    create_changelog_month(args.year, args.month)
