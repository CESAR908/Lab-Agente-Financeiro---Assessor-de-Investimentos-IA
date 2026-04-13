import streamlit as st
import time

def show_login():
    """Exibe a tela de login com animação do abajur"""

    st.set_page_config(
        page_title="Login - Assessor IA",
        page_icon="💡",
        layout="centered"
    )

    # CSS para animação do abajur
    st.markdown("""
        <style>
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
            transition: transform 0.3s ease;
        }

        .lamp-cord:hover {
            cursor: grab;
        }

        .lamp-cord.pulled {
            transform: translateX(-50%) scaleY(0.7);
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
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.8);
            transition: box-shadow 0.3s ease;
        }

        .lamp-bulb.on {
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
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .login-title {
            color: white;
            text-align: center;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            font-weight: bold;
        }

        .login-input {
            width: 100%;
            padding: 0.8rem;
            margin: 0.8rem 0;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.9);
        }

        .login-button {
            width: 100%;
            padding: 0.8rem;
            margin-top: 1rem;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #333;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .login-button:hover {
            transform: scale(1.05);
        }

        .error-message {
            color: #FF6B6B;
            text-align: center;
            margin-top: 1rem;
            font-weight: bold;
        }

        .success-message {
            color: #51CF66;
            text-align: center;
            margin-top: 1rem;
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
    st.markdown("<h1 style='text-align: center; color: #667eea;'>💰 Assessor IA</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Puxe a cordinha do abajur para fazer login</p>", 
                unsafe_allow_html=True)

    # Abajur interativo
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div class="lamp-container">
                <div class="lamp-cord" id="lampCord"></div>
                <div class="lamp-bulb on" id="lampBulb"></div>
                <div class="lamp-base"></div>
            </div>
        """, unsafe_allow_html=True)

        # Botão para puxar a cordinha
        if st.button("🔽 Puxar Cordinha", key="pull_lamp", use_container_width=True):
            st.session_state.lamp_pulled = True
            st.session_state.show_login_form = True
            st.rerun()

    # Formulário de login (aparece após puxar a cordinha)
    if st.session_state.show_login_form:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🔐 Login</div>', unsafe_allow_html=True)

        usuario = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            key="usuario_input"
        )

        senha = st.text_input(
            "Senha",
            placeholder="Digite sua senha",
            type="password",
            key="senha_input"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Entrar", use_container_width=True):
                if usuario == "2026" and senha == "0000":
                    st.session_state.logged_in = True
                    st.markdown('<div class="success-message">✅ Login realizado com sucesso!</div>', 
                               unsafe_allow_html=True)
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.markdown('<div class="error-message">❌ Usuário ou senha incorretos!</div>', 
                               unsafe_allow_html=True)

        with col2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.session_state.show_login_form = False
                st.session_state.lamp_pulled = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Dicas de login
    if not st.session_state.show_login_form:
        st.markdown("""
            <div style='text-align: center; margin-top: 2rem; color: #999;'>
            <p><strong>Credenciais de teste:</strong></p>
            <p>👤 Usuário: <code>2026</code></p>
            <p>🔑 Senha: <code>0000</code></p>
            </div>
        """, unsafe_allow_html=True)


def check_login():
    """Verifica se o usuário está logado"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    return st.session_state.logged_in
