import json
import boto3
import re
from datetime import datetime
from boto3.dynamodb.conditions import Attr
import os

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Get from environment variables
TABLE_NAME = os.environ.get('CONTACTS_TABLE_NAME', 'ContactsTable')
SNS_TOPIC_ARN = os.environ.get('EMAIL_SNS_TOPIC_ARN')

if not SNS_TOPIC_ARN:
    raise ValueError("EMAIL_SNS_TOPIC_ARN environment variable is required")

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        print(f"Event recibido: {json.dumps(event, default=str)}")
        
        # Handle API Gateway event
        if 'body' in event:
            if isinstance(event['body'], str):
                body = json.loads(event['body'])
            else:
                body = event['body']
        else:
            body = event
        
        print(f"Body parseado: {json.dumps(body, default=str)}")
        
        method = body.get('method', '').lower()
        message_id = body.get('id')
        
        if not message_id:
            return response(400, {'error': 'ID es requerido'})
        
        if method == 'valid':
            return handle_valid(body, message_id)
        elif method == 'send':
            return handle_send(body, message_id)
        else:
            return response(400, {'error': 'Método inválido. Use "valid" o "send"'})
        
    except Exception as e:
        print(f"Error completo: {str(e)}")
        import traceback
        traceback.print_exc()
        return response(500, {'error': str(e)})


def handle_valid(body, message_id):
    contact_type = body.get('type')
    
    if contact_type == 'phone':
        return add_contact_phone(body, message_id)
    elif contact_type == 'email':
        return add_contact_email(body, message_id)
    else:
        return response(400, {'error': 'Tipo de contacto inválido'})


def handle_send(body, message_id):
    message_text = body.get('message')
    
    if not message_text:
        return response(400, {'error': 'Mensaje es requerido'})
    
    return send_contact_message(message_text, message_id)


def add_contact_phone(data, message_id):
    validated = validate_phone(data)
    
    if not validated['valid']:
        return response(400, {'error': validated['message']})
    
    lada = data.get('lada', '')
    number = data.get('number', '')
    full_number = (lada + number).replace(' ', '').replace('-', '')
    
    existing = check_existing_contact('phone', full_number)
    
    if existing:
        subscription_arn = existing.get('subscriptionArn', '')
        
        if subscription_arn and subscription_arn != 'pending confirmation':
            contact_id = str(int(datetime.now().timestamp() * 1000))
            save_contact_phone(contact_id, lada, number, full_number, message_id, subscription_arn)
            
            return response(200, {
                'message': 'Contacto ya existe en SNS. Agregado a DynamoDB con nuevo ID',
                'contactId': contact_id,
                'subscriptionArn': subscription_arn,
                'alreadySubscribed': True
            })
    
    contact_id = str(int(datetime.now().timestamp() * 1000))
    save_contact_phone(contact_id, lada, number, full_number, message_id, None)
    
    subscription_result = subscribe_phone_to_sns(full_number, contact_id)
    
    if not subscription_result['success']:
        return response(500, {
            'error': 'No se pudo suscribir el contacto',
            'details': subscription_result.get('error')
        })
    
    table.update_item(
        Key={'contactId': contact_id},
        UpdateExpression='SET subscriptionArn = :arn',
        ExpressionAttributeValues={':arn': subscription_result['subscriptionArn']}
    )
    
    return response(200, {
        'message': 'Contacto guardado y suscrito. Confirmación enviada automáticamente.',
        'contactId': contact_id,
        'subscriptionArn': subscription_result['subscriptionArn'],
        'endpoint': subscription_result['endpoint'],
        'awaitingConfirmation': subscription_result.get('awaitingConfirmation')
    })


def add_contact_email(data, message_id):
    validated = validate_email(data)
    
    if not validated['valid']:
        return response(400, {'error': validated['message']})
    
    email = data.get('email', '')
    domains = data.get('domains', '')
    full_email = email + domains
    
    existing = check_existing_contact('email', full_email)
    
    if existing:
        subscription_arn = existing.get('subscriptionArn', '')
        
        if subscription_arn and subscription_arn != 'pending confirmation':
            contact_id = str(int(datetime.now().timestamp() * 1000))
            save_contact_email(contact_id, email, domains, full_email, message_id, subscription_arn)
            
            return response(200, {
                'message': 'Contacto ya existe en SNS. Agregado a DynamoDB con nuevo ID',
                'contactId': contact_id,
                'subscriptionArn': subscription_arn,
                'alreadySubscribed': True
            })
    
    contact_id = str(int(datetime.now().timestamp() * 1000))
    save_contact_email(contact_id, email, domains, full_email, message_id, None)
    
    subscription_result = subscribe_email_to_sns(full_email, contact_id)
    
    if not subscription_result['success']:
        return response(500, {
            'error': 'No se pudo suscribir el contacto',
            'details': subscription_result.get('error')
        })
    
    table.update_item(
        Key={'contactId': contact_id},
        UpdateExpression='SET subscriptionArn = :arn',
        ExpressionAttributeValues={':arn': subscription_result['subscriptionArn']}
    )
    
    return response(200, {
        'message': 'Contacto guardado y suscrito. Confirmación enviada automáticamente.',
        'contactId': contact_id,
        'subscriptionArn': subscription_result['subscriptionArn'],
        'endpoint': subscription_result['endpoint'],
        'awaitingConfirmation': subscription_result.get('awaitingConfirmation')
    })


def send_contact_message(message_text, message_id):
    contacts = get_contacts_by_message_id(message_id)
    
    if not contacts:
        return response(404, {'error': 'No se encontraron contactos con ese ID'})
    
    results = send_messages(contacts, message_text, message_id)
    
    return response(200, {
        'message': 'Mensajes enviados',
        'results': results
    })


def validate_phone(data):
    lada = data.get('lada', '')
    number = data.get('number', '')
    
    if not lada or not number:
        return {'valid': False, 'message': 'Lada y número son requeridos'}
    
    if not lada.startswith('+'):
        return {'valid': False, 'message': 'Lada debe empezar con +'}
    
    if not number.isdigit():
        return {'valid': False, 'message': 'Número debe contener solo dígitos'}
    
    if len(number) < 10 or len(number) > 15:
        return {'valid': False, 'message': 'Número debe tener entre 10 y 15 dígitos'}
    
    return {'valid': True, 'message': 'Teléfono válido'}


def validate_email(data):
    email = data.get('email', '')
    domain = data.get('domains', '')
    
    if not email or not domain:
        return {'valid': False, 'message': 'Email y dominio son requeridos'}
    
    if not domain.startswith('@'):
        return {'valid': False, 'message': 'Dominio debe empezar con @'}
    
    full_email = email + domain
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, full_email):
        return {'valid': False, 'message': 'Formato de email inválido'}
    
    return {'valid': True, 'message': 'Email válido'}


def check_existing_contact(contact_type, full_contact):
    try:
        if contact_type == 'phone':
            response = table.scan(
                FilterExpression=Attr('fullNumber').eq(full_contact)
            )
        else:
            response = table.scan(
                FilterExpression=Attr('fullEmail').eq(full_contact)
            )
        
        items = response.get('Items', [])
        
        if items:
            return items[0]
        
        return None
        
    except Exception as e:
        print(f"Error verificando contacto existente: {str(e)}")
        return None


def save_contact_phone(contact_id, lada, number, full_number, message_id, subscription_arn):
    item = {
        'contactId': contact_id,
        'type': 'phone',
        'lada': lada,
        'number': number,
        'fullNumber': full_number,
        'confirmed': False,
        'createdAt': datetime.now().isoformat(),
        'status': 'pending_confirmation',
        'lastMessageId': message_id
    }
    
    if subscription_arn:
        item['subscriptionArn'] = subscription_arn
    
    print(f"Guardando item en DynamoDB: {json.dumps(item, default=str)}")
    table.put_item(Item=item)
    print(f"Item guardado con ID: {contact_id}")


def save_contact_email(contact_id, email, domains, full_email, message_id, subscription_arn):
    item = {
        'contactId': contact_id,
        'type': 'email',
        'email': email,
        'domains': domains,
        'fullEmail': full_email,
        'confirmed': False,
        'createdAt': datetime.now().isoformat(),
        'status': 'pending_confirmation',
        'lastMessageId': message_id
    }
    
    if subscription_arn:
        item['subscriptionArn'] = subscription_arn
    
    print(f"Guardando item en DynamoDB: {json.dumps(item, default=str)}")
    table.put_item(Item=item)
    print(f"Item guardado con ID: {contact_id}")


def subscribe_phone_to_sns(full_number, contact_id):
    try:
        print(f"Suscribiendo SMS: {full_number} al topic {SNS_TOPIC_ARN}")
        
        subscribe_response = sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='sms',
            Endpoint=full_number,
            Attributes={
                'FilterPolicy': json.dumps({
                    'contactId': [contact_id]
                }),
                'FilterPolicyScope': 'MessageAttributes'
            },
            ReturnSubscriptionArn=True
        )
        
        subscription_arn = subscribe_response['SubscriptionArn']
        print(f"Suscripción creada: {subscription_arn}")
        
        awaiting = subscription_arn == 'pending confirmation'
        
        return {
            'success': True,
            'subscriptionArn': subscription_arn,
            'endpoint': full_number,
            'protocol': 'sms',
            'awaitingConfirmation': awaiting
        }
        
    except Exception as e:
        print(f"Error suscribiendo a SNS: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def subscribe_email_to_sns(full_email, contact_id):
    try:
        print(f"Suscribiendo email: {full_email} al topic {SNS_TOPIC_ARN}")
        
        subscribe_response = sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=full_email,
            Attributes={
                'FilterPolicy': json.dumps({
                    'contactId': [contact_id]
                }),
                'FilterPolicyScope': 'MessageAttributes'
            },
            ReturnSubscriptionArn=True
        )
        
        subscription_arn = subscribe_response['SubscriptionArn']
        print(f"Suscripción creada: {subscription_arn}")
        
        awaiting = subscription_arn == 'pending confirmation'
        
        return {
            'success': True,
            'subscriptionArn': subscription_arn,
            'endpoint': full_email,
            'protocol': 'email',
            'awaitingConfirmation': awaiting
        }
        
    except Exception as e:
        print(f"Error suscribiendo a SNS: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def get_contacts_by_message_id(message_id):
    try:
        response = table.scan(
            FilterExpression=Attr('lastMessageId').eq(message_id) & 
                           Attr('subscriptionArn').exists() & 
                           Attr('subscriptionArn').ne('pending confirmation')
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error obteniendo contactos: {str(e)}")
        return []


def delete_contacts_by_message_id(message_id):
    try:
        response = table.scan(
            FilterExpression=Attr('lastMessageId').eq(message_id)
        )
        
        items = response.get('Items', [])
        
        deleted_count = 0
        for item in items:
            contact_id = item.get('contactId')
            subscription_arn = item.get('subscriptionArn', '')
            
            try:
                if subscription_arn and subscription_arn != 'pending confirmation':
                    try:
                        sns.unsubscribe(SubscriptionArn=subscription_arn)
                        print(f"Suscripción SNS eliminada: {subscription_arn}")
                    except Exception as e:
                        print(f"Error eliminando suscripción SNS {subscription_arn}: {str(e)}")
                
                table.delete_item(Key={'contactId': contact_id})
                deleted_count += 1
                print(f"Contacto eliminado: {contact_id}")
            except Exception as e:
                print(f"Error eliminando contacto {contact_id}: {str(e)}")
        
        print(f"Total de contactos eliminados: {deleted_count}")
        return deleted_count
        
    except Exception as e:
        print(f"Error en delete_contacts_by_message_id: {str(e)}")
        return 0


def send_messages(contacts, message_text, message_id):
    results = {
        'total': len(contacts),
        'sent': 0,
        'failed': 0,
        'details': []
    }
    
    for contact in contacts:
        try:
            subscription_arn = contact.get('subscriptionArn', '')
            
            if subscription_arn == 'pending confirmation':
                results['failed'] += 1
                results['details'].append({
                    'contactId': contact['contactId'],
                    'type': contact['type'],
                    'success': False,
                    'error': 'Suscripción pendiente de confirmación'
                })
                continue
            
            result = publish_to_topic(contact, message_text, message_id)
            
            if result['success']:
                results['sent'] += 1
                update_contact_status(contact['contactId'], 'sent', message_id)
            else:
                results['failed'] += 1
                update_contact_status(contact['contactId'], 'failed', message_id, result.get('error'))
            
            results['details'].append({
                'contactId': contact['contactId'],
                'type': contact['type'],
                'success': result['success'],
                'error': result.get('error')
            })
            
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'contactId': contact['contactId'],
                'success': False,
                'error': str(e)
            })
    

    x = delete_contacts_by_message_id(message_id)
    return results


def publish_to_topic(contact, message, message_id):
    try:
        publish_params = {
            'TopicArn': SNS_TOPIC_ARN,
            'Message': message,
            'MessageAttributes': {
                'contactId': {
                    'DataType': 'String',
                    'StringValue': contact['contactId']
                }
            }
        }
        
        if contact['type'] == 'email':
            publish_params['Subject'] = 'Notificación'
        
        print(f"Publicando mensaje a {contact['type']}: {contact.get('fullNumber') or contact.get('fullEmail')}")
        
        response = sns.publish(**publish_params)
        
        print(f"Mensaje publicado exitosamente. MessageId: {response['MessageId']}")
        
        return {
            'success': True,
            'messageId': response['MessageId']
        }
        
    except Exception as e:
        print(f"Error publicando mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }


def update_contact_status(contact_id, status, message_id, error=None):
    try:
        update_expr = 'SET #status = :status, lastMessageId = :msgId, updatedAt = :updated'
        expr_values = {
            ':status': status,
            ':msgId': message_id,
            ':updated': datetime.now().isoformat()
        }
        
        if error:
            update_expr += ', lastError = :error'
            expr_values[':error'] = error
        
        table.update_item(
            Key={'contactId': contact_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expr_values
        )
    except Exception as e:
        print(f"Error actualizando contacto {contact_id}: {str(e)}")


def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST,OPTIONS"
        },
        'body': json.dumps(body)
    }
