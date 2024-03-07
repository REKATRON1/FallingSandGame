import pygame as pg
import numpy as np
import random
import colorsys

class sand():
	def __init__(self, _color, _spawn_time, _gravity):
		self.color = _color
		self.spawn_time = _spawn_time
		self.start_fall = _spawn_time
		self.falls = 0
		self.gravity = _gravity
		self.is_stable = False
	def update(self, fell):
		if fell:
			self.falls += 1
		else:
			self.falls = 0
			self.is_stable = True
	def initialize_fall(self, time):
		if self.falls == 0:
			self.start_fall = time
	def get_next_fall(self):
		return self.start_fall + sum([1000/(x*self.gravity) for x in range(1, self.falls+1)])
	def get_color(self, dynamic_colors, time, time_color_change):
		if dynamic_colors:
			c_seed = colorsys.rgb_to_hsv(self.color[0], self.color[1], self.color[2])[0]
			c_seed += (time-self.spawn_time)/time_color_change#-int((time-self.spawn_time)/time_color_change)
			c_seed = c_seed - int(c_seed)
			
			return (255*colorsys.hsv_to_rgb(c_seed,1,1)[0],255*colorsys.hsv_to_rgb(c_seed,1,1)[1],255*colorsys.hsv_to_rgb(c_seed,1,1)[2])
		return self.color

def __main__():
	pg.init()
	pg.font.init()
	main_font = pg.font.SysFont('Comic Sans MS', 20)
	
	screen_size = (1280, 720)
	main_screen = pg.display.set_mode(screen_size)
	screen_center = pg.Vector2(main_screen.get_width()/2, main_screen.get_height()/2)

	fps_clock = pg.time.Clock()
	tick_rate = 500
	delta_time = 0

	zoom_factor = 25

	sand_placing_size = 0
	sand_placing_chance = 1.0
	sand_removing_size = 1
	sand_grid = np.empty((int(screen_size[1]/zoom_factor), int(screen_size[0]/zoom_factor)), dtype=sand)
	stable_stack_heights = [0 for _ in range(int(screen_size[0]/zoom_factor))]
	has_gravity = True
	permanent_falldown = False
	single_update_mode = False
	gravity = 4
	rgb_mode = 1
	time_color_change = 6000
 
	running = True
	start_time = pg.time.get_ticks()
	last_check = start_time
	pressed, update_pressed, current_color, placed_positions = False, False, None, set()
	needs_fall_test = [False for _ in range(int(screen_size[0]/zoom_factor))]
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if pg.key.get_pressed()[pg.K_g]:
					has_gravity = not has_gravity
				elif pg.key.get_pressed()[pg.K_t]:
					permanent_falldown = not permanent_falldown
				elif pg.key.get_pressed()[pg.K_c]:
					single_update_mode = not single_update_mode
				elif pg.key.get_pressed()[pg.K_DELETE]:
					sand_grid = np.empty((int(screen_size[1]/zoom_factor), int(screen_size[0]/zoom_factor)), dtype=sand)
				elif pg.key.get_pressed()[pg.K_q]:
					sand_placing_size = min(sand_placing_size + 1, 10)
				elif pg.key.get_pressed()[pg.K_a]:
					sand_placing_size = max(sand_placing_size - 1, 0)
				elif pg.key.get_pressed()[pg.K_w]:
					gravity = min(gravity + 1, 15)
				elif pg.key.get_pressed()[pg.K_s]:
					gravity = max(gravity - 1, 1)
				elif pg.key.get_pressed()[pg.K_e]:
					sand_placing_chance = min(1.0, sand_placing_chance + 0.1)
				elif pg.key.get_pressed()[pg.K_d]:
					sand_placing_chance = max(0.0, sand_placing_chance - 0.1)
				elif pg.key.get_pressed()[pg.K_r]:
					sand_removing_size = min(sand_removing_size + 1, 12)
				elif pg.key.get_pressed()[pg.K_f]:
					sand_removing_size = max(sand_removing_size - 1, 0)
				elif pg.key.get_pressed()[pg.K_1]:
					rgb_mode = 0
				elif pg.key.get_pressed()[pg.K_2]:
					rgb_mode = 1
				elif pg.key.get_pressed()[pg.K_3]:
					rgb_mode = 2
				elif pg.key.get_pressed()[pg.K_UP]:
					zoom_factor = min(zoom_factor + 3, 50)
					sand_placing_size = 0
					sand_placing_chance = 1.0
					sand_removing_size = 0
					sand_grid = np.empty((int(screen_size[1]/zoom_factor), int(screen_size[0]/zoom_factor)), dtype=sand)
					stable_stack_heights = [0 for _ in range(int(screen_size[0]/zoom_factor))]
					has_gravity = True
					permanent_falldown = False
					single_update_mode = False
					gravity = 4
					rgb_mode = 0
					time_color_change = 6000
					start_time = pg.time.get_ticks()
					last_check = start_time
					pressed, update_pressed, current_color, placed_positions = False, False, None, set()
					needs_fall_test = [False for _ in range(int(screen_size[0]/zoom_factor))]
				elif pg.key.get_pressed()[pg.K_DOWN]:
					zoom_factor = max(zoom_factor - 3, 5)
					sand_placing_size = 0
					sand_placing_chance = 1.0
					sand_removing_size = 0
					sand_grid = np.empty((int(screen_size[1]/zoom_factor), int(screen_size[0]/zoom_factor)), dtype=sand)
					stable_stack_heights = [0 for _ in range(int(screen_size[0]/zoom_factor))]
					has_gravity = True
					permanent_falldown = False
					single_update_mode = False
					gravity = 4
					rgb_mode = 0
					time_color_change = 6000
					start_time = pg.time.get_ticks()
					last_check = start_time
					pressed, update_pressed, current_color, placed_positions = False, False, None, set()
					needs_fall_test = [False for _ in range(int(screen_size[0]/zoom_factor))]
		if  has_gravity and (not single_update_mode or (pg.key.get_pressed()[pg.K_SPACE] and not update_pressed)) and any(needs_fall_test) and (permanent_falldown or not pressed):
			update_pressed = True
			for x, column in enumerate(sand_grid.T):
				if not needs_fall_test[x]:
					continue
				needs_fall_test[x] = False
				stable_stack, stack_height, stack_height_updated = False, 0, False
				for y, _ in enumerate(column[::-1]):
					trueY = len(sand_grid) - y - 1
					s = sand_grid[trueY, x]
					if not s or not s.is_stable or stack_height > stable_stack_heights[max(0,x-1)] or stack_height > stable_stack_heights[min(x+1,len(stable_stack_heights)-1)]:
						stable_stack = False
						if not stack_height_updated:
							stable_stack_heights[x] = stack_height
						stack_height_updated = True
					if not s:
						continue
					if s.is_stable and not stack_height_updated:
						stack_height += 1
						stable_stack = True
					if y == 0:
						if s:
							s.is_stable = True
						continue
					if not stable_stack and s.get_next_fall() <= pg.time.get_ticks():
						fell = False
						if not sand_grid[trueY+1,x]:
							if s.falls > 0:
								sand_grid[trueY,x], sand_grid[trueY+1,x] = None, s
							else:
								s.initialize_fall(pg.time.get_ticks())
							fell = True
							if trueY != 0 and sand_grid[trueY-1,x]:
								sand_grid[trueY-1,x].is_stable=False
							needs_fall_test[x], needs_fall_test[max(0,x-1)], needs_fall_test[min(x+1, len(needs_fall_test)-1)] = True, True, True
						elif x != 0 and not sand_grid[trueY+1,x-1]:
							if s.falls > 0:
								sand_grid[trueY,x], sand_grid[trueY+1,x-1] = None, s
							else:
								s.initialize_fall(pg.time.get_ticks())
							fell = True
							if trueY != 0 and sand_grid[trueY-1,x]:
								sand_grid[trueY-1,x].is_stable=False
							needs_fall_test[x], needs_fall_test[max(0,x-1)], needs_fall_test[min(x+1, len(needs_fall_test)-1)] = True, True, True
						elif x + 1 != len(row) and not sand_grid[trueY+1,x+1]:
							if s.falls > 0:
								sand_grid[trueY,x], sand_grid[trueY+1,x+1] = None, s
							else:
								s.initialize_fall(pg.time.get_ticks())
							fell = True
							if trueY != 0 and sand_grid[trueY-1,x]:
								sand_grid[trueY-1,x].is_stable=False
							needs_fall_test[x], needs_fall_test[max(0,x-1)], needs_fall_test[min(x+1, len(needs_fall_test)-1)] = True, True, True
						s.update(fell)
					elif not stable_stack:
						needs_fall_test[x] = True
		elif not pg.key.get_pressed()[pg.K_SPACE]:
			update_pressed = False
		if any(list(pg.mouse.get_pressed(num_buttons=3))):
			if not pressed:
				pressed = True
				current_color = get_rangom_color()
				if not permanent_falldown:
					placed_positions = set()
			posX, posY = pg.mouse.get_pos()
			cX, cY = int(posX/zoom_factor), int(posY/zoom_factor)
			if pg.mouse.get_pressed(num_buttons=3)[0]:
				sand_size = sand_placing_size
			elif pg.mouse.get_pressed(num_buttons=3)[2]:
				sand_size = sand_removing_size
			else:
				sand_size = 0
			for x_offset in range(-sand_size,sand_size+1,1):
				for y_offset in range(-sand_size,sand_size+1,1):
					y,x = cY+y_offset, cX+x_offset
					y,x = max(0,min(len(sand_grid)-1,y)),max(0,min(len(sand_grid[0])-1,x))
					if pg.mouse.get_pressed(num_buttons=3)[0]:
						if (x, y) in placed_positions and not permanent_falldown:
							continue
						elif not permanent_falldown:
							placed_positions.add((x,y))
						if random.random() <= sand_placing_chance:
							if not sand_grid[y, x]:
								needs_fall_test[x], needs_fall_test[max(0,x-1)], needs_fall_test[min(x+1, len(needs_fall_test)-1)] = True, True, True
								if rgb_mode <= 0:
									sand_grid[y, x] = sand(current_color, pg.time.get_ticks(), gravity)
								elif rgb_mode >= 1:
									current_color = (pg.time.get_ticks()-start_time)/time_color_change-int((pg.time.get_ticks()-start_time)/time_color_change)
									sand_grid[y, x] = sand((255*colorsys.hsv_to_rgb(current_color,1,1)[0],255*colorsys.hsv_to_rgb(current_color,1,1)[1],255*colorsys.hsv_to_rgb(current_color,1,1)[2]), pg.time.get_ticks(), gravity)
					elif pg.mouse.get_pressed(num_buttons=3)[2]:
						if sand_grid[y, x]:
							sand_grid[y, x] = None
							needs_fall_test[x], needs_fall_test[max(0,x-1)], needs_fall_test[min(x+1, len(needs_fall_test)-1)] = True, True, True
		else:
			pressed = False
		
		main_screen.fill("black")

		for y, row in enumerate(sand_grid):
			for x, s in enumerate(row):
				if s:
					pg.draw.rect(main_screen, s.get_color((rgb_mode==2), pg.time.get_ticks(), time_color_change), pg.Rect((x*zoom_factor,y*zoom_factor), (zoom_factor,zoom_factor)))
		if pg.time.get_ticks() - 1000 > last_check:
			last_check = pg.time.get_ticks()
			#print(stable_stack_heights)
		
		text_surface = main_font.render('Zoom: ' + str(zoom_factor) + f"{'Up/Down': >20}", False, "white")
		main_screen.blit(text_surface, (0,0))
		text_surface = main_font.render('Color-Mode: ' + str(rgb_mode+1) + f"{'1/2/3': >11}", False, "white")
		main_screen.blit(text_surface, (0,20))
		text_surface = main_font.render('Paint-Size: ' + str(sand_placing_size*2+1) + f"{'q/a': >12}", False, "white")
		main_screen.blit(text_surface, (0,40))
		text_surface = main_font.render('Delete-Size: ' + str(sand_removing_size*2+1) + f"{'r/f': >9}", False, "white")
		main_screen.blit(text_surface, (0,60))
		text_surface = main_font.render('Paint-Chance: ' + str(np.round(sand_placing_chance,1)) + f"{'e/d': >5}", False, "white")
		main_screen.blit(text_surface, (0,80))

		text_surface = main_font.render('(Reset with Delete)', False, "white")
		main_screen.blit(text_surface, (0,100))

		text_surface = main_font.render('Gravity: ' + str('On' if has_gravity else 'Off') + f"{'g': >18}" , False, "white")
		main_screen.blit(text_surface, (0,140))
		text_surface = main_font.render('Gravity-Strength: ' + str(gravity) + f"{'w/s': >7}", False, "white")
		main_screen.blit(text_surface, (0,160))
		text_surface = main_font.render('Instant-Fall: ' + str('On' if permanent_falldown else 'Off') + f"{'t': >10}" , False, "white")
		main_screen.blit(text_surface, (0,180))
		text_surface = main_font.render('Auto-Update: ' + str('On' if single_update_mode else 'Off') + f"{'c': >8}" , False, "white")
		main_screen.blit(text_surface, (0,200))
		text_surface = main_font.render('(Update with Space)', False, "white")
		main_screen.blit(text_surface, (0,220))

		pg.display.flip()
		delta_time = fps_clock.tick(tick_rate) / 1000

def get_rangom_color():
	r = 255
	g_seed = random.random()
	g = 101*g_seed + 255*(1-g_seed)
	b_seed = random.random()
	b = 36*b_seed + 82*(1-b_seed)
	return pg.Color((r,g,b))

__main__()