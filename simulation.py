import matplotlib.pyplot as plt
from characters import *

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
PREDATOR_SPEED = 6
PREY_SPEED = 3
MAX_TIME_WITHOUT_FOOD = 1.5
REPRODUCTION_COOLDOWN = 5
CHASING_RANGE = 100
extra_time = random.random()
EXTRA_TIME = random.uniform(0, 3)

class Simulation:
    def __init__(self):
        # 초기화 코드 작성
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Predator-Prey Simulation")

        # 데이터 저장을 위한 리스트 초기화
        self.time_steps = []
        self.prey_population = []
        self.predator_population = []
        self.average_preys_speeds = []

        self.half_time_steps = []
        self.half_prey_population = []
        self.half_predator_population = []
        self.average_preys_speeds_every_half_second = []

    def update_population_data(self, current_time, prey_count, predator_count, preys):
        # 인구 데이터 업데이트 코드 작성
        self.time_steps.append(current_time)
        self.prey_population.append(prey_count)
        self.predator_population.append(predator_count)
        prey_speeds = [i.speed for i in preys]
        self.average_preys_speeds.append(sum(prey_speeds) / len(prey_speeds) if len(prey_speeds) > 0 else 0)

    def update_half_population_data(self, population_measure_time, prey_count, predator_count, preys):
        # 반 시간마다 인구 데이터 업데이트 코드 작성
        self.half_time_steps.append(population_measure_time)
        self.half_prey_population.append(prey_count)
        self.half_predator_population.append(predator_count)
        prey_speeds = [i.speed for i in preys]
        self.average_preys_speeds_every_half_second.append(
            sum(prey_speeds) / len(prey_speeds) if len(prey_speeds) > 0 else 0)

    def update_and_display_live_graph(self):
        # 실시간 그래프 업데이트 및 디스플레이 코드 작성
        plt.clf()

        # 개체수 변화 그래프
        plt.subplot(2, 1, 1)
        plt.plot(self.time_steps, self.prey_population, label='Prey', color='green')
        plt.plot(self.time_steps, self.predator_population, label='Predator', color='red')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Population')
        plt.title('Predator-Prey Population Over Time')
        plt.legend()
        plt.grid(True)

        # 평균 속도 변화 그래프
        plt.subplot(2, 1, 2)
        plt.scatter(self.time_steps, self.average_preys_speeds, color='blue', label='Average Prey Speed')

        plt.xlabel('Time (seconds)')
        plt.ylabel('Average Prey Speed')
        plt.legend()
        plt.grid(True)

        plt.pause(0.001)
        plt.draw()

    def scatter(self):
        # scatter 그래프 작성 코드 작성
        plt.subplot(3, 1, 3)
        data = self.average_preys_speeds_every_half_second[20:]
        print("data:",data)
        t = range(len(data))
        print("t:",t)
        plt.plot(t, data, color='purple', label='average speed')
        plt.xlabel('Time (half a second)')
        plt.ylabel('Average Speed')
        plt.legend()
        plt.grid(True)
        plt.scatter(t, data)

    def run_simulation(self, FPS):
        predators = [Predator() for _ in range(NUM_PREDATORS)]
        preys = [Prey() for _ in range(NUM_PREY)]

        running = True

        plt.ion()
        # 시간 표시
        while running:
            start_time = pygame.time.get_ticks() / 1000

            # 스크린 설정
            self.screen.fill(WHITE)
            current_time = pygame.time.get_ticks() / 1000
            population_measure_time = pygame.time.get_ticks() / 2000
            for predator in predators:
                predator.time_without_food = current_time - predator.last_reproduction_time

            # 매 초 피식자 평균 속도 append
            if int(current_time) > len(self.average_preys_speeds_every_half_second):
                prey_speeds = [i.speed for i in preys]
                if len(prey_speeds):
                    average_speed = sum(prey_speeds) / len(prey_speeds)
                    self.average_preys_speeds_every_half_second.append(average_speed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # 추가, 삭제할 피식자, 포식자 리스트 생성
            preys_to_remove = []
            predators_to_remove = []
            preys_to_append = []
            predators_to_append = []

            timer_2 = 0

            for idx, predator in enumerate(predators):
                predator.move()
                predator.draw(self.screen)

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
                    timer_2 += 1
                    prey = predator.chasing_prey
                    predator.direction = np.array([prey.x - predator.x, prey.y - predator.y])
                    predator.direction /= np.linalg.norm(predator.direction)
                    distance = np.linalg.norm(np.array([predator.x - prey.x, predator.y - prey.y]))

                    if timer_2 >= 3:
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
                    print("KILL", idx)
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
                prey.draw(self.screen)
                if prey.can_reproduce(current_time):
                    new_prey = Prey()
                    new_prey.x = prey.x
                    new_prey.y = prey.y
                    # 이동방향 랜덤 설정
                    new_prey.direction = np.array([random.uniform(-1, 1), random.uniform(-1, 1)])
                    constant_of_direction_vector = (1 / (new_prey.direction[0] ** 2 + new_prey.direction[1] ** 2)) ** (
                            1 / 2)
                    new_prey.direction = [new_prey.direction[0] * constant_of_direction_vector,
                                          new_prey.direction[1] * constant_of_direction_vector]

                    # 피식자 돌연변이 속도 변화
                    speed_multiplier = random.uniform(0.5, 1.5)
                    new_prey_speed = PREY_SPEED * speed_multiplier

                    new_prey.speed = new_prey_speed

                    preys_to_append.append(new_prey)
                    prey.last_reproduction_time = current_time
                    new_prey.last_reproduction_time = current_time  # EXTRA_TIME 더해서 그래프 선형으로 만들기

            # 추가할 피식자 리스트에 있는 피식자 추가
            for i in preys_to_append:
                preys.append(i)
            # 60초 지나면 시뮬레이션 중지
            current_time = pygame.time.get_ticks() / 1000
            if int(start_time) >= 30:
                running = False

            # 그래프 업데이트
            self.update_population_data(current_time, len(preys), len(predators), preys)
            self.update_and_display_live_graph()
            # self.scatter()

            pygame.display.flip()
            self.clock.tick(FPS)
            if int(start_time) >= 30:
                print(self.average_preys_speeds_every_half_second)

        plt.ioff()
        plt.show()

        pygame.quit()