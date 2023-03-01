from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
import random
import math
import sys
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *
import random
import warnings
from logging import exception
from gym import spaces


class RoomEnv(Env):
    def __init__(self, FurnitureDimensions, DoorsDim, DoorsPos, WindowsDim, WindowsPos, keywords, RoomDimension, Walls, offsetZ, offsetX, rotations):
        # Actions we can up, down, right, left
        self.action_space = Discrete(4)
        # Room Dimensions
        self.turn = 0
        self.RoomDimension = RoomDimension
        self.observation_space = np.zeros((1, 2))
        # Set start temp
        self.state3 = Walls[0]
        self.walls_dimensions = Walls[1]
        values = [random.randint(0, RoomDimension[0]),
                  random.randint(0, RoomDimension[1])]
        self.state2 = [[random.randint(int(RoomDimension[0]/4), int(RoomDimension[0]/2)), random.randint(
            int(RoomDimension[1]/4), int(RoomDimension[1]/2))] for _ in range(len(keywords))]
        self.state = self.state2[self.turn]
        self.FurnitureQueue = 1
        self.scale_factor = 1
        # add custom room dimentions in the future
        self.screen_width = self.scale_factor*self.RoomDimension[0]
        self.screen_height = self.scale_factor*self.RoomDimension[1]
        self.color = [(252, 198, 108) for elem in keywords]
        # need to change the array from (door pos, door dim) to (door dim , (door 1 pos , door 2 pos , door 3 pos,etc))
        self.doors_pos = DoorsPos
        self.door_dimensions = tuple(
            self.scale_factor * elem for elem in DoorsDim)
        # same for windows
        self.window_pos = WindowsPos
        self.window_dimensions = tuple(
            self.scale_factor * elem for elem in WindowsDim)
        self.rotations = rotations
        self.real_furniture_dimensions = [
            [num for num in sub_list] for sub_list in FurnitureDimensions]
        self.furniture_dimensions = [
            [self.scale_factor * num for num in sub_list] for sub_list in FurnitureDimensions]
        # need to calculate an array of distances not just 3 maybe like (furniture to center , furn to doors(furn to door1 ,etc), furn to windows (furn to window 1 , etc))
        self.entropy = [0, 0]
        self.text = [0, 0]
        self.Furnituretext = [0 for elm in keywords]
        self.lastdistance = 1000000
        self.keywords = keywords
        self.colided = [False, False, False, False]
        self.colided2 = [False, False, False, False]
        self.move = False
        self.offsetZ = offsetZ
        self.offsetX = offsetX
        self.human_block=30
        # Set shower length
        self.move_length = 10000*len(keywords)
        self.screen = None
        self.clock = None
        self.isopen = False
        self.accumulator = 0
        self.maxReward = np.zeros((len(keywords)))
        self.BestStates = [[random.randint(0, RoomDimension[0]), random.randint(
            0, RoomDimension[1])] for _ in range(len(keywords))]
        self.past_dist = np.zeros((len(keywords), 2))

    def check_door_in_axis(self, state, door_pos, door_dimensions, scale_factor):
        if (state[0] < door_pos[0]+(door_dimensions[0]/(scale_factor*2)) and state[0] > door_pos[0]-(door_dimensions[0]/(scale_factor*2))) or (state[1] < door_pos[1]+(door_dimensions[1]/(scale_factor*2)) and state[1] > door_pos[1]-(door_dimensions[1]/(scale_factor*2))):
            return True

        return False

    def GetReward(self, keyword, Furniturepos, dimensions):
        self.colided = self.isColliding(Furniturepos, dimensions)
        self.check_furniture_collision(Furniturepos, dimensions, self.turn)
        reward = int(self.entropy)
        if keyword == "bed":
            if self.colided.count(False) == 3:
                self.color[self.turn] = (0, 255, 0)
                reward = reward+100
                self.color[self.turn] = (0, 0, 255)
            for door_pos in self.doors_pos:
                if (self.check_door_in_axis(Furniturepos, door_pos, self.door_dimensions, self.scale_factor)):
                    reward = -1
                    self.color[self.turn] = (255, 0, 0)
            for KW in range(len(self.keywords)):
                if self.turn > KW:
                    if KW == self.turn:

                        continue
                    if self.keywords[KW] == "bed":
                        for KW2 in range(len(self.keywords)):
                            # need to dynamically align beds
                            if self.keywords[KW2] == "Storage":
                                distance = math.pow(int(math.dist(Furniturepos, (self.state2[KW][0]-(self.real_furniture_dimensions[KW][0]+max(self.real_furniture_dimensions[KW2])+3), self.state2[KW][1]))), 2)
                                break
                            else:
                                distance = math.pow(int(math.dist(Furniturepos, (self.state2[KW][0]-(self.real_furniture_dimensions[KW][0]+self.human_block), self.state2[KW][1]))), 2)
                        if distance >= self.lastdistance:
                            reward = -10

                        else:
                            reward = reward + (5000 / (distance + 1))

                        self.lastdistance = distance

                        self.color[self.turn] = (255, 0, 0)

        return reward

    def policyShaping(self, action, keyword, Furniturepos):

        if keyword == "Storage":
            BedsCount = []
            for KW in range(len(self.keywords)):
                if self.turn > KW:
                    if KW == self.turn:

                        continue
                    if self.keywords[KW] == "bed":
                        BedsCount.append(KW)
                if len(BedsCount) == 2 and not self.move:

                    avg = [(self.state2[BedsCount[0]][0]+self.state2[BedsCount[1]][0])/2,
                           ((self.state2[BedsCount[0]][1]+self.state2[BedsCount[1]][1])/2)]

                    self.state = avg
                    self.move = True
                    self.color[self.turn] = (255, 0, 0)
                if self.move:
                    action = 2
        # this part is only to help the desk and other furnuture in the future to not get stuck
        if keyword == "desk":
            if self.colided2[0] and not (self.colided[2] or self.colided[3]):
                action = 1
         # -------------------------------------------------------------------------------------
        # Chairs
        if keyword == "chair":

            for KW in range(len(self.keywords)):
                if KW == self.turn:
                    continue
                if self.keywords[KW] == "desk":

                    point = (self.state2[KW][0], self.state2[KW]
                             [1]-(self.real_furniture_dimensions[KW][1]))

                    self.state = point
        return action

    def CalculateDistances(self, Furniturepos):

        totalDistance = 0
        for DoorPosI in self.doors_pos:
            totalDistance += int(math.dist(Furniturepos, DoorPosI))
        for WindowPosI in self.window_pos:
            totalDistance += int(math.dist(Furniturepos, WindowPosI))

        totalDistance += int(math.dist([self.door_dimensions[0]/2,
                             self.door_dimensions[1]/2], Furniturepos))
        return totalDistance

    def isColliding(self, Furniturepos, dimensions):
        tempCollison = self.colided
        # if(self.state[0]+FurnitureDimensions[0]==1 ):
        if (Furniturepos[0]+(dimensions[0]/2) >= self.RoomDimension[0]):
            # don't go right
            tempCollison[0] = True

        if (Furniturepos[0]-(dimensions[0]/2) <= 0):
            # don't go left
            tempCollison[1] = True

        if (Furniturepos[1]+(dimensions[1]/2) >= self.RoomDimension[1]):
            # don't go down
            tempCollison[2] = True

        if (Furniturepos[1]-(dimensions[1]/2) <= 0):
            # don't go up
            tempCollison[3] = True

        return tempCollison

    def nextPlease(self):
        self.FurnitureQueue += 1
        self.turn = (self.turn+1) % len(self.keywords)

    def check_furniture_collision(self, furniture_pos, furniture_dimensions, ignore_index=None):
        for i, pos in enumerate(self.state2[:self.FurnitureQueue]):
            if ignore_index is not None and i == ignore_index:
                continue

            other_furniture_dimensions = self.real_furniture_dimensions[i]
            other_furniture_pos = self.state2[i]

            x1, y1 = furniture_pos
            x2, y2 = other_furniture_pos
            w1, h1 = furniture_dimensions
            w2, h2 = other_furniture_dimensions

            # Check if the two pieces of furniture overlap
            if (abs(x1 - x2) * 2 < (w1 + w2)) and (abs(y1 - y2) * 2 < (h1 + h2)):
                # The two pieces of furniture are colliding

                # Check which side of the furniture is colliding
                left_collision = (x1 + w1/2 > x2 - w2 /
                                  2) and (x1 + w1/2 < x2 + w2/2)
                right_collision = (x1 - w1/2 < x2 + w2 /
                                   2) and (x1 - w1/2 > x2 - w2/2)
                bottom_collision = (y1 - h1/2 < y2 + h2 /
                                    2) and (y1 - h1/2 > y2 - h2/2)
                top_collision = (y1 + h1/2 > y2 - h2 /
                                 2) and (y1 + h1/2 < y2 + h2/2)

                self.colided2[0] = left_collision
                self.colided2[1] = right_collision
                self.colided2[2] = top_collision
                self.colided2[3] = bottom_collision

        # If no collision is detected, return None
        return None

    def step(self, action):
        # Apply action

        #  need to adjust bounds to room dimensions dynamically

        self.state = self.state2[self.turn]
        self.move_length -= 1

        # need to calculate an array of distances not just 3 maybe like (furniture to center , furn to doors(furn to door1 ,etc), furn to windows (furn to window 1 , etc))
        self.entropy = self.CalculateDistances(self.state)
        #  a func  or a method to sum distances
        reward = self.GetReward(
            self.keywords[self.turn], self.state, self.real_furniture_dimensions[self.turn])
        action = self.policyShaping(
            action, self.keywords[self.turn], self.state)
        # Calculate reward
        # if( self.past_dist[self.turn]<self.entropy[self.turn]):

        #     reward= -1

        #         reward = int(math.dist(np.mean( np.array([ [50,50], self.door_pos ]), axis=0 ), self.state))
        #         if(self.past_state[0] ==self.state[0] and self.past_state[1] ==self.state[1]):

        #             reward= -1

        if (action == 0 and not self.colided[0] and not self.colided2[0]):
            self.state = np.add([1, 0], self.state)
        elif (action == 1 and not self.colided[1] and not self.colided2[1]):
            self.state = np.add([-1, 0], self.state)
        elif (action == 2 and not self.colided[2] and not self.colided2[2]):
            self.state = np.add([0, 1], self.state)

        elif (action == 3 and not self.colided[3] and not self.colided2[3]):
            self.state = np.add([0, -1], self.state)

            # Reduce move length by 1 second

        if self.maxReward[self.turn] < reward:
            self.maxReward[self.turn] = reward
            self.BestStates[self.turn] = self.state

        self.past_dist = int(self.entropy)
        # Check if the moves are done
        if self.move_length <= 0:
            done = True
        else:
            done = False

        # Apply temperature noise
        # self.state += random.randint(-1,1)
        # Set placeholder for info
        info = {}

        # print(self.colided)
        self.colided[0] = False
        self.colided[1] = False
        self.colided[2] = False
        self.colided[3] = False
        self.colided2[0] = False
        self.colided2[1] = False
        self.colided2[2] = False
        self.colided2[3] = False
        self.state2[self.turn] = self.state

        # Return step information

        return self.state, reward, done, info

    def render(self, mode):
        if not self.isopen:
            self.isopen = True
            pygame.init()
            pygame.display.init()
            pygame.display.set_caption("Layout Optimization")
            font = pygame.font.Font(None, 20)
            self.text[0] = font.render(" window", True, (255, 255, 255))
            if (self.window_dimensions[1] > self.window_dimensions[0]):
                self.text[0] = pygame.transform.rotate(self.text[0], 90)
            self.text[1] = font.render(" Door", True, (255, 255, 255))
            if (self.door_dimensions[1] > self.door_dimensions[0]):
                self.text[1] = pygame.transform.rotate(self.text[1], 90)
            for i in range(len(self.keywords)):

                self.Furnituretext[i] = font.render(
                    self.keywords[i], True, (0, 0, 0))
                if (self.furniture_dimensions[i][1] > self.furniture_dimensions[i][0]):
                    self.Furnituretext[i] = pygame.transform.rotate(
                        self.Furnituretext[i], 90)

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        if self.clock is None:
            self.clock = pygame.time.Clock()

        if self.state is None:
            return None

        x = self.state

        self.screen.fill((143, 0, 255))
        self.clock.tick(200)
        # need to draw rects dynamically in a func
        self.DrawElements()
        self.color[self.turn] = (252, 198, 108)
#         pygame.event.pump()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

    def DrawElements(self):

        # for i in range(len(self.state3)):
        #     print(self.walls_dimensions[i][1])
        #     if(self.rotations[i]):
        #         pygame.draw.rect(self.screen,(0,0,0),(((self.state3[i][0]+self.RoomDimension[0]*self.scale_factor/2)*self.scale_factor-(self.walls_dimensions[i][0]/2)),((self.state3[i][1]+self.RoomDimension[1]*self.scale_factor/2)*self.scale_factor-(self.walls_dimensions[i][1]/2)),self.walls_dimensions[i][0],5))
        #         switch=False
        #     else:
        #         pygame.draw.rect(self.screen,(0,0,0),(((self.state3[i][0]+self.RoomDimension[0]*self.scale_factor/2)*self.scale_factor-(self.walls_dimensions[i][0]/2)),((self.state3[i][1]+self.RoomDimension[1]*self.scale_factor/2)*self.scale_factor-(self.walls_dimensions[i][1]/2)),5,self.walls_dimensions[i][0]))
        #         switch=True

        # for i in range(len(self.keywords)):
        #     pygame.draw.rect(self.screen,(0, 50, 0),((self.BestStates[i][0]*self.scale_factor-(self.furniture_dimensions[i][0]/2)),(self.BestStates[i][1]*self.scale_factor-(self.furniture_dimensions[i][1]/2)),self.furniture_dimensions[i][0],self.furniture_dimensions[i][1]))
        #     self.screen.blit(self.Furnituretext[i], (self.BestStates[i][0]*self.scale_factor, self.BestStates[i][1]*self.scale_factor))

        for i in range(len(self.keywords)):
            pygame.draw.rect(self.screen, self.color[i], ((self.state2[i][0]*self.scale_factor-(self.furniture_dimensions[i][0]/2)), (
                self.state2[i][1]*self.scale_factor-(self.furniture_dimensions[i][1]/2)), self.furniture_dimensions[i][0], self.furniture_dimensions[i][1]))
            self.screen.blit(self.Furnituretext[i], (
                self.state2[i][0]*self.scale_factor, self.state2[i][1]*self.scale_factor))

        for WindowPosI in self.window_pos:
            pygame.draw.rect(self.screen, (0, 0, 0), (WindowPosI[0]*self.scale_factor, WindowPosI[1]
                             * self.scale_factor, self.window_dimensions[0], self.window_dimensions[1]))
            self.screen.blit(
                self.text[0], (WindowPosI[0]*self.scale_factor, WindowPosI[1]*self.scale_factor))

        for DoorPosI in self.doors_pos:
            pygame.draw.rect(self.screen, (0, 0, 0), (DoorPosI[0]*self.scale_factor, DoorPosI[1]
                             * self.scale_factor, self.door_dimensions[0], self.door_dimensions[1]))

            self.screen.blit(
                self.text[1], (DoorPosI[0]*self.scale_factor, DoorPosI[1]*self.scale_factor))

    def close(self):

        self.isopen = False

    def render3(self):

        import numpy as np
        z = np.zeros((100, 100), dtype=int)
        for i in range(100):
            for j in range(100):
                z[i][j] = (int(math.dist([50, 50], [i, j])))+(int(math.dist(
                    self.doors_pos[0], [i, j])))+(int(math.dist(self.window_pos[0], [i, j])))

        for i in range(self.window_pos[0][0], self.window_pos[0][0]+15):
            for j in range(self.window_pos[0][1], self.window_pos[0][1]+2):
                z[i][j] = 0
        for i in range(self.doors_pos[0][0], self.doors_pos[0][0]+2):
            for j in range(self.doors_pos[0][1], self.doors_pos[0][1]+10):
                z[i][j] = 0
        for i in range(self.state[1]-2, min(self.state[1]+2, 99)):
            for j in range(self.state[0]-5, min(self.state[0]+5, 99)):
                z[i][j] = 0

        import matplotlib.pyplot as plt

        plt.imshow(z, cmap='hot', interpolation='nearest')

        plt.title('2-D Heat Map in Room')
        plt.colorbar()
        plt.gca().invert_yaxis()
        plt.show()

    def reset(self):

        # Reset shower time
        self.move_length = 10000*len(self.keywords)
        return self.state
