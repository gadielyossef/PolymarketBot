import subprocess
import sys
import time

def main():
    print("🚀 Iniciando a Orquestração do PolymarketBot HFT...")
    processes = []
    try:
        # 1. Liga a API Bridge (A ponte com o Frontend)
        processes.append(subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.api.main:app", "--port", "8000"]))
        
        # 2. Liga os Feeders (Websocket de Preços)
        processes.append(subprocess.Popen([sys.executable, "-m", "backend.feeders.polymarket_ws"]))
        
        # 3. Liga os Agentes (IA e Risco)
        processes.append(subprocess.Popen([sys.executable, "-m", "backend.agents.gerente"]))
        processes.append(subprocess.Popen([sys.executable, "-m", "backend.agents.shuri"]))
        
        # 4. Liga o Motor Executivo (Fury Scalper)
        processes.append(subprocess.Popen([sys.executable, "-m", "backend.fury"]))

        print("✅ Todos os microserviços HFT estão rodando em background!")
        print("⏸️  Os bots estão aguardando o comando 'Start' da UI para operar.")
        
        # Mantém o orquestrador vivo
        for p in processes:
            p.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Desligando todos os motores...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()