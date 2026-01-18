import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from PIL import Image

# Settings
GRID_SIZE = 50
NUM_wolf = 20
NUM_rabbit = 20
Hunting_skill_average = 0.8
food_counter_wolf = 2 #amount of food that wolf needs to eat to make new wolf (and to be alive)
food_counter_rabbit = 8 #amount of food that rabbit needs to eat to make new rabbit (and to be alive)
FEAR_RADIUS = 3
HUNT_RADIUS = 5

RABBIT_FOOD_PROB = 0.35     # rabbit gains +1 food with this chance each step
WOLF_STARVE_LIMIT = 38      # wolf dies if no food for this many steps

HOME_WOLF_RADIUS = 6   # how close counts as "at home"
PACK_RADIUS = 1        # how close wolves must be to reproduce 

wolf_img = Image.new('RGB', (1, 1), color = 'red') # 1x1 pixel red square
rabbit_img = Image.new('RGB', (1, 1), color = 'blue') # 1x1 pixel blue square

class Agent:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class home_rabbit(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
#    def check(self, rabbit):
# needs to check if there is two rabbits in home, if it is true no more rabbits allowed
class home_wolf(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
#    def check(self, rabbit):
# shood be bigger then one space to be able to take all the wolfs
class wolf(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = np.clip(np.random.normal(Hunting_skill_average, 0.1), 0.1, 0.9)
        self.food_counter = 0
        self.starve_counter = 0  # steps since last meal
        
    def move(self, rabbits, wolf_cells, home_wolf_location, width, height):
        hx, hy = home_wolf_location[0].x, home_wolf_location[0].y
        self.starve_counter += 1
        
        # Manhattan distance to home (good for "zone" check)
        dist_home = abs(self.x - hx) + abs(self.y - hy)

        # If full enough -> go home and stay around home zone
        if self.food_counter >= food_counter_wolf:
            if dist_home > HOME_WOLF_RADIUS:
                # move one step toward home
                dx = hx - self.x
                dy = hy - self.y
                move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                nx = (self.x + move_x) % width
                ny = (self.y + move_y) % height
            else:
                # inside home zone: wander but stay inside zone
                nx = (self.x + random.choice([-1, 0, 1])) % width
                ny = (self.y + random.choice([-1, 0, 1])) % height
                new_dist = abs(nx - hx) + abs(ny - hy)
                if new_dist > HOME_WOLF_RADIUS:
                    nx, ny = self.x, self.y
        else:        
            # Otherwise hunt
            nearby = []
            for r in rabbits:
                dist = np.sqrt((self.x - r.x)**2 + (self.y - r.y)**2)
                if dist <= HUNT_RADIUS:
                    nearby.append(r)

            if nearby:
                avg_x = sum(r.x for r in nearby) / len(nearby)
                avg_y = sum(r.y for r in nearby) / len(nearby)
                dx = avg_x - self.x
                dy = avg_y - self.y
                move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                nx = (self.x + move_x) % width
                ny = (self.y + move_y) % height
            else:
                nx = (self.x + random.choice([-1, 0, 1])) % width
                ny = (self.y + random.choice([-1, 0, 1])) % height

        # block wolf–wolf overlap
        if (nx, ny) not in wolf_cells:
            wolf_cells.discard((self.x, self.y))
            self.x, self.y = nx, ny
            wolf_cells.add((self.x, self.y))


            
class rabbit(Agent):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.food_counter = 0
        self.home_x = None
        self.home_y = None

    
    def move(self, wolfs, rabbit_cells, width, height):
        # Food Counter
        if random.random() < RABBIT_FOOD_PROB: 
            self.food_counter += 1
        #scan for nearby wolfs
        nearby = []
        for w in wolfs:
            dist = np.sqrt((self.x - w.x)**2 + (self.y - w.y)**2)
            if dist <= FEAR_RADIUS:
                nearby.append(w)
        # if there is wolfs nearby run home
        if nearby and self.home_x is not None:
            dx = self.home_x - self.x
            dy = self.home_y - self.y
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0
            nx = (self.x + move_x) % width
            ny = (self.y + move_y) % height
        else:
            nx = (self.x + random.choice([-1, 0, 1])) % width
            ny = (self.y + random.choice([-1, 0, 1])) % height

        # Try to move, but avoid landing on another rabbit
        if (nx, ny) not in rabbit_cells:
            rabbit_cells.discard((self.x, self.y))
            self.x, self.y = nx, ny
            rabbit_cells.add((self.x, self.y))




#The location and spawn setup  
center_x = GRID_SIZE // 2
center_y = GRID_SIZE // 2
#spawn near a point within radius
def spawn_near(cx, cy, radius=4):
    x = cx + random.randint(-radius, radius)
    y = cy + random.randint(-radius, radius)
    # keep inside grid
    x = max(0, min(GRID_SIZE - 1, x))
    y = max(0, min(GRID_SIZE - 1, y))
    return x, y
#spawn far from wolf home 
def spawn_far_from(cx, cy, min_dist=10):
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if abs(x - cx) + abs(y - cy) >= min_dist:   # manhattan distance
            return x, y
        
#Wolves spawn around wolf home      
home_wolf_location = [home_wolf(center_x, center_y)]
wolfs = []
for _ in range(NUM_wolf):
    x, y = spawn_near(center_x, center_y, radius=5)
    wolfs.append(wolf(x, y))

#Rabbit homes spawn away from wolf home and rabbits spawn around rabbit homes
NUM_RABBIT_HOMES = NUM_rabbit // 2
homes_rabbit = []
for _ in range(NUM_RABBIT_HOMES):
    hx, hy = spawn_far_from(center_x, center_y, min_dist=12)
    homes_rabbit.append(home_rabbit(hx, hy))
rabbits = []
base = NUM_rabbit // NUM_RABBIT_HOMES
extra = NUM_rabbit % NUM_RABBIT_HOMES
#Spawn rabbits evenly
for idx, h in enumerate(homes_rabbit):
    count = base + (1 if idx < extra else 0)
    for _ in range(count):
        x, y = spawn_near(h.x, h.y, radius=4)
        rb = rabbit(x, y)
        rb.home_x, rb.home_y = h.x, h.y
        rabbits.append(rb)



def update(frame):
    global wolfs, rabbits, homes_rabbit, home_wolf_location
    
    #Needed for avoiding overlaps
    rabbit_cells = set((r.x, r.y) for r in rabbits)
    wolf_cells = set((w.x, w.y) for w in wolfs)
    home_cells = set((h.x, h.y) for h in homes_rabbit)


    # Movement
    for r in rabbits :
        r.move(wolfs, rabbit_cells, GRID_SIZE, GRID_SIZE)
    for w in wolfs:
        w.move(rabbits,wolf_cells, home_wolf_location, GRID_SIZE, GRID_SIZE)
        
    # Interaction 
    eaten = set()
    
    for w in wolfs:
        for i, r in enumerate(rabbits):
            if w.x == r.x and w.y == r.y:
                if (r.x, r.y) in home_cells:
                    continue
                eaten.add(i)
                w.food_counter += 1
                w.starve_counter = 0
                break
    
    if eaten:
        rabbits = [r for i, r in enumerate(rabbits) if i not in eaten]
        
    #Reproduction
    newborn_rabbits = []
    for r in rabbits:
        if r.food_counter >= food_counter_rabbit:
            r.food_counter -= food_counter_rabbit
            h = random.choice(homes_rabbit)
            bx, by = spawn_near(h.x, h.y, radius=3)
            baby = rabbit(bx, by)
            baby.home_x, baby.home_y = h.x, h.y
            newborn_rabbits.append(baby)
    rabbits.extend(newborn_rabbits)
    
    # Wolves reproduce near home when two FULL wolves are neighbors
    hx, hy = home_wolf_location[0].x, home_wolf_location[0].y
    newborn_wolves = []
    used = set()

    for i in range(len(wolfs)):
        if i in used:
            continue
        w1 = wolfs[i]

        # must be full and in home zone
        if w1.food_counter < food_counter_wolf:
            continue
        if abs(w1.x - hx) + abs(w1.y - hy) > HOME_WOLF_RADIUS:
            continue

        # find partner
        for j in range(i + 1, len(wolfs)):
            if j in used:
                continue
            w2 = wolfs[j]

            if w2.food_counter < food_counter_wolf:
                    continue
            if abs(w2.x - hx) + abs(w2.y - hy) > HOME_WOLF_RADIUS:
                continue

            # meet = neighbor 
            if abs(w1.x - w2.x) + abs(w1.y - w2.y) <= PACK_RADIUS:
                # parents spend food to reproduce
                w1.food_counter -= food_counter_wolf
                w2.food_counter -= food_counter_wolf

                bx, by = spawn_near(hx, hy, radius=3)
                newborn_wolves.append(wolf(bx, by))

                used.add(i)
                used.add(j)
                break

    wolfs.extend(newborn_wolves)     
    
    #starvation for wolfs
    wolfs = [w for w in wolfs if w.starve_counter < WOLF_STARVE_LIMIT]
    
    # Visualization update needed to be done !!!

