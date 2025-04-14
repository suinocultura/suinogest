"""
Script para criar um logo simples para o aplicativo offline
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Definindo cores principais do aplicativo
ROXO_PRIMARIO = "#9C27B0"  # Roxo principal

def create_logo():
    """Cria um logo simples para o aplicativo"""
    # Criar diretório de assets se não existir
    os.makedirs('assets', exist_ok=True)
    
    # Verificar se o logo já existe
    if os.path.exists('assets/logo_placeholder.png'):
        print("O logo já existe, pulando criação.")
        return
    
    # Criar uma nova imagem com fundo transparente
    img = Image.new('RGBA', (200, 200), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Converter cor hex para RGB
    roxo = ROXO_PRIMARIO.lstrip('#')
    roxo_rgb = tuple(int(roxo[i:i+2], 16) for i in (0, 2, 4)) + (255,)  # Adicionando canal alpha
    
    # Desenhar um círculo roxo
    d.ellipse((10, 10, 190, 190), fill=roxo_rgb)
    
    # Adicionar texto, tentando usar uma fonte disponível
    try:
        # Tentar encontrar uma fonte disponível
        font = ImageFont.truetype("arial.ttf", 80)
    except IOError:
        try:
            # Caso não encontre, tentar usar a fonte padrão
            font = ImageFont.load_default()
        except:
            # Caso ainda falhe, desenhar apenas o círculo
            print("Não foi possível carregar uma fonte, o logo terá apenas o círculo.")
            font = None
    
    # Adicionar texto "S" se a fonte foi carregada
    if font:
        text_width, text_height = d.textsize("S", font=font)
        position = ((200 - text_width) // 2, (200 - text_height) // 2)
        d.text(position, "S", fill=(255, 255, 255), font=font)
    
    # Salvar a imagem
    img.save('assets/logo_placeholder.png')
    print("Logo criado com sucesso em assets/logo_placeholder.png")

if __name__ == "__main__":
    create_logo()