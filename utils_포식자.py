from classes import *
import pygame
import random
import numpy as np
import matplotlib.pyplot as plt

# 파이 게임
pygame.init()

# 게임 화면 설정
WIDTH, HEIGHT = 1000, 1000
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 스크린 설정
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Predator-Prey Simulation")

clock = pygame.time.Clock()

# 리스트 설정
prey_population = []
predator_population = []
time_steps = []
time_steps_for_predators_av_spd = []
average_predators_speeds = []



average_predators_speeds_every_second = []


def update_population_data(current_time, prey_count, predator_count, predators):
    time_steps.append(current_time)
    prey_population.append(prey_count)
    predator_population.append(predator_count)
    predator_speeds = [i.speed for i in predators]

    if len(predator_speeds):
        average_predators_speeds.append(sum(predator_speeds) / len(predator_speeds))
    else:
        average_predators_speeds.append(0)


# 실시간 그래프 보이기
def update_and_display_live_graph():
    plt.clf()

    # 개체수 변화 그래프
    plt.subplot(2, 1, 1)
    plt.plot(time_steps, prey_population, label='Prey', color='green')
    plt.plot(time_steps, predator_population, label='Predator', color='red')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Population')
    plt.title('Predator-Prey Population Over Time')
    plt.legend()
    plt.grid(True)

    # 평균 속도 변화 그래프
    plt.subplot(2, 1, 2)
    plt.plot(time_steps_for_predators_av_spd, average_predators_speeds_every_second, color='blue', label='Average Predator Speed')

    plt.xlabel('Time (seconds)')
    plt.ylabel('Average Predator Speed')
    plt.legend()
    plt.grid(True)

    plt.pause(0.001)
    plt.draw()

def run_simulation(FPS):
    FPS = 120
    # 시작 시간 설정
    start_time = 0
    cnt = 0

    # 포식자, 피식자 리스트로 정리하기
    predators = [Predator() for _ in range(NUM_PREDATORS)]
    preys = [Prey() for _ in range(NUM_PREY)]

    running = True

    # 파이게임 시작
    start_time = pygame.time.get_ticks()

    # matplotlib에서 실시간 데이터 그래프에 반영
    plt.ion()
    # 시간 표시
    while running:
        start_time = pygame.time.get_ticks() / 1000

        # 스크린 설정
        screen.fill(WHITE)
        current_time = pygame.time.get_ticks() / 1000
        for predator in predators:
            predator.time_without_food = current_time - predator.last_reproduction_time

        # 매 초 피식자 평균 속도 append
        if int(current_time) > len(average_predators_speeds_every_second):
            predator_speeds = [i.speed for i in predators]
            if len(predator_speeds):
                average_speed = sum(predator_speeds) / len(predator_speeds)
                average_predators_speeds_every_second.append(average_speed)
                cnt += 1
                time_steps_for_predators_av_spd.append(cnt)
                print(time_steps_for_predators_av_spd)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 추가, 삭제할 피식자, 포식자 리스트 생성
        preys_to_remove = []
        predators_to_remove = []
        preys_to_append = []
        predators_to_append = []

        timer = 0

        for idx, predator in enumerate(predators):
            # 먹이 섭취 안 할시 1초당 먹이 섭취 안 한 시간 1초씩 추가
            # 포식자 화면에 생성하고 움직이기
            predator.move()
            predator.draw(screen)

            # 포식자가 피식자를 쫓지 않을 때
            if predator.chasing_prey is None:
                for prey in preys:
                    # 포식자와 피식자 사이 거리
                    distance = np.linalg.norm(np.array([predator.x - prey.x, predator.y - prey.y]))
                    # 사냥 가능 범위 밖이면 쫓아가지 않기
                    if distance < CHASING_RANGE:
                        predator.chasing_prey = prey
                        break

            # 사냥 가능 범위 안이면 쫓아가기
            else:
                timer += 1
                prey = predator.chasing_prey
                predator.direction = np.array([prey.x - predator.x, prey.y - predator.y])
                predator.direction /= np.linalg.norm(predator.direction)
                distance = np.linalg.norm(np.array([predator.x - prey.x, predator.y - prey.y]))

                if timer >= 3:
                    predator.chasing_prey = None

                # 포식자가 피식자와 접촉했을 때(=피시자와 포식자의 사이즈를 더한 것이 둘 사이의 거리보다 작을 때)
                if distance < PREDATOR_SIZE + PREY_SIZE:
                    if predator.can_reproduce(current_time):
                        # 새로운 포식자 클래스 설정
                        new_predator = Predator()
                        new_predator.x = predator.x
                        new_predator.y = predator.y
                        predator.last_reproduction_time = current_time
                        new_predator.last_reproduction_time = current_time

                        # 피식자 돌연변이 속도 변화
                        speed_multiplier = random.uniform(0.5, 1.5)
                        new_predator_speed = PREDATOR_SPEED * speed_multiplier

                        new_predator.speed = new_predator_speed
                        # print(new_predator_speed)

                        # 새로운 포식자 추가할 포식자 리스트에 추가
                        predators_to_append.append(new_predator)
                        # 먹이를 먹은 포식자의 복제 쿨타임 초기화
                        predator.last_reproduction_time = current_time
                        new_predator.last_reproduction_time = current_time



                    # 포식자와 접촉한 피식자 삭제할 피식자 리스트에 추가
                    preys_to_remove.append(prey)
                    # 다시 피식자 쫓는 포식자 = 0
                    predator.chasing_prey = None
                    # 포식자 먹이 없이 생존한 시간 초기화
                    predator.time_without_food = 0
            # 포식자가 일정 시간동안 포식자 사냥 실패시 삭제할 포식자 리스트에 추가
            if predator.time_without_food >= MAX_TIME_WITHOUT_FOOD:
                predators_to_remove.append(idx)

        # 제거할 피식자 리스트에 있는 피식자 제거
        for prey in preys_to_remove:
            if prey in preys:
                preys.remove(prey)

        gap = 0

        # 반복문으로 제거할 리스트에 있는 포식자 모두 삭제
        for idx in predators_to_remove:
            del predators[idx - gap]
            gap += 1
        # 추가할 포식자 리스트에 있는 포식자 추가
        for predator in predators_to_append:
            predators.append(predator)

        # 새로운 피식자 돌연변이 정하기(속도 변화)
        for prey in preys:
            # print(prey.direction)
            prey.move(predators)
            prey.draw(screen)
            if prey.can_reproduce(current_time):
                new_prey = Prey()
                new_prey.x = prey.x
                new_prey.y = prey.y
                # 이동방향 랜덤 설정
                new_prey.direction = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
                constant_of_direction_vector = (1 / (new_prey.direction[0] ** 2 + new_prey.direction[1] ** 2)) ** (1 / 2)
                new_prey.direction = [new_prey.direction[0] * constant_of_direction_vector,
                                      new_prey.direction[1] * constant_of_direction_vector]

                preys_to_append.append(new_prey)
                prey.last_reproduction_time = current_time
                new_prey.last_reproduction_time = current_time

        # 추가할 피식자 리스트에 있는 피식자 추가
        for i in preys_to_append:
            preys.append(i)
        # 60초 지나면 시뮬레이션 중지
        current_time = pygame.time.get_ticks() / 1000
        if int(start_time) >= 60:
            running = False

        # 그래프 업데이트
        update_population_data(current_time, len(preys), len(predators), preys)
        update_and_display_live_graph()


        pygame.display.flip()
        clock.tick(FPS)
        if int(start_time) >= 5:
            print(average_predators_speeds_every_second)


    plt.ioff()
    plt.show()

    pygame.quit()
