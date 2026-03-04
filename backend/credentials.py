from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# A chave privada da sua carteira Polygon (MANTENHA ISSO SEGURO)
private_key = "0x8e8aa00010a5ad1a58a992cdd1f98721238dec929dfeb491686b991da3d871e1" 

# Inicializamos o cliente apontando para a CLOB API
client = ClobClient(
    "https://clob.polymarket.com", 
    key=private_key, 
    chain_id=POLYGON
)

def gerar_credenciais():
    print("Gerando credenciais L2 via assinatura criptográfica...\n")
    
    # Cria as credenciais derivadas da sua carteira
    creds = client.create_or_derive_api_creds()
    
    print("Guarde estes dados em um arquivo .env seguro e NUNCA os exponha:")
    print(f"API_KEY: {creds.api_key}")
    print(f"API_SECRET: {creds.api_secret}")
    print(f"API_PASSPHRASE: {creds.api_passphrase}")

if __name__ == "__main__":
    gerar_credenciais()