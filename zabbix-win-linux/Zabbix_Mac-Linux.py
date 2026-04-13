from venv import create
import customtkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter.filedialog
from pyzabbix import ZabbixAPI
from tkinter import messagebox, Text, END
from PIL import Image
import requests
import csv
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt 
import matplotlib
matplotlib.use('Agg')
#teste


ZABBIX_URL = 'http://ip_do_zabbix:port/' # URL do zabbix
usuario_logado = None
senha_logada = None

def tela_login():
    global usuario_logado, senha_logada
    usuario = login_entry.get()
    senha = senha_entry.get()

    if not usuario or not senha:
        messagebox.showwarning("erro de login", "Usuário ou senha incorretos.")
        login_entry.delete(0, 'end')
        senha_entry.delete(0, 'end')
        login_entry.focus()
        return

    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(usuario, senha)
        messagebox.showinfo("Sucesso", "Login bem-sucedido!")
        usuario_logado = usuario
        senha_logada = senha
        criar_nova_guia()
    except Exception as e:
        messagebox.showerror("Erro de login", f"Falha ao fazer login:\n{e}")

def fechar_login():
    login.destroy()
    sys.exit()

login = customtkinter.CTk()
login.title("Login")
login.geometry("600x600")
login.protocol("WM_DELETE_WINDOW", fechar_login)  # Fecha o programa ao clicar no X

logo_image = customtkinter.CTkImage(light_image=Image.open("IT.png"), size=(450, 150))
logo_label = customtkinter.CTkLabel(login, image=logo_image, text="")
logo_label.pack(pady=(30, 10))

login_entry = customtkinter.CTkEntry(login, placeholder_text="Username")
login_entry.pack(padx=20, pady=20)

senha_entry = customtkinter.CTkEntry(login, placeholder_text="Password", show="*")
senha_entry.pack(padx=30, pady=30)

login.update_idletasks()
width = login.winfo_screenwidth()
height = login.winfo_screenheight()
size = tuple(int(_) for _ in login.geometry().split('+')[0].split('x'))
x = width/2 - size[0]/2
y = height/2 - size[1]/2
login.geometry("%dx%d+%d+%d" % (size + (x, y)))

def mostrar_hosts(frame_conteudo):
    global usuario_logado, senha_logada
    usuario = usuario_logado
    senha = senha_logada
    for widget in frame_conteudo.winfo_children():
        widget.destroy()
    text = customtkinter.CTkLabel(frame_conteudo, text="Hosts do Zabbix", font=("Arial", 20))
    text.pack(padx=20, pady=20)

    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(usuario, senha)
        hosts = zapi.host.get(output=["hostid", "name"])

        scroll_frame_host = customtkinter.CTkScrollableFrame(frame_conteudo, width=700, height=400)
        scroll_frame_host.pack(padx=20, pady=20, fill="both", expand=True)

        if hosts:
            for host in hosts:
                host_label = customtkinter.CTkLabel(
                    scroll_frame_host,
                    text=f"{host['hostid']} - {host['name']}",
                    font=("Arial", 14),
                    anchor="w",
                    justify="left"
                )
                host_label.pack(anchor="w", padx=40)
        else:
            empty_label = customtkinter.CTkLabel(frame_conteudo, text="Nenhum host encontrado.", font=("Arial", 14))
            empty_label.pack(padx=40, pady=10)
    except Exception as e:
        error_label = customtkinter.CTkLabel(frame_conteudo, text=f"Erro ao buscar hosts:\n{e}", font=("Arial", 14))
        error_label.pack(padx=40, pady=10)

def criar_hosts(janela_principal):
    janela_principal.withdraw()  # Oculta o menu principal
    global usuario_logado, senha_logada
    usuario = usuario_logado
    senha = senha_logada

    create = customtkinter.CTk()
    create.title("Criar Hosts")
    create.geometry("400x400")

    create.update_idletasks()
    width = create.winfo_screenwidth()
    height = create.winfo_screenheight()
    size = tuple(int(_) for _ in create.geometry().split('+')[0].split('x'))
    x = width/2 - size[0]/2
    y = height/2 - size[1]/2
    create.geometry("%dx%d+%d+%d" % (size + (x, y)))



    def escolher_csv():
        arquivo_csv = tkinter.filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if arquivo_csv:
            processar_csv(arquivo_csv)

    def processar_csv(arquivo_csv):
        try:
            zapi = ZabbixAPI(ZABBIX_URL)
            zapi.login(usuario_logado, senha_logada)
            with open(arquivo_csv, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hostname = row.get("hostname")
                    ip = row.get("ip")
                    groupid = row.get("groupid")
                    templateid = row.get("templateid")
                    port = row.get("port")
                    if not (hostname and ip and groupid and templateid and port):
                        print(f"Dados faltando na linha: {row}")
                        continue
                    try:
                        zapi.host.create(
                            host=hostname,
                            interfaces=[{
                                "type": 1,
                                "main": 1,
                                "useip": 1,
                                "ip": ip,
                                "dns": "",
                                "port": port
                            }],
                            groups=[{"groupid": groupid}],
                            templates=[{"templateid": templateid}]
                        )
                        print(f"Host criado: {hostname}")
                    except Exception as e:
                        print(f"Erro ao criar host {hostname}: {e}")
            messagebox.showinfo("Concluído", "Processamento do CSV finalizado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar CSV:\n{e}")


    criar_hosts_label = customtkinter.CTkLabel(create, text="Criar Hosts", font=("Arial", 20))
    criar_hosts_label.pack(padx=20, pady=20)


    def voltar_menu():
        create.after(100, lambda: (create.destroy(), janela_principal.deiconify()))

    def fechar_create():
        create.after(100, lambda: (create.destroy(), janela_principal.deiconify()))

    create.protocol("WM_DELETE_WINDOW", fechar_create)

    btn_escolher_csv = customtkinter.CTkButton(create, text="Escolher CSV para Criar Hosts", command=escolher_csv)
    btn_escolher_csv.pack(pady=20)


    btn_voltar = customtkinter.CTkButton(create, text="Voltar ao Menu", command=voltar_menu)
    btn_voltar.pack(pady=20)

    create.mainloop()

def gerar_relatorio_disponibilidade(janela_principal):
    janela_principal.withdraw()  # Oculta o menu principal
    global usuario_logado, senha_logada
    
    GROUP_NAMES_REPORT = [ "casa" ]
    HEADERS_REPORT = {'Content-Type': 'application/json-rpc'}

    relatorio_win = customtkinter.CTk()
    relatorio_win.title("Relatório de Disponibilidade")
    relatorio_win.geometry("800x600")

    # Centralizar a janela
    relatorio_win.update_idletasks()
    width = relatorio_win.winfo_screenwidth()
    height = relatorio_win.winfo_screenheight()
    size = tuple(int(_) for _ in relatorio_win.geometry().split('+')[0].split('x'))
    x = width/2 - size[0]/2
    y = height/2 - size[1]/2
    relatorio_win.geometry("%dx%d+%d+%d" % (size + (x, y)))

    # Frame para os controles de data/hora
    frame_controles = customtkinter.CTkFrame(relatorio_win)
    frame_controles.pack(pady=20, padx=20, fill="x")

    # Título
    titulo = customtkinter.CTkLabel(frame_controles, text="Definir Período do Relatório", font=("Arial", 16))
    titulo.pack(pady=10)

    # Frame para datas
    frame_datas = customtkinter.CTkFrame(frame_controles, fg_color="transparent")
    frame_datas.pack(fill="x", padx=10, pady=10)

    # Data/hora inicial
    lbl_inicio = customtkinter.CTkLabel(frame_datas, text="Data/Hora Inicial:")
    lbl_inicio.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    entry_data_inicio = customtkinter.CTkEntry(frame_datas, placeholder_text="AAAA-MM-DD")
    entry_data_inicio.grid(row=0, column=1, padx=5, pady=5)

    entry_hora_inicio = customtkinter.CTkEntry(frame_datas, placeholder_text="HH:MM:SS")
    entry_hora_inicio.grid(row=0, column=2, padx=5, pady=5)

    # Data/hora final
    lbl_fim = customtkinter.CTkLabel(frame_datas, text="Data/Hora Final:")
    lbl_fim.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    entry_data_fim = customtkinter.CTkEntry(frame_datas, placeholder_text="AAAA-MM-DD")
    entry_data_fim.grid(row=1, column=1, padx=5, pady=5)

    entry_hora_fim = customtkinter.CTkEntry(frame_datas, placeholder_text="HH:MM:SS")
    entry_hora_fim.grid(row=1, column=2, padx=5, pady=5)

    # Função para gerar o relatório (extraída e adaptada da função relatorio() original)
    def gerar_relatorio():
        try:
            # Obter e validar as datas/horas
            data_inicio = entry_data_inicio.get()
            hora_inicio = entry_hora_inicio.get()
            data_fim = entry_data_fim.get()
            hora_fim = entry_hora_fim.get()

            if not all([data_inicio, hora_inicio, data_fim, hora_fim]):
                messagebox.showwarning("Atenção", "Preencha todas as datas e horas!")
                return

            start_time = int(datetime.strptime(f"{data_inicio} {hora_inicio}", "%Y-%m-%d %H:%M:%S").timestamp())
            end_time = int(datetime.strptime(f"{data_fim} {hora_fim}", "%Y-%m-%d %H:%M:%S").timestamp())

            if start_time >= end_time:
                messagebox.showwarning("Atenção", "A data/hora final deve ser após a data/hora inicial!")
                return

            zapi = ZabbixAPI(ZABBIX_URL)
            zapi.login(usuario_logado, senha_logada)

            # Configuração dos grupos (mantida do código original)
            GROUP_NAMES_REPORT = ["casa"]
            
            all_hostgroups = zapi.hostgroup.get(output=["groupid", "name"])
            groups_filtered = {g['name']: g['groupid'] for g in all_hostgroups if g['name'] in GROUP_NAMES_REPORT}
            
            if not groups_filtered:
                messagebox.showwarning("Relatório", f"Nenhum grupo de host encontrado para os nomes: {', '.join(GROUP_NAMES_REPORT)}")
                return

            report_data = []
            total_hosts_in_report = 0

            for group_name, groupid in groups_filtered.items():
                hosts_in_group = zapi.host.get(output=["hostid", "name"], groupids=groupid)
                total_hosts_in_report += len(hosts_in_group)

                for host in hosts_in_group:
                    events = zapi.event.get(
                        output=["eventid", "clock", "value"],
                        hostids=host['hostid'],
                        time_from=start_time,
                        time_till=end_time,
                        sortfield="clock",
                        sortorder="ASC",
                        value=1
                    )
                    recovery_events = zapi.event.get(
                        output=["eventid", "clock", "value"],
                        hostids=host['hostid'],
                        time_from=start_time,
                        time_till=end_time,
                        sortfield="clock",
                        sortorder="ASC",
                        value=0
                    )
                    all_events = sorted(events + recovery_events, key=lambda x: int(x['clock']))

                    # Função auxiliar para calcular downtime (mantida do código original)
                    def calculate_downtime(events, start, end):
                        downtime = 0
                        in_problem = False
                        problem_start = None

                        for e in events:
                            clock = int(e['clock'])
                            if e['value'] == '1':  # Problem
                                if not in_problem:
                                    in_problem = True
                                    problem_start = max(clock, start)
                            elif e['value'] == '0':  # Recovery
                                if in_problem:
                                    downtime += max(0, min(clock, end) - problem_start)
                                    in_problem = False

                        if in_problem:
                            downtime += end - problem_start

                        return downtime

                    downtime = calculate_downtime(all_events, start_time, end_time)
                    total_time = end_time - start_time
                    uptime = total_time - downtime
                    up_percent = round((uptime / total_time) * 100, 2) if total_time > 0 else 0
                    down_percent = round((downtime / total_time) * 100, 2) if total_time > 0 else 0

                    report_data.append([group_name, host['name'], up_percent, down_percent])

            # Exportar CSV (função mantida do código original)
            def export_to_csv(rows, start, end, groups_processed):
                try:
                    with open("availability_report.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([f"# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                        writer.writerow([f"# Período: {datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S')} até {datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')}"])
                        writer.writerow([f"# Grupos processados: {', '.join(groups_processed)}"])
                        writer.writerow([])
                        writer.writerow(["Grupo", "Host", "Tempo UP (%)", "Tempo DOWN (%)"])
                        for row in rows:
                            writer.writerow(row)
                    messagebox.showinfo("Relatório CSV", "Relatório exportado com sucesso para availability_report.csv")
                    return True
                except Exception as e:
                    messagebox.showerror("Erro CSV", f"Erro ao exportar relatório CSV:\n{e}")
                    return False

            # Exportar gráfico (função mantida do código original)
            def export_to_graph(report_data):
                try:
                    hosts = [f"{row[1]}" for row in report_data]
                    up = [row[2] for row in report_data]
                    down = [row[3] for row in report_data]

                    x = range(len(hosts))
                    width = 0.03

                    fig, ax = plt.subplots(figsize=(max(8, len(hosts)*0.5), 4))
                    ax.bar([i - width/2 for i in x], up, width, label='UP (%)', color='green')
                    ax.bar([i + width/2 for i in x], down, width, label='DOWN (%)', color='red')
                    ax.set_ylabel('Percentual (%)')
                    ax.set_title('Disponibilidade dos Hosts')
                    ax.set_xticks(x)
                    ax.set_xticklabels(hosts, rotation=45, ha='right')
                    ax.legend()
                    plt.tight_layout()
                    plt.savefig('availability_report.png')
                    plt.close()
                    messagebox.showinfo("Relatório Gráfico", "Gráfico exportado com sucesso para availability_report.png")
                except Exception as e:
                    messagebox.showerror("Erro Gráfico", f"Erro ao exportar gráfico:\n{e}")

            # Chamar as funções de exportação
            export_to_csv(report_data, start_time, end_time, list(groups_filtered.keys()))
            export_to_graph(report_data)

            # Mostrar resumo se poucos hosts
            if total_hosts_in_report <= 25 and total_hosts_in_report > 0:
                report_summary = "Relatório de Disponibilidade:\n\n"
                for row in report_data:
                    report_summary += f"  Grupo: {row[0]}, Host: {row[1]}, UP: {row[2]}%, DOWN: {row[3]}%\n"
                messagebox.showinfo("Relatório Rápido", report_summary)

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar relatório:\n{e}")

    # Botão para gerar relatório
    btn_gerar = customtkinter.CTkButton(frame_controles, text="Gerar Relatório", command=gerar_relatorio)
    btn_gerar.pack(pady=20)

    # Botão para voltar
    def voltar_menu():
        relatorio_win.after(100, lambda: (relatorio_win.destroy(), janela_principal.deiconify()))

    def fechar_relatorio():
        relatorio_win.after(100, lambda: (relatorio_win.destroy(), janela_principal.deiconify()))
    
    relatorio_win.protocol("WM_DELETE_WINDOW", fechar_relatorio)

    btn_voltar = customtkinter.CTkButton(relatorio_win, text="Voltar ao Menu", command=voltar_menu)
    btn_voltar.pack(pady=20)

    relatorio_win.mainloop()


def mostrar_template(frame_conteudo):
    global usuario_logado, senha_logada
    usuario = usuario_logado
    senha = senha_logada

    for widget in frame_conteudo.winfo_children():
        widget.destroy()
    text = customtkinter.CTkLabel(frame_conteudo, text="Templates e IDs", font=("Arial", 20))
    text.pack(padx=20, pady=20)

    try:
        zapi = ZabbixAPI(ZABBIX_URL)
        zapi.login(usuario, senha)
        templates = zapi.template.get(output=["templateid", "name"])

        scroll_frame = customtkinter.CTkScrollableFrame(frame_conteudo, width=700, height=400)
        scroll_frame.pack(padx=20, pady=20, fill="both", expand=True)

        if templates:
            for template in templates:
                template_label = customtkinter.CTkLabel(
                    scroll_frame,
                    text=f"{template['templateid']} - {template['name']}",
                    font=("Arial", 14),
                    anchor="w",
                    justify="left"
                )
                template_label.pack(anchor="w", padx=20, pady=2)
        else:
            empty_label = customtkinter.CTkLabel(scroll_frame, text="Nenhum template encontrado.", font=("Arial", 14))
            empty_label.pack(padx=40, pady=10)
    except Exception as e:
        error_label = customtkinter.CTkLabel(frame_conteudo, text=f"Erro ao buscar templates:\n{e}", font=("Arial", 14))
        error_label.pack(padx=40, pady=10)

def criar_nova_guia():
    janela1 = customtkinter.CTkToplevel()
    janela1.geometry("900x500")

    janela1.protocol("WM_DELETE_WINDOW", lambda: sys.exit())

    set_appearance_mode  = "dark"
    customtkinter.set_appearance_mode(set_appearance_mode)

    set_default_color_theme = "green"
    customtkinter.set_default_color_theme(set_default_color_theme)
    
    janela1.update_idletasks()
    width = janela1.winfo_screenwidth()
    height = janela1.winfo_screenheight()
    size = tuple(int(_) for _ in janela1.geometry().split('+')[0].split('x'))
    x = width/2 - size[0]/2
    y = height/2 - size[1]/2
    janela1.geometry("%dx%d+%d+%d" % (size + (x, y)))

    janela1.title("Menu Principal")

    frame_menu = customtkinter.CTkFrame(janela1, width=200)
    frame_menu.pack(side="left", fill="y")

    frame_conteudo = customtkinter.CTkFrame(janela1)
    frame_conteudo.pack(side="left", fill="both", expand=True)

    btn_mostrar_hosts = customtkinter.CTkButton(frame_menu, text="Hosts/ID", command=lambda: mostrar_hosts(frame_conteudo))
    btn_mostrar_hosts.grid(row=0, column=0, pady=40, padx=40, sticky="ew")

    btn_TemplateID = customtkinter.CTkButton(frame_menu, text="Templats/ID", command=lambda: mostrar_template(frame_conteudo))
    btn_TemplateID.grid(row=1, column=0, pady=40, padx=40, sticky="ew")

    btn_criar_hosts = customtkinter.CTkButton(frame_menu, text="Criar Hosts", command=lambda: criar_hosts(janela1))
    btn_criar_hosts.grid(row=2, column=0, pady=40, padx=40, sticky="ew")

    btn_relatorio = customtkinter.CTkButton(frame_menu, text="Gerar Relatório de Disponibilidade", 
                                         command=lambda: gerar_relatorio_disponibilidade(janela1))
    btn_relatorio.grid(row=3, column=0, pady=20, padx=20, sticky="ew")
    def logout():
        janela1.after(100, lambda: (
            janela1.destroy(),
            login_entry.delete(0, 'end'),
            senha_entry.delete(0, 'end'),
            login_entry.focus(),
            login.deiconify(),
            messagebox.showinfo("Logout", "Você foi desconectado com sucesso.")
        ))

    logout_button = customtkinter.CTkButton(frame_menu, text="Logout", command=logout, compound="left")
    logout_button.grid(row=4, column=0, pady=40, padx=40, sticky="ew")

    login.withdraw()
    janela1.mainloop()

button = customtkinter.CTkButton(login, text="login", command=tela_login)
button.pack(padx=20, pady=20)

login.mainloop()
