from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.config import limiter
from app.schemas.loan_schema import LoanCreate, LoanResponse, LoanDetailResponse, LoanStatus
from app.services.loan_service import (
    get_all_loans,
    get_loan_by_id,
    create_loan,
    return_loan,
    get_loans_with_details,
)
from app.dependencies.database_dependency import get_db
from app.dependencies.auth_dependency import get_current_active_user, require_role
from app.models.user_model import User

router = APIRouter(prefix="/loans", tags=["Loans"])


def set_custom_headers(response: Response):
    """Cabeceras por respuesta (X-API-Version especifica)."""
    response.headers["X-API-Version"] = "4.0"


@router.get(
    "/",
    response_model=list[LoanResponse],
    summary="Listar prestamos",
    description="Devuelve la lista de prestamos. Permite filtrar por estado, usuario o dispositivo.",
    response_description="Lista de prestamos encontrados",
)
def get_loans(
    response: Response,
    db: Session = Depends(get_db),
    status: Optional[LoanStatus] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
):
    set_custom_headers(response)
    return get_all_loans(db, status=status, user_id=user_id, device_id=device_id)


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Listar prestamos con detalle",
    description="Devuelve los prestamos usando un join con usuarios y dispositivos. Permite filtrar por estado, email del usuario o tipo de dispositivo.",
    response_description="Lista de prestamos con informacion relacionada",
)
def get_loan_details(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "support")),
    status: Optional[LoanStatus] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
):
    set_custom_headers(response)
    return get_loans_with_details(db, status=status, user_email=user_email, device_type=device_type)


@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Consultar prestamo por ID",
    description="Busca y devuelve un prestamo por su ID. Si no existe responde con 404.",
    response_description="Prestamo encontrado",
)
def get_loan(loan_id: int, response: Response, db: Session = Depends(get_db)):
    set_custom_headers(response)
    return get_loan_by_id(db, loan_id)


@router.post(
    "/",
    response_model=LoanResponse,
    status_code=201,
    summary="Crear prestamo",
    description="Registra un nuevo prestamo. Valida que el usuario y el dispositivo existan y que el dispositivo este disponible.",
    response_description="Prestamo creado exitosamente",
)
@limiter.limit("10/minute")
def post_loan(
    request: Request,
    loan: LoanCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    set_custom_headers(response)
    return create_loan(db, loan)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver dispositivo",
    description="Marca el prestamo como devuelto, asigna la fecha de devolucion y libera el dispositivo. Si el prestamo ya fue devuelto responde con 409.",
    response_description="Prestamo devuelto exitosamente",
)
def patch_return_loan(
    loan_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "support")),
):
    set_custom_headers(response)
    return return_loan(db, loan_id)
