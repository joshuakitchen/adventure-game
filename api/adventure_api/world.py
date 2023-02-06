from typing import ClassVar, List


class Cell:
  
  def __init__(self):
    pass

class World:
  _loaded_cells: ClassVar[List[Cell]]
  
  @classmethod
  def get_cell(cls):
    return 'test'

World._loaded_cells = []
