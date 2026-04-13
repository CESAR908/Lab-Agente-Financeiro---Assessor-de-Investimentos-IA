import streamlit as st
import time

def show_login():
    """Exibe a tela de login com animação do abajur"""

    st.set_page_config(
        page_title="Login - Assessor IA",
        page_icon="💡",
        layout="centered"
    )

    # CSS para animação do abajur (simplificado)
    st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .lamp-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 2rem 0;
            position: relative;
            height: 300px;
        }

        .lamp-cord {
            width: 4px;
            height: 150px;
            background: linear-gradient(to bottom, #8B4513, #654321);
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            border-radius: 2px;
        }

        .lamp-bulb {
            width: 60px;
            height: 80px;
            background: radial-gradient(circle at 30% 30%, #FFFF99, #FFD700);
            border-radius: 50% 50% 50% 0;
            position: absolute;
            top: 140px;
            left: 50%;
            transform: translateX(-50%);
            box-shadow: 0 0 50px rgba(255, 215, 0, 1);
        }

        .lamp-base {
            width: 80px;
            height: 15px;
            background: #2C2C2C;
            border-radius: 5px;
            position: absolute;
            top: 220px;
            left: 50%;
            transform: translateX(-50%);
        }

        .login-form {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            margin-top: 2rem;
        }

        .login-title {
            color: white;
            text-align: center;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Inicializar session state
    if 'lamp_pulled' not in st.session_state:
        st.session_state.lamp_pulled = False

    if 'show_login_form' not in st.session_state:
        st.session_state.show_login_form = False

    # Título principal
    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #667eea;'>💰 Assessor IA</h1>
            <p style='color: #666;'>Puxe a cordinha do abajur para fazer login</p>
        </div>
    """, unsafe_allow_html=True)

    # Abajur interativo
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div class="lamp-container">
                <div class="lamp-cord"></div>
                <div class="lamp-bulb"></div>
                <div class="lamp-base"></div>
            </div>
        """, unsafe_allow_html=True)

        # Botão para puxar a cordinha
        if st.button("🔽 Puxar Cordinha", key="pull_lamp", use_container_width=True):
            st.session_state.show_login_form = True
            st.rerun()

    # Formulário de login (aparece após puxar a cordinha)
    if st.session_state.show_login_form:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🔐 Login</div>', unsafe_allow_html=True)

        usuario = st.text_input(
            "👤 Usuário",
            placeholder="Digite seu usuário",
            key="usuario_input"
        )

        senha = st.text_input(
            "🔑 Senha",
            placeholder="Digite sua senha",
            type="password",
            key="senha_input"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Entrar", use_container_width=True, key="btn_entrar"):
                if usuario == "2026" and senha == "0000":
                    st.session_state.logged_in = True
                    st.success("✅ Login realizado com sucesso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")

        with col2:
            if st.button("❌ Cancelar", use_container_width=True, key="btn_cancelar"):
                st.session_state.show_login_form = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Dicas de login
    if not st.session_state.show_login_form:
        st.info("""
        **Credenciais de teste:**
        - 👤 Usuário: `2026`
        - 🔑 Senha: `0000`
        """)


def check_login():
    """Verifica se o usuário está logado"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    return st.session_state.logged_in
