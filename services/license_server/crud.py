import uuid
from sqlalchemy.orm import Session

from . import models, schemas


def create_license(db: Session, license_in: schemas.LicenseCreate) -> models.License:
    license_key = uuid.uuid4().hex
    db_license = models.License(
        key=license_key,
        license_type=license_in.license_type,
        expires_at=license_in.expires_at,
        allowed_domains=license_in.allowed_domains,
        plugins=license_in.plugins,
        settings=license_in.settings,
    )
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license


def get_license(db: Session, key: str) -> models.License | None:
    return db.query(models.License).filter(models.License.key == key).first()
