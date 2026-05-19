# --- STAGE 1: The Builder ---
FROM alpine:latest AS builder

# Install build tools
RUN apk add --no-cache git make g++ 

# Clone the official Stockfish repository
WORKDIR /src
RUN git clone https://github.com/official-stockfish/Stockfish.git .

# Move to the source directory and compile
WORKDIR /src/src
RUN make -j net
RUN make -j build ARCH=x86-64-modern

# --- STAGE 2: The Final Image ---
FROM python:3.12-alpine

# Install only the runtime libraries Stockfish needs
RUN apk add --no-cache libstdc++ libgcc

# Copy the compiled binary from the builder stage
# Standard Stockfish build creates the binary in /src/src/
COPY --from=builder /src/src/stockfish /usr/bin/stockfish

WORKDIR /app

RUN pip install --no-cache-dir python-chess

COPY analyze.py .

ENTRYPOINT ["python", "analyze.py"]