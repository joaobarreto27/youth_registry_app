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
    pattern = re.compile(r"^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}\-?[0-9]{4}$")
    return bool(pattern.match(phone))


def validate_email(email):
    default = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(default, email) is not None


def check_api_healt():
    try:
        # quick timeout for health check to keep UI responsive
        response = requests.get(API_URL.replace("/registered", "/"), timeout=5)
        return response.status_code == 200, response
    except (ConnectionError, ConnectTimeout) as e:
        return False, e
    except Exception as e:
        return False, e


# ==================== VERIFICAÇÃO DE SAÚDE DA API ====================
if "api_awake" not in st.session_state:
    st.session_state.api_awake = False

if "api_attempts" not in st.session_state:
    st.session_state.api_attempts = 0

if not st.session_state.api_awake:
    placeholder = st.empty()

    with placeholder.container():
        with st.status("🚀 Acordando o servidor...", expanded=True):
            awake, response = check_api_healt()  # type: ignore

        if awake:
            st.session_state.api_awake = True
            st.session_state.api_attempts = 0
            placeholder.success("✅ Servidor Online!")
        else:
            st.session_state.api_attempts += 1
            # retry a few times automatically, then show manual retry
            if st.session_state.api_attempts < 3:
                st.warning("😴 A API está acordando, tentando novamente...")
                time.sleep(1)
                st.rerun()
            else:
                st.error(
                    "❌ Não foi possível conectar com a API após múltiplas tentativas."
                )
                # show a helpful debug message
                try:
                    if hasattr(response, "status_code"):
                        st.write(f"Status: {response.status_code}")  # type: ignore
                    else:
                        st.write(str(response))
                except Exception as e:
                    st.error(f"Erro ao exibir detalhes da resposta: {e}")

                if st.button("Tentar novamente"):
                    st.session_state.api_attempts = 0
                    time.sleep(0.2)
                    st.rerun()

# ==================== INTERFACE STREAMLIT ====================

if "members" not in st.session_state:
    st.session_state.members = list_all_members()
members = st.session_state.members

if not isinstance(members, list):
    members = []

# -------------------- COLUNA - CRIAR --------------------
with tab1:
    st.subheader("➕ Cadastrar Novo Jovem")
    st.markdown("Insira as informações necessárias abaixo para cadastrar o Jovem!")

    with st.form("form_create_member", clear_on_submit=True):
        member_name = st.text_input(
            "👤 Nome", placeholder="Digite o nome completo", key="criador_nome"
        )
        phone = st.text_input(
            "Número de Telefone",
            placeholder="(11) 94002-8922",
            help="Digite o número no formato (XX) XXXXX-XXXX",
        )

        t_shirt = st.segmented_control(
            "Escolha o Tamanho da Camiseta",
            ["PP", "P", "M", "G", "GG", "XG", "EG", "G1", "G2", "G3", "G4"],
            default=None,
        )

        food_allergy = st.selectbox(
            "Alergia a Alimento",
            ["Sim", "Não"],
            index=None,
            placeholder="Selecione uma opção",
        )

        sower = st.selectbox(
            "Semeador", ["Sim", "Não"], index=None, placeholder="Selecione uma opção"
        )

        ministry_position = st.selectbox(
            "Cargo Ministerial",
            ["Sim", "Não"],
            index=None,
            placeholder="Selecione uma opção",
        )

        email = st.text_input(
            "Digite Seu E-mail", placeholder="seu.email@exemplo.com", key="email"
        )

        date_birth = st.date_input(
            "Selecione a Data de Nascimento",
            value=date.today(),
            min_value=date(1950, 1, 1),
            max_value=date(2050, 12, 1),
            format="DD/MM/YYYY",
        )

        submit = st.form_submit_button("🚀 Registrar Cadastro")
        if submit:
            # Validações
            if not member_name.strip() or not phone.strip() or not email.strip():
                st.error("❌ Preencha todos os campos obrigatórios")
            elif not validate_phone(phone):
                st.error("❌ Número de telefone inválido")
            elif not validate_email(email):
                st.error("❌ E-mail inválido")
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
                if success and result.status_code == 200:  # type: ignore
                    st.success(f"✅ Jovem: **{member_name}** cadastrado com sucesso!")
                    st.session_state.members = list_all_members()
                    time.sleep(6)
                    st.rerun()
                elif success and result.status_code == 400:  # type: ignore
                    try:
                        detail = result.json().get("detail", "Erro desconhecido")  # type: ignore
                    except Exception:
                        detail = "Erro desconhecido"
                    st.error(f"❌ Falha ao cadastrar **{member_name}**: {detail}")
                else:
                    st.error(
                        f"❌ Erro inesperado: {result if not success else result.status_code}"  # type: ignore
                    )

# -------------------- EDITAR --------------------
with tab2:
    st.subheader("✏️ Editar Cadastro de Jovens")
    edited_members = members.copy() if members else []

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
        expected_cols = [
            "Nome",
            "Número de Telefone",
            "Número da Camiseta",
            "Alergia Alimento",
            "Semeador",
            "Cargo Ministerial",
            "Data de Nascimento",
            "E-mail",
            "Código do Membro",
        ]
        for c in expected_cols:
            if c not in df_edited.columns:
                df_edited[c] = pd.NA

        df_edited = df_edited.reindex(columns=expected_cols)

        df_edited["Código do Membro"] = pd.to_numeric(
            df_edited["Código do Membro"], errors="coerce"
        ).astype("Int64")

        edited_df = st.data_editor(
            df_edited,
            num_rows="fixed",
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
                errors = []
                updated_members = []

                for idx, row in edited_df.iterrows():
                    id_member = row["Código do Membro"]
                    if pd.isna(id_member):
                        continue

                    original_row = df_edited.loc[idx]  # type: ignore
                    changed = False
                    payload = {}

                    for df_col, payload_key in [
                        ("Nome", "member_name"),
                        ("Número de Telefone", "phone_number"),
                        ("Número da Camiseta", "t_shirt"),
                        ("Alergia Alimento", "food_allergy"),
                        ("Semeador", "sower"),
                        ("Cargo Ministerial", "ministry_position"),
                        ("Data de Nascimento", "date_birth"),
                        ("E-mail", "email"),
                    ]:
                        old_val = original_row[df_col]
                        new_val = row[df_col]

                        if df_col == "Data de Nascimento" and pd.notna(new_val):
                            new_val_str = new_val.strftime("%Y-%m-%d")
                            old_val_str = (
                                pd.to_datetime(old_val).strftime("%Y-%m-%d")
                                if pd.notna(old_val)
                                else None
                            )
                            if new_val_str != old_val_str:
                                payload[payload_key] = new_val_str
                                changed = True
                        else:
                            if new_val != old_val:
                                payload[payload_key] = new_val
                                changed = True

                    if changed:
                        try:
                            response = requests.put(
                                f"{API_URL}{int(id_member)}", json=payload, timeout=30
                            )
                            if response.status_code == 200:
                                updated_members.append(row["Nome"])
                            else:
                                errors.append(f"{row['Nome']}: {response.text}")
                        except Exception as e:
                            errors.append(f"{row['Nome']}: {str(e)}")

                if errors:
                    st.error("❌ Erros ao atualizar membros:\n" + "\n".join(errors))
                if updated_members:
                    list_members_edited = ", ".join(updated_members)
                    st.success(
                        f"✅ Cadastro dos jovens: **{list_members_edited}** atualizados com sucesso!"
                    )
                    st.session_state.members = list_all_members()
                    time.sleep(6)
                    st.rerun()

        # ---------- Form para deletar ----------
        st.subheader("🗑️ Deletar Cadastro de Jovens")
        with st.form("form_delete_members"):
            rows_to_delete = st.multiselect(
                "Selecione códigos para deletar o cadastro dos jovens",
                edited_df["Código do Membro"],
                placeholder="Escolha os códigos dos jovens que deseja excluir.",
            )
            submit_delete = st.form_submit_button("✅ Deletar Selecionados")

            members_deleted = []

            if submit_delete:
                for id_member in rows_to_delete:
                    filtered = edited_df.loc[
                        edited_df["Código do Membro"] == id_member, "Nome"
                    ]
                    if not filtered.empty:  # type: ignore
                        members_deleted.append(filtered.values[0])  # type: ignore
                    requests.delete(f"{API_URL}{int(id_member)}", timeout=30)

                if members_deleted:
                    list_members_deleted = ", ".join(members_deleted)
                    st.success(f"✅ Jovens: {list_members_deleted} excluídos!")
                    st.cache_data.clear()

                st.session_state.members = list_all_members()
                time.sleep(6)
                st.rerun()


# -------------------- TABELA DE JOVENS --------------------
with tab3:
    st.subheader("👥 Jovens Cadastrados")
    members = members if members is not None else []

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
