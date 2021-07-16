ARG PYTHON_VERSION=3.9.6

FROM python:${PYTHON_VERSION}-alpine
LABEL maintainer="Insights Engineering <insightsengineering@example.com>"

# Build arguments
ARG APP_NAME="ghm"
ARG SRC_DIR="/usr/src/${APP_NAME}"
ARG USER="${APP_NAME}"
ARG USER_ID=101
ARG USER_GROUP="${APP_NAME}"
ARG USER_GROUP_ID=101
ARG USER_HOME="/home/${USER}"
ENV APP_NAME="${APP_NAME}"

# Add deps, create a non-root user and group,
# and create source dir
RUN apk update --no-cache && \
    apk add --no-cache gcc musl-dev libffi-dev make && \
    rm -rf /var/cache/apk/* && \
    addgroup -S -g ${USER_GROUP_ID} ${USER_GROUP} && \
    adduser -S -u ${USER_ID} -h ${USER_HOME} -G ${USER_GROUP} ${USER} && \
    mkdir -p ${SRC_DIR}

# Copy source files
COPY . ${SRC_DIR}/

# Install sereno
WORKDIR ${SRC_DIR}
RUN python3 setup.py install

# Set the user and work directory
USER ${USER_ID}
WORKDIR ${USER_HOME}

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/${APP_NAME}"]
