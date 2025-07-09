#!/usr/bin/env python3
"""
Script para conectar com o MinIO server e listar buckets existentes.

Requisitos:
    pip install minio

Uso:
    python connect.py
"""

from minio import Minio
from minio.error import S3Error
import sys


def connect_to_minio():
    """
    Conecta com o servidor MinIO usando as credenciais padrão.
    
    Returns:
        Minio: Cliente MinIO configurado
    """
    # Configurações do MinIO (deve corresponder ao docker-compose.yml)
    endpoint = "localhost:9000"
    access_key = "minioadmin"
    secret_key = "minioadmin123"
    secure = False  # False para HTTP, True para HTTPS
    
    try:
        # Criar cliente MinIO
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        
        print(f"✅ Conectado ao MinIO em {endpoint}")
        return client
        
    except Exception as e:
        print(f"❌ Erro ao conectar com o MinIO: {e}")
        sys.exit(1)


def list_buckets(client):
    """
    Lista todos os buckets disponíveis no MinIO.
    
    Args:
        client (Minio): Cliente MinIO configurado
    """
    try:
        buckets = client.list_buckets()
        
        if buckets:
            print("\n📦 Buckets encontrados:")
            print("-" * 50)
            for bucket in buckets:
                print(f"Nome: {bucket.name}")
                print(f"Data de criação: {bucket.creation_date}")
                print("-" * 50)
        else:
            print("\n📦 Nenhum bucket encontrado.")
            print("💡 Dica: Crie um bucket através do console web em http://localhost:9003/")
            
    except S3Error as e:
        print(f"❌ Erro S3 ao listar buckets: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


def create_sample_bucket(client, bucket_name="test-bucket"):
    """
    Cria um bucket de exemplo (opcional).
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket a ser criado
    """
    try:
        # Verificar se o bucket já existe
        if client.bucket_exists(bucket_name):
            print(f"📦 Bucket '{bucket_name}' já existe.")
            return
        
        # Criar o bucket
        client.make_bucket(bucket_name)
        print(f"✅ Bucket '{bucket_name}' criado com sucesso!")
        
    except S3Error as e:
        print(f"❌ Erro S3 ao criar bucket: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao criar bucket: {e}")


def delete_bucket(client, bucket_name):
    """
    Exclui um bucket do MinIO.
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket a ser excluído
    """
    try:
        # Verificar se o bucket existe
        if not client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' não existe.")
            return
        
        # Verificar se o bucket está vazio
        objects = client.list_objects(bucket_name)
        if any(True for _ in objects):
            print(f"⚠️  Bucket '{bucket_name}' não está vazio.")
            response = input("Deseja remover todos os objetos e excluir o bucket? (s/n): ").lower().strip()
            
            if response not in ['s', 'sim', 'y', 'yes']:
                print("❌ Operação cancelada.")
                return
            
            # Remover todos os objetos do bucket
            objects = client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                client.remove_object(bucket_name, obj.object_name)
                print(f"🗑️  Objeto '{obj.object_name}' removido.")
        
        # Excluir o bucket
        client.remove_bucket(bucket_name)
        print(f"✅ Bucket '{bucket_name}' excluído com sucesso!")
        
    except S3Error as e:
        print(f"❌ Erro S3 ao excluir bucket: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao excluir bucket: {e}")


def upload_file(client, bucket_name, file_path, object_name=None):
    """
    Faz upload de um arquivo para o MinIO.
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket de destino
        file_path (str): Caminho do arquivo local
        object_name (str, optional): Nome do objeto no MinIO. Se None, usa o nome do arquivo.
    """
    import os
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            print(f"❌ Arquivo '{file_path}' não encontrado.")
            return
        
        # Verificar se o bucket existe
        if not client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' não existe.")
            response = input("Deseja criar o bucket? (s/n): ").lower().strip()
            
            if response in ['s', 'sim', 'y', 'yes']:
                client.make_bucket(bucket_name)
                print(f"✅ Bucket '{bucket_name}' criado.")
            else:
                print("❌ Upload cancelado.")
                return
        
        # Se object_name não foi especificado, usar o nome do arquivo
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        # Fazer upload do arquivo
        client.fput_object(bucket_name, object_name, file_path)
        print(f"✅ Arquivo '{file_path}' enviado como '{object_name}' no bucket '{bucket_name}'!")
        
        # Mostrar informações do arquivo
        stat = client.stat_object(bucket_name, object_name)
        print(f"📊 Tamanho: {stat.size} bytes")
        print(f"📅 Data de modificação: {stat.last_modified}")
        
    except S3Error as e:
        print(f"❌ Erro S3 ao fazer upload: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao fazer upload: {e}")


def download_file(client, bucket_name, object_name, file_path=None):
    """
    Faz download de um arquivo do MinIO.
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket de origem
        object_name (str): Nome do objeto no MinIO
        file_path (str, optional): Caminho local para salvar. Se None, usa o nome do objeto.
    """
    try:
        # Verificar se o bucket existe
        if not client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' não existe.")
            return
        
        # Verificar se o objeto existe
        try:
            client.stat_object(bucket_name, object_name)
        except S3Error as e:
            if e.code == 'NoSuchKey':
                print(f"❌ Objeto '{object_name}' não encontrado no bucket '{bucket_name}'.")
                return
            raise
        
        # Se file_path não foi especificado, usar o nome do objeto
        if file_path is None:
            file_path = object_name
        
        # Fazer download do arquivo
        client.fget_object(bucket_name, object_name, file_path)
        print(f"✅ Arquivo '{object_name}' baixado como '{file_path}'!")
        
        # Mostrar informações do arquivo
        import os
        size = os.path.getsize(file_path)
        print(f"📊 Tamanho: {size} bytes")
        
    except S3Error as e:
        print(f"❌ Erro S3 ao fazer download: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao fazer download: {e}")


def read_file_content(client, bucket_name, object_name):
    """
    Lê o conteúdo de um arquivo do MinIO (para arquivos de texto).
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket
        object_name (str): Nome do objeto no MinIO
    """
    try:
        # Verificar se o bucket existe
        if not client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' não existe.")
            return
        
        # Verificar se o objeto existe
        try:
            stat = client.stat_object(bucket_name, object_name)
        except S3Error as e:
            if e.code == 'NoSuchKey':
                print(f"❌ Objeto '{object_name}' não encontrado no bucket '{bucket_name}'.")
                return
            raise
        
        # Ler o objeto
        response = client.get_object(bucket_name, object_name)
        content = response.read()
        
        # Tentar decodificar como texto
        try:
            text_content = content.decode('utf-8')
            print(f"📄 Conteúdo do arquivo '{object_name}':")
            print("=" * 50)
            print(text_content)
            print("=" * 50)
        except UnicodeDecodeError:
            print(f"📄 Arquivo '{object_name}' é binário (tamanho: {len(content)} bytes)")
            print("💡 Use a função de download para arquivos binários.")
        
        response.close()
        response.release_conn()
        
    except S3Error as e:
        print(f"❌ Erro S3 ao ler arquivo: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao ler arquivo: {e}")


def list_objects(client, bucket_name):
    """
    Lista todos os objetos em um bucket.
    
    Args:
        client (Minio): Cliente MinIO configurado
        bucket_name (str): Nome do bucket
    """
    try:
        # Verificar se o bucket existe
        if not client.bucket_exists(bucket_name):
            print(f"❌ Bucket '{bucket_name}' não existe.")
            return
        
        # Listar objetos
        objects = client.list_objects(bucket_name, recursive=True)
        object_list = list(objects)
        
        if object_list:
            print(f"\n📁 Objetos no bucket '{bucket_name}':")
            print("-" * 70)
            for obj in object_list:
                print(f"Nome: {obj.object_name}")
                print(f"Tamanho: {obj.size} bytes")
                print(f"Data de modificação: {obj.last_modified}")
                print("-" * 70)
        else:
            print(f"\n📁 Bucket '{bucket_name}' está vazio.")
            
    except S3Error as e:
        print(f"❌ Erro S3 ao listar objetos: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado ao listar objetos: {e}")


def show_menu():
    """Exibe o menu de opções."""
    print("\n" + "=" * 60)
    print("🔧 MENU DE OPERAÇÕES MINIO")
    print("=" * 60)
    print("1. 📦 Listar buckets")
    print("2. ➕ Criar bucket")
    print("3. 🗑️  Excluir bucket")
    print("4. 📁 Listar objetos em um bucket")
    print("5. ⬆️  Upload de arquivo")
    print("6. ⬇️  Download de arquivo")
    print("7. 📄 Ler conteúdo de arquivo (texto)")
    print("8. ❌ Sair")
    print("=" * 60)


def main():
    """Função principal do script."""
    print("🚀 Conectando com o MinIO Server...")
    print("=" * 60)
    
    # Conectar com o MinIO
    client = connect_to_minio()
    
    # Menu interativo
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção (1-8): ").strip()
            
            if choice == '1':
                list_buckets(client)
            
            elif choice == '2':
                bucket_name = input("Nome do bucket: ").strip()
                if bucket_name:
                    create_sample_bucket(client, bucket_name)
                else:
                    print("❌ Nome do bucket não pode estar vazio.")
            
            elif choice == '3':
                bucket_name = input("Nome do bucket para excluir: ").strip()
                if bucket_name:
                    delete_bucket(client, bucket_name)
                else:
                    print("❌ Nome do bucket não pode estar vazio.")
            
            elif choice == '4':
                bucket_name = input("Nome do bucket: ").strip()
                if bucket_name:
                    list_objects(client, bucket_name)
                else:
                    print("❌ Nome do bucket não pode estar vazio.")
            
            elif choice == '5':
                bucket_name = input("Nome do bucket de destino: ").strip()
                file_path = input("Caminho do arquivo local: ").strip()
                object_name = input("Nome do objeto no MinIO (Enter para usar nome do arquivo): ").strip()
                
                if bucket_name and file_path:
                    upload_file(client, bucket_name, file_path, object_name if object_name else None)
                else:
                    print("❌ Bucket e arquivo são obrigatórios.")
            
            elif choice == '6':
                bucket_name = input("Nome do bucket: ").strip()
                object_name = input("Nome do objeto no MinIO: ").strip()
                file_path = input("Caminho local para salvar (Enter para usar nome do objeto): ").strip()
                
                if bucket_name and object_name:
                    download_file(client, bucket_name, object_name, file_path if file_path else None)
                else:
                    print("❌ Bucket e objeto são obrigatórios.")
            
            elif choice == '7':
                bucket_name = input("Nome do bucket: ").strip()
                object_name = input("Nome do objeto: ").strip()
                
                if bucket_name and object_name:
                    read_file_content(client, bucket_name, object_name)
                else:
                    print("❌ Bucket e objeto são obrigatórios.")
            
            elif choice == '8':
                print("\n✨ Encerrando o programa...")
                break
            
            else:
                print("❌ Opção inválida. Escolha entre 1-8.")
        
        except KeyboardInterrupt:
            print("\n\n✨ Programa interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    print("\n✨ Script concluído!")


if __name__ == "__main__":
    main() 