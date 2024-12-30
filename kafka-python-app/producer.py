import time

from confluent_kafka.serialization import SerializationContext, MessageField
from kafka import KafkaProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

import json

def load_avro_schema(file_path):
    with open(file_path, 'r') as schema_file:
        return schema_file.read()
def avro_serializer_with_context(serializer, topic):
    def serialize(value):
        context = SerializationContext(topic,MessageField.VALUE)
        return serializer(value, context)
    return serialize

def hello_world_producer():
    # Kafka configuration
    kafka_properties = {
        'bootstrap_servers': ['localhost:29092', 'localhost:29093', 'localhost:29094'],  # ❷
    }

    sechema_registry_config = {
        'url': 'http://localhost:8081'
    }

    avro_schema = load_avro_schema('../kafka-schemas/hello_world.avsc')
    schema_registry_client = SchemaRegistryClient(sechema_registry_config)

    avro_serializer = AvroSerializer(schema_registry_client, avro_schema)
    value_serializer = avro_serializer_with_context(avro_serializer, "kinaction_helloworld")
    # Create a Kafka producer
    producer = KafkaProducer(
        key_serializer=lambda k:k.encode('utf-8') if k else None,
        value_serializer=value_serializer,
        **kafka_properties)  # ❹

    try:
        # Create a producer record and send a message
        topic = "kinaction_helloworld"
        message = {"message": f"hello world again! {time.time_ns()}"}
        serialized_message = value_serializer(message)
        print(f"Serialized message: {serialized_message}")
        producer.send(topic, value=message)  # ❻
        print(f"Message sent to topic {topic}: {message}")
    finally:
        # Close the producer
        producer.close()




if __name__ == "__main__":
    hello_world_producer()