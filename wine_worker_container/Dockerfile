FROM ubuntu:20.04

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
    mingw-w64 \
    wine64 \
    wine32 \
    xvfb \
    dos2unix \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./build_and_run.sh /app/build_and_run.sh

RUN dos2unix /app/build_and_run.sh

RUN chmod +x /app/build_and_run.sh

CMD ["/app/build_and_run.sh"]