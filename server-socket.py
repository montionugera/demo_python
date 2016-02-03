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
    servers = []

    def regist_client(self,client):
        if client not in self.clients:
            self.clients.append(client)

    def unregist_client(self,client):
        if client in self.clients:
            self.clients.remove(client)

    def regist_server(self,server):
        if server not in self.servers:
            self.servers.append(server)

    def unregist_server(self,server):
        if server in self.servers:
            self.servers.remove(server)

    def did_recieve_message_from_client(self,msg):
        for server in self.servers:
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
        data_man = getClientRecieveDataManager()
        data_man.regist_server(self)

    def on_message(self, message):
        print "New message {}".format(message)
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
        data_man = getClientRecieveDataManager()

        print "Client New message {}".format(message)
        data_man.did_recieve_message_from_client(message)

    def on_close(self):

        # data_man = getClientRecieveDataManager()
        # data_man.unregist_client(self)
        print "Connection closed"

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/ws/', WebSocketHandler),
    (r'/submit/', ClientWSHandler),
])

if __name__ == '__main__':
    app.listen(options.port)
    print "start server socket"
    tornado.ioloop.IOLoop.instance().start()
