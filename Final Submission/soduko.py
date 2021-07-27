import numpy as np
import sys
import random

puzzle_initial = np.loadtxt(sys.argv[1], int) # soduko puzzle to solve
puzzle_initial_row_column = puzzle_initial.flatten()
n_gen = int(sys.argv[2]) # number of generations

# convert row-column order of puzzle to 3x3 subgrids from left->right and top->bottom
puzzle = []
sub_start = [0,3,6,27,30,33,54,57,60]
for start in sub_start:
    subGrid = []
    for i in range(3):
        for j in range(3):
            subGrid.append(puzzle_initial_row_column[start + 9*i + j])
    puzzle.append(subGrid)

# helper functions to get soduko rows and columns from chromosome
def getRow(solution, index):
    row = []
    start = 0
    if (0 <= index <= 2):
        start = 0
    if (3 <= index <= 5):
        start = 3
    if (6 <= index <= 8):
        start = 6

    for block in range(3):
        for element in range(3):
            row.append(solution[start+block][((index-start)*3)+element])

    return row

def getCol(solution, index):
    col = []
    start = 0
    if (0 <= index <= 2):
        start = 0
    if (3 <= index <= 5):
        start = 1
    if (6 <= index <= 8):
        start = 2

    for block in range(3):
        for element in range(3):
            col.append(solution[start+(block*3)][(index-(3*start)) + (element*3)])

    return col

# fitness function
def fitness(solution):
    score = 0
    # rows
    for i in range(9):
        row = getRow(solution,i)
        col = getCol(solution,i)
        for digit in range(1,10):
            count_row = row.count(digit)
            if (count_row == 0):
                score += 1
            else:
                score += (count_row - 1)

            count_col = col.count(digit)
            if (count_col == 0):
                score += 1
            else:
                score += (count_col - 1)

    return score

# generate initial population
population_count = 11
population = []
for entity in range(population_count):
    p = []
    for i in range(9):
        # randomly shuffled list of missing digits in sub-grid
        pick_from = []
        for digit in range(1,10):
            if digit not in puzzle[i]:
                pick_from.append(digit)
        random.shuffle(pick_from)

        block = []
        pick_count = 0
        for j in range(9):
            if (puzzle[i][j] == 0):
                block.append(pick_from[pick_count])
                pick_count += 1
            else:
                block.append(puzzle[i][j])
        p.append(block)

    population.append(p)

# helper function to get row-column coordinates from chromosome coordinates
def getRowColCoordinates(grid, index):
    # row
    if (0 <= index <= 2):
        radd = 0
    if (3 <= index <= 5):
        radd = 1
    if (6 <= index <= 8):
        radd = 2

    if (0 <= grid <= 2):
        rstart = 0
    if (3 <= grid <= 5):
        rstart = 3
    if (6 <= grid <= 8):
        rstart = 6
    row = rstart + radd

    # col
    col = ((grid%3)*3) + (index%3)

    return [row,col]

# helper functions for crossover and mutation
def mutation(solution):
    mutated = solution[:]
    for grid in range(9):
        num_mutations = random.randint(1, 5)
        for mutate in range(num_mutations):
            gene1 = random.randint(0,8)
            gene2 = random.randint(0,8)
            # check if not givens
            if (puzzle[grid][gene1] != 0):
                break
            if (puzzle[grid][gene2] != 0):
                break
            # check if digits occur 0-3 times after swap
            row_col_gene1 = getRowColCoordinates(grid, gene1)
            row_col_gene2 = getRowColCoordinates(grid, gene2)
            row_gene1 = getRow(mutated, row_col_gene1[0])
            col_gene1 = getCol(mutated, row_col_gene1[1])
            row_gene2 = getRow(mutated, row_col_gene2[0])
            col_gene2 = getCol(mutated, row_col_gene2[1])
            swap_count = row_gene1.count(mutated[grid][gene2]) + col_gene1.count(mutated[grid][gene2]) + row_gene2.count(mutated[grid][gene1]) + col_gene2.count(mutated[grid][gene1])
            if (swap_count <= 3):
                temp = mutated[grid][gene2]
                mutated[grid][gene2] = mutated[grid][gene1]
                mutated[grid][gene1] = temp
            # else:
            #     break

    return mutated

def crossover(solution1, solution2):
    child1 = []
    child2 = []
    crossover_points = []
    for i in range(5):
        crossover_points.append(random.randint(0,8))
    for grid in range(9):
        if (grid in crossover_points):
            child1.append(solution1[grid])
            child2.append(solution2[grid])
        else:
            child2.append(solution1[grid])
            child1.append(solution2[grid])

    return [child1, child2]

avg_fitness = []
min_fitness = []
# genetic algorithm
for generation in range(n_gen):
    # sort population by fitness
    fitness_list = []
    for p in population:
        fitness_list.append(fitness(p))

    print("Generation: ", generation)

    points = zip(fitness_list, population)
    sorted_points = sorted(points)
    fitness_sorted = [point[0] for point in sorted_points]
    population = [point[1] for point in sorted_points]

    # average + min fitness
    current_average_fitness = sum(fitness_sorted)/len(fitness_sorted)
    avg_fitness.append(current_average_fitness)
    min_fitness.append(fitness_sorted[0])
    print("Average fitness - ", current_average_fitness)
    print("Min fitness - ", fitness_sorted[0])

    # elitism parent picking
    children = []
    # deep copy of population
    copy_population = []
    for p in population:
        copy_population_element = []
        for block in range(9):
            element = (p[block])[:]
            copy_population_element.append(element)
        copy_population.append(copy_population_element)

    for mating in range(population_count-1, 0, -1):
        # parents
        parent1 = copy_population[random.randint(0, mating)]
        parent2 = copy_population[random.randint(0, mating)]
        # mating crossover
        offspring = crossover(parent1, parent2)
        # mutation
        child1 = mutation(offspring[0])
        child2 = mutation(offspring[1])
        # add
        children.append(child1)
        children.append(child2)

    # join parents and children to form new population
    joined_population = population + children

    # sort new population by fitness
    fitness_list = []
    for p in joined_population:
        fitness_list.append(fitness(p))

    points = zip(fitness_list, joined_population)
    sorted_points = sorted(points)
    fitness_sorted = [point[0] for point in sorted_points]
    joined_population_sorted = [point[1] for point in sorted_points]

    for i in range(population_count):
        population[i] = joined_population_sorted[i]

    # solution found
    if (fitness_sorted[0] == 0):
        break

final_fitness = []
for i in range(population_count):
    final_fitness.append(fitness_sorted[i])

print("Generation: ", n_gen, " (final)")
current_average_fitness = sum(final_fitness)/len(final_fitness)
avg_fitness.append(current_average_fitness)
min_fitness.append(final_fitness[0])
print("Average fitness - ", current_average_fitness)
print("Min fitness - ", final_fitness[0])
print("Final solution:")
print(population[0])

# output to text files
np.savetxt("Average_fitness.txt", np.array(avg_fitness))
np.savetxt("Min_fitness.txt", np.array(min_fitness), fmt='%i')
np.savetxt("Final_solution.txt", np.array(population[0]), fmt='%i')
