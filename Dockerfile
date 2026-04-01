FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libxrender1 \
    libxext6 \
    libsm6

COPY . .

RUN pip install --upgrade pip
RUN pip install streamlit rdkit-pypi

EXPOSE 10000

CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.address=0.0.0.0"]