import faust
from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy
from cassandra.auth import PlainTextAuthProvider
import datetime

app = faust.App('faust-app', broker='kafka://localhost:9092')

class Data(faust.Record, serializer="json"):
    IP: str
    Upload: float
    Download: float
    Ping: float

kafka_topic = app.topic('input-data', value_type=Data, partitions=8)

upload_table = app.Table('upload_table', default=float, partitions=8)
download_table = app.Table('download_table', default=float, partitions=8)
ping_table = app.Table('ping_table', default=float, partitions=8)
reg_table = app.Table('reg_table', default=int, partitions=8 )

@app.agent(kafka_topic)
async def getData(data):
    print(data)
    async for item in data:
        upload_table[item.IP] += item.Upload
        download_table[item.IP] += item.Download
        ping_table[item.IP] += item.Ping
        reg_table[item.IP] += 1

@app.timer(interval=10.0)
async def proccesingData():
    db = cassandra()
    data = {}
    total = 0
    iplist =[]
    for IP, total in reg_table.items():
       data.setdefault(IP, {}).setdefault("total", total)
       iplist.append(IP)
    for IP, upload in upload_table.items():
        avg = upload / data[IP]["total"]
        data[IP]["upload"] = f'{avg:.2f}'
    for IP, download in download_table.items():
        avgdown = download/data[IP]["total"]
        data[IP]["download"] = f'{avgdown:.2f}'
    for IP, ping in ping_table.items():
        avgping = ping/data[IP]["total"]
        data[IP]["ping"] = f'{avgping:.2f}'
    for i in iplist:
        id = db.execute("SELECT next_id FROM network.id WHERE id_name = 'id';")
        db.execute("""
            INSERT INTO network.user (id, ip, upload, download, ping, at)
            VALUES (%(id)s,%(ip)s,%(upload)s,%(download)s,%(ping)s, %(at)s);
        """, {
            "id":id[0][0],
            "ip": i,
            "upload": float(data[i]["upload"]),
            "download": float(data[i]["download"]),
            "ping": float(data[i]["ping"]),
            "at": unix_time_millis(datetime.datetime.now())
        })
        db.execute("""
            UPDATE network.id SET next_id = %(next_id)s where id_name = 'id' if next_id = %(current_id)s
        """, {
            "next_id": int(id[0][0]) + 1,
            "current_id": id[0][0]
        })
        
def cassandra():
    local_dc = 'datacenter1'
    auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
    cluster = Cluster(['localhost'], port=9042, auth_provider=auth_provider, load_balancing_policy=DCAwareRoundRobinPolicy(local_dc=local_dc))
    
    session = cluster.connect('network')
    return session

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return int(unix_time(dt) * 1000.0)