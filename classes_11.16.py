
import random
import numpy as np
import pygame

WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 초기값
NUM_PREDATORS = 5
NUM_PREY = 30
PREDATOR_SIZE = 15
PREY_SIZE = 10
SIMULATION_DURATION = -1

# 상호작용에 관여하는 상수들
PREDATOR_SPEED = 8
PREY_SPEED = 5
MAX_TIME_WITHOUT_FOOD = 6
REPRODUCTION_COOLDOWN = 3
CHASING_RANGE = 100
RUNNING_AWAY_RANGE = 80
extra_time = random.random()
EXTRA_TIME = random.uniform(0, 3)


class Predator:
    # 초깃값: 랜덤 생성 위치, 먹이 없이 생존 가능 시간 = 0, 가장 최근 복제 후 지난 시간 = 0, 시뮬레이션 시작시 이동방향 랜덤, 피식자 쫓기 = None
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.time_without_food = 0
        self.last_reproduction_time = 0
        self.direction = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
        self.direction /= np.linalg.norm(self.direction)
        self.chasing_prey = None
    # 포식자 움직임
    def move(self):

        # 화면 경계와 닿았는지 확인
        if self.x - PREDATOR_SIZE < 0:
            self.direction[0] *= -1
            self.x = PREDATOR_SIZE
        if self.x + PREDATOR_SIZE >= WIDTH:
            # 방향 바꾸기
            self.direction[0] *= -1
            self.x = WIDTH - PREDATOR_SIZE

        if self.y - PREDATOR_SIZE < 0:
            self.direction[1] *= -1
            self.y = PREDATOR_SIZE

        if self.y + PREDATOR_SIZE >= HEIGHT:
            self.direction[1] *= -1
            self.y = HEIGHT - PREDATOR_SIZE

        # 이동 방향 랜덤으로 바꾸기
        if random.random() < 0.01:
            self.direction = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
            # 방향 설정에 필요한 단위 벡터 구하기
            self.direction /= np.linalg.norm(self.direction)

        self.x += self.direction[0] * PREDATOR_SPEED
        self.y += self.direction[1] * PREDATOR_SPEED

    # 포식자가 피식자 먹으면 100% 확률로 복제
    def can_reproduce(self, current_time):
        return current_time - self.last_reproduction_time >= REPRODUCTION_COOLDOWN

    # 포식자 그리기
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), PREDATOR_SIZE)

# 피식자 클래스
class Prey:
    # 초깃값: 랜덤 생성 위치, 시뮬레이션 시작시 이동방향 랜덤, 랜덤 시간 안에 복제, 가장 최근 복제 후 지난 시간 = 0, 현재 시간 = 0
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.direction = ([random.uniform(-1, 1), random.uniform(-1, 1)])
        constant_of_direction_vector = (1/(self.direction[0]**2+self.direction[1]**2))**(1/2)
        self.direction = [self.direction[0]*constant_of_direction_vector, self.direction[1]*constant_of_direction_vector]
        self.reproduction_delay = random.uniform(8, 20)
        self.last_reproduction_time = 0
        self.distance = 0
        self.is_live = 0
        self.speed = PREY_SPEED #PREY_SPEED는 속도의 기본 초기값


    # 피식자 움직이기
    def move(self, predators):

        # 범위 안에 포식자가 있는지 확인
        for predator in predators:
            prey_to_predator_vector = np.array([predator.x - self.x, predator.y - self.y])
            distance = np.linalg.norm(prey_to_predator_vector)

            # 시야 범위 안에 있는지 확인
            if distance < RUNNING_AWAY_RANGE:


                # 포식자로부터 도망치기
                opposite_direction = -prey_to_predator_vector
                self.direction = opposite_direction
                constant_of_direction_vector = (1 / (self.direction[0] ** 2 + self.direction[1] ** 2)) ** (1 / 2)
                self.direction = [self.direction[0] * constant_of_direction_vector,
                                  self.direction[1] * constant_of_direction_vector]
                self.x += self.direction[0] * self.speed
                self.y += self.direction[1] * self.speed
                return

        # 시야 안에 포식자가 없다면 평소처럼 움직이기

        # 화면 경계와 닿았는지 확인
        if self.x - PREY_SIZE < 0:
            self.direction[0] *= -1
            self.x = PREY_SIZE
        if self.x + PREY_SIZE >= WIDTH:
            # 방향 바꾸기
            self.direction[0] *= -1
            self.x = WIDTH-PREY_SIZE

        if self.y - PREY_SIZE < 0:
            self.direction[1] *= -1
            self.y = PREY_SIZE

        if self.y + PREY_SIZE >= HEIGHT:
            self.direction[1] *= -1
            self.y = HEIGHT - PREY_SIZE

        # 이동방향 랜덤으로 바꾸기
        if random.random() < 0.1:
            self.direction = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
            # 방향 설정에 필요한 단위 벡터 구하기
            self.direction /= np.linalg.norm(self.direction)


        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed



    # 피식자 그리기
    def draw(self,screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), PREY_SIZE)

    # 피식자 복제하기
    def can_reproduce(self, current_time):
        if current_time - self.last_reproduction_time >= self.reproduction_delay:
            return True
        return False
