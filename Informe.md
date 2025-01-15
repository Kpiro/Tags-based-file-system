# Informe del Sistema Distribuido de Archivos basado en Etiquetas

## 1. **Arquitectura o el problema de como diseñar el sistema.**
  
El sistema distribuido tendrá una arquitectura orientado a servicios. La topología que mantendrá la red es la de Chord. Cada servidor del sistema estará asociado a un nodo de la red de Chord. Los servicios asociados al sistema son:
- `ReadService`: este servicio estará dedicado solo a aquellas acciones que dependen de leer los datos, como `list` y `download`.
- `WrittenService`: este servicio estará dedicado a aquellas acciones que dependen de modificaciones (escrituras) en los datos, como: `add`, `delete`, `add-tags` y `delete-tags`.   

## 2. **Procesos o el problema de cuántos programas o servicios posee el sistema**
Tipos de procesos:
- Actualización de la red de Chord ante la salida o entrada de un nodo
- Atención a múltiples clientes
- Verificación de la consistencia de la red 

Debido al Global Interpreter Lock (GIL), aunque Python permite la concurrencia con el módulo `threading`,  el paralelismo real (es decir, la ejecución simultánea en múltiples núcleos) está limitado en ciertos contextos. Incluso si usas múltiples hilos con threading, solo un hilo ejecutará código Python a la vez. Los hilos se alternan en la ejecución (como un sistema de turnos).

Sin embargo, como el sistema es altamente concurrente, los hilos resultan ser la opción más eficiente debido a su ligereza y menor sobrecarga. Además, como en el sistema se llevan a cabo principalmente operaciones de lectura y escritura de archivos, el GIL no es un gran problema porque los hilos pueden liberar el GIL mientras esperan el I/O. Esto permite a otros hilos ejecutarse durante ese tiempo.

    
## 3. **Comunicación o el problema de como enviar información mediante la red**

Los tipos de comunicación que se utilizarán son REST y patrones de mensajes como ZeroMQ. Ambos son `no persistentes` por defecto; en el caso de REST la comunicación es `síncrona` por defecto, mientras que en ZeroMQ es `asíncrona`. El estándar de servicios REST será utilizado para la comunicación entre cliente y servidor con el objetivo de que se puedan realizar las operaciones del sistema a partir de las peticiones `GET`, `PUT`, `POST` y `DELETE`. El patrón de mensajes ZeroMQ será utilizado para la comunicación servidor-servidor y para procesos. Tanto Request-Reply como Publisher-Subscriber pueden ser ideales para ZeroMQ. Request-Reply se puede utilizar para manejar acciones síncronas como consultas específicas entre nodos (búsqueda de datos, solicitudes de predecesores/sucesores, modificaciones puntuales). Publisher-Subscriber se puede utilizar para acciones asíncronas como actualizaciones de la estructura del anillo (nuevos nodos, nodos salientes), propagación de cambios en los archivos (creación, modificación, eliminación) o anuncios de replicación o redistribución de datos.    

## 4.  **Coordinación o el problema de poner todos los servicios de acuerdo**

Uso de `locks` para garantizar el acceso exclusivo a recursos y la sincronización de acciones:

Implementar un sistema de locks (bloqueos) para que las acciones sobre los archivos sean secuenciales. Un `lock` impide que otro servicio realice una operación sobre el mismo archivo hasta que la operación anterior haya finalizado.

- **Lock de lectura**: 
Permite que múltiples procesos lean un recurso compartido de manera simultánea, pero previene que otros procesos escriban en ese recurso mientras se está leyendo.

- **Lock de escritura**: 
Asegura que solo un proceso pueda escribir en el recurso a la vez. Además, bloquea el acceso tanto de lectura como de escritura por otros procesos.

Esto garantiza la integridad de los datos, evitando condiciones de carrera.
 



##  5. **Nombrado y Localización o el problema de dónde se encuentra un recurso y como llegar al mismo**

Cada archivo tiene un nombre único que lo identifica. Debido a que Chord es un tipo de DHT, cada archivo o etiqueta que se agrega al sistema tendrá un responsable, que se halla mediante la función hash SHA-1. Por esta razón, es posible obtener el nodo responsable de los datos mediante la función hash. De igual forma, se puede localizar la ubicación de los datos siguiendo la misma lógica. 

## 6. **Consistencia y Replicación o el problema de solucionar los problemas que surgen a partir de tener varias copias de un mismo dato en el sistema.**

Para mantener la consistencia del sistema se distribuirán los datos mediante la creación de copias de dichos datos en múltiples nodos. Debido a que el sistema presenta un nivel dos de tolerancia a fallo, se replicará la información de un nodo x en el succ(x) y en el succ(succ(x)). 

## 7. Tolerancia a fallas o el problema de, para que pasar tanto trabajo distribuyendo datos y servicios si al fallar una componente del sistema todo se viene abajo. 
    
  Cuando uno o varios servidores salen de la red, es necesario actualizar los predecesores/sucesores y la _finger table_ de cada nodo, redistribuir los datos en los nodos nuevos que le correspondan y actualizar los datos de las réplicas que guardan una copia de los datos de cada nodo de la red.








