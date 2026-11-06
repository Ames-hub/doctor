from library.settings import settings
from library.routes import router
from library import security
import requests
import fastapi
import uvicorn
import os

uuid = settings.pc_uuid4().get()

class client:
    @staticmethod
    def send_packet(route:str, data:dict):
        if route.startswith("/"):
            route.replace("/", "", count=1)  # Removes the / from the start of a route

        host: str = settings.hub_server_host().get()
        use_https: bool = settings.enforce_https().get()

        host = f"https://{host}/{route}" if use_https else f"http://{host}/{route}"

        if not host:
            raise ValueError("Hub server host is not configured!")

        # Refuse insecure connections when HTTPS is required
        if use_https and not host.startswith("https://"):
            raise ValueError("HTTPS is required!")

        try:
            response = requests.post(
                host,
                json=data,
                cookies={"uuid": uuid},
                timeout=15,
                verify=True
            )

            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Hub connection failed: {e}")
            return False

    @staticmethod
    def send_health_report(data:dict):
        return client.send_packet("receive-health-report", data)

class server:
    @staticmethod
    async def run():
        port = settings.hub_server_port().get()
        use_https = settings.enforce_https().get()

        fastapp = fastapi.FastAPI()
        fastapp.include_router(router)

        config = uvicorn.Config(
            fastapp,
            host="0.0.0.0",
            port=port,
            loop="asyncio",
            lifespan="on",
            reload=False,
        )

        if use_https:
            os.makedirs("certs", exist_ok=True)
            if not os.path.exists("certs/private.key") or not os.path.exists("certs/public.crt"):
                security.generate_self_signed_cert()
            config.ssl_keyfile = "certs/private.key",
            config.ssl_certfile = "certs/public.crt",

        server = uvicorn.Server(config)
        await server.serve()