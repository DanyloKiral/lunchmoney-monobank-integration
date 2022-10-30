FROM alpine:3.15

# define args
ARG CONFIG_ENV

# set env
#ENV CRON_EXP=$CRON_EXP

# Install required packages
RUN apk add --update --no-cache bash dos2unix

# Install python/pip
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip --upgrade
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/scheduler

# Copy files
COPY jobs/*.* ./jobs/
COPY crontab.* ./
COPY start.sh .

COPY flow/*.py ./flow/
COPY lunchmoney_api/*.py ./lunchmoney_api/
COPY mono_api/*.py ./mono_api/
COPY utils/*.py ./utils/
COPY crontab.* ./
COPY crontab .
COPY start.sh .
COPY integrator.py .
COPY requirements.txt .
COPY config.$CONFIG_ENV.json ./config.json
COPY credentials.$CONFIG_ENV.json ./credentials.json

# install any Python requirements used by the jobs
RUN pip3 install -r requirements.txt

# Fix line endings && execute permissions
RUN dos2unix crontab *.sh *.py \
    && \
    find . -type f -iname "*.sh" -exec chmod +x {} \
    && \
    find . -type f -iname "*.py" -exec chmod +x {} \;

# create cron.log file
RUN touch /var/log/cron.log

# Run cron on container startup
CMD ["./start.sh"]