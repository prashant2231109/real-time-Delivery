# 
from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError
import json
from home.models import LocationUpdate

class Command(BaseCommand):
    help = "Run kafka consumer to listen for location update"
    
    def handle(self, *args, **options):
        conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': "location_group",
            'auto.offset.reset': 'earliest'
        }

        consumer = Consumer(conf)
        consumer.subscribe(["location_updates"])  # <-- Make sure this is the correct topic

        try:
            while True:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Kafka error: {msg.error()}")
                        break

                data = json.loads(msg.value().decode('utf-8'))

                LocationUpdate.objects.create(
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    timestamp=data.get('timestamp')  # safer
                )

                print(f"Received location update: {data}")
        except KeyboardInterrupt:
            print("Consumer stopped.")
        finally:
            consumer.close()
