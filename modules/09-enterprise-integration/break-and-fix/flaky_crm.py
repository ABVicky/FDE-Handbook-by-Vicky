"""A fake CRM for the break & fix: an in-memory contacts API that sometimes loses responses.

Like real networks: the CRM *saves* the contact, then the response never arrives (a timeout).
Uses httpx.MockTransport, so nothing leaves your machine.
"""
import json
import random

import httpx


class FlakyCrm:
    def __init__(self, seed=7, lose_response_rate=0.15):
        self.contacts = {}
        self.random = random.Random(seed)
        self.rate = lose_response_rate

    def handler(self, request):
        body = json.loads(request.content) if request.content else {}
        if request.url.path.endswith("/search"):
            email = body["filterGroups"][0]["filters"][0]["value"]
            hits = [{"id": cid} for cid, props in self.contacts.items() if props.get("email") == email]
            return httpx.Response(200, json={"results": hits})
        if request.method == "POST":
            contact_id = str(5000 + len(self.contacts))
            self.contacts[contact_id] = body["properties"]          # saved…
            if self.random.random() < self.rate:
                raise httpx.ReadTimeout("response lost", request=request)   # …but the caller never hears back
            return httpx.Response(201, json={"id": contact_id})
        if request.method == "PATCH":
            self.contacts[request.url.path.rsplit("/", 1)[1]].update(body["properties"])
            return httpx.Response(200, json={})
        return httpx.Response(404)

    def client(self):
        return httpx.Client(transport=httpx.MockTransport(self.handler), base_url="https://crm.test")

    def duplicates(self):
        emails = [c.get("email") for c in self.contacts.values()]
        return len(emails) - len(set(emails))
