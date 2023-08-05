FROM python:3.11-alpine

WORKDIR /app

# Install dependencies needed for ssh-keygen
RUN apk add --no-cache openssh-keygen gcc musl-dev python3-dev

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Create certificates directory and generate SSH key
RUN mkdir -p ./certificates && ssh-keygen -t rsa -b 4096 -f ./certificates/id_rsa -N ""

ADD . .

EXPOSE 8080
EXPOSE 2222

CMD ["python", "start.py"]
