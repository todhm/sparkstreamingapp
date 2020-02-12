import os
import producer_server



def run_kafka_server():
	# TODO get the json file path
    input_file = "./datacollections/police-department-calls-for-service.json"

    # TODO fill in blanks
    KAFKA_URL = os.environ.get("BROKER_URL")
    producer = producer_server.ProducerServer(
        input_file,
        "kafkapython.kafka_server.sfcrime",
        {
            "bootstrap.servers":KAFKA_URL,
            "auto.offset.reset":"earliest",
            "group.id":"0"

        }
    )

    return producer


def feed():
    producer = run_kafka_server()
    producer.generate_data()


if __name__ == "__main__":
    feed()
