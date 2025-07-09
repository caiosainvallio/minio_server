# MinIO Server

Este projeto configura um servidor MinIO usando Docker Compose para armazenamento de objetos compatível com S3.

## Estrutura do Projeto

```
minio_server/
├── docker-compose.yml  # Configuração do serviço MinIO
├── Makefile           # Comandos para gerenciar o serviço
├── requirements.txt   # Dependências Python
├── connect.py        # Script interativo para gerenciar MinIO
├── exemplo.txt       # Arquivo de exemplo para testes
└── README.md         # Documentação do projeto
```

## Configuração

O serviço MinIO está configurado com:
- **API MinIO**: Porta 9000
- **Console Web**: Porta 9003 (acessível via `http://localhost:9003/`)
- **Credenciais padrão**:
  - Usuário: `minioadmin`
  - Senha: `minioadmin123`

## Como usar

### Opção 1: Usando Makefile (recomendado)

```bash
# Iniciar o serviço
make run

# Ver logs em tempo real
make logs

# Parar o serviço
make stop

# Limpar tudo (containers, volumes e imagens)
make clear_all

# Ver todos os comandos disponíveis
make help
```

### Opção 2: Usando docker-compose diretamente

#### 1. Iniciar o serviço

```bash
docker-compose up -d
```

#### 2. Parar o serviço

```bash
docker-compose down
```

#### 3. Remover dados persistentes (opcional)

```bash
docker-compose down -v
```

### Acessar o console web

Abra seu navegador e acesse: `http://localhost:9003/`

Use as credenciais:
- **Usuário**: `minioadmin`
- **Senha**: `minioadmin123`

## Personalização

Para personalizar as credenciais, edite as variáveis de ambiente no arquivo `docker-compose.yml`:

```yaml
environment:
  MINIO_ROOT_USER: seu_usuario
  MINIO_ROOT_PASSWORD: sua_senha_segura
```

## Verificação de saúde

O serviço inclui um healthcheck que verifica se o MinIO está funcionando corretamente. Você pode verificar o status com:

```bash
docker-compose ps
```

## Comandos do Makefile

| Comando | Descrição |
|---------|-----------|
| `make run` | Inicia o serviço MinIO em background |
| `make stop` | Para o serviço MinIO |
| `make logs` | Exibe os logs do MinIO em tempo real |
| `make build` | Constrói a imagem Docker (se necessário) |
| `make clear_all` | Remove containers, volumes e imagens |
| `make help` | Mostra todos os comandos disponíveis |

## Testando a Conexão

### Script Python de Exemplo

O projeto inclui um script `connect.py` que demonstra como conectar com o MinIO usando Python:

#### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

#### 2. Executar o script

```bash
python connect.py
```

O script oferece um menu interativo com as seguintes funcionalidades:
- 📦 Listar buckets existentes
- ➕ Criar novos buckets
- 🗑️ Excluir buckets (com confirmação)
- 📁 Listar objetos dentro de um bucket
- ⬆️ Upload de arquivos para o MinIO
- ⬇️ Download de arquivos do MinIO
- 📄 Ler conteúdo de arquivos de texto diretamente

#### 3. Exemplos de uso programático

```python
from minio import Minio

# Conectar com o MinIO
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

# Listar buckets
buckets = client.list_buckets()
for bucket in buckets:
    print(f"Bucket: {bucket.name}")

# Criar um bucket
client.make_bucket("meu-bucket")

# Upload de arquivo
client.fput_object("meu-bucket", "documento.txt", "/caminho/para/arquivo.txt")

# Download de arquivo
client.fget_object("meu-bucket", "documento.txt", "/caminho/para/download.txt")

# Listar objetos em um bucket
objects = client.list_objects("meu-bucket")
for obj in objects:
    print(f"Objeto: {obj.object_name}, Tamanho: {obj.size}")

# Ler conteúdo de arquivo
response = client.get_object("meu-bucket", "documento.txt")
content = response.read().decode('utf-8')
print(content)
response.close()
response.release_conn()

# Excluir objeto
client.remove_object("meu-bucket", "documento.txt")

# Excluir bucket (deve estar vazio)
client.remove_bucket("meu-bucket")
```

#### 4. Funcionalidades do Menu Interativo

| Opção | Funcionalidade | Descrição |
|-------|---------------|-----------|
| 1 | 📦 Listar buckets | Lista todos os buckets existentes no MinIO |
| 2 | ➕ Criar bucket | Cria um novo bucket com nome personalizado |
| 3 | 🗑️ Excluir bucket | Remove um bucket (confirma se tem objetos) |
| 4 | 📁 Listar objetos | Mostra todos os arquivos em um bucket |
| 5 | ⬆️ Upload arquivo | Envia arquivo local para o MinIO |
| 6 | ⬇️ Download arquivo | Baixa arquivo do MinIO para o local |
| 7 | 📄 Ler arquivo | Exibe conteúdo de arquivo de texto |
| 8 | ❌ Sair | Encerra o programa |

#### 5. Exemplos de Uso Prático

**Criar um bucket e fazer upload:**
```bash
# 1. Execute o script
python connect.py

# 2. Escolha "2" para criar bucket
# 3. Digite o nome: "documentos"
# 4. Escolha "5" para upload
# 5. Digite: bucket="documentos", arquivo="README.md"
```

**Baixar e ler um arquivo:**
```bash
# 1. Escolha "6" para download
# 2. Digite: bucket="documentos", objeto="README.md"
# 3. Escolha "7" para ler conteúdo
# 4. Digite: bucket="documentos", objeto="README.md"
```

## Volumes

Os dados são persistidos no volume `minio_data`. Isso garante que seus arquivos não sejam perdidos quando o container for reiniciado.

## Dicas e Solução de Problemas

### 🔧 Verificar se o MinIO está rodando

```bash
# Verificar status dos containers
make logs

# Ou usando docker-compose
docker-compose ps
```

### 🌐 Acessos e Portas

- **Console Web**: `http://localhost:9003/` (interface gráfica)
- **API MinIO**: `http://localhost:9000/` (para scripts e aplicações)
- **Credenciais padrão**: `minioadmin` / `minioadmin123`

### 📁 Testando com arquivo de exemplo

O projeto inclui um `exemplo.txt` para facilitar os testes:

```bash
# 1. Inicie o MinIO
make run

# 2. Execute o script
python connect.py

# 3. No menu, escolha:
#    - Opção 2: Criar bucket "test-bucket"
#    - Opção 5: Upload do arquivo "exemplo.txt"
#    - Opção 7: Ler conteúdo do arquivo
```

### ⚠️ Problemas Comuns

**Erro de conexão:**
- Verifique se o MinIO está rodando: `make logs`
- Confirme se as portas 9000 e 9003 estão livres

**Erro de permissão:**
- No macOS/Linux, pode ser necessário `sudo` para volumes
- Verifique as permissões do diretório do projeto

**Bucket não encontrado:**
- Use a opção 1 do script para listar buckets existentes
- Crie o bucket antes de fazer upload (opção 2)

### 🚀 Próximos Passos

1. **Explorar a API**: Use o console web para criar buckets visualmente
2. **Integrar com aplicações**: Use as credenciais para conectar suas apps
3. **Backup e restore**: Experimente backup de dados importantes
4. **Políticas de acesso**: Configure permissões específicas via console