from PIL import Image, ImageDraw, ImageFont
import os, random, re

script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

treshold_degradation = None

def new_painting(width, height, painting_num, number=None):
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    # Calcul du fond
    if number:    
        if number < 1000000: 
            # 1965 à 1971 pour Opalka
            background = "black"
            treshold_degradation = painting_num
        else:
            # À partir de 1972
            background_intensity = (painting_num - treshold_degradation) * 0.01
            background = (int(255 * background_intensity), int(255 * background_intensity), int(255 * background_intensity))
    else:
        # Dégratation dès le début
        background_intensity = (painting_num - 1) * 0.01
        background = (int(255 * background_intensity), int(255 * background_intensity), int(255 * background_intensity))
    
    draw.rectangle([(0, 0), (width, height)], fill=background)

    return image, draw, background


def opacity(digit_painted, background):
    # Calculer l'opacité du blanc
    opacity = 255 - digit_painted * 10
    if opacity < 0:
        opacity = 0

    # Calculer la couleur résultante en mélangeant le blanc avec le fond
    alpha = opacity / 255.0
    blended_color = (
        int(background[0] * (1 - alpha) + 255 * alpha),
        int(background[1] * (1 - alpha) + 255 * alpha),
        int(background[2] * (1 - alpha) + 255 * alpha)
    )
    return blended_color



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

    image, draw, background = new_painting(width, height, painting_num)

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
            white = opacity(digit_painted, background)

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


def extract_number(filename):
    # Utiliser une expression régulière pour extraire le numéro du fichier
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0


def create_montage(output_dir, montage_path, cols=12, rows=8, spacing=5, border=2, montage_width=4600):
    # Charger les images dans l'ordre alphabétique
    image_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')], key=extract_number)
    if len(image_files) != 100:
        raise ValueError("Le dossier doit contenir exactement 100 images.")

    # Largeur d'une image    
    img_width = int((montage_width - (cols + 1) * spacing - 2 * cols * border) // cols)

    # Charger une image pour obtenir sa hauteur
    sample_img_path = os.path.join(output_dir, image_files[0])
    sample_img = Image.open(sample_img_path)
    sample_height = sample_img.height
    sample_width = sample_img.width

    img_height = int(img_width*sample_height/sample_width)
    print(f"img_height: {img_height} img_width: {img_width}")

    # Calculer la hauteur du montage en fonction de la hauteur des images sources
    montage_height = rows * img_height + (rows + 1) * spacing + 2 * rows * border

    print(f"montage_width: {montage_width}, montage_height: {montage_height}")

    # Créer une nouvelle image pour le montage
    montage = Image.new('RGB', (montage_width, montage_height), 'white')
    draw = ImageDraw.Draw(montage)

    # Calculer la taille de chaque image dans le montage
    img_width = (montage_width - (cols - 1) * spacing - 2 * cols * border) // cols
    img_height = (montage_height - (rows - 1) * spacing - 2 * rows * border) // rows

    # Parcourir les images et les ajouter au montage
    for i in range(rows):
        for j in range(cols):
            print(f"Image {i * cols + j + 1}")
            img_index = i * cols + j
            if img_index >= len(image_files):
                break

            img_path = os.path.join(output_dir, image_files[img_index])
            img = Image.open(img_path)
            img = img.resize((img_width, img_height))

            # Calculer la position de l'image dans le montage
            x = j * (img_width + 2 * border + spacing) + border
            y = i * (img_height + 2 * border + spacing) + border

            # Dessiner le cadre
            draw.rectangle([x, y, x + img_width + 2 * border, y + img_height + 2 * border], outline='black', width=border)

            # Coller l'image dans le montage
            montage.paste(img, (x + border, y + border))

    # Sauvegarder le montage
    montage.save(montage_path)

if False:
    # Créer un tableau de test    
    create_opalka_painting(30, 1)

else:
    # All painting
    start = 1
    painting = 1
    for i in range(1, 101):
        start = create_opalka_painting(i, start)
    print(start)

    montage = os.path.join(script_dir, "output", "montage.jpg")
    create_montage(output_dir, montage)

