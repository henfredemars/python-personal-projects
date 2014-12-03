#!/usr/bin/python3

#Simple benchmark task: solve puzzles with backtracking algorithm

class Sudoku:

  def __init__(self,grid):
    self.grid = grid
    self.rowSets = [set() for i in range(9)]
    self.colSets = [set() for i in range(9)]
    self.blockSets = [[set(),set(),set()],[set(),set(),set()],[set(),set(),set()]]
    for m in range(9):
      for n in range(9):
        if self.grid[m][n]:
          self.rowSets[m].add(self.grid[m][n])
          self.colSets[n].add(self.grid[m][n])
          self.blockSets[m//3][n//3].add(self.grid[m][n])
    self.attemptGrid = [[{1,2,3,4,5,6,7,8,9} for _ in range(9)] for _ in range(9)]
    self.visited = []

  def canPlace(self,number,m,n):
    if not number in self.rowSets[m]:
      if not number in self.colSets[n]:
        if not number in self.blockSets[m//3][n//3]:
          return True
    return False

  def place(self,number,m,n):
    self.grid[m][n] = number
    self.rowSets[m].add(number)
    self.colSets[n].add(number)
    self.blockSets[m//3][n//3].add(number)

  def solvePoint(self,m,n):
    for guess in self.attemptGrid[m][n]:
      if self.canPlace(guess,m,n):
        self.place(guess,m,n)
        self.visited.append((m,n))
        self.attemptGrid[m][n].remove(guess)
        return True
    return False

  def solve(self):
    m = 0
    n = 0
    while True:
      if not self.grid[m][n]:
        if self.solvePoint(m,n):
          m += 1
          if m > 8:
            m = 0
            n += 1
          if n > 8:
            return self.grid
        else:
          self.attemptGrid[m][n] = {1,2,3,4,5,6,7,8,9}
          (oldm,oldn) = self.visited.pop()
          oldNumber = self.grid[oldm][oldn]
          self.grid[oldm][oldn] = 0
          self.rowSets[oldm].remove(oldNumber)
          self.colSets[oldn].remove(oldNumber)
          self.blockSets[oldm//3][oldn//3].remove(oldNumber)
          m,n = oldm,oldn
      else:
        m += 1
        if m > 8:
          m = 0
          n += 1
        if n > 8:
          return self.grid

def prettyPrint(grid):
  for row in grid:
    print(row)

def makePuzzles():
  for i in range(9):
    for m in range(9):
      for n in range(9):
        grid = [[0 for _ in range(9)] for _ in range(9)]
        grid[m][n] = i
        yield grid

def sum2d(list1,list2):
  result = [[0 for _ in range(9)] for _ in range(9)]
  for i in range(9):
    for j in range(9):
      result[i][j] = list1[i][j]+list2[i][j]
  return result

if __name__=='__main__':
  result = [[0 for _ in range(9)] for _ in range(9)]
  for grid in makePuzzles():
    puzzle = Sudoku(grid)
    result = sum2d(result,puzzle.solve())
  prettyPrint(result) #Dont let test get optimized away
