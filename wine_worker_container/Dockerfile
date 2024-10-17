FROM ubuntu:20.04

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN DEBIAN_FRONTEND=noninteractive \
    dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    mingw-w64 \
    cmake \
    make \
    wine64 \
    wine32 \
    xvfb \
    && apt-get clean

WORKDIR /app

COPY build_and_run.sh /app/build_and_run.sh

RUN chmod +x /app/build_and_run.sh

CMD ["/app/build_and_run.sh"]