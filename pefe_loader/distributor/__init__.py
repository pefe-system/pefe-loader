from ..config import *
from pefe_common.messaging.json import JSONServer, JSONSocket
from ..error_reporter import ErrorReporter
from ..loader import AbstractLoader
import time

MAX_RETRIES = config['self']['max_retries']

class Distributor(JSONServer):
    def __init__(self, loader, error_reporter):
        # type: (JSONServer, AbstractLoader, ErrorReporter) -> None
        host = config["self"]["host"]
        port = config["self"]["port"]
        super().__init__(host, port)

        self._loader = loader
        self._error_reporter = error_reporter
    
    def start(self):
        super().start()
        host = config["self"]["host"]
        port = config["self"]["port"]
        print(f"Listening on {host}:{port}")
    
    def handle_client(self, conn, addr):
        # type: (Distributor, JSONSocket, str) -> None 
        print(f"New agent [{addr}]")
        identity = f"[{addr}|unknown_identity]"
        try:
            greeting = conn.recv_json()
            identity = greeting['identity']
            identity = f"[{addr}|{identity}]"
            print(f"Agent reported identity: {identity}")
            CONSUMER_ID = self._loader.register_consumer()

            while True:
                try:
                    content = self._loader.consume(CONSUMER_ID)
                except StopIteration:
                    conn.send_json({ "status": "end" })
                    break
                else:
                    retry = 0
                    pop = False
                    while not pop:
                        conn.send_json({ "status": "new_content", "content": content })
                        ack = conn.recv_json()
                        if ack['status'] == 'done':
                            print(f"OK: Agent {identity} processed content {content["title"]}")
                            pop = True
                        elif ack['status'] == 'error':
                            retry += 1
                            if retry > MAX_RETRIES:
                                try:
                                    self._error_reporter.log(identity, content, ack['message'])
                                    print(f"ERROR: Agent {identity} failed on content {content["title"]} ; logged for later review")
                                except Exception as e:
                                    print(f"ERROR: Agent {identity} failed on content {content["title"]} ; COULD NOT LOG FOR LATER REVIEW:")
                                    print(e)
                                pop = True
                            else:
                                print(f"ERROR: Agent {identity} failed on content {content["title"]} ; retrying #{retry}")
                                time.sleep(2)
                    
                    self._loader.consume_done(CONSUMER_ID)

        except ConnectionError:
            print(f"Agent disconnected: {identity}")
