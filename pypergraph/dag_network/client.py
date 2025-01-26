import aiohttp
import json
from urllib.parse import urlencode


class FetchRestService:
    def __init__(self, http_client=None):
        self.http_client = http_client or aiohttp.ClientSession()

    async def invoke(self, options: dict):
        print("Request options:", options)
        request_options = self.build_request(options)
        return await self.make_service_request(request_options)

    def build_request(self, options: dict):
        # Serialize query parameters
        param_str = self.serialize(options.get("query_params"))
        if param_str:
            options["url"] = f"{options['url']}?{param_str}"

        # Build HTTP headers
        http_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if options.get("auth_token") and not options.get("no_auth_header"):
            http_headers["Authorization"] = options["auth_token"]

        if options.get("headers"):
            http_headers.update(options["headers"])

        # Serialize body
        if "body" in options:
            content_type = http_headers.get("Content-Type")
            if content_type == "application/x-www-form-urlencoded":
                options["body"] = self.serialize(options["body"])
            elif content_type == "application/json":
                options["body"] = json.dumps(options["body"])

        return {
            "url": options["url"],
            "body": options.get("body"),
            "headers": http_headers,
            "method": options["method"],
            "transform_response": options.get("transformResponse"),
        }

    async def make_service_request(self, options: dict):
        async with self.http_client(
            method=options["method"],
            url=options["url"],
            headers=options["headers"],
            data=options["body"],
        ) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"HTTP {response.status}: {text}")

            body = await response.text()

            # Attempt to parse JSON body
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                pass

            if options.get("transform_response"):
                return options["transform_response"](body)
            return body

    @staticmethod
    def serialize(obj: dict) -> str:
        if obj:
            return urlencode(obj)
        return ""