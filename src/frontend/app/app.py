import time
import streamlit as st
import requests
from requests.exceptions import ConnectionError
import pandas as pd
import re
from datetime import date
import plotly.express as px
from streamlit_cookies_controller import CookieController
import logging

controller = CookieController()
# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(page_title="Sistema de Cadastro", page_icon="📋", layout="wide")

API_URL = st.secrets["api_base_url"]

st.header("📋 Sistema de Cadastro de Jovens AduPno")


def get_api_url():
    return f"{st.secrets['api_base_url']}/registered"


def get_auth_url():
    return f"{st.secrets['api_base_url']}/auth"


# ==================== LOGIN =================================
def login():
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")

        if submit:
            payload = {"username": username, "password": password}
            try:
                response = requests.post(
                    f"{get_auth_url()}/login", data=payload, timeout=30
                )

                if response.status_code == 200:
                    token = response.json().get("access_token")
                    st.session_state["token"] = token

                    try:
                        controller.set("auth_token", token, max_age=3600)
                    except Exception as e:
                        logging.warning(f"Aviso de Cookie (esperado no 1º login): {e}")

                    st.success("Login realizado!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
            except Exception as e:
                st.error(f"Erro ao conectar: {e}")


# ==================== FUNÇÕES AUXILIARES ====================
@st.cache_data(ttl=5)
def list_all_members():
    try:
        response = requests.get(
            f"{get_api_url()}/", headers=get_auth_header(), timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []
    except ConnectionError:
        st.error("📡 Erro de conexão: O servidor está demorando para responder.")
        return None


def create_member_app(
    member_name,
    gender,
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
            "gender": gender,
            "phone_number": phone_number,
            "t_shirt": t_shirt,
            "food_allergy": food_allergy,
            "sower": sower,
            "ministry_position": ministry_position,
            "date_birth": date_birth.isoformat(),
            "email": email,
        }
        response = requests.post(
            f"{get_api_url()}/", json=payload, headers=get_auth_header(), timeout=30
        )

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
        base = st.secrets["api_base_url"]
        response = requests.get(f"{base}/docs", timeout=15)
        return response.status_code == 200, response
    except Exception as e:
        return False, e


def get_auth_header():
    """Retorna o cabeçalho com o token se o usuário estiver logado."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


# ==================== VERIFICAÇÃO DE SAÚDE DA API ====================
if "api_awake" not in st.session_state:
    st.session_state.api_awake = False
if "api_attempts" not in st.session_state:
    st.session_state.api_attempts = 0

if not st.session_state.api_awake:
    placeholder = st.empty()

    with placeholder.container():
        with st.status(
            f"🚀 Verificando API... (Tentativa {st.session_state.api_attempts + 1})",
            expanded=True,
        ) as status:
            awake, response = check_api_healt()

            if awake:
                st.session_state.api_awake = True
                st.session_state.api_attempts = 0
                status.update(
                    label="✅ Servidor Online!", state="complete", expanded=False
                )
                time.sleep(0.5)
                st.rerun()
            else:
                st.session_state.api_attempts += 1
                if st.session_state.api_attempts < 5:
                    st.warning("😴 A API está acordando, tentando novamente em 2s...")
                    time.sleep(2)
                    st.rerun()
                else:
                    status.update(label="❌ Erro de Conexão", state="error")
                    st.error("Não foi possível conectar à API após várias tentativas.")

                    if hasattr(response, "status_code"):
                        st.info(f"Resposta do Servidor: {response.status_code}")  # type: ignore
                    else:
                        st.code(f"Erro técnico: {response}")

                    if st.button("🔄 Forçar Nova Tentativa"):
                        st.session_state.api_attempts = 0
                        st.rerun()
                    st.stop()


# ==================== INTERFACE STREAMLIT ====================
def main():
    if not st.session_state.get("api_awake"):
        st.stop()

    saved_token = None

    if "token" not in st.session_state:
        try:
            saved_token = controller.get("auth_token")
        except (TypeError, Exception):
            saved_token = None

        if saved_token:
            st.session_state["token"] = saved_token
            st.rerun()

    if "token" not in st.session_state:
        st.divider()
        st.title("🔐 Login")
        login()
        st.stop()

    if "members" not in st.session_state:
        st.session_state.members = list_all_members()
    members = st.session_state.members

    if not isinstance(members, list):
        members = []

    menu = st.sidebar.radio(
        "Selecione uma opção:",
        ["Cadastrar Jovem", "Editar Cadastro", "Indicadores de Cadastro"],
    )
    # -------------------- COLUNA - CRIAR --------------------
    if menu == "Cadastrar Jovem":
        st.divider()
        st.subheader("➕ Cadastrar Novo Jovem")
        st.markdown("Insira as informações necessárias abaixo para cadastrar o Jovem!")

        with st.form("form_create_member", clear_on_submit=True):
            member_name = st.text_input(
                "👤 Nome", placeholder="Digite o nome completo", key="criador_nome"
            )
            gender = st.selectbox(
                "🚻 Gênero",
                ["Masculino", "Feminino"],
                index=None,
                placeholder="Selecione uma opção",
            )
            phone = st.text_input(
                "📱 Número de Telefone",
                placeholder="(11) 94002-8922",
                help="Digite o número no formato (XX) XXXXX-XXXX",
            )
            st.caption(
                "⚠️ :red[**Digite o Número de Telefone no formato (XX) XXXXX-XXXX**]"
            )

            t_shirt = st.segmented_control(
                "👕 Escolha o Tamanho da Camiseta",
                ["PP", "P", "M", "G", "GG", "XG", "EG", "G1", "G2", "G3", "G4"],
                default=None,
            )

            food_allergy = st.selectbox(
                "🥗 Alergia a Alimento",
                ["Sim", "Não"],
                index=None,
                placeholder="Selecione uma opção",
            )

            sower = st.selectbox(
                "🌱 Semeador",
                ["Sim", "Não"],
                index=None,
                placeholder="Selecione uma opção",
            )

            ministry_position = st.selectbox(
                "⛪ Cargo Ministerial",
                ["Sim", "Não"],
                index=None,
                placeholder="Selecione uma opção",
            )

            email = st.text_input(
                "📧 Digite Seu E-mail", placeholder="seu.email@exemplo.com", key="email"
            )

            date_birth = st.date_input(
                "📅 Selecione a Data de Nascimento",
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
                        gender,
                        phone,
                        t_shirt,
                        food_allergy,
                        sower,
                        ministry_position,
                        date_birth,
                        email,
                    )
                    if success and 200 <= result.status_code < 300:  # type: ignore
                        st.success(
                            f"✅ Jovem: **{member_name}** cadastrado com sucesso!"
                        )
                        st.cache_data.clear()
                        st.session_state.members = list_all_members()
                        time.sleep(3)
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
    elif menu == "Editar Cadastro":
        st.divider()
        st.subheader("✏️ Editar Cadastro de Jovens")
        edited_members = members.copy() if members else []

        if not edited_members:
            st.warning("⚠️ Nenhum jovem cadastrado ainda.")
        else:
            df_edited = pd.DataFrame(edited_members)
            df_edited = df_edited.rename(
                columns={
                    "id_member": "Código",
                    "member_name": "Nome",
                    "gender": "Gênero",
                    "phone_number": "Telefone",
                    "t_shirt": "Camiseta",
                    "food_allergy": "Alergia Alimento",
                    "sower": "Semeador",
                    "ministry_position": "Cargo Ministerial",
                    "date_birth": "Data de Nascimento",
                    "email": "E-mail",
                }
            )
            df_edited["Data de Nascimento"] = pd.to_datetime(
                df_edited["Data de Nascimento"], format="%Y-%m-%d", errors="coerce"
            )
            expected_cols = [
                "Código",
                "Nome",
                "Gênero",
                "Telefone",
                "Camiseta",
                "Alergia Alimento",
                "Semeador",
                "Cargo Ministerial",
                "Data de Nascimento",
                "E-mail",
            ]
            for c in expected_cols:
                if c not in df_edited.columns:
                    df_edited[c] = pd.NA

            df_edited = df_edited.reindex(columns=expected_cols)

            df_edited["Código"] = pd.to_numeric(
                df_edited["Código"], errors="coerce"
            ).astype("Int64")

            edited_df = st.data_editor(
                df_edited,
                num_rows="fixed",
                width="content",
                column_config={
                    "Código": st.column_config.TextColumn(disabled=True),
                    "Nome": st.column_config.TextColumn(),
                    "Gênero": st.column_config.SelectboxColumn(
                        options=["Masculino", "Feminino"]
                    ),
                    "Camiseta": st.column_config.SelectboxColumn(
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
                    "Semeador": st.column_config.SelectboxColumn(
                        options=["Sim", "Não"]
                    ),
                    "Cargo Ministerial": st.column_config.SelectboxColumn(
                        options=["Sim", "Não"]
                    ),
                    "Data de Nascimento": st.column_config.DateColumn(),
                    "E-mail": st.column_config.TextColumn(),
                    "Telefone": st.column_config.TextColumn(),
                },
            )

            with st.form("form_update_members"):
                st.write("💾 Atualizar Cadastro Membro")
                submit_update = st.form_submit_button("✅ Salvar alterações")

                if submit_update:
                    errors = []
                    updated_members = []

                    for idx, row in edited_df.iterrows():
                        id_member = row["Código"]
                        if pd.isna(id_member):
                            continue

                        original_row = df_edited.loc[idx]  # type: ignore
                        changed = False
                        payload = {}

                        for df_col, payload_key in [
                            ("Nome", "member_name"),
                            ("Gênero", "gender"),
                            ("Telefone", "phone_number"),
                            ("Camiseta", "t_shirt"),
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
                                    f"{get_api_url()}/{int(id_member)}",
                                    json=payload,
                                    headers=get_auth_header(),
                                    timeout=30,
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
                            f"✅ Cadastro do(s) joven(s): **{list_members_edited}** atualizado(s) com sucesso!"
                        )
                        st.session_state.members = list_all_members()
                        time.sleep(3)
                        st.rerun()

            # ---------- Form para deletar ----------
            st.divider()
            st.subheader("🗑️ Deletar Cadastro de Jovens")
            with st.form("form_delete_members"):
                rows_to_delete = st.multiselect(
                    "Selecione códigos para deletar o cadastro dos jovens",
                    edited_df["Código"],
                    placeholder="Escolha os códigos dos jovens que deseja excluir.",
                )
                submit_delete = st.form_submit_button("✅ Deletar Selecionados")

                members_deleted = []

                if submit_delete:
                    for id_member in rows_to_delete:
                        filtered = edited_df.loc[
                            edited_df["Código"] == id_member, "Nome"
                        ]
                        if not filtered.empty:  # type: ignore
                            members_deleted.append(filtered.values[0])  # type: ignore
                        requests.delete(
                            f"{get_api_url()}/{int(id_member)}",
                            headers=get_auth_header(),
                            timeout=30,
                        )

                    if members_deleted:
                        list_members_deleted = ", ".join(members_deleted)
                        st.success(
                            f"✅ Joven(s): **{list_members_deleted}** excluídos!"
                        )
                        st.cache_data.clear()

                    st.session_state.members = list_all_members()
                    time.sleep(3)
                    st.rerun()

    # -------------------- TABELA DE JOVENS --------------------
    elif menu == "Indicadores de Cadastro":
        st.divider()
        st.subheader("📊 Dashboard de Jovens Cadastrados")

        members = members if members is not None else []

        if members:
            df = pd.DataFrame(members)
            if "member_name" in df.columns:
                df = df.rename(
                    columns={
                        "id_member": "ID",
                        "member_name": "Nome",
                        "gender": "Gênero",
                        "phone_number": "Telefone",
                        "t_shirt": "Camiseta",
                        "food_allergy": "Alergia",
                        "sower": "Semeador",
                        "ministry_position": "Cargo",
                        "date_birth": "Nascimento",
                        "email": "Email",
                    }
                )

                st.divider()
                st.markdown("### 🎛️ Filtros")

                col_f1, col_f2, col_f3 = st.columns(3)

                with col_f1:
                    semeador_sel = st.multiselect(
                        "Semeador",
                        options=sorted(df["Semeador"].dropna().unique()),
                        default=sorted(df["Semeador"].dropna().unique()),
                        placeholder="Selecione uma opção",
                    )
                with col_f2:
                    gender_sel = st.multiselect(
                        "Gênero",
                        options=sorted(df["Gênero"].dropna().unique()),
                        default=sorted(df["Gênero"].dropna().unique()),
                        placeholder="Selecione uma opção",
                    )

                st.divider()
                df["Nascimento"] = pd.to_datetime(df["Nascimento"], errors="coerce")
                today = pd.Timestamp.today()
                df["Idade"] = (today - df["Nascimento"]).dt.days // 365

                df["Alergia"] = df["Alergia"].fillna("Nenhuma")
                df["Cargo"] = df["Cargo"].fillna("Não informado")
                df["Camiseta"] = df["Camiseta"].fillna("Não informado")

                df_filtrado = df[
                    (df["Semeador"].isin(semeador_sel))
                    & (df["Gênero"].isin(gender_sel))
                ]

                col1, col2, col3, col4, col5, col6 = st.columns(6)

                meninas = df_filtrado[df_filtrado["Gênero"] == "Feminino"]
                col1.metric("👩 Meninas", len(meninas))

                meninos = df_filtrado[df_filtrado["Gênero"] == "Masculino"]
                col2.metric("👨 Meninos", len(meninos))

                col3.metric("👥 Jovens Cadastrados", len(df_filtrado))

                val_meninas = df_filtrado[df_filtrado["Gênero"] == "Feminino"][
                    "Idade"
                ].mean()
                label_meninas = (
                    f"{val_meninas:.1f} anos" if pd.notna(val_meninas) else "N/A"
                )
                col4.metric("👩 Idade Média Meninas", label_meninas)

                val_meninos = df_filtrado[df_filtrado["Gênero"] == "Masculino"][
                    "Idade"
                ].mean()
                label_meninos = (
                    f"{val_meninos:.1f} anos" if pd.notna(val_meninos) else "N/A"
                )
                col5.metric("👨 Idade Média Meninos", label_meninos)

                val_geral = df_filtrado["Idade"].mean()
                label_geral = f"{val_geral:.1f} anos" if pd.notna(val_geral) else "N/A"
                col6.metric("👥 Idade Média Mocidade", label_geral)

                col7, col8, col9 = st.columns(3)

                with col7:
                    semeadores = df_filtrado["Semeador"].value_counts().reset_index()
                    semeadores.columns = ["Semeador", "Total"]

                    fig3 = px.bar(
                        semeadores,
                        x="Semeador",
                        y="Total",
                        title="🌱 Semeadores",
                        text="Total",
                    )
                    st.plotly_chart(
                        fig3, width="stretch", config={"doubleClick": "False"}
                    )

                with col8:
                    camisetas = df_filtrado["Camiseta"].value_counts().reset_index()
                    camisetas.columns = ["Camiseta", "Total"]

                    fig1 = px.bar(
                        camisetas,
                        x="Camiseta",
                        y="Total",
                        title="👕 Camisetas",
                        text="Total",
                    )
                    st.plotly_chart(
                        fig1, width="stretch", config={"doubleClick": "False"}
                    )

                with col9:
                    cargos = df_filtrado["Cargo"].value_counts().reset_index()
                    cargos.columns = ["Cargo", "Total"]

                    fig3 = px.bar(
                        cargos,
                        x="Cargo",
                        y="Total",
                        title="⛪ Cargo Ministerial",
                        text="Total",
                    )
                    st.plotly_chart(
                        fig3, width="stretch", config={"doubleClick": "False"}
                    )

                col10, col11 = st.columns(2)

                with col10:
                    alergias = df_filtrado["Alergia"].value_counts().reset_index()
                    alergias.columns = ["Alergia", "Total"]

                    fig3 = px.bar(
                        alergias,
                        x="Alergia",
                        y="Total",
                        title="🥗 Jovens com Alergia a Alimento",
                        text="Total",
                    )
                    st.plotly_chart(
                        fig3, width="stretch", config={"doubleClick": "False"}
                    )

                with col11:
                    fig4 = px.histogram(
                        df_filtrado,
                        x="Idade",
                        nbins=10,
                        title="📅 Faixa Etária",
                    )

                    fig4.update_traces(
                        texttemplate="%{y}",
                        textposition="inside",
                        insidetextanchor="end",
                        marker_line_width=1,
                        marker_line_color="white",
                    )

                    fig4.update_layout(
                        bargap=0.1,
                        xaxis_title="Idade",
                        yaxis_title="Quantidade",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )

                    st.plotly_chart(
                        fig4,
                        width="stretch",
                        config={"doubleClick": False, "displayModeBar": False},
                    )

                st.subheader("👥 Dados completos")
                st.dataframe(df_filtrado)

            else:
                st.error("❌ Erro no formato dos dados de cadastro dos Jovens")
        else:
            st.warning("⚠️ Aguardando primeiro cadastro")


if __name__ == "__main__":
    main()
