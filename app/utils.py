from passlib.context import CryptContext

# Initialize a password hashing context using the bcrypt algorithm, and automatically handle deprecated methods based on the "auto" setting.
# This context will be used for securely hashing and verifying passwords.
pwd_context =CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)