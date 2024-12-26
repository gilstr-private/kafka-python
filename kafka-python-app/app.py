from kafka import KafkaProducer

def hello_world_producer():
    # Kafka configuration
    kafka_properties = {
        'bootstrap_servers': ['localhost:29092', 'localhost:29093', 'localhost:29094'],  # ❷
        'key_serializer': lambda k: k.encode('utf-8') if k else None,  # ❸
        'value_serializer': lambda v: v.encode('utf-8')  # ❸
    }

    # Create a Kafka producer
    producer = KafkaProducer(**kafka_properties)  # ❹

    try:
        # Create a producer record and send a message
        topic = "kinaction_helloworld"
        message = "hello world again!"  # ❺
        producer.send(topic, value=message)  # ❻
        print(f"Message sent to topic {topic}: {message}")
    finally:
        # Close the producer
        producer.close()




if __name__ == "__main__":
    hello_world_producer()