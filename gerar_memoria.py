import os

# --- CONFIGURAÇÕES ---
# Baseado na sua imagem, incluí as extensões que você usa
EXTENSOES_PERMITIDAS = ['.py', '.sql', '.json', '.md', '.txt']
ARQUIVO_SAIDA = 'MEMORIA_PROJETO_COMPLETA.txt'

# Pastas que não interessam para a IA (economiza tokens)
PASTAS_IGNORAR = {'__pycache__', '.git', '.vscode', 'venv', 'env', 'node_modules'}

def gerar_contexto():
    caminho_raiz = os.getcwd()
    
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as outfile:
        # 1. Cabeçalho Explicativo para a IA
        outfile.write("--- INSTRUÇÕES PARA A IA ---\n")
        outfile.write("Abaixo está todo o código fonte do meu projeto atual.\n")
        outfile.write("Cada arquivo inicia com '=== INICIO DO ARQUIVO: [caminho] ==='.\n")
        outfile.write("Use este contexto para responder minhas dúvidas sobre lógica e integração.\n\n")

        # 2. Escreve a Árvore de Arquivos (Visualização da Estrutura)
        outfile.write("--- ESTRUTURA DE PASTAS ---\n")
        for root, dirs, files in os.walk(caminho_raiz):
            # Remove pastas ignoradas da busca
            dirs[:] = [d for d in dirs if d not in PASTAS_IGNORAR]
            
            level = root.replace(caminho_raiz, '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write('{}{}/\n'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in EXTENSOES_PERMITIDAS):
                    outfile.write('{}{}\n'.format(subindent, f))
        
        outfile.write("\n" + "="*50 + "\n")
        outfile.write("--- CONTEÚDO DETALHADO DOS ARQUIVOS ---\n")
        outfile.write("="*50 + "\n\n")

        # 3. Escreve o conteúdo de cada arquivo
        for root, dirs, files in os.walk(caminho_raiz):
            dirs[:] = [d for d in dirs if d not in PASTAS_IGNORAR]
            
            for file in files:
                # Verifica extensão e se não é o próprio script ou o arquivo de saída
                if (any(file.endswith(ext) for ext in EXTENSOES_PERMITIDAS) 
                    and file != os.path.basename(__file__) 
                    and file != ARQUIVO_SAIDA):
                    
                    path_completo = os.path.join(root, file)
                    path_relativo = os.path.relpath(path_completo, caminho_raiz)
                    
                    # --- FORMATAÇÃO DE SEPARAÇÃO PARA A IA ---
                    outfile.write(f"\n{'='*20} INICIO DO ARQUIVO: {path_relativo} {'='*20}\n")
                    
                    try:
                        with open(path_completo, 'r', encoding='utf-8') as infile:
                            conteudo = infile.read()
                            outfile.write(conteudo)
                    except Exception as e:
                        outfile.write(f"[Erro ao ler arquivo: {e}]")
                    
                    outfile.write(f"\n{'='*20} FIM DO ARQUIVO: {path_relativo} {'='*20}\n")

if __name__ == "__main__":
    gerar_contexto()
    print(f"Sucesso! O arquivo '{ARQUIVO_SAIDA}' foi criado na raiz do projeto.")