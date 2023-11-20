## -- CRIAR
#
## Criar Banco de Dados
#python3 run.py database create db -n Database.db
#
## Criar tabela
#python3 run.py database create table PeopleFaces
#
## -- DELETAR
#
## Apagar tabela
#python3 run.py database delete table PeopleFaces
#
## Apagar dados
#python3 run.py database delete data PeopleFaces
#
## Apagar Banco de Dados
#python3 run.py database delete db -n Database.db
#
## -- RECOGNITION
#
## iniciar Reconhecimento Facial
#python3 run.py recognition init
#
### -- IMAGES
#
## Executar tarefa
#python3 run.py images execute-task capturar_imagem
#python3 run.py images execute-task nomear_imagem
#python3 run.py images execute-task recortar_imagem
#python3 run.py images execute-task "*"
#
## -- WEB
#
## Entrar na página
#python3.run.py web enter