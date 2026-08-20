"""HTTP-facing logic for the jwt-decoder tool."""

from fastapi import HTTPException

from app.modules.devtools.services.jwt_service import jwt_service


class JwtController:
    def jwt_decode(self, token: str) -> dict:
        try:
            return {"success": True, "data": jwt_service.jwt_decode(token)}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err)) from err


jwt_controller = JwtController()
