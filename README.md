# Proyecto de Big Data
Este proyecto está basado en la evaluación 3 para el ramo de Big Data de la carrera Ingeniería en Informática de INACAP

## Resumen
Este proyecto se basa en consumir servicios de datos en tiempo real. En este caso, los datos a consumir son las métricas de la red segun distintas direcciones IP (Velocidad de subida, Velocidad de bajada, Ping). Estos datos, luego se procesan y se genera un promedio cada 10 segundos, el cual se almacenará en una base de datos para su posterior análisis. La arquitectura seleccionada para este proyecto es la arquitectura Kappa

## Tecnologías
  - Docker
  - Python
  - Apache Kafka
  - Apache Cassandra

## Instalación
### Obtener repositorio
Para obtener el repositorio se debe ingresar el siguiente comando dentro de la consola de comandos: `git clone https://github.com/JavierGonzalez998/Evaluacion_BigData.git`
### Apache kafka
Para Apache Kafka, una vez en el repositorio, en la consola de comandos, ir al directorio de Kafka con `cd kafka`. Luego ejecutar `docker-compose up` en la consola de comandos.

Esto ejecutará la instancia de Apache Kafka con Zookeper y con sus conexiones configuradas.
#### Crear tópicos
Para crear el tópico que se conectará la fuente de datos y enviará los datos en tiempo real, se debe ingresar a la consola del contenedor previamente iniciado.
Para eso se debe ejecutar el siguiente comando en una nueva consola de comandos: `docker exec -it kafka-broker-1 bash`.

Una vez dentro del bash del contenedor de Kafka, se debe escutar el siguiente comando: `kafka-topics --bootstrap-server kafka-broker-1:9092 --create --topic input-data` Este comando crea el topico "input-data" que se conectará la fuente de datos. Sólo basta una vez que se cree el tópico, luego se mantiene cada vez que se inicia el contenedor.
#### Crear Consumidor
Para que Kafka empiece a recibir los datos, se debe crear un consumidor, el cual se encargue de recibir los datos que envíe la fuente de datos. Para eso se debe usar el siguiente comando: `kafka-console-consumer --bootstrap-server kafka-broker-1:9092 --topic input-data --from-beginning`.

Así, el servicio de Apache Kafka está listo para recibir datos

### Cassandra
Para configurar Apache Cassandra. Se debe obtener la imagen de Apache Cassandra. Para ello, en una nueva terminal, se debe ejecutar el siguiente comando: `docker run cassandra:latest`. Luego de obtener la imagen de Docker de Cassandra, dentro del proyecto y en el directorio de cassandra ejecutar `docker-compose up`. Esto creará el contenedor de Cassandra con toda su configuración.

#### Creacion de tablas
Para crear las tablas que almacenarán los datos procesados, se debe entrar al contenedor de docker. Para ello se debe ingresar en una nueva terminal `docker ps`. Este comando listará todos los contenedores activos. se debe copiar el id del contenedor de Cassandra.

Para entrar al contenedor de Cassandra, se debe ingresar el siguiente comando: `docker exec -it id_container /bin/bash`. Dónde id_container es la id copiada previamente. 

Una vez en la consola, se debe entrar al entrono de cassandra con el siguiente comando: `cqlsh`. Si solicita credenciales, son las siguientes: `username: cassandra` `password: cassandra`.

dentro del entrono de cassandra, se debe crear un Keyspace, que vendría siendo una base de datos. El cual se nombrará "network". Para esto, se debe ejecutar: `CREATE KEYSPACE network WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1} ;`

Una vez creada el Keyspace, se deben crear las tablas. Para esto, se crearán 2 tablas. Una almacenará la id del último registro ingresado, el cual se actualizará y se aumentará cada vez que se ingresa un nuevo registro. Esto, porque Cassandra no admite valores autoincrementables para sus primary keys. La otra tabla se almacenarán los datos del promedio de conexiones por IP.

#### Tabla de Ids
` CREATE TABLE network.id(id_name text PRIMARY KEY, next_id int);`

Para empezar con el Id 1, se debe ingresar manualmente el primer registo. Luego el script de python que procesa los datos irá aumentando por cada registro.

`INSERT INTO ids (id_name, next_id)VALUES ('id', 1);`

#### Tabla de datos
Para los datos que se almacenarán en esta tabla, se consideran las siguientes columnas:
  - id: Id autoincrementable
  - ip: IP de la red a analizar
  - download: promedio de velocidad de descarga en intervalos de 10 segundos
  - upload: promedio de velocidad de subida en intervalos de 10 segundos
  - ping: promedio de latencia de la red en intervalos de 10 segundos
  - at: timestamp de la subida del registro

`CREATE TABLE network.user(id int PRIMARY KEY,ip text, upload double, download double, ping double, at timestamp ) ;`

### Python
Para iniciar los scripts de python se debe crear un entorno virtual con el siguiente comando en la raíz del proyecto:

`python3 -m venv .venv`

Esto creará el entorno virtual para poder ejecutar los scripts. Para conectar al entorno virtual se debe ejecutar el siguiente comando:
 - Windows: `./.venv/Script/activate`
 - Linux: `. ./venv/bin/activate`

Una vez en el entorno virtual se debe ejecutar el siguiente comando para instalar las dependencias necesarias: `pip install -r requirements.txt`
#### Fuente de datos
Para la fuente de datos y una vez estando en el entorno virtual, solo se debe ejecutar `python index.py`. Esto iniciará el script, se conectará al tópico de Kafka (Debe estar inicializado y con sus tópicos y consumidores) y enviará los datos.

#### Procesamientos de datos
Para el procesamiento de datos en tiempo real, se utilizó una tecnología llamada Python Faust, que se encarga de procesar y obtener los datos en tiempo real.

Para iniciar el procesamiento de datos y una vez en el entorno virtual, en una nueva terminal y en el directorio de faust, ingresar el siguiente comando: `faust -A consumer worker -l info`

Esto iniciará el worker de Faust, que se encargará de obtener los datos, almacenarlos en una tabla de la sesión y cada 10 segundos, consultar a esa tabla para obtener el promedio de los datos y almacenarlos en la base de datos de Cassandra.
