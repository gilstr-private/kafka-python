import logging
import signal
import threading

from kafka import KafkaConsumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HelloWorldConsumer")

class HelloWorldConsumer:
    def __init__(self):
        self.keep_consuming = True  # Flag to control consumption loop
        self.lock = threading.Lock()  # Lock to synchronize access to shared resources

    def consume(self, kafka_properties):
        # Create Kafka consumer
        consumer = KafkaConsumer(
            kafka_properties["topic"],
            bootstrap_servers=kafka_properties["bootstrap_servers"],
            group_id=kafka_properties["group_id"],
            enable_auto_commit=kafka_properties["enable_auto_commit"],
            auto_commit_interval_ms=kafka_properties["auto_commit_interval_ms"],
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            value_deserializer=lambda v: v.decode("utf-8"),
        )
        logger.info("Subscribed to topic: %s", kafka_properties["topic"])

        try:
            # Main consumption loop
            while self.is_consuming():
                records = consumer.poll(timeout_ms=250)  # Poll for records
                for topic_partition, messages in records.items():
                    for message in messages:
                        logger.info(
                            "kinaction_info offset = %s, topic partition = %s, kinaction_value = %s",
                            message.offset,
                            topic_partition,
                            message.value,
                        )
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

    # Instantiate the consumer
    hello_world_consumer = HelloWorldConsumer()

    # Graceful shutdown handling
    def handle_shutdown(signal, frame):
        logger.info("Shutdown signal received")
        hello_world_consumer.shutdown()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Start consuming
    hello_world_consumer.consume(kafka_properties)

if __name__ == "__main__":
    main()