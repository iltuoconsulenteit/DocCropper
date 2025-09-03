import os
from typing import List, Dict
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(
    title="DocCropper Simple Webapp",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

security = HTTPBasic()

# in-memory store for licenses
LICENSES: Dict[str, Dict] = {}


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.getenv("WEBAPP_USER", "admin")
    password = os.getenv("WEBAPP_PASSWORD", "admin")
    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class License(BaseModel):
    id: str
    customer: str
    product: str
    feature_flags: Dict[str, bool] = {}


class LicenseCreate(BaseModel):
    customer: str
    product: str
    feature_flags: Dict[str, bool] = {}


@app.get(
    "/licenses",
    response_model=List[License],
    summary="Elenco delle licenze disponibili",
    responses={200: {"description": "Lista delle licenze"}, 401: {"description": "Credenziali non valide"}},
)
def list_licenses(user: str = Depends(get_current_user)):
    return list(LICENSES.values())


@app.post(
    "/licenses",
    response_model=License,
    status_code=status.HTTP_201_CREATED,
    summary="Crea una nuova licenza",
    responses={
        201: {"description": "Licenza creata"},
        401: {"description": "Credenziali non valide"},
    },
)
def create_license(data: LicenseCreate, user: str = Depends(get_current_user)):
    license_id = str(uuid4())
    lic = License(id=license_id, **data.dict())
    LICENSES[license_id] = lic.dict()
    return lic


@app.get(
    "/licenses/{license_id}",
    response_model=License,
    summary="Recupera una licenza esistente",
    responses={
        200: {"description": "Licenza trovata"},
        401: {"description": "Credenziali non valide"},
        404: {"description": "Licenza non trovata"},
    },
)
def get_license(license_id: str, user: str = Depends(get_current_user)):
    lic = LICENSES.get(license_id)
    if not lic:
        raise HTTPException(status_code=404, detail="License not found")
    return lic

