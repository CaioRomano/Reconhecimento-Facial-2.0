from flask import Flask, render_template, request, session
import os
from src.config import DIR_IMG

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Obtenha a lista de nomes de arquivo de imagens no diretório
image_files = [f for f in os.listdir(DIR_IMG)]
# Configurações padrão
default_images_per_page = 10
default_images_per_row = 4

# Configurações do número mínimo e máximo de imagens por página
min_images_per_page = 5
max_images_per_page = len(image_files)

# Calcule o número total de páginas
total_pages = -(-len(image_files) // default_images_per_page)


def get_total_pages(images_per_page):
    total_images = len(os.listdir(DIR_IMG))
    return max(1, (total_images + images_per_page - 1) // images_per_page)


@app.route('/')
def show_images():
    try:
        images_per_page = int(request.args.get('ipp', session.get('images_per_page', 5)))
        current_page = int(request.args.get('page', 1))

        image_files = sorted([f for f in os.listdir(DIR_IMG)])

        total_pages = get_total_pages(images_per_page)

        start_index = (current_page - 1) * images_per_page
        end_index = min(start_index + images_per_page, len(image_files))

        visible_images = image_files[start_index:end_index]

        session['images_per_page'] = images_per_page  # Atualiza o valor do controle na sessão

        return render_template(
            'index.html',
            image_files=visible_images,
            current_page=current_page,
            total_pages=total_pages,
            images_per_page=images_per_page
        )
    except Exception as e:
        return f"Erro: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
