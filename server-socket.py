import random
import time
import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

define("port", default=8001, type=int)

Manager = {}
class DataManager(object):
    clients = []
    servers = {}

    def regist_client(self,client):
        if client not in self.clients:
            self.clients.append(client)

    def unregist_client(self,client):
        if client in self.clients:
            self.clients.remove(client)

    def regist_server(self,server,room_id):
        room_id = str(room_id)
        print "regist room _id"
        if room_id not in self.servers:
            self.servers[room_id] = []
        self.servers[room_id].append(server)
        print self.servers

    def unregist_server(self,server):
        for room_id in self.servers:
            servers = self.servers.get(room_id,[])
            if server in servers:
                servers.remove(server)

    def did_recieve_message_from_client(self,msg,room_id):
        room_id = str(room_id)
        servers = self.servers.get(room_id,[])
        for server in servers:
            server.write_message(msg)


def getClientRecieveDataManager():
    key = 'data_man'
    if Manager.get(key,None) is None:
        Manager[key] = DataManager()
    return Manager[key]

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        # self.render("index.html")

        self.write_message("get ok.")


import threading


class SocketWorker(threading.Thread):
    _signal_close = False

    def __init__(self, thread_id=1, handler=None):
        self.handler = handler
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self._signal_close = False

    def run(self):
        while True or not self._signal_close:
            time.sleep(0.2)
            self.handler.re_submit_data()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    last_data_recieve = ""
    thread_worker = None

    def re_submit_data(self):
        if self.last_data_recieve != 'stop':
            print "re_submit_data"
            self.write_message(self.last_data_recieve+str(random.uniform(0, 1.9)))

    def __init__(self, *args, **kwargs):
        print "init WebSocketHandler"
        super(WebSocketHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def kill_thread(self):
        if self.thread_worker is not None:
            self.thread_worker._signal_close = True
            self.thread_worker = None

    def open(self, *args):
        print "New connection"
        self.kill_thread()
        self.thread_worker = SocketWorker(thread_id=random.uniform(0,99), handler=self)
        self.thread_worker.start()
        self.write_message("Welcome!")

    def on_message(self, message):
        print "New message {}".format(message)
        if message.startswith("room_id"):
            room_id= message.split(":")[1]
            data_man = getClientRecieveDataManager()
            data_man.regist_server(self,room_id)
        else:
            self.last_data_recieve = message
            self.write_message(message.upper())

    def on_close(self):
        self.kill_thread()
        data_man = getClientRecieveDataManager()
        data_man.unregist_server(self)
        print "Connection closed"

class ClientWSHandler(tornado.websocket.WebSocketHandler):
    last_data_recieve = ""

    def check_origin(self, origin):
        return True

    def open(self, *args):
        print "New Client connection"
        #
        # data_man = getClientRecieveDataManager()
        # data_man.regist_client(self)
        self.write_message("Welcome!")

    def on_message(self, message):
        if message.startswith("room_id"):
            room_id= message.split(":")[1]
            self.room_id = room_id
            print "my room_id ="+room_id
        else:
            data_man = getClientRecieveDataManager()
            print "%s : Client New message %s"%(self.room_id,message)
            data_man.did_recieve_message_from_client(message,self.room_id)

    def on_close(self):

        # data_man = getClientRecieveDataManager()
        # data_man.unregist_client(self)
        print "Connection closed"

class ClientAllWSHandler(ClientWSHandler):
    last_data_recieve = ""

    def open(self, *args):
        print "New Client connection"
        self.room_id = 1
        self.write_message("Welcome!")



app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws/', WebSocketHandler),
    (r'/submit/', ClientWSHandler),
    (r'/submit_all/', ClientAllWSHandler),
])

if __name__ == '__main__':
    app.listen(options.port)
    print "start server socket"
    tornado.ioloop.IOLoop.instance().start()
