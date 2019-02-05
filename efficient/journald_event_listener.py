# Acts like a event stream for tracker
# Listens for events from the log source
# Creates typed events
# Auto generates events for AutoExpiringEvents
'''
 Implementation:
    __init__ takes a tracker
        Hook the __init__ to start of efficient
    Check for jouranld events
        How to identify the event is from this App - Use a MessageId. Configured with a guid
        Run epoll in a background loop - backgroud thread that calls epoll.poll()
        Have a way to quit epoll - epoll.unregister() ??
    If an event occurs convert it to the appropriate type of known events
    push the event to the list of trackers if the tracker can handle the request
    Keep looping until exit - link the exit condition with the exit condition of efficient.end
'''
from select import poll, POLLIN
from systemd import journal
from threading import Thread,RLock

class JournaldEventListener(object):
    PollingIntervalMs = 1000

    def __init__(self, tracker, journald_message_id):
        self._tracker = tracker

        self._journal_reader = self._create_journalreader_for(journald_message_id)
        self._poller = self._create_poller_for(self._journal_reader)

        self._running = False
        self._lock = RLock()

    def start(self):
        if self._running:
            return

        with self._lock:
            if not self._running:
                self._running = True
                self._start_event_processing_thread()

    def end(self):
        with self._lock:
            self._running = False

    def _create_journalreader_for(self, journald_message_id):
        journal_reader = journal.Reader()
        journal_reader.this_boot()
        journal_reader.this_machine()
        journal_reader.add_match(MESSAGE_ID=journald_message_id)
        return journal_reader

    def _create_poller_for(self, journal_reader):
        p = poll()
        p.register(journal_reader, POLLIN)
        return p

    def _start_event_processing_thread(self):
        processor = Thread(name="EventProcessor", target=self._receive_events)
        processor.daemon = True
        processor.start()

    # This method can be run simultaneously if two threads are active which is a possibility since it is all controlled
    # by a single self._running. This may cause events to be missed or duplicated
    def _receive_events(self):
        self._journal_reader.seek_tail()
        while self._running:
            reader_ready = self._poller.poll(JournaldEventListener.PollingIntervalMs)
            if reader_ready:
                for event in JournaldEventListener._filter_events(self._journal_reader):
                    self._handle_event(event)
                self._journal_reader.process()

    def _handle_event(self, event):
        self._tracker.handle(event)

    @staticmethod
    def _filter_events(message_stream):
        return filter(lambda message: 'EVENT_NAME' in message, message_stream)