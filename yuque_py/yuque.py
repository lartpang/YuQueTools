import typing

from .client import AbstractClient, Client


class User:
    def __init__(self, client: AbstractClient):
        self._client = client

    def get(self, login: typing.Optional[str] = None) -> typing.Dict:
        api = f"users/{login}" if login else "user"
        return self._client.request(api=api, method="GET", requests_data=None)


class Group:
    def __init__(self, client: AbstractClient):
        self._client = client

    def list(
        self,
        login: typing.Optional[str] = None,
        data: typing.Optional[typing.Dict] = None,
    ) -> typing.Dict:
        api = f"users/{login}/groups" if login else "groups"
        return self._client.request(api, method="GET", requests_data=data)

    def create(self, data: typing.Dict) -> typing.Dict:
        assert "name" in data
        assert "login" in data
        api = "groups"
        return self._client.request(api, method="POST", requests_data=data)

    def get(self, login: str) -> typing.Dict:
        assert login
        api = f"groups/{login}"
        return self._client.request(api, method="GET")

    def update(self, login: str, data: typing.Dict) -> typing.Dict:
        assert login
        api = f"groups/{login}"
        return self._client.request(api, method="PUT", requests_data=data)

    def delete(self, login: str) -> typing.Dict:
        assert login
        api = f"groups/{login}"
        return self._client.request(api, method="DELETE")

    def list_user(self, login: str) -> typing.Dict:
        return self._client.request(f"groups/{login}/users", method="GET")

    def add_user(self, group: str, user: str, data: typing.Dict) -> typing.Dict:
        assert group
        assert user
        api = f"groups/{group}/users/{user}"
        return self._client.request(api, method="PUT", requests_data=data)

    def remove_user(self, group: str, user: str) -> typing.Dict:
        assert group
        assert user
        api = f"groups/{group}/users/{user}"
        return self._client.request(api, method="DELETE")

    @staticmethod
    def _get_url(user: str, group: str):
        assert user or group
        api = f"users/{user}/repos" if user else f"users/{group}/repos"
        return api


class Repo:
    def __init__(self, client: AbstractClient):
        self._client = client

    def list(
        self,
        user: typing.Optional[str] = None,
        group: typing.Optional[str] = None,
        data: typing.Optional[typing.Dict] = None,
    ) -> typing.Dict:
        api = self._get_url(user, group)
        return self._client.request(api, method="GET", requests_data=data)

    def create(
        self,
        user: typing.Optional[str] = None,
        group: typing.Optional[str] = None,
        data: typing.Optional[typing.Dict] = None,
    ) -> typing.Dict:
        api = self._get_url(user, group)
        assert data
        return self._client.request(api, method="POST", requests_data=data)

    def get(self, namespace: str, data: typing.Dict = None) -> typing.Dict:
        assert namespace
        return self._client.request(
            f"repos/{namespace}", method="GET", requests_data=data
        )

    def update(self, namespace: str, data: typing.Dict) -> typing.Dict:
        assert namespace
        return self._client.request(
            f"repos/{namespace}", method="PUT", requests_data=data
        )

    def delete(self, namespace: str) -> typing.Dict:
        assert namespace
        return self._client.request(f"repos/{namespace}", method="DELETE")

    @staticmethod
    def _get_url(user: typing.Optional[str], group: typing.Optional[str]):
        assert user or group
        api = f"users/{user}/repos" if user else f"groups/{group}/repos"
        return api


class Doc:
    def __init__(self, client: AbstractClient):
        self._client = client

    def get(
        self, namespace: str, slug: str, data: typing.Optional[typing.Dict] = None
    ) -> typing.Dict:
        assert namespace
        assert slug
        api = f"repos/{namespace}/docs/{slug}"
        return self._client.request(api, method="GET", requests_data=data)

    def create(
        self, namespace: str, data: typing.Optional[typing.Dict] = None
    ) -> typing.Dict:
        assert namespace
        api = f"repos/{namespace}/docs"
        return self._client.request(api, method="POST", requests_data=data)

    def update(
        self, namespace: str, doc_id: str, data: typing.Optional[typing.Dict] = None
    ) -> typing.Dict:
        assert namespace
        assert doc_id
        api = f"repos/{namespace}/docs/{doc_id}"
        return self._client.request(api, method="PUT", requests_data=data)

    def delete(self, namespace: str, doc_id: str) -> typing.Dict:
        assert namespace
        assert doc_id
        api = f"repos/{namespace}/docs/{doc_id}"
        return self._client.request(api, method="DELETE")


class Yuque:
    def __init__(self, api_host: str, user_token: str):
        self._client = Client(api_host, user_token)
        self.users = User(self._client)
        self.groups = Group(self._client)
        self.repos = Repo(self._client)
        self.docs = Doc(self._client)
