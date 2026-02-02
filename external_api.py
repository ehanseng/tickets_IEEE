"""
API Externa para módulos independientes.
Permite que aplicaciones externas se autentiquen y consulten datos del núcleo
usando API Keys y tokens temporales de usuario.
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session, joinedload
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/external", tags=["External API"])


# ============================================================
# DEPENDENCIAS DE SEGURIDAD
# ============================================================

async def validate_api_key(
    x_api_key: str = Header(..., description="API Key del módulo externo"),
    db: Session = Depends(get_db)
) -> models.ExternalModule:
    """Valida que el API Key corresponda a un módulo activo"""
    module = db.query(models.ExternalModule).filter(
        models.ExternalModule.api_key == x_api_key,
        models.ExternalModule.is_active == True
    ).first()
    if not module:
        raise HTTPException(status_code=401, detail="API Key inválida")
    return module


def require_scope(scope: str):
    """Genera una dependencia que verifica que el módulo tenga el scope requerido"""
    async def checker(
        module: models.ExternalModule = Depends(validate_api_key)
    ) -> models.ExternalModule:
        scopes = json.loads(module.allowed_scopes)
        if scope not in scopes:
            raise HTTPException(
                status_code=403,
                detail=f"El módulo no tiene permiso para el scope: {scope}"
            )
        return module
    return checker


# ============================================================
# AUTENTICACIÓN DE USUARIOS
# ============================================================

@router.post("/auth/verify", response_model=schemas.ExternalAuthVerifyResponse)
def verify_user_token(
    body: schemas.ExternalAuthVerifyRequest,
    module: models.ExternalModule = Depends(validate_api_key),
    db: Session = Depends(get_db)
):
    """
    Verifica un token temporal de usuario.
    El módulo externo envía el token que recibió en la redirección.
    Retorna los datos básicos del usuario si el token es válido.
    El token se marca como usado (un solo uso).
    """
    token_record = db.query(models.ExternalUserToken).filter(
        models.ExternalUserToken.token == body.user_token,
        models.ExternalUserToken.module_id == module.id,
        models.ExternalUserToken.used == False,
        models.ExternalUserToken.expires_at > datetime.utcnow()
    ).first()

    if not token_record:
        return schemas.ExternalAuthVerifyResponse(valid=False)

    token_record.used = True
    db.commit()

    user = token_record.user
    return schemas.ExternalAuthVerifyResponse(
        valid=True,
        user=schemas.ExternalUserInfo(
            id=user.id,
            name=user.name,
            email=user.email,
            branch_role=user.branch_role,
            is_ieee_member=user.is_ieee_member
        ),
        module=module.name
    )


# ============================================================
# PROYECTOS
# ============================================================

@router.get("/projects/active", response_model=list[schemas.ExternalProjectResponse])
def get_active_projects(
    module: models.ExternalModule = Depends(require_scope("projects")),
    db: Session = Depends(get_db)
):
    """Lista todos los proyectos activos"""
    projects = db.query(models.Project).filter(
        models.Project.status == models.ProjectStatus.active
    ).order_by(models.Project.display_order).all()
    return projects


@router.get("/projects/{project_id}/members", response_model=list[schemas.ExternalProjectMemberResponse])
def get_project_members(
    project_id: int,
    module: models.ExternalModule = Depends(require_scope("projects")),
    db: Session = Depends(get_db)
):
    """Lista los miembros asignados a un proyecto"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    # Consultar miembros con su rol en el proyecto
    from sqlalchemy import text
    result = db.execute(
        text("""
            SELECT u.id, u.name, u.email, pm.role
            FROM project_members pm
            JOIN users u ON u.id = pm.user_id
            WHERE pm.project_id = :project_id
        """),
        {"project_id": project_id}
    ).fetchall()

    return [
        schemas.ExternalProjectMemberResponse(
            id=row[0], name=row[1], email=row[2], role=row[3]
        )
        for row in result
    ]


# ============================================================
# REUNIONES
# ============================================================

@router.get("/meetings", response_model=list[schemas.MeetingResponse])
def get_meetings(
    upcoming_only: bool = True,
    project_id: int = None,
    module: models.ExternalModule = Depends(require_scope("meetings")),
    db: Session = Depends(get_db)
):
    """Lista reuniones. Por defecto solo las próximas."""
    query = db.query(models.Meeting).filter(models.Meeting.is_active == True)

    if upcoming_only:
        query = query.filter(models.Meeting.meeting_date >= datetime.utcnow())

    if project_id:
        query = query.filter(models.Meeting.project_id == project_id)

    return query.order_by(models.Meeting.meeting_date).all()


@router.post("/meetings", response_model=schemas.MeetingResponse)
def create_meeting(
    body: schemas.MeetingCreate,
    module: models.ExternalModule = Depends(require_scope("meetings")),
    db: Session = Depends(get_db)
):
    """Crear una reunión"""
    meeting = models.Meeting(
        title=body.title,
        description=body.description,
        meeting_type=models.MeetingType(body.meeting_type),
        meeting_date=body.meeting_date,
        duration_minutes=body.duration_minutes,
        location=body.location,
        virtual_link=body.virtual_link,
        project_id=body.project_id
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/meetings/{meeting_id}/attendance", response_model=list[schemas.AttendanceResponse])
def get_meeting_attendance(
    meeting_id: int,
    module: models.ExternalModule = Depends(require_scope("meetings")),
    db: Session = Depends(get_db)
):
    """Ver la asistencia de una reunión"""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")

    attendances = db.query(models.MeetingAttendance).options(
        joinedload(models.MeetingAttendance.user)
    ).filter(
        models.MeetingAttendance.meeting_id == meeting_id
    ).all()

    return [
        schemas.AttendanceResponse(
            id=a.id,
            meeting_id=a.meeting_id,
            user_id=a.user_id,
            user_name=a.user.name if a.user else None,
            attended=a.attended,
            checked_in_at=a.checked_in_at,
            notes=a.notes
        )
        for a in attendances
    ]


@router.post("/meetings/{meeting_id}/attendance", response_model=dict)
def record_attendance(
    meeting_id: int,
    body: schemas.AttendanceBulkRequest,
    module: models.ExternalModule = Depends(require_scope("meetings")),
    db: Session = Depends(get_db)
):
    """Registrar asistencia en bloque para una reunión"""
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Reunión no encontrada")

    for record in body.records:
        existing = db.query(models.MeetingAttendance).filter(
            models.MeetingAttendance.meeting_id == meeting_id,
            models.MeetingAttendance.user_id == record.user_id
        ).first()

        if existing:
            existing.attended = record.attended
            existing.notes = record.notes
            if record.attended and not existing.checked_in_at:
                existing.checked_in_at = datetime.utcnow()
        else:
            db.add(models.MeetingAttendance(
                meeting_id=meeting_id,
                user_id=record.user_id,
                attended=record.attended,
                checked_in_at=datetime.utcnow() if record.attended else None,
                notes=record.notes
            ))

    db.commit()
    return {"message": "Asistencia registrada", "records": len(body.records)}


# ============================================================
# MIEMBROS
# ============================================================

@router.get("/members", response_model=list[schemas.ExternalMemberResponse])
def get_members(
    module: models.ExternalModule = Depends(require_scope("members")),
    db: Session = Depends(get_db)
):
    """Lista todos los miembros activos de la rama (info mínima)"""
    users = db.query(models.User).order_by(models.User.name).all()
    return users
