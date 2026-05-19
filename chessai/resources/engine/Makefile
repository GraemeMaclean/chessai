# --- Configuration Variables ---
IMAGE_NAME = stockfish-analyzer
START_FEN  = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

.PHONY: default build test run clean info

default: info

## build: Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

## test: Run the test script
test:
	chmod +x test.sh
	./test.sh

## run: Run an interactive, analysis instance with the default starting FEN
run:
	docker run --rm $(IMAGE_NAME) $(START_FEN) "" 15

## clean: Remove build images and clear dangling layers
clean:
	@docker rmi $(IMAGE_NAME) 2>/dev/null || true
	@docker rmi $$(docker images -f "dangling=true" -q) 2>/dev/null || true

## info: Show this command menu with descriptions
info:
	@echo "Available commands:"
	@awk '/^##/{sub(/^## /, ""); split($$0, a, ":"); printf "  %-10s %s\n", a[1], a[2]}' Makefile