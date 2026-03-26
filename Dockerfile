# Dockerfile - src/backend/Dockerfile

FROM python:3.12-slim

# Instala git e outras dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    git \
    && apt-get clean

# Diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências
COPY ./requirements.txt /app/requirements.txt

# Instala as dependências do Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --upgrade -r requirements.txt

# Expõe a porta 7860
EXPOSE 7860

# Copia o restante da aplicação
COPY ./src ./src

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.backend.app.main:app", "--host", "0.0.0.0", "--port", "7860"]
