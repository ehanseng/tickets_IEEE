"""
Script para generar un favicon.ico simple
"""
from PIL import Image, ImageDraw, ImageFont
import io

def create_favicon():
    # Crear imagen de 32x32 (tamaño estándar de favicon)
    size = 32
    img = Image.new('RGBA', (size, size), color=(0, 98, 155, 255))  # Color IEEE azul

    draw = ImageDraw.Draw(img)

    # Dibujar un ticket simplificado (rectángulo con borde)
    margin = 4
    draw.rectangle(
        [(margin, margin), (size-margin, size-margin)],
        outline=(255, 255, 255, 255),
        width=2
    )

    # Dibujar línea punteada en el medio (simula perforación del ticket)
    mid = size // 2
    for i in range(margin+2, size-margin-2, 3):
        draw.point((i, mid), fill=(255, 255, 255, 255))
        draw.point((i, mid+1), fill=(255, 255, 255, 255))

    # Guardar como ICO
    img.save('static/favicon.ico', format='ICO', sizes=[(32, 32)])
    print("OK - favicon.ico generado exitosamente")

if __name__ == "__main__":
    try:
        create_favicon()
    except Exception as e:
        print(f"Error: {e}")
        print("Nota: Si falla, el favicon.svg funcionará igual")
