import json
from urllib.parse import quote, urlencode, urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class ResourceNotFound(Exception):
    pass


class ResourceConflict(Exception):
    pass


class Server:
    def __init__(self, uri):
        self.uri = uri.rstrip("/") + "/"

    def __getitem__(self, db_name):
        return Database(self.uri, db_name)


class Database:
    def __init__(self, server_uri, db_name):
        self.server_uri = server_uri.rstrip("/") + "/"
        self.db_name = db_name
        self.db_url = urljoin(self.server_uri, quote(db_name, safe=""))

    def _request(self, method, path="", data=None, params=None, stream=False):
        url = self.db_url
        if path:
            url += "/" + path.lstrip("/")
        if params:
            encoded = {}
            for key, value in params.items():
                if isinstance(value, (dict, list, tuple)):
                    encoded[key] = json.dumps(value)
                elif isinstance(value, bool):
                    encoded[key] = "true" if value else "false"
                else:
                    encoded[key] = str(value)
            url += "?" + urlencode(encoded)

        payload = None
        headers = {}
        if data is not None:
            payload = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=payload, headers=headers, method=method)
        try:
            response = urlopen(request)
        except HTTPError as exc:
            if exc.code == 404:
                raise ResourceNotFound() from exc
            if exc.code == 409:
                raise ResourceConflict() from exc
            raise

        if stream:
            return response

        body = response.read()
        if not body:
            return {}
        return json.loads(body.decode("utf-8"))

    def get(self, docid):
        return self._request("GET", quote(str(docid), safe=""))

    def save_doc(self, doc):
        if "_id" in doc and doc["_id"]:
            return self._request(
                "PUT",
                quote(str(doc["_id"]), safe=""),
                data=doc,
            )
        return self._request("POST", data=doc)

    def delete_doc(self, doc):
        return self._request(
            "DELETE",
            quote(str(doc["_id"]), safe=""),
            params={"rev": doc["_rev"]},
        )

    def view(self, view_name, **kwargs):
        design, view = view_name.split("/", 1)
        result = self._request("GET", f"_design/{design}/_view/{view}", params=kwargs)
        return result.get("rows", [])

    def fetch_attachment(self, doc_or_id, filename, stream=False):
        doc_id = doc_or_id.get("_id") if isinstance(doc_or_id, dict) else doc_or_id
        path = f"{quote(str(doc_id), safe='')}/{quote(str(filename), safe='')}"
        response = self._request("GET", path, stream=stream)
        if stream:
            return response
        return response.read()

    def save_docs(self, docs, all_or_nothing=True):
        payload = {"docs": docs}
        if all_or_nothing:
            payload["all_or_nothing"] = True
        return self._request("POST", "_bulk_docs", data=payload)

    def delete_docs(self, docs, all_or_nothing=True):
        to_delete = []
        for doc in docs:
            item = dict(doc)
            item["_deleted"] = True
            to_delete.append(item)
        payload = {"docs": to_delete}
        if all_or_nothing:
            payload["all_or_nothing"] = True
        return self._request("POST", "_bulk_docs", data=payload)


class Consumer:
    def __init__(self, db):
        self.db = db

    def fetch(self, since=0):
        return self.db._request("GET", "_changes", params={"since": since})
