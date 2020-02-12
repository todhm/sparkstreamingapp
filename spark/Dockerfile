FROM bde2020/spark-submit:2.4.4-hadoop2.7


COPY template.sh /
WORKDIR /app
RUN apk add make automake gcc g++ subversion python3-dev
RUN python3 -m pip install --upgrade pip
COPY requirements_pyspark.txt /app/

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt /app/
RUN pip3 install -r requirements_pyspark.txt 
RUN pip3 install -r requirements.txt

# Copy the source code
COPY . /app
CMD ["/bin/bash", "/template.sh"]


