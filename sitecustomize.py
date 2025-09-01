import bcrypt
from types import SimpleNamespace

# Ensure Passlib can read the bcrypt version even on newer releases
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", ""))
