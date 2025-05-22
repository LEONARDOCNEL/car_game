import pygame
from pygame.locals import *
import random
import os

seed = random.randint(1000, 9999)
a = random.randint(1000, 9999)
c = random.randint(1000, 9999)
m = 1000

def alglin(seed, ite, a, c, m):
    datos = []
    for i in range(ite):
        var = (a * seed + c) % m
        ri = round(var / (m - 1), 5)
        datos.append(ri)
        seed = var
    return datos

lcg_index = 0
lcg_datos = alglin(seed, 1000, a, c, m)
def get_lcg():
    global lcg_index
    if lcg_index >= len(lcg_datos):
        lcg_index = 0
    valor = lcg_datos[lcg_index]
    lcg_index += 1
    return valor

pygame.init()

ancho = 1000
alto = 700
pantalla = pygame.display.set_mode((ancho, alto), RESIZABLE)
pygame.display.set_caption('Car racing (Proyecto simulación)')

gris = (100, 100, 100)
verde = (76, 208, 56)
negro = (0, 0, 0)
blanco = (255, 255, 255)
amarillo = (255, 232, 0)

pygame.mixer.init()
colision_sonido = pygame.mixer.Sound("colision.wav")
pygame.mixer.music.load("musica_fondo.mp3")
pygame.mixer.music.play(-1)

ancho_carretera = 300
ancho_marcador = 10
alto_marcador = 50

centro_pantalla = ancho // 2
carril_izquierdo = centro_pantalla - 100
carril_centro = centro_pantalla
carril_derecho = centro_pantalla + 100
carriles = [carril_izquierdo, carril_centro, carril_derecho]

carretera = (centro_pantalla - ancho_carretera // 2, 0, ancho_carretera, alto)
borde_izquierdo = (carretera[0] - 5, 0, ancho_marcador, alto)
borde_derecho = (carretera[0] + ancho_carretera - 5, 0, ancho_marcador, alto)

marcador_y = 0

pos_x_jugador = carril_centro
pos_y_jugador = alto - 100

reloj = pygame.time.Clock()
fps = 120

juego_terminado = False
velocidad = 5 #velocidad inicial
puntaje = 0
vidas = 3
nombre_jugador = ''

archivo_puntajes = 'mejores_puntajes.txt'
mejores_puntajes = []
if os.path.exists(archivo_puntajes):
    with open(archivo_puntajes, 'r') as f:
        for linea in f:
            partes = linea.strip().split(',')
            if len(partes) == 2:
                nombre, valor = partes
                mejores_puntajes.append((nombre, int(valor)))
    mejores_puntajes.sort(key=lambda x: x[1], reverse=True)

class Vehiculo(pygame.sprite.Sprite):
    def __init__(self, imagen, x, y):
        super().__init__()
        escala = 45 / imagen.get_rect().width
        nuevo_ancho = int(imagen.get_rect().width * escala)
        nuevo_alto = int(imagen.get_rect().height * escala)
        self.image = pygame.transform.scale(imagen, (nuevo_ancho, nuevo_alto))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class AutoJugador(Vehiculo):
    def __init__(self, x, y):
        imagen = pygame.image.load('images/car.png')
        super().__init__(imagen, x, y)

grupo_jugador = pygame.sprite.Group()
grupo_vehiculos = pygame.sprite.Group()

jugador = AutoJugador(pos_x_jugador, pos_y_jugador)
grupo_jugador.add(jugador)

imagenes_vehiculos = []
for archivo in ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']:
    img = pygame.image.load('images/' + archivo)
    imagenes_vehiculos.append(img)

imagen_explosion = pygame.image.load('images/crash.png')
rect_explosion = imagen_explosion.get_rect()

corazon = pygame.image.load('images/corazon.png')
corazon = pygame.transform.scale(corazon, (40, 40))

# Cargar texturas de fondo y carretera
imagen_pasto = pygame.image.load('images/pasto.png')
imagen_carretera = pygame.image.load('images/carretera.png')

def pedir_nombre():
    nombre = ''
    fuente = pygame.font.Font(None, 32)
    input_activo = True

    while input_activo:
        pantalla.fill(gris)
        mensaje = fuente.render("\u00a1Nuevo récord! Escribe tu nombre:", True, blanco)
        rect_mensaje = mensaje.get_rect(center=(ancho / 2, 150))
        pantalla.blit(mensaje, rect_mensaje)

        caja = pygame.Rect(ancho / 2 - 100, 200, 200, 40)
        pygame.draw.rect(pantalla, blanco, caja, 2)

        texto_input = fuente.render(nombre, True, blanco)
        pantalla.blit(texto_input, (caja.x + 5, caja.y + 5))

        pygame.display.flip()
        reloj.tick(30)

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == KEYDOWN:
                if evento.key == K_RETURN and nombre:
                    return nombre
                elif evento.key == K_BACKSPACE:
                    nombre = nombre[:-1]
                elif len(nombre) < 12:
                    nombre += evento.unicode

def mostrar_menu():
    opciones = ['Iniciar Juego', 'Salir']
    seleccion = 0
    fuente = pygame.font.Font(None, 60)
    seleccionando = True
    fondo_menu = pygame.image.load("images/fondo_menu.jpg")

    while seleccionando:
        pantalla.blit(pygame.transform.scale(fondo_menu, (ancho, alto)), (0, 0))

        for i, opcion in enumerate(opciones):
            color = amarillo if i == seleccion else blanco
            texto_opcion = fuente.render(opcion, True, color)
            pantalla.blit(texto_opcion, texto_opcion.get_rect(center=(ancho // 2, 450 + i * 80)))

        pygame.display.flip()
        reloj.tick(30)

        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                exit()
            if evento.type == KEYDOWN:
                if evento.key == K_UP:
                    seleccion = (seleccion - 1) % len(opciones)
                elif evento.key == K_DOWN:
                    seleccion = (seleccion + 1) % len(opciones)
                elif evento.key == K_RETURN:
                    if opciones[seleccion] == 'Iniciar Juego':
                        seleccionando = False
                    elif opciones[seleccion] == 'Salir':
                        pygame.quit()
                        exit()

mostrar_menu()

ejecutando = True
while ejecutando:
    reloj.tick(fps)

    for evento in pygame.event.get():
        if evento.type == QUIT:
            ejecutando = False
        if evento.type == KEYDOWN:
            if evento.key == K_ESCAPE:
                fuente = pygame.font.Font(None, 36)
                texto_confirmar = fuente.render('Seguro que deseas salir? (Y/N)', True, blanco)
                pantalla.blit(texto_confirmar, (ancho // 2 - 150, alto // 2))
                pygame.display.flip()
                esperando_confirmacion = True
                while esperando_confirmacion:
                    for e in pygame.event.get():
                        if e.type == QUIT:
                            ejecutando = False
                            esperando_confirmacion = False
                        if e.type == KEYDOWN:
                            if e.key == K_y:
                                ejecutando = False
                                esperando_confirmacion = False
                            elif e.key == K_n:
                                esperando_confirmacion = False
            if not juego_terminado:
                if evento.key == K_LEFT and jugador.rect.center[0] > carril_izquierdo:
                    jugador.rect.x -= 100
                elif evento.key == K_RIGHT and jugador.rect.center[0] < carril_derecho:
                    jugador.rect.x += 100

    # Dibujar fondo de pasto
    pantalla.blit(pygame.transform.scale(imagen_pasto, (ancho, alto)), (0, 0))

    # Dibujar carretera encima
    pantalla.blit(pygame.transform.scale(imagen_carretera, (ancho_carretera, alto)), (carretera[0], carretera[1]))

    pygame.draw.rect(pantalla, amarillo, borde_izquierdo)
    pygame.draw.rect(pantalla, amarillo, borde_derecho)

    marcador_y += velocidad * 2
    if marcador_y >= alto_marcador * 2:
        marcador_y = 0
    for y in range(-alto_marcador * 2, alto, alto_marcador * 2):
        pygame.draw.rect(pantalla, blanco, (carril_izquierdo + 45, y + marcador_y, ancho_marcador, alto_marcador))
        pygame.draw.rect(pantalla, blanco, (carril_centro + 45, y + marcador_y, ancho_marcador, alto_marcador))

    grupo_jugador.draw(pantalla)

    if len(grupo_vehiculos) < 2:
        agregar = True
        for v in grupo_vehiculos:
            if v.rect.top < v.rect.height * 1.5:
                agregar = False
        if agregar:
            carril = carriles[int(get_lcg() * len(carriles))]
            imagen = imagenes_vehiculos[int(get_lcg() * len(imagenes_vehiculos))]
            auto = Vehiculo(imagen, carril, -200)
            grupo_vehiculos.add(auto)

    for v in grupo_vehiculos:
        v.rect.y += velocidad
        if v.rect.top >= alto:
            v.kill()
            puntaje += 10 #score
            if puntaje % 100 == 0:
                velocidad += 2 # de cuanto en cuanto va la velocidad

    grupo_vehiculos.draw(pantalla)

    fuente = pygame.font.Font(None, 50)
    texto = fuente.render(f'Score: {puntaje}', True, amarillo)
    pantalla.blit(texto, (ancho - 250, 20))

    for i in range(vidas):
        pantalla.blit(corazon, (20 + i * 50, 20))

    colisiones = pygame.sprite.spritecollide(jugador, grupo_vehiculos, True)
    if colisiones and not juego_terminado:
        colision_sonido.play()
        vidas -= 1
        rect_explosion.center = jugador.rect.center
        pantalla.blit(imagen_explosion, rect_explosion)
        pygame.display.update()
        pygame.time.delay(500)

        if vidas <= 0:
            if len(mejores_puntajes) < 3 or puntaje > mejores_puntajes[-1][1]:
                nombre_jugador = pedir_nombre()
                mejores_puntajes.append((nombre_jugador, puntaje))
                mejores_puntajes.sort(key=lambda x: x[1], reverse=True)
                mejores_puntajes = mejores_puntajes[:3]
                with open(archivo_puntajes, 'w') as f:
                    for nombre, score in mejores_puntajes:
                        f.write(f"{nombre},{score}\n")
            juego_terminado = True

    if juego_terminado:
        pantalla.blit(imagen_explosion, rect_explosion)
        pygame.draw.rect(pantalla, negro, (0, 50, ancho, 300))

        fuente_game_over = pygame.font.Font(None, 60)
        fuente_top = pygame.font.Font(None, 36)

        texto_game_over = fuente_game_over.render('Game Over. ¿Jugar de nuevo? (Y/N)', True, blanco)
        texto_puntaje = fuente_game_over.render(f'Tu puntaje: {puntaje}', True, blanco)
        texto_top = fuente_top.render('Top 3 puntajes:', True, blanco)

        pantalla.blit(texto_game_over, texto_game_over.get_rect(center=(ancho // 2, 80)))
        pantalla.blit(texto_puntaje, texto_puntaje.get_rect(center=(ancho // 2, 140)))
        pantalla.blit(texto_top, texto_top.get_rect(center=(ancho // 2, 200)))

        for i, (nombre, score) in enumerate(mejores_puntajes):
            linea = f"{i+1}. {nombre} - {score} puntos"
            texto_linea = fuente_top.render(linea, True, blanco)
            pantalla.blit(texto_linea, texto_linea.get_rect(center=(ancho // 2, 240 + i * 30)))

    pygame.display.update()

    while juego_terminado:
        reloj.tick(fps)
        for evento in pygame.event.get():
            if evento.type == QUIT:
                juego_terminado = False
                ejecutando = False
            if evento.type == KEYDOWN:
                if evento.key == K_y:
                    juego_terminado = False
                    velocidad = 2
                    puntaje = 0
                    vidas = 3
                    grupo_vehiculos.empty()
                    jugador.rect.center = [pos_x_jugador, pos_y_jugador]
                elif evento.key == K_n:
                    juego_terminado = False
                    ejecutando = False

pygame.quit()

