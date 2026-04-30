import requests
from django.conf import settings
from shared.domain.exceptions import ExternalServiceException
from shared.domain.value_objects import Ruc
from modules.empresa.domain.exceptions import RucInvalidoException


class SunatService:
    def __init__(self):
        self._api_url = settings.SUNAT_API_URL
        self._token   = settings.SUNAT_API_TOKEN
        self._timeout = 10

    def consultar_ruc(self, ruc: str) -> dict:
        Ruc(ruc)

        try:
            response = requests.get(
                f"{self._api_url}/{ruc}",
                headers={
                    "X-API-KEY":    self._token,
                    "Content-Type": "application/json",
                },
                timeout=self._timeout,
            )
        except requests.exceptions.Timeout:
            raise ExternalServiceException("SUNAT", "tiempo de espera agotado.")
        except requests.exceptions.ConnectionError:
            raise ExternalServiceException("SUNAT", "no se pudo establecer conexión.")

        if response.status_code == 401:
            raise ExternalServiceException("SUNAT", "API key inválida o sin permisos.")

        if response.status_code == 404:
            raise RucInvalidoException(ruc)

        if response.status_code == 429:
            raise ExternalServiceException("SUNAT", "límite de consultas alcanzado.")

        if not response.ok:
            raise ExternalServiceException("SUNAT", f"código de respuesta {response.status_code}.")

        data = response.json()

        if data.get("code") != "200" or data.get("mensaje") != "OK":
            raise RucInvalidoException(ruc)

        if data.get("estado") != "ACTIVO":
            raise RucInvalidoException(ruc)

        if data.get("condicion") != "HABIDO":
            raise RucInvalidoException(ruc)

        return {
            "ruc":              data.get("ruc", ruc),
            "razon_social":     data.get("razon_social", ""),
            "nombre_comercial": data.get("razon_social", ""),
            "direccion":        data.get("direccion", ""),
            "distrito":         data.get("distrito", ""),
            "provincia":        data.get("provincia", ""),
            "departamento":     data.get("departamento", ""),
            "ubigeo":           data.get("ubigeo", ""),
            "estado":           data.get("estado", ""),
            "condicion":        data.get("condicion", ""),
        }