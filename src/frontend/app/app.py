import time
import streamlit as st
import requests
from requests.exceptions import ConnectionError, ConnectTimeout
import pandas as pd
import re
from datetime import date

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(page_title="Sistema de Cadastro", page_icon="📋", layout="wide")

API_URL = st.secrets.get("api_base_url", "http://localhost:8000") + "/registered/"

st.header("📋 Sistema de Cadastro de Jovens AduPno")

tab1, tab2, tab3 = st.tabs(
    ["Cadastrar Jovem", "Editar Cadastro", "Indicadores de Cadastro"]
)


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(ttl=5)
def list_all_members():
    try:
        response = requests.get(f"{API_URL}", timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except ConnectionError:
        st.error("📡 Erro de conexão: O servidor está demorando para responder.")
        return None


def create_member_app(
    member_name,
    phone_number,
    t_shirt,
    food_allergy,
    sower,
    ministry_position,
    date_birth,
    email,
):
    try:
        payload = {
            "member_name": member_name,
            "phone_number": phone_number,
            "t_shirt": t_shirt,
            "food_allergy": food_allergy,
            "sower": sower,
            "ministry_position": ministry_position,
            "date_birth": date_birth.isoformat(),
            "email": email,
        }
        response = requests.post(f"{API_URL}", json=payload, timeout=30)

        return True, response
    except Exception as e:
        return False, str(e)


def validate_phone(phone):
    # Padrão básico para telefone brasileiro
    pattern = re.compile(r"^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$")
    return bool(pattern.match(phone))


def validate_email(email):
    default = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(default, email) is not None


def check_api_healt():
    try:
        response = requests.get(API_URL.replace("/registered", "/"), timeout=30)
        return True, response
    except (ConnectionError, ConnectTimeout):
        return False
    except Exception:
        return False


# ==================== VERIFICAÇÃO DE SAÚDE DA API ====================
if "api_awake" not in st.session_state:
    st.session_state.api_wake = False

if not st.session_state.api_wake:
    placeholder = st.empty()

    with placeholder.container():
        with st.status("🚀 Acordando o servidor...", expanded=True) as status:
            if check_api_healt():
                st.session_state.api_awake = True
                status.update(
                    label="✅ Servidor Online!", state="complete", expanded=False
                )
                time.sleep(0.5)
                placeholder.empty()
            else:
                st.warning(
                    "😴 A API está em modo de espera. Isso pode levar até 30 segundos."
                )
                time.sleep(2)
                st.rerun()

# ==================== INTERFACE STREAMLIT ====================

members = list_all_members()

if not isinstance(members, list):
    members = []

# -------------------- COLUNA - CRIAR --------------------
with tab1:
    st.cache_data.clear()
    st.subheader("➕ Cadastrar Novo Jovem")
    st.markdown("Insira as informações necessárias abaixo para cadastrar o Jovem!")

    member_name = st.text_input(
        "👤 Nome", placeholder="Digite o nome completo", key="criador_nome"
    )
    phone = st.text_input(
        "Número de Telefone",
        placeholder="(11) 94002-8922",
        help="Digite o número no formato (XX) XXXXX-XXXX",
    )
    if phone:
        if validate_phone(phone):
            st.success("✅ Número de telefone válido")
        else:
            st.error("❌ Número de telefone inválido. Use o formato (XX) XXXXX-XXXX")

    t_shirt = st.segmented_control(
        "Escolha o Tamanho da Camiseta",
        ["PP", "P", "M", "G", "GG", "XG", "EG", "G1", "G2", "G3", "G4"],
        default=None,  # Começa sem seleção
    )

    food_allergy = st.selectbox(
        "Alergia a Alimento",
        options=["Sim", "Não"],
        index=None,
        placeholder="Selecione uma opção",
        help="Selecione se há algum tipo de alergia a alimento",
    )

    sower = st.selectbox(
        "Semeador",
        options=["Sim", "Não"],
        index=None,
        placeholder="Selecione uma opção",
        help="Selecione se o jovem é semeador",
    )

    ministry_position = st.selectbox(
        "Cargo Ministerial",
        options=["Sim", "Não"],
        index=None,
        placeholder="Selecione uma opção",
        help="Selecione se o jovem tem cargo ministerial",
    )

    email = st.text_input(
        "Digite Seu E-mail", placeholder="seu.email@exemplo.com", key="email"
    )

    if email:
        if validate_email(email):
            st.success("✅ E-mail válido")
        else:
            st.error("❌ E-mail inválido. Use o formato seu.email@exemplo.com")

    date_birth = st.date_input(
        "Selecione a Data de Nascimento",
        value=date.today(),
        min_value=date(1950, 1, 1),
        max_value=date(2050, 12, 1),
        format="DD/MM/YYYY",
    )
    if st.button("🚀 Registrar Cadastro", width="stretch"):
        if not member_name.strip() or not phone.strip() or not email.strip():
            st.error("❌ Preencha todos os campos obrigatórios")
        else:
            success, result = create_member_app(
                member_name,
                phone,
                t_shirt,
                food_allergy,
                sower,
                ministry_position,
                date_birth,
                email,
            )
            if success:
                if result.status_code == 200:  # type: ignore
                    st.success("✅ Jovem cadastrado com sucesso!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                elif result.status_code == 400:  # type: ignore
                    try:
                        detail = result.json().get("detail", "Erro desconhecido")  # type: ignore
                    except Exception:
                        detail = "❌ Erro desconhecido"
                    st.error(f"❌ Falha ao cadastrar **{member_name}**: {detail}")
                else:
                    st.error(f"❌ Erro inesperado: {result.status_code}")  # type: ignore
            else:
                st.error(f"❌ Falha ao conectar com a API: {result}")

# -------------------- CRIAR --------------------
with tab2:
    st.cache_data.clear()
    time.sleep(0.1)
    edited_members = list_all_members()

    if not edited_members:
        st.warning("⚠️ Nenhum jovem cadastrado ainda.")
    else:
        df_edited = pd.DataFrame(edited_members)
        df_edited = df_edited.rename(
            columns={
                "member_name": "Nome",
                "phone_number": "Número de Telefone",
                "t_shirt": "Número da Camiseta",
                "food_allergy": "Alergia Alimento",
                "sower": "Semeador",
                "ministry_position": "Cargo Ministerial",
                "date_birth": "Data de Nascimento",
                "email": "E-mail",
                "id_member": "Código do Membro",
            }
        )
        df_edited["Data de Nascimento"] = pd.to_datetime(
            df_edited["Data de Nascimento"], format="%Y-%m-%d", errors="coerce"
        )

        edited_df = st.data_editor(
            df_edited,
            num_rows="dynamic",
            width="content",
            column_config={
                "Número da Camiseta": st.column_config.SelectboxColumn(
                    options=[
                        "PP",
                        "P",
                        "M",
                        "G",
                        "GG",
                        "XG",
                        "EG",
                        "G1",
                        "G2",
                        "G3",
                        "G4",
                    ]
                ),
                "Alergia Alimento": st.column_config.SelectboxColumn(
                    options=["Sim", "Não"]
                ),
                "Semeador": st.column_config.SelectboxColumn(options=["Sim", "Não"]),
                "Cargo Ministerial": st.column_config.SelectboxColumn(
                    options=["Sim", "Não"]
                ),
                "Data de Nascimento": st.column_config.DateColumn(),
                "E-mail": st.column_config.TextColumn(),
                "Número de Telefone": st.column_config.TextColumn(),
                "Nome": st.column_config.TextColumn(),
                "Código do Membro": st.column_config.TextColumn(disabled=True),
            },
        )

        with st.form("form_update_members"):
            st.write("💾 Atualizar Cadastro Membro")
            submit_update = st.form_submit_button("✅ Salvar alterações")

            if submit_update:
                for _, row in edited_df.iterrows():
                    if pd.isna(row["Código do Membro"]):
                        continue
                    id_member = int(row["Código do Membro"])
                    payload = {
                        "member_name": row["Nome"],
                        "phone_number": row["Número de Telefone"],
                        "t_shirt": row["Número da Camiseta"],
                        "food_allergy": row["Alergia Alimento"],
                        "sower": row["Semeador"],
                        "ministry_position": row["Cargo Ministerial"],
                        "date_birth": None,
                        "email": row["E-mail"],
                    }

                    if pd.notna(row["Data de Nascimento"]):
                        payload["date_birth"] = row["Data de Nascimento"].strftime(
                            "%Y-%m-%d"
                        )

                    payload = {k: v for k, v in payload.items() if v is not None}

                    response = requests.put(
                        f"{API_URL}{id_member}", json=payload, timeout=30
                    )
                    if response.status_code != 200:
                        st.error(f"❌ Erro ao atualizar {id_member}: {response.text}")

                st.success("✅ Alterações salvas com sucesso!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()

        # ---------- Form para deletar ----------
        with st.form("form_delete_members"):
            rows_to_delete = st.multiselect(
                "Selecione códigos para deletar o cadastro dos jovens",
                edited_df["Código do Membro"],
                placeholder="Escolha os códigos dos jovens que deseja excluir.",
            )
            submit_delete = st.form_submit_button("Deletar Selecionados")

            if submit_delete:
                for id_member in rows_to_delete:
                    requests.delete(f"{API_URL}{int(id_member)}", timeout=30)
                st.success("✅ Jovens excluídos!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()


# -------------------- TABELA DE JOVENS --------------------
with tab3:
    st.cache_data.clear()
    time.sleep(0.1)
    st.subheader("👥 Jovens Cadastrados")
    members = list_all_members()

    if members:
        df = pd.DataFrame(members)
        if "member_name" in df.columns:
            st.metric("Total de Jovens Cadastrados", len(df))
            st.dataframe(
                df.rename(
                    columns={
                        "member_name": "Nome",
                        "phone_number": "Número de Telefone",
                        "t_shirt": "Número da Camiseta",
                        "food_allergy": "Alergia Alimento",
                        "sower": "Semeador",
                        "ministry_position": "Cargo Ministerial",
                        "date_birth": "Data de Nascimento",
                        "email": "E-mail",
                        "id_member": "Código do Membro",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
        else:
            st.error("❌ Erro no formato dos dados de cadastro dos Jovens")
    else:
        st.warning("⚠️ Aguardando primeiro cadastro")
