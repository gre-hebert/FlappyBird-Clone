import pygame
import os
import random

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.mixer.init()
pygame.font.init()
FONTE_PONTOS = pygame.font.Font('fonts/Grand9K Pixel.ttf', 35)
FONTE_EXIT = pygame.font.Font('fonts/Grand9K Pixel.ttf', 15)
jumpsfx = pygame.mixer.Sound('sfx/jump.wav')

# Música de fundo
pygame.mixer.music.load('music/bgmusic.wav')
pygame.mixer.music.play(-1)

class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 2
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -5
        self.tempo = 1
        self.altura = self.y
        jumpsfx.play()

    def mover(self):
        # calcular o deslocamento
        self.tempo += .35
        deslocamento = .75 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 7.5:
            deslocamento = 7.5
        elif deslocamento < 0:
            deslocamento -= 1

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0:
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo += self.VELOCIDADE_ROTACAO*5
        else:
            if self.angulo > -60:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -10:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 210
    VELOCIDADE = 3.5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 3.5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaro, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)
    Exit = FONTE_EXIT.render('[ESC] SAIR', 1, (216, 247, 215))
    Space = FONTE_EXIT.render('[SPACE] FLY', 1, (216, 247, 215))
    texto = FONTE_PONTOS.render(f'Pontuação: {pontos}', 1, (216, 247, 215))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    tela.blit(Exit, (0, 0))
    chao.desenhar(tela)
    tela.blit(Space, (0, TELA_ALTURA - Space.get_height()))
    pygame.display.update()


def main():
    passaro = Passaro(230, 350)
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    relogio_velocidade = 60
    DESENVOLVEDOR = False

    while True:
        relogio.tick(relogio_velocidade)

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    passaro.pular()
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if DESENVOLVEDOR:
                    if evento.key == pygame.K_LEFT:
                        if relogio_velocidade < 11:
                            relogio_velocidade = 1
                        else:
                            relogio_velocidade -= 10
                    if evento.key == pygame.K_RIGHT:
                        relogio_velocidade += 10
                    if evento.key == pygame.K_DOWN:
                        if relogio_velocidade == 1:
                            relogio_velocidade = 1
                        else:
                            relogio_velocidade -= 1
                    if evento.key == pygame.K_UP:
                        relogio_velocidade += 10
                    
        # mover as coisas
        passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            if cano.colidir(passaro):
                main()
            if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        if (passaro.y + passaro.imagem.get_height()) > chao.y:
                main()
        if passaro.y < 0:
            passaro.y = 0


        desenhar_tela(tela, passaro, canos, chao, pontos)


if __name__ == '__main__':
    main()
