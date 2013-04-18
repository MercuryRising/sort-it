import sys, pygame
import time
import random

'''
Sort it
A game where you see how quickly you sort a list, getting better and better sorting tools as you complete levels
'''

pygame.init()
scale = 8
size = width, height = 96*scale, 64*scale

# Define the colors that we'll use
# Black is the background, grey1 is the color of grabbed bars
# grey2 is the normal color of the bars, and white is the current selection
black = 10, 10, 10
grey1 = 200, 200, 200
grey2 = 127, 127, 127
white = 255, 255, 255

screen = pygame.display.set_mode(size)

# Number of rectangles, this will add difficulty (and tedium), but given
# more "power ups" or better ways of sorting (like selecting more than one element to shift)
# it could be fun to modify on the fly
num_rectangles = 15
rect_width = 4

# Offset for the display surface
width_offset = 40
height_offset = 40

sort_surface_width = width-width_offset
sort_surface_height = height-height_offset
sort_surface = pygame.Surface((width-width_offset, height-height_offset))
sort_surface.fill((0,0,0))

# This font doesn't look that nice
# This needs to be changed for the calculator spirit.
myfont = pygame.font.SysFont("monospace", 15)

'''
Gameplay variables
'''

# Selected rectangle grabs the index of different rectangles and is 
# used to color them, and for pressing space to grab them
selected_rect = 0
grabbed_rect = -1

sorting_complete = False

# When the first move is made, we use this to start the timer
started = False

# Time elapsed
total_time = 0

# Spacing for printing
print_offset = 10

# This is the same as the score
swaps = 0

# Bubble sort swaps every one to move
# Another way would be to pick one, pick another one, then sort them directly (jump sort)
# Another way would be merge sort where you could select more than one rectangle at a time
game_mode = "bubble"


def populate_rectangles():
	'''
	Creates rectangles evenly spaced from the rectangle grid.

	There's something wrong with creating them though, as sometimes 0 height
	rectangles are created
	'''
	# Grab the spots for the X positions of the rectangles
	rectangle_grid = [rect_width + 4*rect_width*x for x in range(num_rectangles)]

	rectangles = []
	for index, x in enumerate(rectangle_grid):
		# Grab a random height for a rectangle
		# This would be better if it was a coarser range, as rectangles with 1 px diff are hard to tell
		rect_height = random.randint(20, height-5)

		rect = pygame.Rect(x, height-rect_height, rect_width, rect_height)
		rectangles.append(rect) 
	return rectangles

def check_sorted():
	'''
	This function checks if the list of rectangles is sorted
	It doesn't do this in a good way. If there are two rectangles of the same height,
	it does not say that the list is sorted (these elements should be reversible, but they're
		not at the moment)

	The sorting_complete variable tells the game we're done and displays the "SORTED COMPLETE"
	'''
	global rects, game_time, sorting_complete

	# As our data structure sucks right now, sorting by the x's and sorting by the heights can
	# lead to two differences when sorting by rectangle x's and rectangle heights
	# If any two rectangles are the same height, sorting by their X might switch them,
	# and then they won't be 'sorted', when in actuality they are
	if sorted(rects, key=lambda rect: rect.x) == sorted(rects, key=lambda rect: rect.height):
		if not sorting_complete:			
			# Grab total game time and say sorting is complete
			game_time = time.time()-game_start
			sorting_complete = True
	else:
		sorting_complete = False

def swap_rects(indX, indY):
	'''
	Swaps two rectangles from the list of rectangles.

	Consider changing the data structure so the X values of the rectangles is their index
	(with some sort of scale between them), it would make it a lot simpler

	This function also keeps a tally on the score (number of rectangle swaps that have been done)
	'''
	global rects, swaps
	if indX != indY:

		# Swap indices in list of rects, and swap X values for two rects of interest
		r1 = rects[indX]
		r2 = rects[indY]
		r1.x, r2.x = r2.x, r1.x
		rects[indX], rects[indY] = rects[indY], rects[indX]
		swaps += 1

	check_sorted()

def assert_selection(selected_rect):
	# A helper function to make sure the selected_rectangle is in the bounds of our list
	if selected_rect > num_rectangles-1:
		selected_rect = num_rectangles-1
	elif selected_rect < 0:
		selected_rect = 0
	return selected_rect

def handle_selection_change(event):
	'''
	Handle selection changes dependent on keyboard input
	Currently the only keys we respond to here are left, right, and spacebar

	This function houses the movement logic, that isn't well documented and was
	haphazardly put together through trial and error.

	I don't know if this function should house the movement logic if we add more
	game types (like adding a merge sort where I can select more than one rectangle)
	'''
	global selected_rect, grabbed_rect

	if event.key == 276:
		# Go left
		if game_mode == "bubble" and grabbed_rect >= 0:
			current = grabbed_rect
			selected_rect = assert_selection(selected_rect-1)
			swap_rects(current, selected_rect)
			grabbed_rect = selected_rect
		else:
			selected_rect = assert_selection(selected_rect-1)

	elif event.key == 275:
		# go right
		if game_mode == "bubble" and grabbed_rect >= 0:
			current = grabbed_rect
			selected_rect = assert_selection(selected_rect+1)
			swap_rects(current, selected_rect)
			grabbed_rect = selected_rect
		else:
			selected_rect = assert_selection(selected_rect+1)
	if event.key == 32:
		# Handle space bar press
		if game_mode == "bubble" and grabbed_rect < 0:
			grabbed_rect = selected_rect
		elif game_mode == "bubble" and grabbed_rect >= 0:
			selected_rect = grabbed_rect
			grabbed_rect = -1
	print selected_rect, grabbed_rect

def humanize_time(time_delta):
	'''
	Make the timer look nice

	Returns a formatted string that has Time: MM:SS.X in it (x being MS)

	'''
	minutes = time_delta/60
	seconds = time_delta%60
	seconds = round(seconds, 1)
	if seconds < 10:
		seconds = "0%s"%round(seconds, 1)
	return "Time: %2d:%s" %(minutes, seconds)

def play_again():
	'''
	Reset the counters to play the game again.
	'''
	global rects, sorting_complete, started, score, game_time, grabbed_rect, selected_rect
	rects = populate_rectangles()
	started = False
	sorting_complete = False
	selected_rect = 0
	grabbed_rect = -1
	swaps = 0
	game_time = 0
	screen.fill(black)
	sort_surface.fill((25, 25, 25))
	pygame.display.flip()


# Grab the list of rectangles we'll use
rects = populate_rectangles()

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			sys.exit()

		if event.type == pygame.KEYDOWN:
			# Do something special with control and or shift
			if event.key == 306:
				modifier_key = True

			if event.key in [276, 275, 32]:
				# Call the handle_selection function to take care of left, right, space presses
				handle_selection_change(event)
				# Handle starting the game on the first left/right/space press
				if not started:
					started = True
					game_start = time.time()

			# Restart the game
			if event.unicode == "p":
				play_again()

			# Use r to repopulate the rectangles (if you get a crappy list of them)
			if event.unicode == "r":
				rects = populate_rectangles()

		# This function never worked, so the modifier would get stuck
		if event.type == pygame.KEYUP:
			if event.key == 306:
				modifier_key = False


	# Redraw
	screen.fill(black)
	sort_surface.fill(black)

	# Draw in the rectangles all the same color
	[pygame.draw.rect(sort_surface, grey2, rect, 5) for rect in rects]

	# Draw the selected rectangle as being white
	pygame.draw.rect(sort_surface, white, rects[selected_rect], 5)

	# If we grabbed one (pressed space on a rectangle) draw it in as light gray
	if grabbed_rect >= 0:
		pygame.draw.rect(sort_surface, grey1, rects[grabbed_rect], 5)

	# Display a counter for the time
	if started and not sorting_complete:
		label = myfont.render("Score: %s   %s" %(swaps, humanize_time(time.time()-game_start)), 1, white)
		screen.blit(label, (0, 0))

	# Or else print a bunch of stuff
	elif started and sorting_complete:
		label = myfont.render("Score: %s   %s" %(swaps, humanize_time(game_time)), 1, white)
		screen.blit(label, (0, 0))
		label = myfont.render("SORTED!", 1, white)
		sort_surface.blit(label, (sort_surface_width/2-print_offset, 50))
		label = myfont.render("%s" %(humanize_time(game_time)), 1, white)
		sort_surface.blit(label, (sort_surface_width/2-print_offset, 70))
		label = myfont.render("Score:  %2d" %(swaps), 1, white)
		sort_surface.blit(label, (sort_surface_width/2-print_offset, 90))
		label = myfont.render("press p to play again", 1, white)
		sort_surface.blit(label, (sort_surface_width/2-print_offset, 110))

	# Add our sort surface onto the background
	screen.blit(sort_surface, (width_offset/2, height_offset-5))
	# Display
	pygame.display.flip()