import os
from typing import List, Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title="DocCropper Simple Webapp")

security = HTTPBasic()

# in-memory store for licenses
LICENSES: Dict[str, Dict] = {
    # Pre-populated demo license limited to a test domain
    "demo-full": {
        "id": "demo-full",
        "customer": "Demo User",
        "product": "DocCropper",
        "license_type": "demo_full",
        "allowed_domains": ["test.example.com"],
        "feature_flags": {},
    }
}


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
    license_type: str = "free"
    allowed_domains: List[str] = []
    feature_flags: Dict[str, bool] = {}


class LicenseCreate(BaseModel):
    customer: str
    product: str
    license_type: str = "free"
    allowed_domains: Optional[List[str]] = None
    feature_flags: Dict[str, bool] = {}


@app.get("/licenses", response_model=List[License])
def list_licenses(user: str = Depends(get_current_user)):
    return list(LICENSES.values())


@app.post("/licenses", response_model=License, status_code=status.HTTP_201_CREATED)
def create_license(data: LicenseCreate, user: str = Depends(get_current_user)):
    license_id = str(uuid4())
    payload = data.dict()
    if payload.get("allowed_domains") is None:
        payload["allowed_domains"] = []
    lic = License(id=license_id, **payload)
    LICENSES[license_id] = lic.dict()
    return lic


@app.get("/licenses/{license_id}", response_model=License)
def get_license(license_id: str, user: str = Depends(get_current_user)):
    lic = LICENSES.get(license_id)
    if not lic:
        raise HTTPException(status_code=404, detail="License not found")
    return lic


@app.delete("/licenses/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_license(license_id: str, user: str = Depends(get_current_user)):
    if license_id in LICENSES:
        del LICENSES[license_id]
    return None


@app.get("/verify")
def verify_license_endpoint(license_id: str, domain: Optional[str] = None):
    """Simple verification endpoint returning license info."""
    lic = LICENSES.get(license_id)
    if not lic:
        return {"valid": False}
    domains = lic.get("allowed_domains") or []
    if domain and domains and domain not in domains:
        return {"valid": False}
    features = [name for name, ok in lic.get("feature_flags", {}).items() if ok]
    return {
        "valid": True,
        "license_type": lic.get("license_type", "free"),
        "features": features,
    }

