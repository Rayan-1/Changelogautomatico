import requests
import base64
from datetime import datetime, timedelta
import calendar

def is_weekday(date):
    return date.weekday() < 5  

current_date = datetime.now()
year = current_date.year
month = current_date.month

pat = ""
base_url = "https://dev.azure.com/fitbank/Infra/_apis/wiki/wikis/Infra.wiki"
headers = {
    "Authorization": "Basic " + base64.b64encode(bytes(f":{pat}", "ascii")).decode("ascii"),
    "Content-Type": "application/json"
}


months = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]
month_name = months[month - 1]

month_folder_path = f"/Janela/{month_name}"
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

for day in range(current_date.day, calendar.monthrange(year, month)[1] + 1):  
    try:
        
        date = datetime(year, month, day)

        
        if is_weekday(date):
            formatted_date = date.strftime("%d-%m-%Y")
            wiki_path_parent = f"{month_folder_path}/{formatted_date}"

            
            parent_page_url = f"{base_url}/pages?path={wiki_path_parent}&api-version=6.0"
            response = requests.get(parent_page_url, headers=headers)

            if response.status_code == 200:
                print(f"A página pai '{wiki_path_parent}' já existe.")
            else:
                print(f"A página pai '{wiki_path_parent}' não existe. Criando...")

                parent_page_data = {
                    "content": "",
                    "contentType": "markdown",
                    "isDefaultContent": True
                }
                response = requests.put(parent_page_url, json=parent_page_data, headers=headers)

                if response.status_code == 200 or response.status_code == 201:
                    print(f"Página pai '{wiki_path_parent}' criada com sucesso.")
                else:
                    print(f"Erro ao criar a página pai '{wiki_path_parent}': {response.text}")
                    continue

            
            child_files = ["MS", "API", "Sites"]
            with open("ChangeAutoPython/Funcionalidades.txt", "r") as file:
                content = file.read()

            for file_name in child_files:
                wiki_path_child = f"{wiki_path_parent}/{file_name}"
                page_url = f"{base_url}/pages?path={wiki_path_child}&api-version=6.0"

                child_page_response = requests.get(page_url, headers=headers)

                if child_page_response.status_code == 404:
                    data = {
                        "content": content,  
                        "contentType": "markdown",
                        "isDefaultContent": False
                    }

                    response = requests.put(page_url, json=data, headers=headers)

                    if response.status_code == 200:
                        print(f"Página '{wiki_path_child}' criada com sucesso e conteúdo adicionado.")
                    else:
                        print(f"Erro ao criar página '{wiki_path_child}': {response.text}")
                elif child_page_response.status_code == 200:
                    print(f"A página '{wiki_path_child}' já existe.")
                else:
                    print(f"Erro ao verificar página '{wiki_path_child}': {child_page_response.text}")

    except ValueError:
        
        pass
