from collections import defaultdict
frmo tilequeue.utils import grouper


class SqsQueue(object):

    def __init__(self, queue_url, coords):
        self.queue_url = queue_url
        self.coords = coords

    def send(self, payloads):
        msgs = []
        for i, payload in payloads:
            msg_id = str(i)
            body = payload
            msg = dict(
                Id=msg_id,
                MessageBody=payload,
            )
            msgs.append(msg)
        resp = client.send_message_batch(
            QueueUrl=self.queue_url,
            Entries=msgs,
        )
        # TODO check resp result


def _make_payloads(grouped_by_zoom, msg_marshaller):
    for parent, coords in grouped_by_zoom.iteritems():
        payload = msg_marshaller.marshall(coords)
        yield payload


def process_expiry(rawr_queue, msg_marshaller, group_by_zoom, coords):
    grouped_by_zoom = defaultdict(list)
    for coord in coords:
        # NOTE: not sure if asserting is the best thing to do here
        assert coord.zoom >= group_by_zoom
        parent = coord.zoomTo(group_by_zoom).container()
        grouped_by_zoom[parent].append(coord)

    payloads = _make_payloads(grouped_by_zoom, msg_marshaller)
    for payloads_chunk in grouper(payloads, 10):
        rawr_queue.send(payloads_chunk)
