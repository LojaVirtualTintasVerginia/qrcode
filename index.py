import requests
from flask import Flask, request, render_template, send_file
import qrcode
from PIL import Image, ImageOps
from io import BytesIO

app = Flask(__name__)

def gerar_qrcode_com_logo(texto, logo_url='https://verginia.vtexassets.com/assets/vtex.file-manager-graphql/images/fc2eb161-4473-4914-b81e-20f3a2128146___9837c08760fd78d564c1d14383a852cf.jpg', largura_max_logo=200, altura_max_logo=50):
    # Gera o QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # H para melhor correção de erro
        box_size=15,  # Aumenta o tamanho dos boxes
        border=4,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    # Cria a imagem do QR Code
    img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Baixa o logo da URL
    response = requests.get(logo_url)
    logo = Image.open(BytesIO(response.content))

    # Converte o logo para RGBA (com transparência) e redimensiona mantendo a proporção
    logo = logo.convert("RGBA")
    logo.thumbnail((largura_max_logo, altura_max_logo), Image.Resampling.LANCZOS)

    # Criar uma nova imagem maior para adicionar a logo abaixo do QR code
    largura_final = img_qr.width
    altura_final = img_qr.height + logo.height + 10  # 10 pixels de margem entre QR code e logo

    nova_imagem = Image.new('RGB', (largura_final, altura_final), (255, 255, 255))
    nova_imagem.paste(img_qr, (0, 0))  # Cola o QR code no topo
    posicao_logo = ((largura_final - logo.width) // 2, img_qr.height + 10)  # Centraliza a logo
    nova_imagem.paste(logo, posicao_logo, mask=logo.split()[3])  # Cola a logo

    # Salva a imagem em um buffer para ser enviada ao usuário
    buffer = BytesIO()
    nova_imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        texto = request.form.get('texto')
        if texto:
            # Gera o QR Code com logo fora do QR code
            buffer = gerar_qrcode_com_logo(texto)
            return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='pixverginia.png')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)