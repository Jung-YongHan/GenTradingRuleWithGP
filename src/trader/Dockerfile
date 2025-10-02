# 베이스 이미지 설정
FROM continuumio/miniconda3:23.10.0-1

#Docker 이미지 내부에서 RUN, CMD, ENTRYPOINT의 명령이 실행될 디렉터리를 설정합니다.
WORKDIR /app

# 현재 디렉터리에 있는 파일들을 이미지 내부 /app 디렉터리에 추가함
COPY . /app

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV TZ=Asia/Seoul

RUN conda install python=3.11 -y &&  \
    pip install -r ./requirements.txt --no-cache-dir &&\
    pip3 install torch --index-url "https://download.pytorch.org/whl/cpu" &&\
    conda install -c anaconda psycopg2==2.9.9 -y &&  \
    conda install -c conda-forge ta-lib==0.5.1 -y &&\
    conda clean -all
