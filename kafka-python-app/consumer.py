import logging
import signal
import threading
import fastavro
import json
import io
from kafka import KafkaConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient, SchemaRegistryError
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HelloWorldConsumer")


class HelloWorldConsumer:
    def __init__(self, avro_deserializer, kafka_properties, schema_registry_client):
        self.keep_consuming = True  # Flag to control consumption loop
        self.lock = threading.Lock()  # Lock to synchronize access to shared resources
        self.avro_deserializer = avro_deserializer
        self.kafka_properties = kafka_properties
        self.schema_registry_client = schema_registry_client

    def consume(self):
        # Create Kafka consumer
        consumer = KafkaConsumer(
            self.kafka_properties["topic"],
            bootstrap_servers=self.kafka_properties["bootstrap_servers"],
            group_id=self.kafka_properties["group_id"],
            enable_auto_commit=self.kafka_properties["enable_auto_commit"],
            auto_offset_reset="earliest",
        )
        logger.info("Subscribed to topic: %s", self.kafka_properties["topic"])

        try:
            # Fetch schema from Schema Registry
            subject = f"{self.kafka_properties['topic']}-value"
            schema = self.schema_registry_client.get_latest_version(subject).schema.schema_str
            parsed_schema = fastavro.parse_schema(json.loads(schema))

            # Main consumption loop
            while self.is_consuming():
                records = consumer.poll(timeout_ms=250)  # Poll for records
                for topic_partition, messages in records.items():
                    for message in messages:
                        try:
                            logger.info("Raw message value: %s", message.value)# Decode Avro message using fastavro
                            decoded_value = fastavro.schemaless_reader(
                                io.BytesIO(message.value), parsed_schema
                            )
                            logger.info(
                                "kinaction_info offset = %s, topic partition = %s, kinaction_value = %s",
                                message.offset,
                                topic_partition,
                                decoded_value,  # Decoded Avro message
                            )
                        except Exception as e:
                            logger.error("Failed to decode message: %s", e)
        except SchemaRegistryError as e:
            logger.error("Failed to fetch schema from registry: %s", e)
        finally:
            consumer.close()
            logger.info("Consumer closed")
    def is_consuming(self):
        with self.lock:
            return self.keep_consuming

    def shutdown(self):
        # Gracefully stop the consumer
        with self.lock:
            self.keep_consuming = False


def main():
    # Kafka configuration
    kafka_properties = {
        "bootstrap_servers": ["localhost:29092", "localhost:29093", "localhost:29094"],
        "group_id": "kinaction_helloconsumer",
        "enable_auto_commit": True,
        "auto_commit_interval_ms": 1000,
        "topic": "kinaction_helloworld",
    }

    schema_registry_config = {
        'url': 'http://localhost:8081'
    }

    schema_registry_client = SchemaRegistryClient(schema_registry_config)

    # Create Avro deserializer
    avro_deserializer = AvroDeserializer(
        schema_registry_client=schema_registry_client
    )

    # Instantiate the consumer
    hello_world_consumer = HelloWorldConsumer(avro_deserializer, kafka_properties, schema_registry_client)

    # Graceful shutdown handling
    def handle_shutdown(signal, frame):
        logger.info("Shutdown signal received")
        hello_world_consumer.shutdown()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Start consuming
    hello_world_consumer.consume()


if __name__ == "__main__":
    main()