# Custom Airflow Docker Image with dbt and additional requirements
FROM apache/airflow:2.7.0-python3.11

# Switch to root user to install system dependencies
USER root

# Install system dependencies including MySQL client libraries
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --user -r /requirements.txt

# Set environment variables
ENV PYTHONPATH="${PYTHONPATH}:/opt/airflow"