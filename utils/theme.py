from utils.theme import aplicar_estilo

def aplicar_estilo():
    st.markdown("""
    <style>

    /* =========================
       BASE (STREAMLIT FIX)
    ========================= */

    .main .block-container {
        padding: 1.2rem 1.2rem 2rem 1.2rem;
    }

    /* =========================
       CARD PRINCIPAL
    ========================= */

    .card {
        background: linear-gradient(135deg,#7b2cbf,#9d4edd);
        padding: 24px;
        border-radius: 22px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0px 6px 18px rgba(0,0,0,0.25);
        transition: 0.3s ease;
    }

    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.35);
    }

    /* =========================
       TEXTO DO CARD
    ========================= */

    .titulo {
        font-size: 18px;
        font-weight: 600;
        opacity: 0.9;
        margin-bottom: 5px;
    }

    .valor {
        font-size: 38px;
        font-weight: 800;
        margin: 10px 0;
        letter-spacing: 0.5px;
    }

    .sub {
        font-size: 14px;
        opacity: 0.85;
        line-height: 1.4;
    }

    /* =========================
       MELHORIA MOBILE
    ========================= */

    @media (max-width: 768px) {
        .valor {
            font-size: 28px;
        }

        .card {
            padding: 18px;
        }
    }

    </style>
    """, unsafe_allow_html=True)