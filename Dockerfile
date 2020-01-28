FROM python:3

ARG USER_ID
ARG GROUP_ID

# Setup user and group
RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

WORKDIR /home/user

COPY demo.sh .
COPY README.md .
COPY bin bin/
COPY machsmt machsmt/
COPY requirements.txt .
COPY setup.py .
COPY artifact-data.tar.xz .

# Install machsmt
RUN python3 setup.py develop --user
ENV PATH="/home/user/.local/bin:${PATH}"

# Unpack benchmarks and SMT-COMP'19 results
RUN tar xJf artifact-data.tar.xz
RUN rm artifact-data.tar.xz
