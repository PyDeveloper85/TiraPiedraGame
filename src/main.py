import asyncio
import pygame
import random
import sys
import os
async def main():
    # Inicializar pygame
    pygame.init()
    pygame.mixer.init()

    # Intentar cargar la música de forma segura
    try:
        pygame.mixer.music.load(os.path.join("Assets/audio", "sound1.wav"))
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    # Configuración de la pantalla
    ANCHO = 800
    ALTO = 400
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Tira piedras 🦁")

    # Colores
    SABANA_FONDO = (128, 191, 255)
    SUELO_COLOR = (128, 128, 128)
    TEXTO_COLOR = (255, 255, 255)

    # Reloj y FPS
    reloj = pygame.time.Clock()
    FPS = 60
    ALTURA_SUELO = 380

    # --- CARGA DE IMÁGENES ---
    try:
        IMAGEN_LEON = pygame.image.load(os.path.join("Assets/Leon", "Leon.png")).convert_alpha()
        IMAGEN_FONDO = pygame.image.load(os.path.join("Assets/Fondo", "fondo.png")).convert_alpha()
        IMAGEN_FONDO = pygame.transform.scale(IMAGEN_FONDO, (ANCHO, ALTO))

        # 3 tipos de obstáculos terrestres
        IMAG_OBSTACULO_1 = pygame.image.load(os.path.join("Assets/Obstaculos", "roca.png")).convert_alpha()
        IMAG_OBSTACULO_2 = pygame.image.load(os.path.join("Assets/Obstaculos", "arbusto.png")).convert_alpha()

        # 2 tipos de aves (obstáculos aéreos)
        IMAG_AVE_1 = pygame.image.load(os.path.join("Assets/BIrds", "bird01.png")).convert_alpha()
        IMAG_AVE_2 = pygame.image.load(os.path.join("Assets/BIrds", "bird02.png")).convert_alpha()

    except pygame.error as e:
        print(f"Error al cargar imágenes: {e}")
        pygame.quit()
        sys.exit()

    # --- SISTEMA DE RÉCORD (PERSISTENCIA DE ARCHIVOS) ---
    ARCHIVO_RECORD = os.path.join("Assets/HIghscores)", "record.txt")

    def cargar_record():
        # Si el archivo no existe, lo inicializamos en 0
        if not os.path.exists(ARCHIVO_RECORD):
            with open(ARCHIVO_RECORD, "w") as f:
                f.write("0")
            return 0
        try:
            with open(ARCHIVO_RECORD, "r") as f:
                contenido = f.read().strip()
                return int(contenido) if contenido.isdigit() else 0
        except IOError:
            return 0

    def guardar_record(nuevo_record):
        try:
            with open(ARCHIVO_RECORD, "w") as f:
                f.write(str(nuevo_record))
        except IOError:
            print("No se pudo guardar el récord en el archivo.")

    # Cargar el récord histórico al iniciar el juego
    record_maximo = cargar_record()

    # Clase del León (Jugador)
    class Leon:
        def __init__(self):
            self.ancho = 100
            self.alto = 100
            self.imagen = pygame.transform.scale(IMAGEN_LEON, (self.ancho, self.alto))

            self.x = 100
            self.y = ALTURA_SUELO - self.alto
            self.vel_y = 0
            self.gravedad = 0.9
            self.salto_fuerza = -21.5
            self.en_el_suelo = True

        def saltar(self):
            if self.en_el_suelo:
                self.vel_y = self.salto_fuerza
                self.en_el_suelo = False

        def actualizar(self):
            self.vel_y += self.gravedad
            self.y += self.vel_y

            if self.y >= ALTURA_SUELO - self.alto:
                self.y = ALTURA_SUELO - self.alto
                self.vel_y = 0
                self.en_el_suelo = True

        def dibujar(self, superficie):
            superficie.blit(self.imagen, (self.x, self.y))

        def obtener_rect(self):
            return pygame.Rect(self.x + 15, self.y + 15, self.ancho - 30, self.alto - 15)

    # Clase de los Obstáculos
    class Obstaculo:
        def __init__(self, velocidad, tipo, x_pos=ANCHO):
            self.alto = 80
            self.ancho = 80
            self.tipo = tipo
            self.velocidad = velocidad
            self.x = x_pos
            self.y = ALTURA_SUELO - self.alto

            if self.tipo == 'roca':
                self.ancho, self.alto = 130, 130
                self.imagen = pygame.transform.scale(IMAG_OBSTACULO_1, (self.ancho, self.alto))
                self.y = ALTURA_SUELO - self.alto
            elif self.tipo == 'arbusto':
                self.ancho, self.alto = 100, 100
                self.imagen = pygame.transform.scale(IMAG_OBSTACULO_2, (self.ancho, self.alto))
                self.y = ALTURA_SUELO - self.alto
            elif self.tipo == 'bird01':  # <--- ACÁ
                self.ancho, self.alto = 30, 30
                self.imagen = pygame.transform.scale(IMAG_AVE_1, (self.ancho, self.alto))
                self.y = ALTURA_SUELO - 160
            elif self.tipo == 'bird02':  # <--- Y ACÁ
                self.ancho, self.alto = 65, 55
                self.imagen = pygame.transform.scale(IMAG_AVE_2, (self.ancho, self.alto))
                self.y = ALTURA_SUELO - 110

        def actualizar(self):
            self.x -= self.velocidad

        def dibujar(self, superficie):
            superficie.blit(self.imagen, (self.x, self.y))

        def obtener_rect(self):
            margen_x = 15
            margen_y = 10
            return pygame.Rect(
                self.x + margen_x,
                self.y + margen_y,
                self.ancho - (margen_x * 2),
                self.alto - (margen_y * 2),
            )

    # Variables del juego
    leon = Leon()
    obstaculos = []
    puntuacion = 0
    velocidad_juego = 7
    frecuencia_obstaculo = 0

    # Variables para el movimiento del fondo
    fondo_x1 = 0
    fondo_x2 = ANCHO

    fuente = pygame.font.SysFont("Orbitron", 25)
    fuente_grande = pygame.font.SysFont("Orbitron", 50)
    fuente_titulo = pygame.font.SysFont("Orbitron", 60, bold=True)

    # Estados del juego
    en_menu = True
    jugando = True
    game_over = False

    # Bucle principal
    while jugando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jugando = False
                pygame.mixer.quit()
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if en_menu:
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                        en_menu = False
                else:
                    if evento.key == pygame.K_SPACE or evento.key == pygame.K_UP:
                        if not game_over:
                            leon.saltar()
                        else:
                            # Reiniciar juego desde Game Over
                            leon = Leon()
                            obstaculos = []
                            puntuacion = 0
                            velocidad_juego = 7
                            fondo_x1 = 0
                            fondo_x2 = ANCHO
                            game_over = False
                            SABANA_FONDO = (128, 191, 255)
                            if pygame.mixer.get_init():
                                pygame.mixer.music.play(-1)

        if en_menu:
            # --- PANTALLA DE MENÚ PRINCIPAL ---
            pantalla.fill(SABANA_FONDO)
            pantalla.blit(IMAGEN_FONDO, (0, 0))

            # Textos del menú
            texto_tit = fuente_titulo.render("Kuka Tira Piedras", True, (143, 0, 255))
            texto_instrucciones = fuente.render("Presioná ESPACIO o ENTER para empezar", True, TEXTO_COLOR)
            texto_record_menu = fuente.render(f"MAXIMA SUPERVIVENCIA: {record_maximo} DÍAS", True, (255, 255, 255))

            # Centrar los textos en pantalla
            pantalla.blit(texto_tit, (ANCHO // 2 - texto_tit.get_width() // 2, ALTO // 4))
            pantalla.blit(texto_record_menu, (ANCHO // 2 - texto_record_menu.get_width() // 2, ALTO // 2 - 20))
            pantalla.blit(texto_instrucciones, (ANCHO // 2 - texto_instrucciones.get_width() // 2, ALTO // 2 + 40))

        else:
            # --- LÓGICA DE LA PARTIDA ACTIVA ---
            if not game_over:
                if puntuacion > 30:
                    SABANA_FONDO = (17, 17, 255)

                velocidad_fondo = velocidad_juego * 0.5
                fondo_x1 -= velocidad_fondo
                fondo_x2 -= velocidad_fondo

                if fondo_x1 <= -ANCHO:
                    fondo_x1 = fondo_x2 + ANCHO
                if fondo_x2 <= -ANCHO:
                    fondo_x2 = fondo_x1 + ANCHO

                leon.actualizar()
                velocidad_juego += 0.002
                frecuencia_obstaculo -= 1

                # Generador de obstáculos aleatorios
                # Generador de obstáculos aleatorios
                if frecuencia_obstaculo <= 0 and random.random() < 0.04:
                    tipos_disponibles = ['roca', 'arbusto', 'bird01', 'bird02']
                    # Configuramos las probabilidades de aparición de cada uno
                    pesos = [40, 25, 15, 10]
                    tipo_elegido = random.choices(tipos_disponibles, weights=pesos)[0]  # Recordar el [0] al final

                    if tipo_elegido in ['roca', 'arbusto'] and random.random() < 0.3:
                        cantidad = random.choice([1, 2])  # Grupos de 1 o 2 obstáculos
                        espacio = 30
                        for i in range(cantidad):
                            x_inicial = ANCHO + i * (80 + espacio)
                            obstaculos.append(Obstaculo(velocidad_juego, tipo_elegido, x_inicial))
                            frecuencia_obstaculo = 80 + (cantidad * 30)
                    else:
                        # Si es un ave o un obstáculo individual, lo añadimos directamente
                        obstaculos.append(Obstaculo(velocidad_juego, tipo_elegido, ANCHO))
                        frecuencia_obstaculo = 85

            for obstaculo in obstaculos[:]:
                obstaculo.actualizar()

                if leon.obtener_rect().colliderect(obstaculo.obtener_rect()):
                    game_over = True
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()

                    # --- CHEQUEO DE NUEVO RÉCORD ---
                    puntos_finales = int(puntuacion)
                    if puntos_finales > record_maximo:
                        record_maximo = puntos_finales
                        guardar_record(record_maximo)

                if obstaculo.x + obstaculo.ancho < 0:
                    obstaculos.remove(obstaculo)
                    puntuacion += 0.5

                # --- DIBUJAR JUEGO EN PANTALLA ---
            pantalla.fill(SABANA_FONDO)
            pantalla.blit(IMAGEN_FONDO, (fondo_x1, 0))
            pantalla.blit(IMAGEN_FONDO, (fondo_x2, 0))

            # Suelo
            pygame.draw.rect(pantalla, SUELO_COLOR, (0, ALTURA_SUELO, ANCHO, ALTO - ALTURA_SUELO))

            leon.dibujar(pantalla)
            for obstaculo in obstaculos:
                obstaculo.dibujar(pantalla)

            # Interfaz de puntos
            texto_puntos = fuente.render(f"DIAS DE GESTION: {int(puntuacion)}", True, TEXTO_COLOR)
            texto_record_vivo = fuente.render(f"RÉCORD: {record_maximo}", True, (50, 50, 50))

            pantalla.blit(texto_puntos, (10, 10))
            pantalla.blit(texto_record_vivo, (ANCHO - texto_record_vivo.get_width() - 10, 10))

            if game_over:
                texto_fin = fuente_grande.render("¡FIN DEL JUEGO!", True, (139, 0, 0))
                texto_reiniciar = fuente.render("Presiona ESPACIO para volver a rugir", True, TEXTO_COLOR)
                pantalla.blit(texto_fin, (ANCHO // 2 - 180, ALTO // 2 - 50))
                pantalla.blit(texto_reiniciar, (ANCHO // 2 - 180, ALTO // 2 + 10))

        pygame.display.flip()
        reloj.tick(FPS)
        await asyncio.sleep(0)
asyncio.run(main())

