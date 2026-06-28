from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DB_NAME = "financas.db" # Certifique-se de que é o mesmo nome usado no seu database.py

def atualizar_plano_via_webhook(username, novo_plano):
    """Atualiza o plano diretamente no banco de dados quando o webhook dispara"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET plano = ? WHERE username = ?", (novo_plano, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao atualizar banco via webhook: {e}")
        return False

@app.route('/kiwify-webhook', methods=['POST'])
def kiwify_webhook():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"status": "error", "message": "Sem dados enviados"}), 400
        
    # Captura o status do pedido e o e-mail/username do cliente enviado pela Kiwify
    status_pedido = dados.get("order_status")
    
    # A Kiwify envia os dados do cliente dentro do objeto 'Customer'
    customer = dados.get("Customer", {})
    email_cliente = customer.get("email")
    
    # Nota: Como o login do seu app usa 'username', o ideal é que no cadastro 
    # o usuário use o mesmo e-mail ou que você busque o usuário pelo e-mail corporativo.
    # Para este fluxo, vamos assumir que buscará o username correspondente ao e-mail.
    
    if status_pedido == "paid": # Pedido Aprovado (Pix, Cartão, etc)
        # Identifica o plano comprado com base no ID do produto ou nome do produto na Kiwify
        produto_nome = dados.get("product_name", "").lower()
        
        if "anual" in produto_nome:
            plano_destino = "Anual"
        elif "semestral" in produto_nome:
            plano_destino = "Mensal" # Ou mapeie para a lógica que seu banco aceita
        else:
            plano_destino = "Mensal"
            
        # Localiza o usuário no banco pelo e-mail e atualiza
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            # Busca o username atrelado àquele e-mail
            cursor.execute("SELECT username FROM usuarios WHERE email = ?", (email_cliente,))
            user = cursor.fetchone()
            
            if user:
                username_encontrado = user[0]
                atualizar_plano_via_webhook(username_encontrado, plano_destino)
                print(f"🚀 Plano {plano_destino} liberado automaticamente para {username_encontrado}!")
            else:
                print(f"⚠️ E-mail {email_cliente} pagou, mas não possui conta criada no FinanScore.")
                
            conn.close()
        except Exception as e:
            print(f"Erro ao processar webhook: {e}")

    elif status_pedido in ["refunded", "chargedback", "canceled"]:
        # Se o cliente pedir reembolso ou cancelar, o sistema remove o acesso premium
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM usuarios WHERE email = ?", (email_cliente,))
            user = cursor.fetchone()
            if user:
                atualizar_plano_via_webhook(user[0], "Gratuito")
                print(f"🔒 Acesso Premium revogado para {user[0]} (Motivo: {status_pedido}).")
            conn.close()
        except Exception as e:
            print(f"Erro ao revogar plano: {e}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Roda localmente na porta 5000 para testes
    app.run(port=5000, debug=True)