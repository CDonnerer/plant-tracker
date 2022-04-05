"""My fun cloud function
"""

# TODO: logging.


def hello_world(event, context):
    print(f"Hello world {context.event_id}")
    print(f"Here's yer bucket... {event}")

    # print('Event ID:' , context.event_id)
    # print('Event type:', context.event_type)
    # print('Bucket:', event['bucket'])
    # print('File:',  event['name'])
    # print('Metageneration:',  event['metageneration'])
    # print('Created:',  event['timeCreated'])
    # print('Updated:',  event['updated'])

