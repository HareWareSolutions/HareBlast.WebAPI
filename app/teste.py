from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha = "teste4040"
hash = pwd_context.hash(senha)
print(hash)
