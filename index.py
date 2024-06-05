from kafka import KafkaProducer
from time import sleep
import random
import json

producer = KafkaProducer(bootstrap_servers= 'localhost:9092')
ip = ['152.173.14.227', '101.46.175.255', '104.132.202.255', '104.135.166.0']
while True: 
    msg = {
        "IP": random.choice(ip),
        "Upload":   float(f'{random.uniform(50.0, 150.99):.2f}') ,
        "Download": float(f'{random.uniform(100.0, 800.99):.2f}'),
        "Ping": float(f'{random.uniform(50.0, 300.99):.2f}')
    }
    jsondict = json.dumps(msg)
    producer.send('input-data', bytes(jsondict, encoding='utf8'))
    print('enviando data...')
    sleep(1)