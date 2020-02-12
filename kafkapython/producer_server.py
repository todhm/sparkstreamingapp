import logging
import json
import time
from datetime import datetime as dt 
from confluent_kafka import avro, Consumer, Producer
from confluent_kafka.avro import AvroConsumer, AvroProducer, CachedSchemaRegistryClient

logger = logging.getLogger(__name__)


class ProducerServer(Producer):

    def __init__(self, input_file, topic,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.input_file = input_file
        self.topic = topic

    #TODO we're generating a dummy data
    def generate_data(self):
        with open(self.input_file) as f:
            data_list = json.load(f)
            
        #To produce data looks similar to real words I sorted data in timestamp order
        data_list = sorted(data_list,key=lambda x:dt.strptime(x['call_date_time'],"%Y-%m-%dT%H:%M:%S.%f"))

        
        for line in data_list:
            message = self.dict_to_binary(line)
            # TODO send the correct data
            try:
                self.produce(self.topic,message)
            except Exception as e:
                logger.error("Error producing data "+ str(e))

            time.sleep(1)

    # TODO fill this in to return the json dictionary to binary
    def dict_to_binary(self, json_dict):
        return json.dumps(json_dict).encode('utf-8')
        