# MinIO Server

Este projeto configura um servidor MinIO usando Docker Compose para armazenamento de objetos compatível com S3.

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

## Volumes

Os dados são persistidos no volume `minio_data`. Isso garante que seus arquivos não sejam perdidos quando o container for reiniciado.