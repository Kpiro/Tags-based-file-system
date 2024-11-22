class ChordNode:
    def __init__(self, id, address, m):
        self.id = id  # ID del nodo (hash único)
        self.address = address  # Dirección del nodo (IP:Puerto)
        self.successor = None  # Nodo sucesor
        self.predecessor = None  # Nodo predecesor
        self.m = m # Número de bits
        self.finger_table = [ChordNode]*self.m  # Tabla de finger
        self.data = {}  # Archivos y etiquetas de los que es responsable

    def find_successor(self, key_id):
        """Encontrar el sucesor responsable de un ID de clave."""
        if self.id == key_id:   
            return self

        for row in self.finger_table.reverse():
            if row.id <= key_id:
                return row.find_succesor(key_id)
            
        return self.successor
        
