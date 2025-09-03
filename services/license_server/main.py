from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import crud, schemas, models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="License Server")


@app.post("/licenses", response_model=schemas.LicenseResponse)
def issue_license(license_in: schemas.LicenseCreate, db: Session = Depends(get_db)):
    return crud.create_license(db, license_in)


@app.get("/verify", response_model=schemas.LicenseVerifyResponse)
def verify_license(email: str, license: str, token: str, db: Session = Depends(get_db)):
    db_license = crud.get_license(db, license)
    return schemas.LicenseVerifyResponse(valid=db_license is not None, license=db_license)
