import sqlite3

DB_NAME = "mission_control.db"

def inicializar_mission_control():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Memória de Longo Prazo (O que o OpenClaw chama de "Lessons Learned")
    c.execute('''CREATE TABLE IF NOT EXISTS memoria_longo_prazo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, token_id TEXT, lucro REAL, licao TEXT
    )''')
    
    # O "Active Feed" do Bhanu: Caixa de Entrada de eventos do WebSocket
    c.execute('''CREATE TABLE IF NOT EXISTS inbox_tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT, agente_destino TEXT, token_id TEXT, preco_atual REAL, status TEXT DEFAULT 'PENDENTE'
    )''')
    
    conn.commit()
    conn.close()
    print("🧠 Banco de Dados 'Mission Control' inicializado com sucesso!")

def adicionar_tarefa(agente, token_id, preco):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Adiciona a tarefa na caixa de entrada para o agente acordar e ler
    c.execute("INSERT INTO inbox_tarefas (agente_destino, token_id, preco_atual) VALUES (?, ?, ?)", (agente, token_id, preco))
    conn.commit()
    conn.close()
    
def pegar_tarefa_pendente():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Pega a tarefa mais antiga que não foi processada
    c.execute("SELECT id, agente_destino, token_id, preco_atual FROM inbox_tarefas WHERE status = 'PENDENTE' LIMIT 1")
    tarefa = c.fetchone()
    if tarefa:
        # Marca como em progresso para outro agente não pegar a mesma
        c.execute("UPDATE inbox_tarefas SET status = 'PROCESSANDO' WHERE id = ?", (tarefa[0],))
        conn.commit()
    conn.close()
    return tarefa

def concluir_tarefa(id_tarefa):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM inbox_tarefas WHERE id = ?", (id_tarefa,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    inicializar_mission_control()