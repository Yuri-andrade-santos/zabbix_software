# Aplicativo Zabbix Docker

## Visão Geral
O Aplicativo Zabbix Docker é uma aplicação GUI desenvolvida em Python que interage com a API do Zabbix. Ele permite que usuários gerenciem hosts e templates do Zabbix de forma simples e intuitiva. As principais funcionalidades incluem login de usuário, exibição de hosts cadastrados, criação de novos hosts a partir de um arquivo CSV , visualização de templates e geração de relatórios em csv e em graficos.

## Funcionalidades
- **Login de Usuário**: Autenticação segura para acesso ao sistema.
- **Exibir Hosts**: Recupera e exibe a lista de hosts cadastrados no Zabbix.
- **Criar Hosts**: Permite criar novos hosts no Zabbix através do upload de um arquivo CSV com os detalhes dos hosts.
- **Exibir Templates**: Visualiza os templates disponíveis e seus respectivos IDs.
- **Relatórios**: Gera relatórios em formato CSV e gráficos para análise de dados.

## Instalação
Para instalar e utilizar o Aplicativo Zabbix Docker, siga os passos abaixo:

1. **Clone o Repositório**:
   ```
   git clone <url-do-repositorio>
   cd zabbix-docker
   ```

2. **Instale as Dependências**:
   Certifique-se de ter o Python instalado. Em seguida, instale os pacotes necessários:
   ```
   pip install -r requirements.txt
   ```

## Uso
1. **Execute a Aplicação**:
   Rode o script principal:
   ```
   python docker1.py
   ```

2. **Login**:
   Informe seu usuário e senha do Zabbix na janela de login.

3. **Navegação**:
   - Utilize o menu lateral para exibir hosts, criar novos hosts ou visualizar templates.
   - Ao criar hosts, siga as instruções para selecionar e enviar um arquivo CSV.
   - Para gerar relatórios, selecione a opção desejada no menu e siga as instruções.

## Formato do CSV para Criação de Hosts
O arquivo CSV deve conter os seguintes cabeçalhos:
- `hostname`: Nome do equipamento.
- `ip`: Endereço IP do equipamento.
- `groupid`: ID do grupo ao qual o equipamento pertence.
- `templateid`: ID do template a ser utilizado.

## Dependências
A aplicação utiliza as seguintes bibliotecas Python:
- `customtkinter`: Para a interface gráfica.
- `pyzabbix`: Para integração com a API do Zabbix.
- `PIL`: Para manipulação de imagens.
- `matplotlib`: Para geração de gráficos.
- `csv`: Para manipulação de arquivos CSV.

## Agradecimentos
- Agradecimentos à comunidade Zabbix pela documentação e suporte.
- Agradecimento especial aos colaboradores que ajudaram a aprimorar esta aplicação.

## Imagens do sistema

