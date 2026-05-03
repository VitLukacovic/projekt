import csv
import heapq
import random
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional, Dict

COLOR_WALL: Tuple[int, int, int] = (0, 0, 0)
COLOR_PATH: Tuple[int, int, int] = (255, 255, 255)
COLOR_ROUTE: Tuple[int, int, int] = (255, 0, 0)


class Maze:
    """
    Třída reprezentující bludiště a operace pro hledání cesty a generování.
    """

    def __init__(self, grid: Optional[np.ndarray] = None) -> None:
        """
        Inicializuje instanci bludiště.
        """
        self.grid: Optional[np.ndarray] = grid
        self.shortest_path: List[Tuple[int, int]] = []
        
        self._incidence_matrix: Optional[np.ndarray] = None
        self._id_to_node: Dict[int, Tuple[int, int]] = {}
        self._node_to_id: Dict[Tuple[int, int], int] = {}

    @property
    def size(self) -> int:
        """
        Vrací velikost hrany bludiště (n). Pokud mřížka neexistuje, vrací 0.
        """
        if self.grid is None:
            return 0
        return self.grid.shape[0]

    @classmethod
    def from_csv(cls, file_path: str) -> 'Maze':
        """
        Načte bludiště z CSV souboru.
        """
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    parsed_row = [unit == '1' for unit in row]
                    data.append(parsed_row)
            return cls(np.array(data, dtype=bool))
        except FileNotFoundError:
            print(f"Soubor {file_path} nebyl nalezen.")
            return cls(None)

    def _build_incidence_matrix(self) -> None:
        """
        Sestaví incidenční matici pro aktuální stav bludiště.
        """
        if self.grid is None:
            return

        passable_cells = [
            (r, c) for r in range(self.size) for c in range(self.size) 
            if not self.grid[r, c]
        ]
        
        self._node_to_id = {node: i for i, node in enumerate(passable_cells)}
        self._id_to_node = {i: node for i, node in enumerate(passable_cells)}
        
        edges = []
        for r, c in passable_cells:
            for dr, dc in [(0, 1), (1, 0)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in self._node_to_id:
                    edges.append((self._node_to_id[(r, c)], self._node_to_id[(nr, nc)]))
                    
        num_nodes = len(passable_cells)
        num_edges = len(edges)
        self._incidence_matrix = np.zeros((num_nodes, num_edges), dtype=int)
        
        for edge_idx, (u, v) in enumerate(edges):
            self._incidence_matrix[u, edge_idx] = 1
            self._incidence_matrix[v, edge_idx] = 1

    def find_shortest_path(self) -> List[Tuple[int, int]]:
        """
        Najde nejkratší cestu. Pokud neexistuje, vypíše hlášku a vrátí prázdný seznam.
        """
        if self.grid is None:
            print("Bludiště není inicializováno.")
            return []

        self._build_incidence_matrix()
        
        start_node = (0, 0)
        end_node = (self.size - 1, self.size - 1)
        
        if start_node not in self._node_to_id:
            print("Vstup je blokován")
            return []
        elif end_node not in self._node_to_id:
            print("Výstup je blokován")
            return []
            
        start_id = self._node_to_id[start_node]
        end_id = self._node_to_id[end_node]
        
        distances = {i: float('inf') for i in self._id_to_node}
        distances[start_id] = 0
        predecessors = {i: None for i in self._id_to_node}
        
        priority_queue = [(0, start_id)]
        visited = set()
        
        while priority_queue:
            current_dist, u = heapq.heappop(priority_queue)
            
            if u == end_id:
                break
                
            if u in visited:
                continue
            visited.add(u)
            
            connected_edges = np.where(self._incidence_matrix[u, :] == 1)[0]
            for edge_idx in connected_edges:
                nodes_on_edge = np.where(self._incidence_matrix[:, edge_idx] == 1)[0]
                
                if len(nodes_on_edge) == 2:
                    v = nodes_on_edge[0] if nodes_on_edge[0] != u else nodes_on_edge[1]
                    new_dist = current_dist + 1
                    
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        predecessors[v] = u
                        heapq.heappush(priority_queue, (new_dist, v))
                        
        if distances[end_id] == float('inf'):
            # Neexistuje cesta ven z bludiště
            self.shortest_path = []
            return []
            
        path_ids = []
        current_node = end_id
        while current_node is not None:
            path_ids.append(current_node)
            current_node = predecessors[current_node]
            
        path_ids.reverse()
        self.shortest_path = [self._id_to_node[node_id] for node_id in path_ids]
        
        return self.shortest_path

    def _apply_template(self, template: str = "empty") -> None:
        """
        Aplikuje počáteční šablonu.
            Možnosti jsou: 'empty', 'slalom', 'X', '+', 'mrizka'.
            Výchozí je 'empty'.
        """
        self.grid = np.zeros((self.size, self.size), dtype=bool)
        
        center = self.size // 2
        
        if template == "empty":
            pass
            
        elif template == "slalom":
            for r in range(self.size):
                if r % 2 == 1:
                    gap_col = 0 if (r // 2) % 2 == 0 else self.size - 1
                    for c in range(self.size):
                        if c != gap_col:
                            self.grid[r, c] = True
        
        elif template == "X":
            for r in range(self.size):
                for c in range(self.size):
                    if r == c or r + c == self.size - 1:
                        if not (self.size % 2 == 1 and r == center and c == center):
                            self.grid[r, c] = True
                            
        elif template == "+":
            for r in range(self.size):
                for c in range(self.size):
                    if r == center or c == center:
                        if 0 < r < self.size - 1 and 0 < c < self.size - 1:
                            self.grid[r, c] = True
                            
        elif template == "mrizka":
            for r in range(self.size):
                for c in range(self.size):
                    if r % 2 == 1 and c % 2 == 1:
                        self.grid[r, c] = True
        
        else:
            print(f"Šablona '{template}' není definována.")
        
        self.grid[0, 0] = False
        self.grid[self.size - 1, self.size - 1] = False

    def generate_maze(self, size: int, template: str = "empty", fill_attempts: int = 50) -> None:
        """
        Vygeneruje řešitelné bludiště použití šablony a přidáváním náhodných stěn.
            Možnosti jsou: 'empty', 'slalom', 'X', '+', 'mrizka'.
            Výchozí je 'empty'.
        """
        self.grid = np.zeros((size, size), dtype=bool)
        self._apply_template(template)
        
        cells = [
            (r, c) for r in range(self.size) for c in range(self.size)
            if (r, c) not in [(0, 0), (self.size - 1, self.size - 1)]
        ]
        
        random.shuffle(cells)
        
        attempts = 0
        
        for r, c in cells:
            if attempts >= fill_attempts:
                break
            if self.grid[r, c]:
                continue
                
            self.grid[r, c] = True
            
            if not self.find_shortest_path():
                self.grid[r, c] = False
            else:
                attempts += 1
                
        self.find_shortest_path()

    def save_to_image(self, output_path: str = "saved_maze.png", scale: int = 20) -> None:
        """
        Exportuje bludiště do obrázku.
        """
        if self.grid is None:
            return

        img_array = np.zeros((self.size, self.size, 3), dtype=np.uint8)
        img_array[self.grid] = COLOR_WALL
        img_array[~self.grid] = COLOR_PATH
        
        for r, c in self.shortest_path:
            img_array[r, c] = COLOR_ROUTE
            
        img = Image.fromarray(img_array)
        img = img.resize((self.size * scale, self.size * scale), Image.Resampling.NEAREST)
        img.save(output_path)