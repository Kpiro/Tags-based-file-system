import bisect

class ChordNode:
    def __init__(self, id, address, m):
        self.id = id  # ID del nodo (hash único)
        self.address = address  # Dirección del nodo (IP:Puerto)
        self.successor = None  # Nodo sucesor
        self.predecessor = None  # Nodo predecesor
        self.m = m # Número de bits
        self.finger_table = [None]*self.m  # Tabla de finger
        self.data = {}  # Archivos y etiquetas de los que es responsable

    def find_successor(self, key_id):
        """Encontrar el sucesor responsable de un ID de clave."""
        if self.id == key_id:   
            return self

        for row in self.finger_table.reverse():
            if row.id <= key_id:
                return row.find_succesor(key_id)
            
        return self.successor
    
    def update_finger_table(self, nodes, nodes_ids):
        """Actualiza los datos de la finger table del nodo."""
        for i, row in enumerate(self.finger_table):
            x = (self.id + 2**i)%(2**self.m) # Valor del enrutamiento 
            pos = bisect.bisect_left(nodes_ids, x) 
            if pos == len(nodes_ids): id_found = nodes_ids[0] # Nodo responsable del nodo x
            else: id_found = nodes_ids[pos] # Nodo responsable del nodo x
            self.finger_table[i] = nodes[id_found] # Actualizar tabla

    
class ChordRing:
    def __init__(self, m):
        self.m = m
        self.nodes = [None]*(2**self.m)
        self.nodes_ids = []

    def add(self, node : ChordNode):
        """Añadir un nodo al anillo de Chord."""
        self.nodes[node.id] = node
        bisect.insort(self.nodes_ids, node.id)
        self.update_finger_tables()

    def update_finger_tables(self):
        """Actualizar los finger tables de todos los nodos."""
        for node in self.nodes:
            if node is None: continue
            node.update_finger_table(self.nodes, self.nodes_ids)

# ------------- Probando el anillo de Chord ------------- 
ring = ChordRing(5)

node1 = ChordNode(1, None, 5)
ring.add(node1)
node4 = ChordNode(4, None, 5)
ring.add(node4)
node9 = ChordNode(9, None, 5)
ring.add(node9)
node11 = ChordNode(11, None, 5)
ring.add(node11)
node14 = ChordNode(14, None, 5)
ring.add(node14)
node18 = ChordNode(18, None, 5)
ring.add(node18)
node20 = ChordNode(20, None, 5)
ring.add(node20)
node21 = ChordNode(21, None, 5)
ring.add(node21)
node28 = ChordNode(28, None, 5)
ring.add(node28)

for node in ring.nodes_ids:
    print(f'----Node {node}----')
    for i,row in enumerate(ring.nodes[node].finger_table, 1):
        print(f'{i} -> {row.id}')