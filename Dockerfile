FROM python:3.11.0rc1-alpine AS builder
COPY . /app
WORKDIR /app

# We are installing a dependency here directly into our app source dir
RUN pip install --target=/app --requirement /app/requirements.txt

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]
