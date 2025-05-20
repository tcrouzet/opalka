from PIL import Image, ImageDraw, ImageFont
import os, random

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)


def new_painting(width, height, number, painting_num):
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    # Calcul du fond
    if number < 1000000:  # 1965 à 1971
        background = "black"
    else:  # À partir de 1972
        background_intensity = (painting_num - 40) * 0.01
        background = (int(255 * background_intensity), int(255 * background_intensity), int(255 * background_intensity))
    
    draw.rectangle([(0, 0), (width, height)], fill=background)

    return image, draw


def create_opalka_painting(painting_num, number, height=9000):

    # Dimensions des tableaux 196/135 cm
    # 40 ans pour 233 tableau => 5,8 par ans
    # 40 tableau avant éclaircissement nu noir ou à partir de 1M

    #entre 400 et 500 sur les tableaux
    lignes_toile = random.randint(400, 500)

    pixels_ligne = int(height/lignes_toile)

    width = int(height*135/196)

    # Charger la police
    google_font = os.path.join(script_dir, "Satisfy-Regular.ttf") 
    try:
        font = ImageFont.truetype(google_font, pixels_ligne*1.1)
    except IOError:
        font = ImageFont.load_default(pixels_ligne*1.1)

    # Création des tableaux
    digit_painted = 0
    x, y = 10, 10
    line = 1
    
    # Nombre de digit avec une charge du pinceau
    treshold = random.randint(12, 22)

    image, draw = new_painting(width, height, number, painting_num)

    while(True):
        # Création d'une nouvelle image
        print(number)

        nombre_str = str(number)
        if len(nombre_str) + digit_painted > treshold:
            treshold = random.randint(12, 22)
            digit_painted = 0

        for digit in nombre_str:
            digit_width = draw.textlength(digit, font=font)
            if x + digit_width > width:
                # Passer à la ligne suivante
                print(f"new line {line}")
                x = 10
                y += pixels_ligne
                line += 1
                if y + pixels_ligne > height:
                    image_path = os.path.join(output_dir, f"{painting_num}-{number}.png")
                    image.save(image_path)
                    return number + 1

            # Calculer l'intensité du blanc
            brush_intensity = 255 - digit_painted*10
            white_intensity = int(brush_intensity)
            white = (white_intensity, white_intensity, white_intensity)

            # Y aléaloite
            y_offset = random.choice([-1, 0, 0, 0, 1])
            y_random = y + y_offset

            draw.text((x, y_random), digit, fill=white, font=font)
            
            x_offset = random.choice([-2, -1, 0, 1, 2])
            x += digit_width+x_offset
            digit_painted += 1

        # Ajouter un espace entre les nombres
        x += int(digit_width/6 + (digit_width / 10) * random.uniform(0.8, 1.2))

        number += 1


create_opalka_painting(1, 1)
exit()

start = 1
painting = 1
for i in range(1, 234):
    start = create_opalka_painting(i, start)
print(start)
