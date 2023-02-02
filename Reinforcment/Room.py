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
class RoomEnv(Env):
    def __init__(self,FurnitureDimensions,DoorsDim , DoorsPos,WindowsDim,WindowsPos , keywords):
        # Actions we can up, down, right, left
        self.action_space = Discrete(4)
        # Room Dimensions
        self.observation_space = Box(low=0, high=100, shape=(1,2),dtype=np.int16)
        # Set start temp
        self.state = [random.randint(25, 75),random.randint(25, 75)]
        self.scale_factor = 4
        # add custom room dimentions in the future 
        self.screen_width=self.scale_factor*self.observation_space.high[0][0]
        self.screen_height=self.scale_factor*self.observation_space.high[0][0]

        # need to change the array from (door pos, door dim) to (door dim , (door 1 pos , door 2 pos , door 3 pos,etc))
        self.doors_pos = DoorsPos
        self.door_dimensions = tuple(self.scale_factor * elem for elem in DoorsDim)
        # same for windows 
        self.window_pos = WindowsPos
        self.window_dimensions = tuple(self.scale_factor * elem for elem in WindowsDim)

        self.furniture_dimensions=tuple(self.scale_factor * elem for elem in FurnitureDimensions)
        # need to calculate an array of distances not just 3 maybe like (furniture to center , furn to doors(furn to door1 ,etc), furn to windows (furn to window 1 , etc))
        self.entropy=self.CalculateDistances()
        self.text=[0,0,0]
        self.keywords= keywords
        self.colided = [False, False,False,False ]
        
        # Set shower length
        self.move_length = 100*len(keywords)
        self.screen = None
        self.clock = None
        self.isopen = True
        self.accumulator = 0
        self.past_state=[0,0]
        self.past_dist = 0
    def GetReward(self,keyword):
        self.isColliding()
        reward=int(self.entropy)/10
        if keyword == "bed":
            
            if self.colided.count(False)==3:
                print(self.colided)
                reward=int(self.entropy)/10 +100
            else:
                reward = -1
    
        return reward
    def CalculateDistances(self):
        totalDistance =0
        for DoorPosI in self.doors_pos:
            totalDistance+=int(math.dist(self.state, DoorPosI ))
        for WindowPosI in self.window_pos:
            totalDistance+=int(math.dist(self.state, WindowPosI ))

        totalDistance+=int(math.dist( [50,50], self.state ))
        return totalDistance
        
    def isColliding(self):
        
        # if(self.state[0]+FurnitureDimensions[0]==1 ):
        if(self.state[0]>=100 ):
          # go right
          self.colided[0]=True
         
        if(self.state[0]<=0 ):
          # go left
          self.colided[1]=True
        
        if(self.state[1]>=100):
          # go down
          self.colided[2]=True
          
        if(self.state[1]>0):
          # go up
          self.colided[3]=True
          
        

    def step(self, action):
        # Apply action

        #  need to adjust bounds to room dimensions dynamically

       
       
        if(action==0 and self.state[0]<100 ):
            self.state = np.add([1,0],self.state)
        elif(action==1 and self.colided[0] ):
            self.state = np.add([-1,0],self.state)
        elif(action==2 and self.state[1]<100):
            self.state = np.add([0,1],self.state)
        
        elif(action==3 and self.state[1]>0):
            self.state = np.add([0,-1],self.state)
             # Reduce move length by 1 second
        
        self.move_length -= 1 


        # need to calculate an array of distances not just 3 maybe like (furniture to center , furn to doors(furn to door1 ,etc), furn to windows (furn to window 1 , etc))
        self.entropy=self.CalculateDistances()
        #  a func  or a method to sum distances

        # Calculate reward
        if(self.past_dist<int(self.entropy)):
            reward= self.GetReward(self.keywords[0])
        else:
            reward= -1
            
        #         reward = int(math.dist(np.mean( np.array([ [50,50], self.door_pos ]), axis=0 ), self.state))
        #         if(self.past_state[0] ==self.state[0] and self.past_state[1] ==self.state[1]):
            
        #             reward= -1



        self.past_state =self.state

        self.past_dist=int(self.entropy)
        # Check if the moves are done
        if self.move_length <= 0: 
            done = True
        else:
            done = False

        # Apply temperature noise
        #self.state += random.randint(-1,1)
        # Set placeholder for info
        info = {}

        
        
        # Return step information
        return self.state, reward, done, info
    def render(self,mode):
        if self.screen is None:
            
            pygame.init()
            pygame.display.init()
            pygame.display.set_caption("Layout Optimization")
            font = pygame.font.Font(None, 20)
            self.text[0] = font.render(" window", True, (255, 255, 255))
            if(self.window_dimensions[1]>self.window_dimensions[0]):
                self.text[0]= pygame.transform.rotate(self.text[0], 90)
            self.text[1] = font.render(" Door", True, (255, 255, 255))
            if(self.door_dimensions[1]>self.door_dimensions[0]):
                self.text[1]= pygame.transform.rotate(self.text[1], 90)
            self.text[2] = font.render(self.keywords[0], True, (0, 0, 0))
            if(self.furniture_dimensions[1]>self.furniture_dimensions[0]):
                self.text[2]= pygame.transform.rotate(self.text[2], 90)

           
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        if self.clock is None:
            self.clock = pygame.time.Clock()



        if self.state is None:
            return None

        x = self.state
        
        self.screen.fill((143,0,255))
        
        
        # need to draw rects dynamically in a func 
        self.DrawElements()
#         pygame.event.pump()
        self.clock.tick(50)
        pygame.display.flip()
        
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                self.close()
  
    def DrawElements(self):
        
        # make for loop in the future for multibile furniture
        pygame.draw.rect(self.screen,(252, 198, 108),((self.state[0]*self.scale_factor-(self.furniture_dimensions[0]/2)),(self.state[1]*self.scale_factor-(self.furniture_dimensions[1]/2)),self.furniture_dimensions[0],self.furniture_dimensions[1])) 
        self.screen.blit(self.text[2], (self.state[0]*self.scale_factor, self.state[1]*self.scale_factor))
        
        for WindowPosI in self.window_pos:
            pygame.draw.rect(self.screen,(0,0,0),(WindowPosI[0]*self.scale_factor,WindowPosI[1]*self.scale_factor,self.window_dimensions[0],self.window_dimensions[1]))
            self.screen.blit(self.text[0], (WindowPosI[0]*self.scale_factor, WindowPosI[1]*self.scale_factor))

        
        for DoorPosI in self.doors_pos:
            pygame.draw.rect(self.screen,(0,0,0),(DoorPosI[0]*self.scale_factor,DoorPosI[1]*self.scale_factor,self.door_dimensions[0],self.door_dimensions[1]))
            
            self.screen.blit(self.text[1], (DoorPosI[0]*self.scale_factor, DoorPosI[1]*self.scale_factor))

    def close(self):
            
            pygame.display.quit()
            pygame.quit()
            self.isopen = False
            warnings.filterwarnings("ignore")
            sys.exit(0)

    def render2(self):
        print(self.state)
        grid = np.zeros((101, 101))
        grid = np.transpose(grid)
        
        
        grid[self.state[1]+50-1][self.state[0]+50-1]=1
        plt.figure(figsize = (10,10))
        gridx, gridy = grid.shape
        plt.ylim(0,100)
        # plt.xlim(-50,50)
        
        plt.imshow(grid)
        
    def render3(self):
        import numpy as np
        z=np.zeros((self.observation_space.high[0][0],self.observation_space.high[0][0]), dtype=int)
        for i in range(self.observation_space.high[0][0]):
            for j in range(self.observation_space.high[0][0]):
                z[i][j]=(int(math.dist( [50,50], [i,j] )))+(int(math.dist( self.doors_pos, [i,j] )))+(int(math.dist( self.window_pos, [i,j] )))
                
        for i in range(self.window_pos[0],self.window_pos[0]+15):
            for j in range(self.window_pos[1],self.window_pos[1]+2):
                z[i][j]=0
        for i in range(self.doors_pos[0],self.doors_pos[0]+2):
            for j in range(self.doors_pos[1],self.doors_pos[1]+10):
                z[i][j]=0
        for i in range(self.state[1]-2,min(self.state[1]+2,99)):
            for j in range(self.state[0]-5,min(self.state[0]+5,99)):
                z[i][j]=0
                
        
        import matplotlib.pyplot as plt
        

        

        plt.imshow(z, cmap='hot', interpolation='nearest')

        plt.title('2-D Heat Map in Room')
        plt.colorbar()
        plt.gca().invert_yaxis()
        plt.show()
    
    def reset(self):
        
        # Reset shower temperature
        # print("reset called")
        # print(self.state)
        self.state = [random.randint(25, 75),random.randint(25, 75)]
        # Reset shower time
        self.move_length = 100*len(self.keywords)
        return  self.state
    