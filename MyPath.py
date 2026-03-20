import json
import os
from datetime import datetime, timedelta

"""
Estrutura do arquivo estudos.json

{
    "estudos": [
        {
            "data": str,          # Data do registro no formato DD/MM/AAAA
            "status": str,        # Pode ser "Estudado", "Não Estudado" ou "Justificado"
            "horas": float,       # Quantidade de horas estudadas no dia
            "justificativa": str, # Texto explicando o motivo (usado apenas se status = "Justificado")
            "meta_amanha": str    # Meta definida para o dia seguinte
        },
        ...
    ]
}
"""

# ---------------- Funções de persistência ---------------- #


def carregar_dados():
    """
        Carrega os dados do arquivo 'estudos.json'.
        Retorna um dicionário com a chave "estudos": lista de registros de estudo

    Analogia: Imagine um caderno:
    Se o caderno existe → abra e leia o que está escrito
    Se não existe → crie um caderno novo e vazio

    """
    if os.path.exists("estudos.json"):
        with open("estudos.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {"estudos": []}


def salvar_dados(dados):
    """
    Salva os dados (estudos) no arquivo 'estudos.json'.
    """
    with open("estudos.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


# ---------------- Funções de lógica ---------------- #


def calcular_total_horas(dados):
    """
    Calcula o total de horas estudadas somando todos os registros.
    Analogia:
    Você tem uma pilha de notas fiscais. Vai passando uma por uma, pegando o valor, e somando no total.
    """
    total = 0
    for log in dados["estudos"]:
        horas = log.get("horas", 0)
        total += horas
    return total
    # return sum(log.get('horas', 0) for log in dados["estudos"]) > versão compacta.


def gerar_relatorio(dados):
    """
    Gera um relatório com estatísticas básicas:
    - Total de horas estudadas
    - Número de dias registrados
    - Média diária de horas
    - Dia com maior número de horas
    - Contagem de dia por status (Estudado...)
    Retorna:
        dicionário: com todas as estatisticas atualizadas
    """
    logs = dados["estudos"]
    if not logs:
        return {
            "total_horas": 0,
            "total_dias": 0,
            "media_diaria": 0,
            "recorde": "Nenhum",
            "contagem_status": {
                "Estudado": 0,
                "Não Estudado": 0,
                "Justificado": 0,
            },
        }

    total_horas = sum(log.get("horas", 0) for log in logs)
    total_dias = len(logs)
    media_diaria = total_horas / total_dias if total_dias > 0 else 0

    # lambda = função anônima (sem nome)
    # max(logs, key=lambda x: x['horas']) significa: "Pegue o máximo da lista logs"
    # Mas compare usando as HORAS de cada item"
    maior_dia = max(logs, key=lambda x: x["horas"])
    dia_recorde = (maior_dia["data"], maior_dia["horas"])

    # Contagem por status
    contagem_status = {"Estudado": 0, "Não Estudado": 0, "Justificado": 0}
    for log in logs:
        status = log.get("status", "")
        if status in contagem_status:
            contagem_status[status] += 1

    return {
        "total_horas": total_horas,
        "total_dias": total_dias,
        "media_diaria": media_diaria,
        "recorde": dia_recorde,
        "contagem_status": contagem_status,
    }


def obter_meta_hoje(dados):
    """
    Retorna a meta definida ontem para hoje, se existir.
    """
    if not dados["estudos"]:
        return None

    hoje = datetime.now().strftime("%d/%m/%Y")
    ontem = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")

    # Procura o registro de ontem > #VERSÃO COMPACTA
    # registro_ontem = next((log for log in dados["estudos"] if log['data'] == ontem), None)

    registro_ontem = None
    for log in dados["estudos"]:
        if log["data"] == ontem:
            registro_ontem = log
            break

    if registro_ontem is not None:
        if "meta_amanha" in registro_ontem:
            return registro_ontem["meta_amanha"]

    # VERSÃO COMPACTA
    # if registro_ontem and registro_ontem.get('meta_amanha'):
    # return registro_ontem['meta_amanha']

    return None


def verificar_dias_faltantes(dados):
    """
    Verifica se existem dias entre o último registro e hoje que não foram registrados.
    Retorna uma lista com as datas faltantes.
    """
    if not dados["estudos"]:
        return []

    # Ordena os registros por data
    registros_ordenados = sorted(
        dados["estudos"],
        key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"),
    )

    ultimo_registro = registros_ordenados[-1]
    data_ultimo = datetime.strptime(ultimo_registro["data"], "%d/%m/%Y")
    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    dias_faltantes = []
    data_atual = data_ultimo + timedelta(days=1)

    while data_atual < hoje:
        data_str = data_atual.strftime("%d/%m/%Y")
        # Verifica se já não existe um registro para esse dia
        if not any(log["data"] == data_str for log in dados["estudos"]):
            dias_faltantes.append(data_str)
        data_atual += timedelta(days=1)

    return dias_faltantes


def registrar_dia(dados, data_str):
    """
    Registra um dia específico (pode ser passado ou hoje).
    """
    registro_existente = next(
        (log for log in dados["estudos"] if log["data"] == data_str), None
    )

    print(f"\n📅 Data: {data_str}")
    if registro_existente:
        print(
            f"⚠️ Você já tem {registro_existente['horas']}h registradas neste dia."
        )
        print(f"   Status atual: {registro_existente['status']}")
        confirma = input("Deseja atualizar? (s/n): ")
        if confirma.lower() != "s":
            return

    print("Status: [1] Estudei | [2] Não Estudei | [3] Justificado")
    st = input("Opção: ")

    valor_horas = 0
    justificativa = ""
    status_texto = ""

    if st == "1":
        valor_horas = float(input("Quantas horas de estudo? "))
        status_texto = "Estudado"
    elif st == "2":
        status_texto = "Não Estudado"
    elif st == "3":
        status_texto = "Justificado"
        justificativa = input("Qual foi o imprevisto? ")
    else:
        print("❌ Opção inválida!")
        return

    if registro_existente:
        registro_existente["horas"] = valor_horas
        registro_existente["status"] = status_texto
        if justificativa:
            registro_existente["justificativa"] = justificativa
    else:
        novo_registro = {
            "data": data_str,
            "status": status_texto,
            "horas": valor_horas,
        }
        if justificativa:
            novo_registro["justificativa"] = justificativa

        dados["estudos"].append(novo_registro)

    salvar_dados(dados)
    print("\n✅ Registro salvo com sucesso!")


# ---------------- Menu principal ---------------- #


def menu():
    """
    Exibe o menu principal do programa e controla o fluxo de opções:
    1. Registrar/Atualizar estudo de hoje
    2. Registrar dia passado
    3. Ver histórico/relatório
    4. Planejar meta para amanhã
    5. Sair
    """
    dados = carregar_dados()

    while True:
        total = calcular_total_horas(dados)
        meta_hoje = obter_meta_hoje(dados)
        dias_faltantes = verificar_dias_faltantes(dados)

        print("\n" + "=" * 40)
        print(" 🔥 THE GRIND - LOG DE ESTUDOS")
        print(f" TOTAL ACUMULADO: {total} HORAS")
        if meta_hoje:
            print(f" 🎯 META PARA HOJE: {meta_hoje}")
        if dias_faltantes:
            print(f" ⚠️  {len(dias_faltantes)} dia(s) não registrado(s)!")
        print("=" * 40)
        print("1. Registrar/Atualizar Estudo de Hoje")
        print("2. Registrar Dia Passado")
        print("3. Ver Histórico/Relatório")
        print("4. Planejar Meta para Amanhã")
        print("5. Sair")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            # --- Registrar estudo de hoje ---
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            registrar_dia(dados, data_hoje)

        elif opcao == "2":
            # --- Registrar dia passado ---
            dias_faltantes = verificar_dias_faltantes(dados)

            if dias_faltantes:
                print("\n📋 Dias não registrados:")
                for i, dia in enumerate(dias_faltantes, 1):
                    print(f"   {i}. {dia}")
                print(f"   {len(dias_faltantes) + 1}. Digitar outra data")

                escolha = input(
                    "\nEscolha o dia ou digite o número para outra data: "
                )

                try:
                    idx = int(escolha) - 1
                    if 0 <= idx < len(dias_faltantes):
                        data_registrar = dias_faltantes[idx]
                    else:
                        data_registrar = input("Digite a data (DD/MM/AAAA): ")
                except ValueError:
                    data_registrar = input("Digite a data (DD/MM/AAAA): ")
            else:
                data_registrar = input(
                    "Digite a data que deseja registrar (DD/MM/AAAA): "
                )

            # Validação básica da data
            try:
                datetime.strptime(data_registrar, "%d/%m/%Y")
                registrar_dia(dados, data_registrar)
            except ValueError:
                print("❌ Data inválida! Use o formato DD/MM/AAAA")

        elif opcao == "3":
            # --- Relatório ---
            relatorio = gerar_relatorio(dados)
            print("-" * 40)
            print(
                f"📊 RESUMO: {relatorio['total_horas']}h em {relatorio['total_dias']} dias."
            )
            print(f"📈 Média diária: {relatorio['media_diaria']:.2f}h")
            if relatorio["recorde"] != "Nenhum":
                print(
                    f"🏆 Recorde: {relatorio['recorde'][1]}h no dia {relatorio['recorde'][0]}"
                )
            print("📌 Status dos dias:")
            for status, qtd in relatorio["contagem_status"].items():
                print(f"   - {status}: {qtd} dia(s)")

            # Mostra dias faltantes se houver
            dias_faltantes = verificar_dias_faltantes(dados)
            if dias_faltantes:
                print(f"\n⚠️  Dias não registrados: {len(dias_faltantes)}")
                print(f"   (Use a opção 2 para registrar)")

        elif opcao == "4":
            # --- Definir meta para amanhã ---
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            registro_hoje = next(
                (log for log in dados["estudos"] if log["data"] == data_hoje),
                None,
            )

            if not registro_hoje:
                print(
                    "❌ Registre o dia de hoje primeiro para definir uma meta."
                )
            else:
                meta = input("\nQual sua meta de estudo para amanhã? ")
                registro_hoje["meta_amanha"] = meta
                salvar_dados(dados)
                print(f"✅ Meta anotada para amanhã!")

        elif opcao == "5":
            # --- Sair ---
            print("\n👋 Até logo! Continue firme nos estudos!")
            break
        else:
            print("\n❌ Opção inválida! Tente novamente.")


if __name__ == "__main__":
    menu()
