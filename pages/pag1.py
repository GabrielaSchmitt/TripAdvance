import streamlit as st

def check_login():
    """Verifica se o usuário está logado"""
    if not st.session_state.get('logged_in', False):
        st.warning("Por favor, faça login para acessar esta página")
        st.switch_page("home.py")
        return False
    return True

def main():
    if not check_login():
        return
        
    st.title("Bem-vindo!")
    st.write(f"Olá {st.session_state['email']}")
    
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['email'] = None
        st.switch_page("home.py")

if __name__ == "__main__":
    main()