# ARG
ARG WORKDIR=/opt/workspace
ARG LIB_PATH=/opt/python_libs


# Build
FROM python:3.7.9-alpine3.12 as build
ARG LIB_PATH

# Install
COPY requirements/web.txt requirements.txt
RUN pip install -t $LIB_PATH -r requirements.txt




# Output
FROM python:3.7.9-alpine3.12
ARG LIB_PATH
ARG WORKDIR
WORKDIR $WORKDIR

# ENV
ENV PYTHONPATH=$LIB_PATH
ENV PATH=$PATH:$LIB_PATH/bin

# User
RUN adduser -HD -u 1001 user
RUN chown -R user $WORKDIR
USER user

# Source
COPY --chown=user --from=build $LIB_PATH $LIB_PATH
COPY --chown=user src/db src/db
COPY --chown=user src/util src/util
COPY --chown=user src/web src/web

# CMD
CMD ["gunicorn", "-b", "0.0.0.0:5000", "src.web.web:app"]