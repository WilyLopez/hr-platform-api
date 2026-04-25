from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from modules.usuario.domain.exceptions import TokenInvalidoException


class JwtService:
    def generar_tokens(self, usuario, rol_nombre: str) -> dict:
        refresh = RefreshToken.for_user(self._fake_user(usuario))
        refresh["usuario_id"] = usuario.id
        refresh["empresa_id"] = usuario.empresa_id
        refresh["codigo_unico"] = str(usuario.codigo_unico)
        refresh["rol"] = rol_nombre
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def refrescar_access_token(self, refresh_token: str) -> str:
        try:
            token = RefreshToken(refresh_token)
            return str(token.access_token)
        except TokenError:
            raise TokenInvalidoException()

    def invalidar_refresh_token(self, refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise TokenInvalidoException()

    def _fake_user(self, usuario):
        class _User:
            pk = usuario.id
            id = usuario.id

        return _User()


class PasswordService:
    def hash(self, raw_password: str) -> str:
        from django.contrib.auth.hashers import make_password
        return make_password(raw_password)

    def verify(self, raw_password: str, hashed: str) -> bool:
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, hashed)

    def generar_temporal(self) -> str:
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(12))